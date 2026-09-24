"""langchain domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ChainRegistered:
    chain_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    chain_type: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class AgentRegistered:
    agent_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    agent_type: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class ChainInvoked:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    chain_id: uuid.UUID
    latency_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class AgentStepExecuted:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    step: int
    kind: str
    latency_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class MemoryUpdated:
    memory_id: uuid.UUID
    tenant_id: uuid.UUID
    memory_type: str
    size_bytes: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class RunCompleted:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    kind: str
    status: str
    latency_ms: int
    tokens_used: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class RunFailed:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    error: str
    occurred_at: datetime = field(default_factory=_now)
