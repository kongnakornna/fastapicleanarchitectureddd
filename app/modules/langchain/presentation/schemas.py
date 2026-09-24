"""langchain Pydantic schemas"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.langchain.domain.enums import (
    AgentType, ChainType, MemoryType,
)


class ChainCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    chain_type: ChainType = ChainType.LCEL
    config: dict[str, Any] = Field(default_factory=dict)
    description: str = ""
    version: str = "1.0.0"


class ChainOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    chain_type: str
    version: str
    is_active: bool


class AgentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    agent_type: AgentType = AgentType.REACT
    tools: list[str] = Field(default_factory=list)
    model: str = "gpt-4o-mini"
    max_iterations: int = Field(default=10, ge=1, le=50)
    system_prompt: str = ""
    config: dict[str, Any] = Field(default_factory=dict)


class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    agent_type: str
    model: str
    max_iterations: int
    is_active: bool


class InvokeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    inputs: dict[str, Any] = Field(default_factory=dict)
    question: Optional[str] = None


class InvokeResponse(BaseModel):
    run_id: uuid.UUID
    output: dict[str, Any] = Field(default_factory=dict)
    status: str
    latency_ms: int
    tokens_used: int = 0
    trace_steps: int = 0


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    kind: str
    target_id: uuid.UUID
    status: str
    latency_ms: int
    tokens_used: int
    error_message: str
    created_at: datetime


class TraceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    run_id: uuid.UUID
    step: int
    kind: str
    latency_ms: int


class MemoryUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    conversation_id: uuid.UUID
    memory_type: MemoryType = MemoryType.BUFFER
    messages: list[dict[str, Any]] = Field(default_factory=list)


class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    conversation_id: uuid.UUID
    memory_type: str
    size_bytes: int
