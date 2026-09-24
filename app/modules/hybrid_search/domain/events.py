"""hybrid_search domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ConfigCreated:
    config_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    fusion_type: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class SearchExecuted:
    query_id: uuid.UUID
    tenant_id: uuid.UUID
    query_text: str
    result_count: int
    latency_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class RerankCompleted:
    query_id: uuid.UUID
    tenant_id: uuid.UUID
    reranker_type: str
    input_count: int
    output_count: int
    latency_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class MetricsComputed:
    query_id: uuid.UUID
    tenant_id: uuid.UUID
    mrr: float
    ndcg: float
    occurred_at: datetime = field(default_factory=_now)
