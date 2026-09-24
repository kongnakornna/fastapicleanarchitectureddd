"""vector_db domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class CollectionCreated:
    collection_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    dimension: int
    metric: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class CollectionDeleted:
    collection_id: uuid.UUID
    tenant_id: uuid.UUID
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class VectorsUpserted:
    collection_id: uuid.UUID
    tenant_id: uuid.UUID
    count: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class VectorDeleted:
    collection_id: uuid.UUID
    tenant_id: uuid.UUID
    vector_id: uuid.UUID
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class IndexBuilt:
    index_id: uuid.UUID
    collection_id: uuid.UUID
    index_type: str
    size_bytes: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class IndexBuildFailed:
    index_id: uuid.UUID
    collection_id: uuid.UUID
    error: str
    occurred_at: datetime = field(default_factory=_now)
