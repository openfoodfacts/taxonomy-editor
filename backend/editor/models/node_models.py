"""
Required pydantic models for API
"""
from enum import Enum

from .base_models import BaseModel


class NodeType(str, Enum):
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
