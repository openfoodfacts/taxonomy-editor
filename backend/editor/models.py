"""
Required pydantic models for API
"""
from typing import List

from fastapi import Query
from pydantic import BaseConfig, BaseModel

BaseConfig.arbitrary_types_allowed = True


class Marginal(BaseModel):
    preceding_lines: List = Query(description="A list of preceding lines")


class Header(Marginal):
    pass


class Footer(Marginal):
    pass


class CommonParameters(BaseModel):
    branch: str = Query(description="Name of the branch")
    taxonomy_name: str = Query(description="Name of the taxonomy")


class Entry(CommonParameters):
    entry: str = Query(description="Name of the entry")
    id: str = Query(description="Id of the entry")


class ImportFromGithubParameters(CommonParameters):
    pass


class ImportFromGithubResponse(BaseModel):
    status: bool = Query(description="True if import was successful")


class CreateNodeParameters(CommonParameters):
    pass


class EditEntryParameters(CommonParameters):
    entry: str = Query(description="Name of the entry")


class EditEntryResponse(BaseModel):
    result: List[Entry]


class EditChildrenParameters(CommonParameters):
    entry: str = Query(description="Name of the entry")


class EditChildrenResponse(BaseModel):
    result: List


class EditSynonymParameters(CommonParameters):
    entry: str = Query(description="Name of the entry")


class EditSynonymResponse(BaseModel):
    result: List


class EditHeaderParameters(CommonParameters):
    incoming_data: Header


class EditHeaderResponse(BaseModel):
    result: dict


class EditFooterParameters(CommonParameters):
    incoming_data: Footer


class EditFooterResponse(BaseModel):
    result: dict
