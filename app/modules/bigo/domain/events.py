"""bigo domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class ProfileCaptured:
    profile_id: uuid.UUID
    tenant_id: uuid.UUID
    function_name: str
    complexity: str
    sample_size: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class ComplexityDegraded:
    profile_id: uuid.UUID
    tenant_id: uuid.UUID
    function_name: str
    previous_complexity: str
    current_complexity: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class MemoryThresholdExceeded:
    tenant_id: uuid.UUID
    process_id: int
    rss_mb: int
    threshold_mb: int
    pressure: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class MemoryLeakDetected:
    leak_id: uuid.UUID
    tenant_id: uuid.UUID
    object_type: str
    growth_rate_mb_per_hour: float
    leak_type: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class KafkaLagExceeded:
    consumer_id: uuid.UUID
    tenant_id: uuid.UUID
    topic: str
    group_id: str
    lag: int
    threshold: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class BackpressureActivated:
    topic: str
    tenant_id: uuid.UUID
    queue_depth: int
    action: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class AlertTriggered:
    alert_id: uuid.UUID
    tenant_id: uuid.UUID
    severity: str
    kind: str
    message: str
    payload: dict[str, Any]
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class PipelineReportPersisted:
    report_id: uuid.UUID
    tenant_id: uuid.UUID
    trace_id: str
    n: int
    complexity: str
    status: str
    priority: str
    occurred_at: datetime = field(default_factory=_now)
