from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Annotated, Literal, NamedTuple, Self

from pydantic import (
    Field,
    StringConstraints,
    TypeAdapter,
    model_validator,
)

from .base_models import BaseModel
from .node_models import EntryNode


@dataclass(frozen=True)
class CypherQuery:
    query: str
    params: dict[str, str] = field(default_factory=dict)


class AbstractFilterSearchTerm(BaseModel, ABC):
    filter_type: str
    filter_value: str

    @abstractmethod
    def build_cypher_query(self, param_name: str) -> CypherQuery:
        pass


class IsFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["is"]
    filter_value: Literal["root"]

    def build_cypher_query(self, _param_name: str) -> CypherQuery:
        match self.filter_value:
            case "root":
                return CypherQuery("NOT (n)-[:is_child_of]->()")
            case _:
                raise ValueError("Invalid filter value")


class LanguageFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["language"]
    # Only allow 2-letter language codes
    filter_value: Annotated[str, StringConstraints(pattern="^(not:)?[a-z]{2}$")]
    negated: bool = False

    @model_validator(mode="after")
    def validate_negation(self) -> Self:
        """
        After model validation, update the negated flag and filter_value
        if filter_value is not parsed yet.
        Usage docs: https://docs.pydantic.dev/latest/concepts/validators/#model-validators
        """
        if self.filter_value.startswith("not:"):
            self.filter_value = self.filter_value[4:]
            self.negated = True
        return self

    def build_cypher_query(self, _param_name: str) -> CypherQuery:
        if self.negated:
            return CypherQuery(f"n.tags_ids_{self.filter_value} IS NULL")
        else:
            return CypherQuery(f"n.tags_ids_{self.filter_value} IS NOT NULL")


class ParentFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["parent"]

    def build_cypher_query(self, param_name: str) -> CypherQuery:
        return CypherQuery(
            "(n)<-[:is_child_of]-(:ENTRY {id: $" + param_name + "})",
            {param_name: self.filter_value},
        )


class ChildFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["child"]

    def build_cypher_query(self, param_name: str) -> CypherQuery:
        return CypherQuery(
            "(n)-[:is_child_of]->(:ENTRY {id: $" + param_name + "})",
            {param_name: self.filter_value},
        )


class AncestorFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["ancestor"]

    def build_cypher_query(self, param_name: str) -> CypherQuery:
        return CypherQuery(
            "(n)<-[:is_child_of*]-(:ENTRY {id: $" + param_name + "})",
            {param_name: self.filter_value},
        )


class DescendantFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["descendant"]

    def build_cypher_query(self, param_name: str) -> CypherQuery:
        return CypherQuery(
            "(n)-[:is_child_of*]->(:ENTRY {id: $" + param_name + "})",
            {param_name: self.filter_value},
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
