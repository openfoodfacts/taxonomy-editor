from ..graph_db import get_current_transaction
from ..models.project_models import Project, ProjectCreate, ProjectEdit


async def get_project(project_id: str) -> Project:
    """
    Get project by id
    """
    query = """
    MATCH (p:PROJECT {id: $project_id})
    RETURN p
    """
    params = {"project_id": project_id}
    result = await get_current_transaction().run(query, params)
    return Project(**(await result.single())["p"])


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
