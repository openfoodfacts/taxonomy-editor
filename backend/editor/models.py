"""
Required pydantic models for API
"""
from typing import List

from pydantic import BaseModel


class Marginal(BaseModel):
    preceding_lines: List


class Header(Marginal):
    pass


class Footer(Marginal):
    pass


# Models for FastAPI


class ImportFromGithubParameters(BaseModel):
    branch: str
    taxonomy_name: str


class ImportFromGithubResponse(BaseModel):
    status: str


class CreateNodeParameters(BaseModel):
    branch: str
    taxonomy_name: str


class EditEntryParameters(BaseModel):
    branch: str
    taxonomy_name: str
    entry: str


class EditEntryResponse(BaseModel):
    result = []


class EditChildrenParameters(BaseModel):
    branch: str
    taxonomy_name: str
    entry: str


class EditChildrenResponse(BaseModel):
    result = []


class EditSynonymParameters(BaseModel):
    branch: str
    taxonomy_name: str
    entry: str


class EditSynonymResponse(BaseModel):
    result = []


class EditHeaderParameters(BaseModel):
    incoming_data: Header
    branch: str
    taxonomy_name: str


class EditHeaderResponse(BaseModel):
    result: []


class EditFooterParameters(BaseModel):
    incoming_data: Footer
    branch: str
    taxonomy_name: str


class EditFooterResponse(BaseModel):
    result: []
