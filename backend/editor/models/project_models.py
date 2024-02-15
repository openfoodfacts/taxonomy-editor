from enum import Enum

from .base_models import BaseModel
from .types.datetime import DateTime


# Project status states
# --> LOADING --> OPEN --> EXPORTED
#        |------> FAILED
class ProjectStatus(str, Enum):
    OPEN = "OPEN"
    EXPORTED = "EXPORTED"
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
    github_checkout_commit_sha: str | None = None
    github_file_latest_sha: str | None = None
    github_pr_url: str | None = None


class ProjectEdit(BaseModel):
    status: ProjectStatus | None = None
    github_checkout_commit_sha: str | None = None
    github_file_latest_sha: str | None = None
    github_pr_url: str | None = None
