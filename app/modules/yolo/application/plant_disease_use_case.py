"""Plant disease use case"""
from __future__ import annotations
import uuid
from typing import Any
import structlog
from app.modules.yolo.domain.applications.plant_disease import (
    DISEASE_CATALOG, PlantDiseaseDiagnoser,
)

log = structlog.get_logger()


class PlantDiseaseUseCase:
    def __init__(self, detector: Any, registry: Any,
                  class_repo: Any, settings_repo: Any) -> None:
        self._detector = detector
        self._registry = registry
        self._classes = class_repo
        self._settings = settings_repo

    async def diagnose_image(self, ctx: Any, model_id: uuid.UUID,
                               image_bytes: bytes,
                               dataset_id: uuid.UUID | None = None,
                               plant_species: str | None = None) -> dict:
        settings = await self._settings.find_by_tenant(ctx, ctx.tenant_id)
        conf = float(settings.conf_threshold) if settings else 0.25
        iou = float(settings.iou_threshold) if settings else 0.45
        try:
            await self._registry.load(model_id, str(model_id), "pt")
        except Exception:
            pass
        detections = await self._detector.detect(model_id, image_bytes, conf, iou)
        class_map: dict[int, str] = {}
        if dataset_id:
            classes = await self._classes.find_by_dataset(ctx, dataset_id)
            class_map = {c.class_index: c.name for c in classes}
        diagnoser = PlantDiseaseDiagnoser()
        diagnosis = diagnoser.diagnose(detections, class_map, plant_species)
        result = diagnosis.to_dict()
        result["model_id"] = str(model_id)
        return result

    async def get_catalog(self, ctx: Any,
                           pathogen_type: str | None = None) -> list[dict]:
        items: list[dict] = []
        for code, info in DISEASE_CATALOG.items():
            if pathogen_type and info.pathogen_type != pathogen_type:
                continue
            items.append({"code": info.code, "name_th": info.name_th,
                           "name_en": info.name_en,
                           "pathogen_type": info.pathogen_type,
                           "treatment": list(info.treatment),
                           "prevention": list(info.prevention)})
        return items

    async def get_treatment_plan(self, ctx: Any, disease_code: str) -> dict:
        info = DISEASE_CATALOG.get(disease_code)
        if info is None:
            raise ValueError(f"disease {disease_code} not found")
        return {"code": info.code, "name_th": info.name_th,
                "name_en": info.name_en,
                "treatment": list(info.treatment),
                "prevention": list(info.prevention),
                "plan": [{"day": 0, "action": "spray",
                           "product": info.treatment[0] if info.treatment else "-"},
                          {"day": 7, "action": "inspect"},
                          {"day": 14, "action": "spray",
                           "product": info.treatment[0] if info.treatment else "-"}]}
