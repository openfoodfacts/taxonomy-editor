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


class CommonParameters:
    branch = "branch"
    taxonomy_name = "taxonomy_name"


parameters = CommonParameters()


class ImportFromGithubParameters(BaseModel):
    parameters.parameters.branch: str
    parameters.parameters.taxonomy_name: str


class ImportFromGithubResponse(BaseModel):
    status: str


class CreateNodeParameters(BaseModel):
    parameters.parameters.branch: str
    parameters.parameters.taxonomy_name: str


class EditEntryParameters(BaseModel):
    parameters.branch: str
    parameters.taxonomy_name: str
    entry: str


class EditEntryResponse(BaseModel):
    result = []


class EditChildrenParameters(BaseModel):
    parameters.branch: str
    parameters.taxonomy_name: str
    entry: str


class EditChildrenResponse(BaseModel):
    result = []


class EditSynonymParameters(BaseModel):
    parameters.branch: str
    parameters.taxonomy_name: str
    entry: str


class EditSynonymResponse(BaseModel):
    result = []


class EditHeaderParameters(BaseModel):
    incoming_data: Header
    parameters.branch: str
    parameters.taxonomy_name: str


class EditHeaderResponse(BaseModel):
    result: []


class EditFooterParameters(BaseModel):
    incoming_data: Footer
    parameters.branch: str
    parameters.taxonomy_name: str


class EditFooterResponse(BaseModel):
    result: []
