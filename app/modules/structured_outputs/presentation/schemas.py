"""structured_outputs Pydantic schemas"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.structured_outputs.domain.enums import SOStrategy


class SchemaCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100,
                      pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    description: str = ""
    json_schema: dict[str, Any] = Field(default_factory=dict)
    pydantic_model: str = ""
    strict: bool = False
    strategy: SOStrategy = SOStrategy.JSON_MODE


class SchemaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    description: str
    strategy: str
    strict: bool
    version: str


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1)
    schema_id: uuid.UUID
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_repairs: int = Field(default=2, ge=0, le=10)


class GenerateResponse(BaseModel):
    status: str
    parsed: Optional[dict[str, Any]] = None
    is_valid: bool
    attempts: int
    errors: list[str] = []
    tokens_used: int = 0
    latency_ms: int = 0


class ValidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_id: uuid.UUID
    payload: dict[str, Any] = Field(default_factory=dict)


class ValidateResponse(BaseModel):
    is_valid: bool
    errors: list[dict[str, Any]] = []


class OutputOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    request_id: uuid.UUID
    is_valid: bool
    attempts: int
    tokens_used: int
    created_at: datetime
