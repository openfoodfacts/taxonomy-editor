from ..graph_db import get_current_transaction
from ..models.project_models import Project, ProjectCreate, ProjectEdit, ProjectStatus
from .node_controller import delete_project_nodes
from .utils.result_utils import get_unique_record


def get_project_id(branch_name: str, taxonomy_name: str) -> str:
    return "p_" + taxonomy_name + "_" + branch_name


def eventually_remove_keys(query, params, exclude_props, source_name="_p", target_name="p"):
    """Eventually remove keys from a node

    the query must contains a '_p as p' clause (or with source / target name)
    """
    if exclude_props:
        names = (source_name, target_name)
        original = "%s as %s" % names
        new = "apoc.map.removeKeys(%s {.*}, $exclude_props) as %s" % names
        query = query.replace(original, new)
        params = dict(params, exclude_props=exclude_props)
    return query, params


async def get_project(project_id: str, exclude_props=["original_text"]) -> Project:
    """
    Get project by id

    By default we exclude original_text property which is heavy
    """
    query = """
    MATCH (_p:PROJECT {id: $project_id})
    RETURN _p as p
    """
    params = {"project_id": project_id}
    query, params = eventually_remove_keys(query, params, exclude_props)
    result = await get_current_transaction().run(query, params)
    project_record = await get_unique_record(result, project_id)
    return Project(**project_record["p"])


async def get_projects_by_status(status: ProjectStatus, exclude_props=["original_text"]) -> list[Project]:
    """
    Get projects by status
    """
    query = """
    MATCH (_p:PROJECT {status: $status})
    RETURN _p as p
    """
    params = {"status": status}
    query, params = eventually_remove_keys(query, params, exclude_props)
    result = await get_current_transaction().run(query, params)
    return [Project(**record["p"]) async for record in result]


async def get_all_projects(exclude_props=["original_text"]) -> list[Project]:
    query = """
    MATCH (_p:PROJECT)
    RETURN _p as p
    ORDER BY p.created_at DESC
    """
    params = {}
    query, params = eventually_remove_keys(query, params, exclude_props)
    result = await get_current_transaction().run(query, params)
    return [Project(**record["p"]) async for record in result]


async def create_project(project: ProjectCreate):
    """
    Create project
    """
    query = """
    CREATE (p:PROJECT $project) SET p.created_at = datetime()
    """
    params = {"project": project.model_dump()}
    await get_current_transaction().run(query, params)


async def edit_project(project_id: str, project_edit: ProjectEdit):
    """
    Edit project
    """
    query = """
    MATCH (p:PROJECT {id: $project_id})
    SET p += $project_edit
    """
    params = {
        "project_id": project_id,
        "project_edit": project_edit.model_dump(exclude_unset=True),
    }
    await get_current_transaction().run(query, params)


async def delete_project(project_id: str):
    """
    Delete project, its nodes and relationships
    """
    query = """
    MATCH (p:PROJECT {id: $project_id})
    DETACH DELETE p
    """
    params = {"project_id": project_id}
    await get_current_transaction().run(query, params)
    await delete_project_nodes(project_id)


async def clone_project(source_branch: str, taxonomy_name: str, target_branch: str):
    """
    Clone a project using a new branch name

    Currently used for tests only.
    """
    source_id = get_project_id(source_branch, taxonomy_name)
    target_id = get_project_id(target_branch, taxonomy_name)
    # clone project node
    query = """
        MATCH (p:PROJECT {id: $project_id})
        WITH p
        CALL apoc.refactor.cloneNodes([p], true, ['id', 'branch'] )
        YIELD output as new_node
        WITH new_node
        SET new_node.created_at = datetime(),
            new_node.branch_name = $target_branch,
            new_node.id = $target_id
        RETURN new_node
    """
    params = {
        "project_id": source_id,
        "target_branch": target_branch,
        "target_id": get_project_id(target_branch, taxonomy_name),
    }
    await get_current_transaction().run(query, params)
    # clone nodes thanks to apoc.refactor.cloneSubgraph
    query = f"""
        MATCH (n:{source_id})
        WITH collect(n) AS source_nodes
        CALL apoc.refactor.cloneSubgraph(source_nodes)
        YIELD output as new_node
        WITH new_node
        REMOVE new_node:{source_id}
        SET new_node:{target_id}
    """
    await get_current_transaction().run(query)
