from dataclasses import dataclass
import math
from ..models.node_models import EntryNode, EntryNodeSearchResult
from ..graph_db import get_current_transaction

from openfoodfacts_taxonomy_parser import utils as parser_utils


@dataclass
class FilterSearchTerm:
    filter_name: str
    filter_value: str


@dataclass
class Query:
    project_id: str
    name_search_term: str | None
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
        # If we are not inside quotes and we encounter a whitespace, we are at the end of the current search term
        elif query[term_end] == " " and not inside_quotes:
            search_term = query[term_start:term_end]
            search_terms.append(search_term)
            term_start = term_end + 1

    search_terms.append(query[term_start:])

    return search_terms


def is_name_search_term(search_term: str) -> bool:
    """
    Check if search term is a name
    """
    return search_term.startswith('"') or ":" not in search_term


def validate_name_search_term(search_term: str) -> str | None:
    if search_term.startswith('"') and search_term.endswith('"'):
        search_term = search_term[1:-1]

    if '"' in search_term:
        return None

    return search_term


def validate_filter_search_term(search_term: str) -> FilterSearchTerm | None:
    if ":" not in search_term:
        return None

    filter_name, filter_value = search_term.split(":", maxsplit=1)

    if filter_value.startswith('"') and filter_value.endswith('"'):
        filter_value = filter_value[1:-1]

    if '"' in filter_value:
        return None

    return FilterSearchTerm(filter_name, filter_value)


def validate_query(project_id: str, query: str) -> Query | None:
    """
    A query is composed of search terms separated by whitespaces.
    A search term is either a name search term or a filter search term.

    A name search term is unique and is surrounded by quotes if it contains whitespaces or semi-colons. It cannot contain quotes.
    The name search term allows for a text search on a node's tags.

    A filter search term is of the format `filter:value`. Some filters can sometimes be negated with the format `not(filter):value`.
    The `value` is surrounded by quotes if it contains whitespaces. The value cannot contain quotes.

    The possible filters are:
      - `is`: `root` is the only possible value. It allows to filter on the root nodes. It cannot be negated.
      - `language`: the value is a language code. It allows to filter on if the language exists on the node. It can be negated.
      - `parent`: the value is a node's id. It allows to filter on if the node is a parent of the node with the given id. It cannot be negated.
      - `child`: the value is a node's id. It allows to filter on if the node is a child of the node with the given id. It cannot be negated.
      - `ancestor`: the value is a node's id. It allows to filter on if the node is an ancestor of the node with the given id. It cannot be negated.
      - `descendant`: the value is a node's id. It allows to filter on if the node is a descendant of the node with the given id. It cannot be negated.

    Examples:
    - "is:root language:en not(language):fr"
    - "parent:"en:apple juice" descendant:en:juices "fruit concentrate""
    """

    search_terms = split_query_into_search_terms(query)

    name_search_term = None
    filter_search_terms = []

    for search_term in search_terms:
        if is_name_search_term(search_term):
            if name_search_term is not None:
                return None

            name_search_term = validate_name_search_term(search_term)
            if name_search_term is None:
                return None

        else:
            filter_search_term = validate_filter_search_term(search_term)
            if filter_search_term is None:
                return None

            filter_search_terms.append(filter_search_term)

    return Query(project_id, name_search_term, filter_search_terms)


def build_cypher_name_search_term(
    project_id: str, search_value: str
) -> tuple[str, str, dict[str, str]] | None:
    """
    The name search term can trigger two types of searches:
    - if the search value is in the format `language_code:search_value`, it triggers a fuzzy search on the tags_ids_{language_code} index with the normalized search value
    - else it triggers a fuzzy search on the tags_ids index with the normalized search value
    """
    language_code = None

    if search_value[2] == ":" and search_value[0:2].isalpha():
        language_code, search_value = search_value.split(":", maxsplit=1)
        language_code = language_code.lower()
        normalized_text = parser_utils.normalize_text(search_value, language_code)
    else:
        normalized_text = parser_utils.normalize_text(search_value)

    # If normalized text is empty, no searches are found
    if normalized_text.strip() == "":
        return None

    tags_ids_index = project_id + "_SearchTagsIds"
    fuzzy_query = normalized_text + "~"

    if language_code is not None:
        fuzzy_query = f"tags_ids_{language_code}:{fuzzy_query}"

    query_params = {
        "tags_ids_index": tags_ids_index,
        "fuzzy_query": fuzzy_query,
    }

    query = """
            CALL db.index.fulltext.queryNodes($tags_ids_index, $fuzzy_query)
            YIELD node, score
            WHERE score > 0.1
            WITH node.id AS nodeId 
            WITH COLLECT(nodeId) AS nodeIds
        """

    where_clause = "n.id IN nodeIds"

    return query, where_clause, query_params


