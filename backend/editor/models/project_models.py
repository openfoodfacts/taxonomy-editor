from datetime import datetime
from enum import Enum
from typing import Any

from neo4j.time import DateTime
from pydantic import field_validator

from .base_models import BaseModel


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
    created_at: datetime
    github_checkout_commit_sha: str | None = None
    github_file_latest_sha: str | None = None
    github_pr_url: str | None = None

    @field_validator("created_at", mode="before")
    @classmethod
    def convert_to_native_datetime(cls, v: Any) -> datetime:
        if not isinstance(v, DateTime):
            raise ValueError("Unexpected type for created_at, expected neo4j.time.DateTime")
        return v.to_native()


class ProjectEdit(BaseModel):
    status: ProjectStatus | None = None
    github_checkout_commit_sha: str | None = None
    github_file_latest_sha: str | None = None
    github_pr_url: str | None = None
