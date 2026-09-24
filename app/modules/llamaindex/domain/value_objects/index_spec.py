"""IndexSpec VO"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.modules.llamaindex.domain.enums import IndexType


class IndexSpec(BaseModel):
    """TH: ข้อกำหนด index | EN: Index specification"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    index_type: IndexType = IndexType.VECTOR_STORE
    embed_model: str = Field(default="text-embedding-3-small", max_length=100)
    storage_kind: str = Field(default="pgvector", max_length=50)
    config: dict[str, Any] = Field(default_factory=dict)
