"""Plant growth monitoring domain"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from app.modules.yolo.domain.value_objects import Detection


class GrowthStage(StrEnum):
    SEEDLING = "seedling"; VEGETATIVE = "vegetative"
    FLOWERING = "flowering"; FRUITING = "fruiting"
    MATURE = "mature"; HARVEST = "harvest"


@dataclass(frozen=True, slots=True)
class GrowthMetrics:
    stage: str
    stage_confidence: float
    plant_height_px: float
    plant_height_cm: float | None
    leaf_area_px: float
    leaf_area_pct: float
    leaf_count: int
    canopy_width_px: float
    greenness_index: float
    health_score: float
    growth_rate_pct: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"stage": self.stage,
                "stage_confidence": self.stage_confidence,
                "plant_height_px": self.plant_height_px,
                "plant_height_cm": self.plant_height_cm,
                "leaf_area_px": self.leaf_area_px,
                "leaf_area_pct": self.leaf_area_pct,
                "leaf_count": self.leaf_count,
                "canopy_width_px": self.canopy_width_px,
                "greenness_index": self.greenness_index,
                "health_score": self.health_score,
                "growth_rate_pct": self.growth_rate_pct}


@dataclass(frozen=True, slots=True)
class GrowthAssessment:
    plant_id: uuid.UUID | None
    field_id: uuid.UUID | None
    image_id: uuid.UUID
    metrics: GrowthMetrics
    stage_history: tuple[tuple[str, str], ...] = ()
    predictions: tuple[dict[str, Any], ...] = ()
    alerts: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {"image_id": str(self.image_id),
                "plant_id": str(self.plant_id) if self.plant_id else None,
                "field_id": str(self.field_id) if self.field_id else None,
                "metrics": self.metrics.to_dict(),
                "stage_history": [{"date": d, "stage": s}
                                   for d, s in self.stage_history],
                "predictions": list(self.predictions),
                "alerts": list(self.alerts),
                "recommendations": list(self.recommendations),
                "generated_at": self.generated_at.isoformat()}


class PlantGrowthAnalyzer:
    DEFAULT_STAGE_MAP = {
        0: GrowthStage.SEEDLING.value,
        1: GrowthStage.VEGETATIVE.value,
        2: GrowthStage.FLOWERING.value,
        3: GrowthStage.FRUITING.value,
        4: GrowthStage.MATURE.value,
        5: GrowthStage.HARVEST.value,
    }

    def assess(self, detections: list[Detection],
                img_size: tuple[int, int],
                px_per_cm: float | None = None,
                greenness: float = 0.5,
                stage_map: dict[int, str] | None = None) -> GrowthMetrics:
        img_w, img_h = img_size
        smap = stage_map or self.DEFAULT_STAGE_MAP
        stage = GrowthStage.VEGETATIVE.value
        stage_conf = 0.5
        if detections:
            top = max(detections, key=lambda d: d.confidence)
            stage = smap.get(top.class_id, GrowthStage.VEGETATIVE.value)
            stage_conf = top.confidence
        h_px, h_cm = self._estimate_height(detections, img_h, px_per_cm)
        leaf_area_px = sum(d.bbox.width * d.bbox.height * img_w * img_h
                            for d in detections)
        leaf_area_pct = leaf_area_px / (img_w * img_h)
        canopy_w_px = max((d.bbox.width * img_w for d in detections), default=0.0)
        health = self._health_score(greenness, leaf_area_pct, len(detections))
        return GrowthMetrics(
            stage=stage, stage_confidence=stage_conf,
            plant_height_px=round(h_px, 2),
            plant_height_cm=round(h_cm, 2) if h_cm else None,
            leaf_area_px=round(leaf_area_px, 2),
            leaf_area_pct=round(leaf_area_pct, 4),
            leaf_count=len(detections),
            canopy_width_px=round(canopy_w_px, 2),
            greenness_index=round(greenness, 3),
            health_score=round(health, 2))

    @staticmethod
    def _estimate_height(detections: list[Detection], img_h: int,
                          px_per_cm: float | None) -> tuple[float, float | None]:
        if not detections:
            return 0.0, None
        y_top = min(d.bbox.y_center - d.bbox.height / 2 for d in detections)
        y_bot = max(d.bbox.y_center + d.bbox.height / 2 for d in detections)
        h_px = (y_bot - y_top) * img_h
        h_cm = h_px / px_per_cm if px_per_cm and px_per_cm > 0 else None
        return h_px, h_cm

    @staticmethod
    def _health_score(greenness: float, leaf_pct: float, leaf_count: int) -> float:
        g = min(greenness, 1.0) * 50
        l = min(leaf_pct / 0.3, 1.0) * 30
        c = min(leaf_count / 20.0, 1.0) * 20
        return g + l + c

    @staticmethod
    def predict_growth(history: list[tuple[str, GrowthStage]],
                        days_ahead: int = 7) -> list[dict[str, Any]]:
        if len(history) < 2:
            return []
        stage_order = list(GrowthStage)
        idx = {s.value: i for i, s in enumerate(stage_order)}
        recent = [idx.get(h[1].value if hasattr(h[1], "value") else h[1], 0)
                  for h in history[-3:]]
        avg_rate = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
        last_stage = history[-1][1]
        current_idx = idx.get(last_stage.value if hasattr(last_stage, "value")
                                else last_stage, 0)
        preds: list[dict[str, Any]] = []
        for d in range(1, days_ahead + 1, max(days_ahead // 3, 1)):
            future_idx = int(current_idx + avg_rate * d / 7)
            future_idx = max(0, min(future_idx, len(stage_order) - 1))
            preds.append({"day": d, "stage": stage_order[future_idx].value,
                           "confidence": max(0.4, 0.9 - 0.05 * d)})
        return preds

    @staticmethod
    def generate_alerts(metrics: GrowthMetrics,
                         expected_stage: str | None = None) -> list[str]:
        alerts: list[str] = []
        if metrics.health_score < 50:
            alerts.append("สุขภาพพืชต่ำกว่าเกณฑ์ (<50)")
        if metrics.growth_rate_pct is not None and metrics.growth_rate_pct < 0:
            alerts.append("การเติบโตลดลงจากครั้งก่อน")
        if expected_stage and metrics.stage != expected_stage:
            alerts.append(f"ระยะไม่ตรงกับคาด: {metrics.stage} vs {expected_stage}")
        return alerts


def calc_greenness(image_bytes: bytes) -> float:
    try:
        import io
        import numpy as np
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.asarray(img, dtype=float)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        exg = 2 * g - r - b
        return float(np.clip(np.mean(exg) / 255.0, 0.0, 1.0))
    except Exception:
        return 0.5
