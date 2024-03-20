import math
from dataclasses import dataclass

from openfoodfacts_taxonomy_parser import utils as parser_utils
from pydantic import ValidationError

from ..graph_db import get_current_transaction
from ..models.node_models import EntryNode
from ..models.search_models import (
    CypherQuery,
    EntryNodeSearchResult,
    FilterSearchTerm,
    FilterSearchTermValidator,
)


def get_query_param_name_prefix(index: int) -> str:
    return f"value_{index}"


@dataclass(frozen=True)
class Query:
    project_id: str
    search_terms: list[str]
    name_search_terms: list[str]
    filter_search_terms: list[FilterSearchTerm]


def split_query_into_search_terms(query: str) -> list[str]:
    """
    Queries should be split by whitespaces that are not inside quotes
    """
    query = query.strip()
    search_terms = []

    inside_quotes = False
    term_start = 0

    for term_end in range(len(query)):
        if query[term_end] == '"':
            inside_quotes = not inside_quotes
        # If we are not inside quotes and we encounter a whitespace
        # we are at the end of the current search term
        elif query[term_end] == " " and not inside_quotes:
            # If the term is not empty, we add it to the list of search terms
            if term_start != term_end:
                search_term = query[term_start:term_end]
                search_terms.append(search_term)
            term_start = term_end + 1

    search_terms.append(query[term_start:])

    return search_terms


def parse_filter_search_term(search_term: str) -> FilterSearchTerm | None:
    """
    Parses a filter search term of the format `filter:value` if possible
    OR
    Returns None
    """

    if ":" not in search_term:
        return None

    filter_name, filter_value = search_term.split(":", maxsplit=1)

    if filter_value.startswith('"') and filter_value.endswith('"'):
        filter_value = filter_value[1:-1]

    # If the filter value contains quotes, it is invalid
    if '"' in filter_value:
        return None

    try:
        return FilterSearchTermValidator.validate_python(
            {"filter_type": filter_name, "filter_value": filter_value}
        )
    except ValidationError:
        return None


def validate_query(project_id: str, query: str) -> Query:
    """
    A query is composed of search terms separated by whitespaces.
    A search term is either a name search term or a filter search term.

    A filter search term is of the format `filter:value` where `filter` is a valid filter value
    and `value` is a valid search value for the particular filter.
    Some filters can sometimes be negated with the format `not(filter):value`.
    The `value` is surrounded by quotes if it contains whitespaces.
    The value cannot contain quotes.

    All other terms are considered name search terms.
    The name search term allows for a text search on a node's tags.

    The possible filters are:
      - `is`: `root` is the only possible value. It allows to filter on the root nodes.
        It cannot be negated.
      - `language`: the value is a language code. It allows to filter on if the language exists
        on the node. It can be negated.
      - `parent`: the value is a node's id. It allows to filter on if the node is a
        parent of the node with the given id. It cannot be negated.
      - `child`: the value is a node's id. It allows to filter on if the node is a child of
        the node with the given id. It cannot be negated.
      - `ancestor`: the value is a node's id. It allows to filter on if the node is an ancestor
        of the node with the given id. It cannot be negated.
      - `descendant`: the value is a node's id. It allows to filter on if the node is a descendant
        of the node with the given id. It cannot be negated.

    Examples:
    - "is:root language:en not(language):fr"
    - "parent:"en:apple juice" descendant:en:juices "fruit concentrate""
    """

    search_terms = split_query_into_search_terms(query)

    parsed_search_terms = []
    name_search_terms = []
    filter_search_terms = []

    for search_term in search_terms:
        if (filter_search_term := parse_filter_search_term(search_term)) is not None:
            filter_search_terms.append(filter_search_term)
            parsed_search_terms.append(filter_search_term.to_query_string())
        else:
            name_search_terms.append(search_term)
            parsed_search_terms.append(search_term)

    return Query(project_id, parsed_search_terms, name_search_terms, filter_search_terms)


def _get_token_query(token: str) -> str:
    """
    Returns the lucene query for a token.
    The tokens are additive and the fuzziness of the search depends on the length of the token.
    """

    token = "+" + token
    if len(token) > 10:
        return token + "~2"
    elif len(token) > 4:
        return token + "~1"
    else:
        return token


