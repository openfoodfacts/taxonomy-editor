from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, alias_generators


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )
