"""rag Pydantic schemas"""
from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.modules.rag.domain.enums import (
    ChunkerType, RerankerType, RetrieverType,
)


class IngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str = Field(min_length=1)
    source_uri: str = Field(default="", max_length=1000)
    mime_type: str = "text/plain"
    title: str = Field(default="", max_length=500)
    pipeline_id: Optional[uuid.UUID] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    chunk_count: int
    size_bytes: int


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1)
    pipeline_id: Optional[uuid.UUID] = None
    conversation_id: Optional[uuid.UUID] = None
    use_cache: bool = True


class CitationOut(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    score: float
    rank: int
    snippet: str = ""


class UsageOut(BaseModel):
    total_tokens: int = 0
    cost_usd: Decimal = Decimal("0")


class QueryResponse(BaseModel):
    run_id: str
    answer: str
    citations: list[CitationOut] = []
    usage: UsageOut
    cached: bool = False


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    source_uri: str
    mime_type: str
    title: str
    status: str
    size_bytes: int
    chunk_count: int
    created_at: datetime


class ChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    ordinal: int
    content: str
    token_count: int


class DocumentDetailOut(DocumentOut):
    chunks: list[ChunkOut] = []


class PipelineCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    chunker_type: ChunkerType = ChunkerType.RECURSIVE
    chunk_size: int = Field(default=512, ge=64, le=8192)
    chunk_overlap: int = Field(default=50, ge=0, le=2048)
    retriever_type: RetrieverType = RetrieverType.VECTOR
    top_k: int = Field(default=5, ge=1, le=100)
    reranker_type: RerankerType = RerankerType.NONE
    embedding_model: str = "text-embedding-3-small"
    generation_model: str = "gpt-4o-mini"


class PipelineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    chunker_type: str
    chunk_size: int
    chunk_overlap: int
    retriever_type: str
    top_k: int
    reranker_type: str
    embedding_model: str
    generation_model: str
    is_active: bool


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    query: str
    answer: str
    model_name: str
    latency_ms: int
    total_tokens: int
    cost_usd: Decimal
    status: str
    created_at: datetime
