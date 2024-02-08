"""
Required pydantic models for API
"""
from .base_models import BaseModel


class Header(BaseModel):
    pass


class Footer(BaseModel):
    pass


class EntryNodeCreate(BaseModel):
    main_language_code: str
    tags: dict[str, list[str]]  # {language_code: [tag1, tag2, ...]}
