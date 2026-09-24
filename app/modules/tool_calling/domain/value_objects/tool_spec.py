"""ToolSpec value object"""
from __future__ import annotations
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.tool_calling.domain.enums import (
    RiskLevel, ToolKind, ToolVisibility,
)


class ToolSpec(BaseModel):
    """TH: spec ของ tool | EN: tool spec VO"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(
        min_length=1, max_length=100,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
    )
    description: str = Field(default="", max_length=2000)
    parameters_json: dict[str, Any] = Field(default_factory=dict)
    returns_json: dict[str, Any] = Field(default_factory=dict)
    kind: ToolKind = ToolKind.HTTP
    risk_level: RiskLevel = RiskLevel.LOW
    visibility: ToolVisibility = ToolVisibility.TENANT
    timeout_seconds: int = Field(default=30, ge=1, le=600)
