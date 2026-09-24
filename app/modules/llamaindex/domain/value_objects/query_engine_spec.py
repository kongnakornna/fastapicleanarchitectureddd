"""QueryEngineSpec VO"""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field

from app.modules.llamaindex.domain.enums import ResponseMode


class QueryEngineSpec(BaseModel):
    """TH: ข้อกำหนด query engine | EN: Query engine spec"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    retriever_type: str = Field(default="vector", max_length=30)
    top_k: int = Field(default=5, ge=1, le=100)
    response_mode: ResponseMode = ResponseMode.COMPACT
    similarity_top_k: int = Field(default=5, ge=1, le=100)
