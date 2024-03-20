from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, TypeAdapter, computed_field

from .base_models import BaseModel
from .node_models import EntryNode


@dataclass(frozen=True)
class CypherQuery:
    query: str
    params: dict[str, str] = field(default_factory=dict)


class AbstractFilterSearchTerm(BaseModel, ABC):
    filter_type: str
    filter_value: str

    def to_query_string(self) -> str:
        filter_value = self.filter_value
        if " " in self.filter_value:
            filter_value = f'"{self.filter_value}"'
        return f"{self.filter_type}:{filter_value}"

    @abstractmethod
    def build_cypher_query(self, param_name: str) -> CypherQuery:
        """Builds a Cypher query for the filter search term.

        Args:
            param_name (str): The param_name is used to avoid name conflicts in the Cypher query.
        """
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

    @computed_field
    def negated(self) -> bool:
        return self.filter_value.startswith("not:")

    @computed_field
    def language(self) -> str:
        return self.filter_value[4:] if self.negated else self.filter_value

    def build_cypher_query(self, _param_name: str) -> CypherQuery:
        if self.negated:
            return CypherQuery(f"n.tags_ids_{self.language} IS NULL")
        else:
            return CypherQuery(f"n.tags_ids_{self.language} IS NOT NULL")


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
    q: str = ""
    node_count: int = 0
    page_count: int = 0
    filters: list[FilterSearchTerm] = Field(default_factory=list)
    nodes: list[EntryNode] = Field(default_factory=list)
