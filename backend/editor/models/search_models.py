from abc import ABC, abstractmethod
from typing import Literal

from pydantic import Field

from .base_models import BaseModel
from .node_models import EntryNode


class AbstractFilterSearchTerm(BaseModel, ABC):
    filter_type: str
    filter_value: str

    @abstractmethod
    def build_cypher_query(self, param_name: str) -> tuple[str, str | None]:
        pass


class IsFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["is"] = "is"
    filter_value: Literal["root"]

    def build_cypher_query(self, _param_name: str) -> tuple[str, None]:
        match self.filter_value:
            case "root":
                return "NOT (n)-[:is_child_of]->()", None
            case _:
                raise ValueError("Invalid filter value")


class LanguageFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["language"] = "language"
    negated: bool = False

    def build_cypher_query(self, _param_name: str) -> tuple[str, None]:
        if self.negated:
            return f"n.tags_ids_{self.filter_value} IS NULL", None
        else:
            return f"n.tags_ids_{self.filter_value} IS NOT NULL", None


class ParentFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["parent"] = "parent"

    def build_cypher_query(self, param_name: str) -> tuple[str, str]:
        return (
            "(n)<-[:is_child_of]-(:ENTRY {id: $" + param_name + "})",
            self.filter_value,
        )


class ChildFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["child"] = "child"

    def build_cypher_query(self, param_name: str) -> tuple[str, str]:
        return (
            "(n)-[:is_child_of]->(:ENTRY {id: $" + param_name + "})",
            self.filter_value,
        )


class AncestorFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["ancestor"] = "ancestor"

    def build_cypher_query(self, param_name: str) -> tuple[str, str]:
        return (
            "(n)<-[:is_child_of*]-(:ENTRY {id: $" + param_name + "})",
            self.filter_value,
        )


class DescendantFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["descendant"] = "descendant"

    def build_cypher_query(self, param_name: str) -> tuple[str, str]:
        return (
            "(n)-[:is_child_of*]->(:ENTRY {id: $" + param_name + "})",
            self.filter_value,
        )


FilterSearchTerm = (
    IsFilterSearchTerm
    | LanguageFilterSearchTerm
    | ParentFilterSearchTerm
    | ChildFilterSearchTerm
    | AncestorFilterSearchTerm
    | DescendantFilterSearchTerm
)


class EntryNodeSearchResult(BaseModel):
    node_count: int = 0
    page_count: int = 0
    nodes: list[EntryNode] = Field(default_factory=list)
    filters: list[FilterSearchTerm] = Field(default_factory=list)
