"""Report use case"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
import structlog
from app.modules.yolo.domain.report import InferenceReport, TrainingReport

log = structlog.get_logger()


class ReportUseCase:
    def __init__(self, training_repo: Any, model_repo: Any,
                  dataset_repo: Any, inference_repo: Any) -> None:
        self._trainings = training_repo
        self._models = model_repo
        self._datasets = dataset_repo
        self._inferences = inference_repo

    async def training_report(self, ctx: Any, training_id: uuid.UUID) -> dict:
        tr = await self._trainings.find_by_id(ctx, training_id)
        if tr is None:
            raise ValueError(f"training {training_id} not found")
        models = await self._models.find_by_training(ctx, training_id)
        best = models[0] if models else None
        report = TrainingReport(
            training_id=tr.id, model_id=best.id if best else uuid.UUID(int=0),
            dataset_id=tr.dataset_id, model_type=tr.model_type,
            epochs_completed=tr.epochs, duration_ms=tr.duration_ms or 0,
            final_mAP50=float(best.mAP50) if best else 0.0,
            final_mAP50_95=float(best.mAP50_95) if best else 0.0,
            best_epoch=tr.epochs)
        return report.to_dict()

    async def model_report(self, ctx: Any, model_id: uuid.UUID,
                            period_days: int = 30) -> dict:
        since = datetime.now(UTC) - timedelta(days=period_days)
        stats = await self._inferences.stats_by_model(ctx, model_id, since)
        report = InferenceReport(
            model_id=model_id, period_start=since,
            period_end=datetime.now(UTC),
            total_inferences=stats.get("count", 0),
            total_detections=stats.get("total_detections", 0),
            avg_latency_ms=stats.get("avg_latency_ms", 0.0),
            p50_latency_ms=stats.get("avg_latency_ms", 0.0),
            p95_latency_ms=stats.get("max_latency_ms", 0.0),
            p99_latency_ms=stats.get("max_latency_ms", 0.0))
        return report.to_dict()

    async def dataset_report(self, ctx: Any, dataset_id: uuid.UUID) -> dict:
        ds = await self._datasets.find_by_id(ctx, dataset_id)
        if ds is None:
            raise ValueError(f"dataset {dataset_id} not found")
        return {"dataset_id": str(dataset_id), "name": ds.name,
                "format": ds.format, "image_count": ds.image_count,
                "class_count": ds.class_count, "status": ds.status}

    async def tenant_summary(self, ctx: Any) -> dict:
        _, total = await self._datasets.find_paginated(ctx, 1, 1000)
        models = await self._models.find_active(ctx)
        return {"datasets_total": total, "models_total": len(models),
                "top_models": [{"id": str(m.id), "name": m.name,
                                 "mAP50": str(m.mAP50),
                                 "mAP50_95": str(m.mAP50_95)}
                                for m in models[:5]]}
