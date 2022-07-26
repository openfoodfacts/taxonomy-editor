from typing import List
from pydantic import BaseModel

class Header(BaseModel):
    preceding_lines: List

class Footer(BaseModel):
    preceding_lines: List