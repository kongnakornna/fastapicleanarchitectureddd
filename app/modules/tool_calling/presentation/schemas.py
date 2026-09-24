"""tool_calling Pydantic v2 schemas"""
from __future__ import annotations
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.modules.tool_calling.domain.enums import (
    RiskLevel, ToolKind, ToolVisibility,
)


class ToolCreateRequest(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
    )
    description: str = Field(default="", max_length=2000)
    parameters_json: dict[str, Any] = Field(default_factory=dict)
    returns_json: dict[str, Any] = Field(default_factory=dict)
    kind: ToolKind = ToolKind.HTTP
    risk_level: RiskLevel = RiskLevel.LOW
    visibility: ToolVisibility = ToolVisibility.TENANT
    timeout_seconds: int = Field(default=30, ge=1, le=600)
    model_config = ConfigDict(extra="forbid")


class ToolResponse(BaseModel):
    id: str
    name: str
    description: str = ""
    kind: str = "http"
    risk_level: str = "low"
    visibility: str = "tenant"
    timeout_seconds: int = 30
    is_active: bool = True
    model_config = ConfigDict(extra="forbid")


class ToolDetailResponse(BaseModel):
    id: str
    name: str
    description: str = ""
    parameters_json: dict[str, Any] = Field(default_factory=dict)
    kind: str = "http"
    is_active: bool = True
    model_config = ConfigDict(extra="forbid")


class InvokeRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)
    role: str = "user"
    model_config = ConfigDict(extra="forbid")


class InvokeResponse(BaseModel):
    invocation_id: str
    tool_name: str
    status: str
    output: Any = None
    error: str = ""
    latency_ms: int = 0
    model_config = ConfigDict(extra="forbid")


class InvocationResponse(BaseModel):
    id: str
    tool_id: str
    tool_name: str = ""
    status: str = "SUCCESS"
    latency_ms: int = 0
    created_at: str = ""
    model_config = ConfigDict(extra="forbid")
