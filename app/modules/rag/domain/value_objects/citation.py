"""CitationVO"""
from __future__ import annotations
import uuid
from pydantic import BaseModel, ConfigDict, Field


class CitationVO(BaseModel):
    """TH: การอ้างอิง 1 รายการ | EN: Citation"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: uuid.UUID
    document_id: uuid.UUID
    score: float
    rank: int = Field(ge=1)
    snippet: str = ""
