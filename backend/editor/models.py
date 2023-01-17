"""
Required pydantic models for API
"""
from typing import List

from fastapi import Query
from pydantic import BaseModel


class Marginal(BaseModel):
    preceding_lines: List


class Header(Marginal):
    pass


class Footer(Marginal):
    pass


# Models for FastAPI


class Entry:
    result: []


class CommonParameters:
    branch = "branch"
    taxonomy_name = "taxonomy_name"


class ImportFromGithubParameters(CommonParameters):
    pass


class ImportFromGithubResponse(BaseModel):
    status: str


class CreateNodeParameters(CommonParameters):
    pass


class EditEntryParameters(CommonParameters):
    entry: str


class EditEntryResponse(BaseModel):
    result: list[Entry] = Query(default=[])


class EditChildrenParameters(CommonParameters):
    entry: str


class EditChildrenResponse(BaseModel):
    result = []


class EditSynonymParameters(CommonParameters):
    entry: str


class EditSynonymResponse(BaseModel):
    result = []


class EditHeaderParameters(CommonParameters):
    incoming_data: Header


class EditHeaderResponse(BaseModel):
    result: []


class EditFooterParameters(CommonParameters):
    incoming_data: Footer


class EditFooterResponse(BaseModel):
    result: []