def build_lucene_name_search_query(search_value: str) -> str | None:
    """
    The name search term can trigger two types of searches:
    - if the search value is in the format `language_code:raw_search_value`,
      it triggers a search on the tags_ids_{language_code} index
    - else it triggers a search on the tags_ids index

    If the `raw_search_value` is surrounded by quotes, the search will be exact.
    Otherwise, the search is fuzzy when the search value is longer than 4 characters
    (the edit distance depends of the length of the search value)
    """
    language_code = None

    # get an eventual language prefix
    if len(search_value) > 2 and search_value[2] == ":" and search_value[0:2].isalpha():
        language_code, search_value = search_value.split(":", maxsplit=1)
        language_code = language_code.lower()

    def get_search_query() -> str | None:
        if search_value.startswith('"') and search_value.endswith('"'):
            return search_value if len(search_value) > 2 else None

        if language_code is not None:
            normalized_text = parser_utils.normalize_text(search_value, language_code)
        else:
            normalized_text = parser_utils.normalize_text(search_value)

        # If normalized text is empty, no searches are found
        if normalized_text.strip() == "":
            return None

        tokens = normalized_text.split("-")

        return "(" + " ".join(map(_get_token_query, tokens)) + ")"

    search_query = get_search_query()

    if search_query is None:
        return None

    if language_code is not None:
        search_query = f"tags_ids_{language_code}:{search_query}"

    return search_query


def build_cypher_query(query: Query, skip: int, limit: int) -> tuple[str, str, dict[str, str]]:
    # build part of the query doing full text search
    lucene_name_search_queries = list(
        filter(
            lambda q: q is not None, map(build_lucene_name_search_query, query.name_search_terms)
        )
    )

    # build part of the query for filter:value members
    cypher_filter_search_terms = [
        term.build_cypher_query(get_query_param_name_prefix(index))
        for index, term in enumerate(query.filter_search_terms)
    ]

    full_text_search_query, order_clause = "", ""
    query_params = {}

    if lucene_name_search_queries:
        SEARCH_QUERY_PARAM_NAME = "search_query"
        MIN_SEARCH_SCORE = 0.1

        full_text_search_query = f"""
            CALL db.index.fulltext.queryNodes("{query.project_id}_SearchTagsIds",
            ${SEARCH_QUERY_PARAM_NAME})
            YIELD node, score
            WHERE score > {MIN_SEARCH_SCORE}
            WITH node.id AS nodeId
            WITH COLLECT(nodeId) AS nodeIds
        """
        query_params[SEARCH_QUERY_PARAM_NAME] = " AND ".join(lucene_name_search_queries)

        order_clause = "WITH n, apoc.coll.indexOf(nodeIds, n.id) AS index ORDER BY index"

        name_filter_search_term = "n.id IN nodeIds"
        cypher_filter_search_terms.append(CypherQuery(name_filter_search_term))

    for cypher_filter_search_term in cypher_filter_search_terms:
        query_params |= cypher_filter_search_term.params

    combined_filter_query = (
        f"WHERE {' AND '.join([cypher_query.query for cypher_query in cypher_filter_search_terms])}"
        if cypher_filter_search_terms
        else ""
    )

    base_query = f"""
    {full_text_search_query}
    MATCH (n:{query.project_id}:ENTRY)
    {combined_filter_query}
    """

    page_subquery = f"""
    {order_clause}
    WITH collect(n) AS nodeList, count(n) AS nodeCount
    UNWIND nodeList AS node
    WITH node, nodeCount
    SKIP {skip} LIMIT {limit}
    WITH collect(node) AS nodeList, nodeCount
    RETURN nodeList, nodeCount;
    """

    count_subquery = """
    RETURN count(n) AS nodeCount;
    """

    page_query = base_query + page_subquery
    count_query = base_query + count_subquery

    return page_query, count_query, query_params


async def search_entry_nodes(project_id: str, raw_query: str, page: int) -> EntryNodeSearchResult:
    """
    Search for entry nodes in the database
    """
    query = validate_query(project_id, raw_query)

    parsed_query_string = " ".join(query.search_terms)
    # For better UX on the search bar
    if parsed_query_string != "":
        parsed_query_string += " "

    PAGE_LENGTH = 50
    skip = max(0, (page - 1) * PAGE_LENGTH)

    cypher_query = build_cypher_query(query, skip, PAGE_LENGTH)

    page_query, count_query, query_params = cypher_query

    result = await get_current_transaction().run(page_query, query_params)
    search_result = await result.single()

    if search_result is None:
        count_result = await get_current_transaction().run(count_query, query_params)
        node_count = (await count_result.single())["nodeCount"]
        return EntryNodeSearchResult(
            node_count=node_count,
            page_count=math.ceil(node_count / PAGE_LENGTH),
            q=parsed_query_string,
            filters=query.filter_search_terms,
        )

    node_count, nodes = search_result["nodeCount"], search_result["nodeList"]
    return EntryNodeSearchResult(
        node_count=node_count,
        page_count=math.ceil(node_count / PAGE_LENGTH),
        q=parsed_query_string,
        filters=query.filter_search_terms,
        nodes=[EntryNode(**node) for node in nodes],
    )
