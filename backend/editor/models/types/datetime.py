from datetime import datetime
from typing import Annotated, Any
from neo4j.time import DateTime as Neo4JDateTime
from pydantic import BeforeValidator


def convert_to_native_datetime(raw_value: Any) -> datetime:
    if not isinstance(raw_value, Neo4JDateTime):
        # Pass through non-datetime values to the default validator
        return raw_value
    return raw_value.to_native()


# Augmented type for datetime fields that are stored as Neo4JDateTime in the database
DateTime = Annotated[datetime, BeforeValidator(convert_to_native_datetime)]
