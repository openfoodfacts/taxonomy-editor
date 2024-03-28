from enum import StrEnum
from typing import Any

from pydantic import model_validator

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


class EntryNode(BaseModel):
    id: str
    preceding_lines: list[str]
    src_position: int
    main_language: str
    tags: dict[str, list[str]]
    properties: dict[str, str]
    comments: dict[str, list[str]]
    is_external: bool = False
    original_taxonomy: str | None = None

    @model_validator(mode="before")
    @classmethod
    def construct_tags_and_properties_and_comments(cls, data: Any) -> Any:
        """
        Before model validation, construct tags, properties, and comments from the data dict.
        Usage docs: https://docs.pydantic.dev/latest/concepts/validators/#model-validators
        """
        if not isinstance(data, dict):
            return data

        is_tag_property_or_comment = (
            lambda key: key.startswith("tags_")
            or key.startswith("prop_")
            or key.endswith("_comments")
        )

        parsed_data = {
            key: value for key, value in data.items() if not is_tag_property_or_comment(key)
        }

        parsed_data["tags"] = parsed_data.get("tags", {})
        parsed_data["properties"] = parsed_data.get("properties", {})
        parsed_data["comments"] = parsed_data.get("comments", {})

        for key, value in data.items():
            if key.endswith("_comments"):
                parsed_data["comments"][key] = value
            elif key.startswith("tags_"):
                parsed_data["tags"][key] = value
            elif key.startswith("prop_"):
                parsed_data["properties"][key] = value

        return parsed_data


class ErrorNode(BaseModel):
    id: str
    taxonomy_name: str
    branch_name: str
    created_at: DateTime
    warnings: list[str]
    errors: list[str]
