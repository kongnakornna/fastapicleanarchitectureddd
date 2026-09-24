"""structured_outputs domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class SchemaRegistered:
    schema_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    strategy: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class OutputGenerated:
    output_id: uuid.UUID
    tenant_id: uuid.UUID
    request_id: uuid.UUID
    is_valid: bool
    attempts: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class OutputValidated:
    output_id: uuid.UUID
    tenant_id: uuid.UUID
    attempt: int
    passed: bool
    error_count: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class OutputRepaired:
    output_id: uuid.UUID
    tenant_id: uuid.UUID
    attempt: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class GenerationFailed:
    tenant_id: uuid.UUID
    schema_name: str
    error: str
    occurred_at: datetime = field(default_factory=_now)
