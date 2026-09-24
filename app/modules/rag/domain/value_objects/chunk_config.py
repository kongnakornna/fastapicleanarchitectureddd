"""ChunkConfig VO"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.rag.domain.enums import ChunkerType


class ChunkConfig(BaseModel):
    """TH: การตั้งค่าการแบ่ง chunk | EN: Chunk config"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    chunker_type: ChunkerType = ChunkerType.RECURSIVE
    chunk_size: int = Field(default=512, ge=64, le=8192)
    chunk_overlap: int = Field(default=50, ge=0, le=2048)
    separators: Optional[list[str]] = None
    min_chunk_size: int = Field(default=64, ge=1, le=2048)
