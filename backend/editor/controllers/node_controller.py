from ..graph_db import get_current_transaction


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
