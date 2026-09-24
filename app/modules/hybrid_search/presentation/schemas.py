"""hybrid_search Pydantic schemas"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.hybrid_search.domain.enums import (
    FusionType, RerankerType,
)


class ConfigCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    fusion_type: FusionType = FusionType.RRF
    rrf_k: int = Field(default=60, ge=1, le=1000)
    bm25_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    vector_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    top_k: int = Field(default=10, ge=1, le=500)
    reranker_type: RerankerType = RerankerType.NONE


class ConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    fusion_type: str
    rrf_k: int
    bm25_weight: float
    vector_weight: float
    top_k: int
    reranker_type: str
    is_active: bool


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=2000)
    config_id: Optional[uuid.UUID] = None
    top_k: Optional[int] = Field(default=None, ge=1, le=500)
    collection_id: Optional[uuid.UUID] = None
    embedding_model: str = "text-embedding-3-small"
    corpus: Optional[list[dict[str, Any]]] = None


class SearchHitOut(BaseModel):
    source_id: str
    chunk_id: Optional[uuid.UUID] = None
    score: float
    rank: int
    source_kind: str
    snippet: str = ""
    metadata: Optional[dict[str, Any]] = None


class SearchResponse(BaseModel):
    query_id: uuid.UUID
    config_id: uuid.UUID
    fusion_type: str
    reranker_type: str
    top_k: int
    results: list[SearchHitOut] = []
    sparse_count: int = 0
    dense_count: int = 0
    latency_ms: int = 0
    metrics: dict[str, float] = Field(default_factory=dict)


class QueryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    config_id: uuid.UUID
    query_text: str
    latency_ms: int
    result_count: int
    created_at: datetime


class RankingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    stage: str
    source_kind: str
    source_id: str
    raw_score: float
    normalized_score: float
    rank: int


class MetricsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    retrieved_ids: list[str] = Field(default_factory=list)
    relevant_ids: list[str] = Field(default_factory=list)
    relevances: list[float] = Field(default_factory=list)
    k: int = Field(default=10, ge=1, le=200)


class MetricsResponse(BaseModel):
    mrr: float = 0.0
    ndcg: float = 0.0
    recall_at_k: float = 0.0
    precision_at_k: float = 0.0
