"""YOLO domain events"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class DatasetRegistered:
    dataset_id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    format: str
    image_count: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class ImagesUploaded:
    dataset_id: uuid.UUID
    tenant_id: uuid.UUID
    image_ids: tuple[uuid.UUID, ...]
    count: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class AnnotationsCreated:
    image_id: uuid.UUID
    tenant_id: uuid.UUID
    count: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class TrainingStarted:
    training_id: uuid.UUID
    tenant_id: uuid.UUID
    dataset_id: uuid.UUID
    model_type: str
    epochs: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class TrainingCompleted:
    training_id: uuid.UUID
    model_id: uuid.UUID
    tenant_id: uuid.UUID
    mAP50: float
    mAP50_95: float
    duration_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class ModelExported:
    model_id: uuid.UUID
    tenant_id: uuid.UUID
    format: str
    export_uri: str
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class InferenceServed:
    inference_id: uuid.UUID
    model_id: uuid.UUID
    tenant_id: uuid.UUID
    detection_count: int
    latency_ms: int
    occurred_at: datetime = field(default_factory=_now)


@dataclass(frozen=True, slots=True)
class ModelDriftDetected:
    model_id: uuid.UUID
    tenant_id: uuid.UUID
    drift_score: float
    threshold: float
    occurred_at: datetime = field(default_factory=_now)
