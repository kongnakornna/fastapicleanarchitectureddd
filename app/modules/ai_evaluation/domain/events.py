"""ai_evaluation domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DatasetCreated:
    dataset_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    task_type: str
    case_count: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class EvalRunStarted:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    dataset_id: uuid.UUID
    target_model: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class EvalRunCompleted:
    run_id: uuid.UUID
    tenant_id: uuid.UUID
    status: str
    metrics_json: str
    duration_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class MetricComputed:
    run_id: uuid.UUID
    case_id: uuid.UUID
    metric_name: str
    score: float
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True)
class HallucinationDetected:
    run_id: uuid.UUID
    case_id: uuid.UUID
    severity: str
    occurred_at: datetime = field(default_factory=_now)
