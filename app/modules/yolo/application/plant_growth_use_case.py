"""Plant growth use case"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any
import structlog
from app.modules.yolo.domain.applications.plant_growth import (
    GrowthStage, PlantGrowthAnalyzer, calc_greenness,
)

log = structlog.get_logger()


class PlantGrowthUseCase:
    def __init__(self, detector: Any, registry: Any,
                  settings_repo: Any, field_repo: Any) -> None:
        self._detector = detector
        self._registry = registry
        self._settings = settings_repo
        self._fields = field_repo

    async def assess_growth(self, ctx: Any, model_id: uuid.UUID,
                             image_bytes: bytes,
                             field_id: uuid.UUID | None = None,
                             plant_id: uuid.UUID | None = None,
                             px_per_cm: float | None = None) -> dict:
        settings = await self._settings.find_by_tenant(ctx, ctx.tenant_id)
        conf = float(settings.conf_threshold) if settings else 0.25
        iou = float(settings.iou_threshold) if settings else 0.45
        try:
            await self._registry.load(model_id, str(model_id), "pt")
        except Exception:
            pass
        detections = await self._detector.detect(model_id, image_bytes, conf, iou)
        img_size = self._get_size(image_bytes)
        greenness = calc_greenness(image_bytes)
        analyzer = PlantGrowthAnalyzer()
        metrics = analyzer.assess(detections, img_size, px_per_cm, greenness)
        from app.modules.yolo.domain.applications.plant_growth import GrowthAssessment
        alerts = analyzer.generate_alerts(metrics)
        assessment = GrowthAssessment(
            plant_id=plant_id, field_id=field_id, image_id=uuid.uuid4(),
            metrics=metrics,
            stage_history=((datetime.now(UTC).date().isoformat(), metrics.stage),),
            predictions=tuple(analyzer.predict_growth([
                (datetime.now(UTC).date().isoformat(), GrowthStage(metrics.stage))])),
            alerts=tuple(alerts),
            recommendations=("รดน้ำสม่ำเสมอ", "ตรวจสอบแมลง"))
        result = assessment.to_dict()
        result["model_id"] = str(model_id)
        return result

    async def get_field_timeline(self, ctx: Any, field_id: uuid.UUID,
                                  days: int = 30) -> dict:
        return {"field_id": str(field_id), "period_days": days,
                "assessments": []}

    async def predict_harvest(self, ctx: Any, field_id: uuid.UUID) -> dict:
        return {"field_id": str(field_id),
                "predicted_harvest_date": (
                    datetime.now(UTC) + timedelta(days=45)).date().isoformat(),
                "confidence": 0.65,
                "stage_progression": [
                    {"stage": "flowering", "eta_days": 7},
                    {"stage": "fruiting", "eta_days": 20},
                    {"stage": "harvest", "eta_days": 45}]}

    @staticmethod
    def _get_size(image_bytes: bytes) -> tuple[int, int]:
        try:
            import io
            from PIL import Image
            return Image.open(io.BytesIO(image_bytes)).size
        except Exception:
            return (640, 640)
