"""SOResult VO"""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.structured_outputs.domain.enums import SOStatus


class SOResult(BaseModel):
    """TH: ผลลัพธ์การ generate | EN: Structured output result"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: SOStatus
    parsed: Optional[dict[str, Any]] = None
    raw_text: str = ""
    is_valid: bool = False
    attempts: int = Field(default=0, ge=0)
    errors: list[str] = Field(default_factory=list)
    tokens_used: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
