"""Invocation VOs"""
from __future__ import annotations
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvocationRequest(BaseModel):
    """TH: คำขอ | EN: request"""
    model_config = ConfigDict(extra="forbid")
    tool_name: str = Field(min_length=1, max_length=100)
    arguments: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = Field(default=None, max_length=100)


class InvocationResult(BaseModel):
    """TH: ผลลัพธ์ | EN: result"""
    model_config = ConfigDict(extra="forbid")
    invocation_id: str
    tool_name: str
    status: str
    output: Any = None
    error: str = ""
    latency_ms: int = 0
