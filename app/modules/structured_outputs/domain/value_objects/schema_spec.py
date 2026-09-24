"""SchemaSpec VO"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.modules.structured_outputs.domain.enums import SOStrategy


class SchemaSpec(BaseModel):
    """TH: ข้อกำหนด schema | EN: Schema specification"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=100,
                      pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    json_schema: dict[str, Any] = Field(default_factory=dict)
    pydantic_model: str = ""
    strict: bool = False
    strategy: SOStrategy = SOStrategy.JSON_MODE
    description: str = ""
