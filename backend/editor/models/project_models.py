from enum import Enum
from pydantic import BaseModel


class ProjectStatus(str, Enum):
    """
    Enum for project status filter
    """

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    LOADING = "LOADING"
    FAILED = "FAILED"


class Project(BaseModel):
    id: str
    status: ProjectStatus
    taxonomy_name: str
    branch_name: str
    description: str
    created_at: str
    is_from_github: bool


class ProjectEdit(BaseModel):
    status: ProjectStatus | None = None
