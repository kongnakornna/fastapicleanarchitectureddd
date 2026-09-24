"""llm Pydantic v2 schemas"""
from __future__ import annotations
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    conversation_id: str | None = None
    model: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=100000)
    system_prompt: str = ""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, ge=1, le=128000)
    stream: bool = False
    model_config = ConfigDict(extra="forbid")


class ChatResponse(BaseModel):
    conversation_id: str
    model: str
    content: str
    finish_reason: str = "stop"
    usage: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int = 0
    model_config = ConfigDict(extra="forbid")


class CompletionRequest(BaseModel):
    model: str = Field(..., min_length=1, max_length=100)
    prompt: str = Field(..., min_length=1, max_length=100000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=128000)
    model_config = ConfigDict(extra="forbid")


class ConversationCreateRequest(BaseModel):
    model: str = Field(..., min_length=1, max_length=100)
    title: str = ""
    model_config = ConfigDict(extra="forbid")


class ConversationResponse(BaseModel):
    id: str
    title: str = ""
    model_id: str = ""
    status: str = "ACTIVE"
    message_count: int = 0
    total_tokens: int = 0
    model_config = ConfigDict(extra="forbid")


class ConversationDetailResponse(BaseModel):
    id: str
    title: str
    status: str
    model_id: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
    model_config = ConfigDict(extra="forbid")


class ProviderResponse(BaseModel):
    id: str
    name: str
    provider_type: str
    base_url: str = ""
    is_active: bool = True
    priority: int = 100
    model_config = ConfigDict(extra="forbid")


class ModelResponse(BaseModel):
    id: str
    name: str
    display_name: str = ""
    context_window: int = 4096
    max_output_tokens: int = 4096
    supports_streaming: bool = True
    supports_tools: bool = False
    model_config = ConfigDict(extra="forbid")


class UsageResponse(BaseModel):
    tenant: dict[str, Any]
    user: dict[str, Any]
    since: str
    model_config = ConfigDict(extra="forbid")
