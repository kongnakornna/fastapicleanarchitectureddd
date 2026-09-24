"""tool_calling domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class ToolRegistered:
    tool_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    kind: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class ToolInvoked:
    invocation_id: uuid.UUID
    tool_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    latency_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class ToolFailed:
    invocation_id: uuid.UUID
    tool_id: uuid.UUID
    tenant_id: uuid.UUID
    error_code: str
    message: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class PermissionDenied:
    tool_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    occurred_at: datetime = field(default_factory=_now)
