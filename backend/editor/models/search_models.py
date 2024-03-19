from abc import ABC, abstractmethod
from typing import Annotated, Literal, Self

from pydantic import (
    Field,
    StringConstraints,
    TypeAdapter,
    model_validator,
)

from .base_models import BaseModel
from .node_models import EntryNode


class AbstractFilterSearchTerm(BaseModel, ABC):
    filter_type: str
    filter_value: str

    @abstractmethod
    def build_cypher_query(self, param_name: str) -> tuple[str, str | None]:
        pass


class IsFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["is"]
    filter_value: Literal["root"]

    def build_cypher_query(self, _param_name: str) -> tuple[str, None]:
        match self.filter_value:
            case "root":
                return "NOT (n)-[:is_child_of]->()", None
            case _:
                raise ValueError("Invalid filter value")


class LanguageFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["language"]
    # Only allow 2-letter language codes
    filter_value: Annotated[str, StringConstraints(pattern="^(not:)?[a-z]{2}$")]
    negated: bool = False

    @model_validator(mode="after")
    def validate_negation(self) -> Self:
        if self.filter_value.startswith("not:"):
            self.filter_value = self.filter_value[4:]
            self.negated = True
        return self

    def build_cypher_query(self, _param_name: str) -> tuple[str, None]:
        if self.negated:
            return f"n.tags_ids_{self.filter_value} IS NULL", None
        else:
            return f"n.tags_ids_{self.filter_value} IS NOT NULL", None


class ParentFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["parent"]

    def build_cypher_query(self, param_name: str) -> tuple[str, str]:
        return (
            "(n)<-[:is_child_of]-(:ENTRY {id: $" + param_name + "})",
            self.filter_value,
        )


class ChildFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["child"]

    def build_cypher_query(self, param_name: str) -> tuple[str, str]:
        return (
            "(n)-[:is_child_of]->(:ENTRY {id: $" + param_name + "})",
            self.filter_value,
        )


class AncestorFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["ancestor"]

    def build_cypher_query(self, param_name: str) -> tuple[str, str]:
        return (
            "(n)<-[:is_child_of*]-(:ENTRY {id: $" + param_name + "})",
            self.filter_value,
        )


class DescendantFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["descendant"]

    def build_cypher_query(self, param_name: str) -> tuple[str, str]:
        return (
            "(n)-[:is_child_of*]->(:ENTRY {id: $" + param_name + "})",
            self.filter_value,
        )


FilterSearchTerm = Annotated[
    (
        IsFilterSearchTerm
        | LanguageFilterSearchTerm
        | ParentFilterSearchTerm
        | ChildFilterSearchTerm
        | AncestorFilterSearchTerm
        | DescendantFilterSearchTerm
    ),
    Field(discriminator="filter_type"),
]

# https://docs.pydantic.dev/dev/concepts/type_adapter/
FilterSearchTermValidator = TypeAdapter(FilterSearchTerm)


class EntryNodeSearchResult(BaseModel):
    node_count: int = 0
    page_count: int = 0
    nodes: list[EntryNode] = Field(default_factory=list)
    filters: list[FilterSearchTerm] = Field(default_factory=list)
