from openfoodfacts_taxonomy_parser import utils as parser_utils

from ..graph_db import get_current_transaction
from ..models.node_models import EntryNodeCreate


async def delete_project_nodes(project_id: str):
    """
    Remove all nodes for project.
    This includes entries, stopwords, synonyms and errors
    """

    query = f"""
    MATCH (n:{project_id})
    DETACH DELETE n
    """
    await get_current_transaction().run(query)


async def create_entry_node(
    project_id: str, entry_node: EntryNodeCreate, stopwords: dict[str, list[str]]
) -> str:
    """
    Creates a new entry node in the database
    """
    # Create params dict
    params = {"entry_node": {"main_language": entry_node.main_language_code, "preceding_lines": []}}

    # Add tags and normalized tags for each language
    for language_code, tags in entry_node.tags.items():
        normalized_tags = [
            parser_utils.normalize_text(tag, language_code, stopwords=stopwords) for tag in tags
        ]
        params["entry_node"][f"tags_{language_code}"] = tags
        params["entry_node"][f"tags_ids_{language_code}"] = normalized_tags

    # Add node id
    params["entry_node"]["id"] = (
        entry_node.main_language_code
        + ":"
        + params["entry_node"][f"tags_ids_{entry_node.main_language_code}"][0]
    )

    query = f"""
    CREATE (n:{project_id}:ENTRY $entry_node)
    RETURN n.id
    """

    result = await get_current_transaction().run(query, params)
    return (await result.data())[0]["n.id"]
