from enum import Enum
from neo4j.time import DateTime
from .base_models import BaseModel


class ProjectStatus(str, Enum):
    """
    Enum for project status filter
    """

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    LOADING = "LOADING"
    FAILED = "FAILED"


class ProjectCreate(BaseModel):
    id: str
    status: ProjectStatus = ProjectStatus.LOADING
    taxonomy_name: str
    branch_name: str
    description: str
    is_from_github: bool


class Project(ProjectCreate):
    created_at: DateTime
    github_commit_sha: str | None
    github_file_sha: str | None


class ProjectEdit(BaseModel):
    status: ProjectStatus | None = None
    github_commit_sha: str | None = None
    github_file_sha: str | None = None
