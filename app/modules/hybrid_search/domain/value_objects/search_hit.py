"""SearchHit VO"""
from __future__ import annotations
import uuid
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class SearchHit(BaseModel):
    """TH: ผลลัพธ์ 1 รายการ | EN: Search hit"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str = Field(min_length=1)
    chunk_id: Optional[uuid.UUID] = None
    score: float = 0.0
    rank: int = Field(default=0, ge=0)
    source_kind: str = "hybrid"
    snippet: str = ""
    metadata: Optional[dict[str, Any]] = None
