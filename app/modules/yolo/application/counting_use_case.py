"""Counting use case"""
from __future__ import annotations
import uuid
from typing import Any
import structlog
from app.modules.yolo.domain.applications.counting import (
    CountingConfig, ProductCounter,
)

log = structlog.get_logger()


class CountingUseCase:
    def __init__(self, detector: Any, registry: Any,
                  settings_repo: Any, model_repo: Any) -> None:
        self._detector = detector
        self._registry = registry
        self._settings = settings_repo
        self._models = model_repo

    async def count_image(self, ctx: Any, model_id: uuid.UUID,
                           image_bytes: bytes,
                           config: CountingConfig) -> dict[str, Any]:
        settings = await self._settings.find_by_tenant(ctx, ctx.tenant_id)
        conf = float(settings.conf_threshold) if settings else 0.25
        iou = float(settings.iou_threshold) if settings else 0.45
        try:
            await self._registry.load(model_id, str(model_id), "pt")
        except Exception:
            pass
        detections = await self._detector.detect(model_id, image_bytes, conf, iou)
        counter = ProductCounter(config)
        img_size = self._get_size(image_bytes)
        result = counter.count(detections, img_size)
        return {"model_id": str(model_id), "mode": config.mode,
                **result.to_dict()}

    async def count_batch(self, ctx: Any, model_id: uuid.UUID,
                            images: list[bytes],
                            config: CountingConfig) -> dict[str, Any]:
        results = []
        total = 0
        for img in images:
            r = await self.count_image(ctx, model_id, img, config)
            results.append(r)
            total += r["total_count"]
        return {"model_id": str(model_id), "total": total, "results": results}

    @staticmethod
    def _get_size(image_bytes: bytes) -> tuple[int, int]:
        try:
            from PIL import Image
            import io
            return Image.open(io.BytesIO(image_bytes)).size
        except Exception:
            return (640, 640)
