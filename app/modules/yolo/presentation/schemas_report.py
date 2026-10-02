"""Report schemas"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class TrainingReportResponse(BaseModel):
    training_id: str; model_id: str; dataset_id: str; model_type: str
    epochs_completed: int; duration_ms: int
    final_mAP50: float; final_mAP50_95: float; best_epoch: int
    loss_curve: list[list[Any]] = Field(default_factory=list)
    per_class_ap: dict[str, float] = Field(default_factory=dict)
    generated_at: str
    model_config = ConfigDict(extra="forbid")


class InferenceReportResponse(BaseModel):
    model_id: str; period_start: str; period_end: str
    total_inferences: int = 0; total_detections: int = 0
    avg_latency_ms: float = 0.0; p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0; p99_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    top_classes: dict[str, int] = Field(default_factory=dict)
    drift_score: float = 0.0
    model_config = ConfigDict(extra="forbid")
