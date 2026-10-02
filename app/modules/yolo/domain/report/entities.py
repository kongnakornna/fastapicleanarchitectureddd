"""Report entities"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class TrainingReport:
    training_id: uuid.UUID
    model_id: uuid.UUID
    dataset_id: uuid.UUID
    model_type: str
    epochs_completed: int
    duration_ms: int
    final_mAP50: float
    final_mAP50_95: float
    best_epoch: int
    loss_curve: tuple[tuple[int, float], ...] = ()
    per_class_ap: tuple[tuple[str, float], ...] = ()
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        return {"training_id": str(self.training_id),
                "model_id": str(self.model_id),
                "dataset_id": str(self.dataset_id),
                "model_type": self.model_type,
                "epochs_completed": self.epochs_completed,
                "duration_ms": self.duration_ms,
                "final_mAP50": self.final_mAP50,
                "final_mAP50_95": self.final_mAP50_95,
                "best_epoch": self.best_epoch,
                "loss_curve": list(self.loss_curve),
                "per_class_ap": dict(self.per_class_ap),
                "generated_at": self.generated_at.isoformat()}


@dataclass(frozen=True, slots=True)
class InferenceReport:
    model_id: uuid.UUID
    period_start: datetime
    period_end: datetime
    total_inferences: int = 0
    total_detections: int = 0
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    top_classes: tuple[tuple[str, int], ...] = ()
    drift_score: float = 0.0

    def to_dict(self) -> dict:
        return {"model_id": str(self.model_id),
                "period_start": self.period_start.isoformat(),
                "period_end": self.period_end.isoformat(),
                "total_inferences": self.total_inferences,
                "total_detections": self.total_detections,
                "avg_latency_ms": self.avg_latency_ms,
                "p50_latency_ms": self.p50_latency_ms,
                "p95_latency_ms": self.p95_latency_ms,
                "p99_latency_ms": self.p99_latency_ms,
                "cache_hit_rate": self.cache_hit_rate,
                "top_classes": dict(self.top_classes),
                "drift_score": self.drift_score}
