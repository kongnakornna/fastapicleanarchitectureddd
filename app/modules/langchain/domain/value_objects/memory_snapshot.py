"""MemorySnapshot VO"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.modules.langchain.domain.enums import MemoryType


class MemorySnapshot(BaseModel):
    """TH: snapshot ของ memory | EN: Memory snapshot"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    memory_type: MemoryType = MemoryType.BUFFER
    payload: list[dict[str, Any]] = Field(default_factory=list)
    size_bytes: int = Field(default=0, ge=0)
