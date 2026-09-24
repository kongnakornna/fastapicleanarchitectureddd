"""embeddings domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class EmbeddingCreated:
    vector_id: uuid.UUID
    tenant_id: uuid.UUID
    model_id: uuid.UUID
    dimension: int
    tokens: int
    cached: bool
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class BatchStarted:
    batch_id: uuid.UUID
    tenant_id: uuid.UUID
    total: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class BatchCompleted:
    batch_id: uuid.UUID
    tenant_id: uuid.UUID
    completed: int
    failed: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class BatchFailed:
    batch_id: uuid.UUID
    tenant_id: uuid.UUID
    error: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class CacheHit:
    tenant_id: uuid.UUID
    model_id: uuid.UUID
    hash: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class CacheMiss:
    tenant_id: uuid.UUID
    model_id: uuid.UUID
    hash: str
    occurred_at: datetime = field(default_factory=_now)
