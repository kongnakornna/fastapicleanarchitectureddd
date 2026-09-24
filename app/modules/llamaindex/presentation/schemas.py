"""llamaindex Pydantic schemas"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.llamaindex.domain.enums import (
    IndexType, ResponseMode,
)


class IndexCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    index_type: IndexType = IndexType.VECTOR_STORE
    embed_model: str = "text-embedding-3-small"
    storage_kind: str = "pgvector"
    config: dict[str, Any] = Field(default_factory=dict)


class IndexOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    index_type: str
    embed_model: str
    storage_kind: str
    is_active: bool


class IngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str = Field(min_length=1)
    source_uri: str = ""
    mime_type: str = "text/plain"
    title: str = ""
    chunk_size: int = Field(default=512, ge=64, le=8192)
    chunk_overlap: int = Field(default=50, ge=0, le=2048)


class IngestResponse(BaseModel):
    document_id: uuid.UUID
    index_id: uuid.UUID
    status: str
    node_count: int


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1)
    query_engine_id: Optional[uuid.UUID] = None
    top_k: Optional[int] = Field(default=None, ge=1, le=100)
    response_mode: Optional[ResponseMode] = None
    model: str = "gpt-4o-mini"


class SourceNodeOut(BaseModel):
    source_id: str
    chunk_id: Optional[str] = None
    score: float = 0.0
    content: str = ""
    metadata: Optional[dict[str, Any]] = None


class QueryResponse(BaseModel):
    run_id: uuid.UUID
    answer: str
    source_nodes: list[SourceNodeOut] = []
    latency_ms: int = 0
    tokens_used: int = 0
    response_mode: str = "compact"


class QueryEngineCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    retriever_type: str = "vector"
    top_k: int = Field(default=5, ge=1, le=100)
    response_mode: ResponseMode = ResponseMode.COMPACT
    similarity_top_k: int = Field(default=5, ge=1, le=100)


class QueryEngineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    index_id: uuid.UUID
    name: str
    retriever_type: str
    top_k: int
    response_mode: str
    similarity_top_k: int


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    index_id: uuid.UUID
    query: str
    answer: str
    status: str
    latency_ms: int
    tokens_used: int
    created_at: datetime


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    index_id: uuid.UUID
    source_uri: str
    mime_type: str
    title: str
    status: str
    node_count: int
    created_at: datetime
