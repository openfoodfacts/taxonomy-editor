"""
Required pydantic models for API
"""
from typing import List

from .base_models import BaseModel


class Marginal(BaseModel):
    preceding_lines: List


class Header(Marginal):
    pass


class Footer(Marginal):
    pass
