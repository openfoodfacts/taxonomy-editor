import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, TypeAdapter, computed_field, field_validator

from .base_models import BaseModel
from .node_models import EntryNode


@dataclass(frozen=True)
class CypherQuery:
    """
    Each search filter will return a CypherQuery with a condition (query)
    and corresponding parameters (params)
    """

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
    filter_value: Literal["root"] | Literal["external"] | Literal["not:external"]

    def build_cypher_query(self, _param_name: str) -> CypherQuery:
        match self.filter_value:
            case "root":
                return CypherQuery("NOT (n)-[:is_child_of]->()")
            case "external":
                return CypherQuery("n.is_external = true")
            case "not:external":
                return CypherQuery("(n.is_external IS NULL OR n.is_external = false)")
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


class PropertyFilterSearchTerm(AbstractFilterSearchTerm):
    filter_type: Literal["property"]
    filter_value: str

    @field_validator("filter_value")
    @classmethod
    def validate_filter_value(cls, filter_value: str):
        """
        The filter value is in the format `not:inherited:property_name:property_value`
        where `not:` and `inherited:` and `:property_value` are optional.
        Note that a property_name is always of format `name:lc`.
        """
        parsed_value = filter_value
        if parsed_value.startswith("not:"):
            parsed_value = parsed_value[4:]
        if parsed_value.startswith("inherited:"):
            parsed_value = parsed_value[10:]

        assert ":" in parsed_value, "A property_name is mandatory and must contain a colon"

        terms = parsed_value.split(":")
        property_name = terms[0] + ":" + terms[1]

        if not re.match(r"^[^:\\]+:[a-z]{2}$", property_name):
            raise ValueError("Invalid property_name")

        return filter_value

    @computed_field
    def negated(self) -> bool:
        return self.filter_value.startswith("not:")

    @computed_field
    def inherited(self) -> bool:
        filter_value = self.get_parsed_filter_value(self.negated)
        return filter_value.startswith("inherited:")

    @computed_field
    def property_name(self) -> str:
        filter_value = self.get_parsed_filter_value(self.negated, self.inherited)
        terms = filter_value.split(":")
        return terms[0] + "_" + terms[1]

    @computed_field
    def property_value(self) -> str | None:
        filter_value = self.get_parsed_filter_value(self.negated, self.inherited)
        terms = filter_value.split(":")
        return ":".join(terms[2:]) if len(terms) > 2 else None

    def get_parsed_filter_value(self, negated=False, inherited=False):
        filter_value = self.filter_value
        if negated:
            filter_value = filter_value[4:]
        if inherited:
            filter_value = filter_value[10:]
        return filter_value

    def build_cypher_query(self, param_name: str) -> CypherQuery:
        branches = {
            "negated": self.negated,
            "inherited": self.inherited,
            "with_value": self.property_value is not None,
        }
        match branches:
            case {"negated": False, "inherited": False, "with_value": False}:
                return CypherQuery(f"n.prop_{self.property_name} IS NOT NULL")
            case {"negated": True, "inherited": False, "with_value": False}:
                return CypherQuery(f"n.prop_{self.property_name} IS NULL")
            case {"negated": False, "inherited": False, "with_value": True}:
                return CypherQuery(
                    f"n.prop_{self.property_name} = ${param_name}",
                    {param_name: self.property_value},
                )
            case {"negated": True, "inherited": False, "with_value": True}:
                return CypherQuery(
                    f"n.prop_{self.property_name} <> ${param_name}",
                    {param_name: self.property_value},
                )
            case {"negated": False, "inherited": True, "with_value": False}:
                return CypherQuery(
                    f"""(n.prop_{self.property_name} IS NOT NULL OR
                    any(
                        ancestor IN [(n)<-[:is_child_of*]-(p:ENTRY) | p]
                        WHERE ancestor.prop_{self.property_name} IS NOT NULL)
                    )""",
                )
            case {"negated": True, "inherited": True, "with_value": False}:
                return CypherQuery(
                    f"""(n.prop_{self.property_name} IS NULL AND
                    all(
                        ancestor IN [(n)<-[:is_child_of*]-(p:ENTRY) | p]
                        WHERE ancestor.prop_{self.property_name} IS NULL)
                    )""",
                )
            case {"negated": False, "inherited": True, "with_value": True}:
                return CypherQuery(
                    f"""
                    [
                        property IN
                        [n.prop_{self.property_name}] +
                        [(n)<-[:is_child_of*]-(p:ENTRY) | p.prop_{self.property_name}]
                        WHERE property IS NOT NULL
                    ][0]
                    = ${param_name}""",
                    {param_name: self.property_value},
                )
            case {"negated": True, "inherited": True, "with_value": True}:
                return CypherQuery(
                    f"""((n.prop_{self.property_name} IS NULL AND
                    all(
                        ancestor IN [(n)<-[:is_child_of*]-(p:ENTRY) | p]
                        WHERE ancestor.prop_{self.property_name} IS NULL)
                    ) OR
                    [
                        property IN
                        [n.prop_{self.property_name}] +
                        [(n)<-[:is_child_of*]-(p:ENTRY) | p.prop_{self.property_name}]
                        WHERE property IS NOT NULL
                    ][0]
                    <> ${param_name})""",
                    {param_name: self.property_value},
                )


FilterSearchTerm = Annotated[
    (
        IsFilterSearchTerm
        | LanguageFilterSearchTerm
        | ParentFilterSearchTerm
        | ChildFilterSearchTerm
        | AncestorFilterSearchTerm
        | DescendantFilterSearchTerm
        | PropertyFilterSearchTerm
    ),
    Field(discriminator="filter_type"),
]

# This will create the right FilterSearchTerm based upon filter_type
# https://docs.pydantic.dev/dev/concepts/type_adapter/
FilterSearchTermValidator = TypeAdapter(FilterSearchTerm)


class EntryNodeSearchResult(BaseModel):
    q: str = ""
    node_count: int = 0
    page_count: int = 0
    filters: list[FilterSearchTerm] = Field(default_factory=list)
    nodes: list[EntryNode] = Field(default_factory=list)
