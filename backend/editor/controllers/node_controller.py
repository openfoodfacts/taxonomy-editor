import datetime
import logging

from openfoodfacts_taxonomy_parser import utils as parser_utils

from ..graph_db import get_current_transaction
from ..models.node_models import EntryNode, EntryNodeCreate, ErrorNode
from .utils.result_utils import get_unique_record

log = logging.getLogger(__name__)


async def delete_project_nodes(project_id: str):
    """
    Remove all nodes for project.
    This includes entries, stopwords, synonyms, errors and removed entries
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
    name, language_code = entry_node.name, entry_node.main_language_code
    normalized_name = parser_utils.normalize_text(name, language_code, stopwords=stopwords)

    # Create params dict
    entry_node_data = {
        "main_language": language_code,
        "preceding_lines": [],
        "id": language_code + ":" + normalized_name,
        f"tags_{language_code}": [name],
        f"tags_ids_{language_code}": [normalized_name],
        "modified": datetime.datetime.now().timestamp(),
    }
    params = {"entry_node": entry_node_data}

    query = f"""
    CREATE (n:{project_id}:ENTRY $entry_node)
    RETURN n.id
    """

    result = await get_current_transaction().run(query, params)
    return (await result.data())[0]["n.id"]


async def get_entry_node(project_id: str, node_id: str) -> EntryNode:
    query = (
        f"""
        MATCH (n:{project_id}:ENTRY
        """
        + """{id: $node_id})
        RETURN n
        """
    )
    params = {"node_id": node_id}
    result = await get_current_transaction().run(query, params)

    entry_record = await get_unique_record(result, node_id)
    node = EntryNode(**entry_record["n"])
    return node


async def get_error_node(project_id: str) -> ErrorNode | None:
    query = """
    MATCH (n:ERRORS {id: $project_id})
    RETURN n
    """
    params = {"project_id": project_id}
    result = await get_current_transaction().run(query, params)
    error_node = await result.single()
    if error_node is None:
        return None
    return ErrorNode(**error_node["n"])
