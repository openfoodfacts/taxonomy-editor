"""
Required pydantic models for API
"""

from enum import StrEnum

from .base_models import BaseModel
from .types.datetime import DateTime


class NodeType(StrEnum):
    TEXT = "TEXT"
    SYNONYMS = "SYNONYMS"
    STOPWORDS = "STOPWORDS"
    ENTRY = "ENTRY"


class Header(BaseModel):
    pass


class Footer(BaseModel):
    pass


class EntryNodeCreate(BaseModel):
    name: str
    main_language_code: str


class ErrorNode(BaseModel):
    id: str
    taxonomy_name: str
    branch_name: str
    created_at: DateTime
    warnings: list[str]
    errors: list[str]
