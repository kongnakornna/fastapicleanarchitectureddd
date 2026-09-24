"""vector_db Pydantic schemas"""
from __future__ import annotations
import uuid
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.vector_db.domain.enums import (
    ANNIndexType, VectorMetric,
)


class CollectionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    dimension: int = Field(ge=1, le=8192)
    metric: VectorMetric = VectorMetric.COSINE
    backend: str = "pgvector"
    config: dict[str, Any] = Field(default_factory=dict)


class CollectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    dimension: int
    metric: str
    backend: str
    is_active: bool


class VectorItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_id: str = Field(min_length=1, max_length=200)
    vector: list[float] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpsertRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[VectorItem] = Field(min_length=1, max_length=10000)


class UpsertResponse(BaseModel):
    collection_id: uuid.UUID
    upserted: int


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vector: list[float] = Field(min_length=1)
    top_k: int = Field(default=10, ge=1, le=1000)
    metric: Optional[VectorMetric] = None
    filter: Optional[dict[str, Any]] = None
    include_metadata: bool = True
    score_threshold: Optional[float] = None


class SearchHitOut(BaseModel):
    vector_id: uuid.UUID
    source_id: str
    score: float
    metadata: Optional[dict[str, Any]] = None
    rank: int = 0


class QueryResponse(BaseModel):
    collection_id: uuid.UUID
    hits: list[SearchHitOut]


class IndexCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    index_type: ANNIndexType = ANNIndexType.HNSW
    params: dict[str, Any] = Field(default_factory=dict)


class IndexOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    collection_id: uuid.UUID
    name: str
    index_type: str
    build_status: str
    size_bytes: int


class StatsOut(BaseModel):
    collection_id: uuid.UUID
    vector_count: int
    size_bytes: int
    avg_latency_ms: float
    updated_at: Optional[str] = None
