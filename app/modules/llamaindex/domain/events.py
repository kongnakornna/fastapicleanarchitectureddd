"""llamaindex domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class IndexCreated:
    index_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    index_type: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class DocumentIngested:
    document_id: uuid.UUID
    tenant_id: uuid.UUID
    index_id: uuid.UUID
    source_uri: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class NodesCreated:
    index_id: uuid.UUID
    tenant_id: uuid.UUID
    node_count: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class QueryExecuted:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    query_engine_id: uuid.UUID
    latency_ms: int
    source_count: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class ResponseSynthesized:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    response_mode: str
    tokens_used: int
    occurred_at: datetime = field(default_factory=_now)
