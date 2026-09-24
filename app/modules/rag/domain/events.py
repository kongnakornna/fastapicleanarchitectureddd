"""rag domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DocumentIngested:
    document_id: uuid.UUID
    tenant_id: uuid.UUID
    source_uri: str
    size_bytes: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class DocumentChunked:
    document_id: uuid.UUID
    tenant_id: uuid.UUID
    chunk_count: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class RetrievalCompleted:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    retriever_type: str
    top_k: int
    latency_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class RAGAnswerGenerated:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    model_name: str
    citation_count: int
    tokens_used: int
    cost_usd: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class PipelineCreated:
    pipeline_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    occurred_at: datetime = field(default_factory=_now)
