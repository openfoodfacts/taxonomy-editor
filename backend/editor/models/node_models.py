import re
from enum import StrEnum
from typing import Any

from openfoodfacts_taxonomy_parser import utils as parser_utils
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
    preceding_lines: list[str] = []
    main_language: str
    tags: dict[str, list[str]]
    tags_ids: dict[str, list[str]]
    properties: dict[str, str]
    comments: dict[str, list[str]]
    is_external: bool = False
    original_taxonomy: str | None = None

    def flat_dict(self) -> dict[str, Any]:
        """
        Flatten the EntryNode model into a single dictionary.
        """
        flat_data = dict(self)
        flat_data.update(self.tags)
        del flat_data["tags"]
        flat_data.update(self.tags_ids)
        del flat_data["tags_ids"]
        flat_data.update(self.properties)
        del flat_data["properties"]
        flat_data.update(self.comments)
        del flat_data["comments"]
        return flat_data

    def recompute_tags_ids(self):
        """Recompute the tags_ids dictionary based on the tags dictionary
        and the provided stopwords."""
        self.tags_ids = {}
        for key, values in self.tags.items():
            # Normalise tags and store them in tags_ids
            keys_language_code = key.split("_", 1)[1]
            normalised_value = []
            for value in values:
                normalised_value.append(parser_utils.normalize_text(value, keys_language_code))
            self.tags_ids["tags_ids" + key[4:]] = normalised_value

    def recompute_id(self):
        """Recompute id based on main_language and tag_ids

        You must ensure you called recompute_tags_ids() before calling this method if needed
        """
        main_tag_id = self.tags_ids[f"tags_ids_{self.main_language}"][0]
        self.id = f"{self.main_language}:{main_tag_id}"

    @model_validator(mode="before")
    @classmethod
    def construct_tags_and_properties_and_comments(cls, data: Any) -> Any:
        """
        Before model validation, construct tags, properties, and comments from the data dict.
        Usage docs: https://docs.pydantic.dev/latest/concepts/validators/#model-validators
        """
        if not isinstance(data, dict):
            return data

        # Sanity check keys
        for key in data.keys():
            if not re.match(r"^\w+$", key):
                raise ValueError("Invalid key: %s", key)

        is_tag_property_or_comment = (
            lambda key: key.startswith("tags_")
            or key.startswith("prop_")
            or key.endswith("_comments")
        )

        parsed_data = {
            key: value for key, value in data.items() if not is_tag_property_or_comment(key)
        }

        parsed_data["tags"] = parsed_data.get("tags", {})
        parsed_data["tags_ids"] = parsed_data.get("tags_ids", {})
        parsed_data["properties"] = parsed_data.get("properties", {})
        parsed_data["comments"] = parsed_data.get("comments", {})

        for key, value in data.items():
            if value is None or value == []:
                continue
            if key.endswith("_comments"):
                parsed_data["comments"][key] = value
            elif key.startswith("tags_"):
                if "_ids_" in key:
                    parsed_data["tags_ids"][key] = value
                else:
                    parsed_data["tags"][key] = value
            elif key.startswith("prop_"):
                parsed_data["properties"][key] = value

        if parsed_data.get("main_language") is None and parsed_data.get("id"):
            parsed_data["main_language"] = parsed_data["id"].split(":", 1)[1]

        return parsed_data


class ErrorNode(BaseModel):
    id: str
    taxonomy_name: str
    branch_name: str
    created_at: DateTime
    warnings: list[str]
    errors: list[str]
