"""
Required pydantic models for API
"""
from .base_models import BaseModel


class Header(BaseModel):
    pass


class Footer(BaseModel):
    pass


class EntryNodeCreate(BaseModel):
    name: str
    main_language_code: str
