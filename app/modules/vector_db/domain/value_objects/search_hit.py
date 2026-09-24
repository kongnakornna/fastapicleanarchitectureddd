"""SearchHit VO"""
from __future__ import annotations
import uuid
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class SearchHit(BaseModel):
    """TH: ผลลัพธ์ 1 รายการ | EN: Search hit"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    vector_id: uuid.UUID
    source_id: str
    score: float
    metadata: Optional[dict[str, Any]] = None
    rank: int = 0
