"""
Required pydantic models for API
"""
from typing import List

from fastapi import Query
from pydantic import BaseModel, BaseConfig, validate_arguments

BaseConfig.arbitrary_types_allowed = True


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

class Entry:
    default: []
    title: str
    description: str

class ImportFromGithubParameters(CommonParameters):
    pass


class ImportFromGithubResponse(BaseModel):
    status: bool


class CreateNodeParameters(CommonParameters):
    pass


class EditEntryParameters(CommonParameters):
    entry: str


class EditEntryResponse(BaseModel):
    result: list[Entry] = Query(
        default=[], title="Result of edited entry", description="Returns a list of Entry objects"
    )


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
    result: dict


class EditFooterParameters(CommonParameters):
    incoming_data: Footer


class EditFooterResponse(BaseModel):
    result: dict