def get_query_param_name(index: int) -> str:
    return f"value_{index}"


def build_cypher_is_search_term(search_value: str) -> tuple[str, None] | None:
    match search_value:
        case "root":
            return "NOT (n)-[:is_child_of]->()", None
        case _:
            return None


def build_cypher_language_search_term(
    search_value: str, negated: bool = False
) -> tuple[str, None] | None:
    if len(search_value) != 2 and search_value.isalpha():
        return None

    if negated:
        return f"n.tags_ids_{search_value} IS NULL", None
    else:
        return f"n.tags_ids_{search_value} IS NOT NULL", None


def build_cypher_parent_search_term(index: int, search_value: str) -> tuple[str, str]:
    return "(n)<-[:is_child_of]-(:ENTRY {id: $" + get_query_param_name(index) + "})", search_value


def build_cypher_child_search_term(index: int, search_value: str) -> tuple[str, str]:
    return "(n)-[:is_child_of]->(:ENTRY {id: $" + get_query_param_name(index) + "})", search_value


def build_cypher_ancestor_search_term(index: int, search_value: str) -> tuple[str, str]:
    return "(n)<-[:is_child_of*]-(:ENTRY {id: $" + get_query_param_name(index) + "})", search_value


def build_cypher_descendant_search_term(index: int, search_value: str) -> tuple[str, str]:
    return "(n)-[:is_child_of*]->(:ENTRY {id: $" + get_query_param_name(index) + "})", search_value


def build_cypher_filter_search_term(
    enumerate_pair: tuple[int, FilterSearchTerm]
) -> tuple[str, str | None] | None:
    index, search_term = enumerate_pair
    match search_term.filter_name:
        case "is":
            return build_cypher_is_search_term(search_term.filter_value)
        case "language":
            return build_cypher_language_search_term(search_term.filter_value)
        case "not(language)":
            return build_cypher_language_search_term(search_term.filter_value, negated=True)
        case "parent":
            return build_cypher_parent_search_term(index, search_term.filter_value)
        case "child":
            return build_cypher_child_search_term(index, search_term.filter_value)
        case "ancestor":
            return build_cypher_ancestor_search_term(index, search_term.filter_value)
        case "descendant":
            return build_cypher_descendant_search_term(index, search_term.filter_value)
        case _:
            return None


def build_cypher_query(query: Query, skip: int, limit: int) -> tuple[str, dict[str, str]] | None:
    cypher_name_search_term = (
        build_cypher_name_search_term(query.project_id, query.name_search_term)
        if query.name_search_term is not None
        else None
    )

    cypher_filter_search_terms = list(
        map(build_cypher_filter_search_term, enumerate(query.filter_search_terms))
    )

    if None in cypher_filter_search_terms:
        return None

    full_text_search_query = ""
    query_params = {}

    if cypher_name_search_term is not None:
        full_text_search_query, name_filter_search_term, query_params = cypher_name_search_term
        cypher_filter_search_terms.append((name_filter_search_term, None))

    query_params |= {
        get_query_param_name(index): cypher_filter_search_term[1]
        for index, cypher_filter_search_term in enumerate(cypher_filter_search_terms)
    }

    combined_filter_query = (
        f"WHERE {' AND '.join(map(lambda x: x[0], cypher_filter_search_terms))}"
        if cypher_filter_search_terms
        else ""
    )

    base_query = f"""
    {full_text_search_query}
    MATCH (n:{query.project_id}:ENTRY)
    {combined_filter_query}
    """

    page_subquery = f"""
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

    if query is None:
        return EntryNodeSearchResult()

    PAGE_LENGTH = 50
    skip = max(0, (page - 1) * PAGE_LENGTH)

    cypher_query = build_cypher_query(query, skip, PAGE_LENGTH)

    if cypher_query is None:
        return EntryNodeSearchResult()

    page_query, count_query, query_params = cypher_query

    result = await get_current_transaction().run(page_query, query_params)
    search_result = await result.single()
    if search_result is None:
        count_result = await get_current_transaction().run(count_query, query_params)
        node_count = (await count_result.single())["nodeCount"]
        return EntryNodeSearchResult(
            node_count=node_count,
            page_count=math.ceil(node_count / PAGE_LENGTH),
            nodes=[],
        )

    node_count, nodes = search_result["nodeCount"], search_result["nodeList"]
    return EntryNodeSearchResult(
        node_count=node_count,
        page_count=math.ceil(node_count / PAGE_LENGTH),
        nodes=[EntryNode(**node) for node in nodes],
    )
