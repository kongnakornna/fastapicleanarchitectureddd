"""YOLO use cases"""
from __future__ import annotations
import time
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import structlog

from app.modules.yolo.application.utils import hash_bytes, image_cache_key
from app.modules.yolo.domain.enums import DatasetStatus, InferenceSource, TrainingStatus
from app.modules.yolo.domain.events import (
    AnnotationsCreated, DatasetRegistered, ImagesUploaded,
    InferenceServed, ModelExported, TrainingCompleted, TrainingStarted,
)
from app.modules.yolo.domain.exceptions import (
    DatasetNotFoundError, ModelNotFoundError, TrainingFailedError,
)
from app.modules.yolo.domain.value_objects import AugConfig, BBox, Detection, TrainConfig
from app.modules.yolo.infrastructure.models import (
    AnnotationModel, ClassModel, DatasetModel, ImageModel,
    InferenceModel, ModelModel, TrainingModel,
)

log = structlog.get_logger()


class YOLOUseCase:
    def __init__(self, dataset_repo: Any, class_repo: Any, image_repo: Any,
                 annotation_repo: Any, training_repo: Any, model_repo: Any,
                 inference_repo: Any, trainer: Any, detector: Any,
                 model_registry: Any, exporter: Any, artifact_store: Any,
                 cache: Any, rate_limiter: Any, event_bus: Any) -> None:
        self._dataset_repo = dataset_repo
        self._class_repo = class_repo
        self._image_repo = image_repo
        self._annotation_repo = annotation_repo
        self._training_repo = training_repo
        self._model_repo = model_repo
        self._inference_repo = inference_repo
        self._trainer = trainer
        self._detector = detector
        self._registry = model_registry
        self._exporter = exporter
        self._store = artifact_store
        self._cache = cache
        self._rate = rate_limiter
        self._bus = event_bus

    # Datasets
    async def create_dataset(self, ctx: Any, name: str, format_: str = "yolo") -> dict:
        ds = DatasetModel(tenant_id=ctx.tenant_id, name=name,
                           format=format_, status=DatasetStatus.DRAFT.value)
        saved = await self._dataset_repo.save(ctx, ds)
        await self._bus.publish(DatasetRegistered(
            dataset_id=saved.id, tenant_id=ctx.tenant_id,
            name=name, format=format_, image_count=0))
        return {"id": str(saved.id), "name": saved.name,
                "format": saved.format, "status": saved.status}

    async def list_datasets(self, ctx: Any, page: int = 1, size: int = 50) -> dict:
        rows, total = await self._dataset_repo.find_paginated(ctx, page, size)
        return {"items": [{"id": str(r.id), "name": r.name, "format": r.format,
                            "status": r.status, "image_count": r.image_count,
                            "class_count": r.class_count, "version": r.version}
                           for r in rows],
                "total": total, "page": page, "size": size}

    async def get_dataset(self, ctx: Any, dataset_id: uuid.UUID) -> dict:
        ds = await self._dataset_repo.find_by_id(ctx, dataset_id)
        if ds is None:
            raise DatasetNotFoundError(f"dataset {dataset_id} not found")
        classes = await self._class_repo.find_by_dataset(ctx, dataset_id)
        return {"id": str(ds.id), "name": ds.name, "format": ds.format,
                "root_uri": ds.root_uri, "image_count": ds.image_count,
                "class_count": ds.class_count, "status": ds.status,
                "version": ds.version, "splits": dict(ds.splits_json or {}),
                "classes": [{"id": str(c.id), "name": c.name,
                              "class_index": c.class_index, "color": c.color}
                             for c in classes]}

    async def define_classes(self, ctx: Any, dataset_id: uuid.UUID,
                              classes: list[dict]) -> dict:
        ds = await self._dataset_repo.find_by_id(ctx, dataset_id)
        if ds is None:
            raise DatasetNotFoundError(f"dataset {dataset_id} not found")
        rows = [ClassModel(tenant_id=ctx.tenant_id, dataset_id=dataset_id,
                            name=c["name"], class_index=c["class_index"],
                            color=c.get("color", "#FF0000")) for c in classes]
        saved = await self._class_repo.bulk_create(ctx, rows)
        ds.class_count = len(saved)
        await self._dataset_repo.update(ctx, ds)
        return {"dataset_id": str(dataset_id), "class_count": len(saved),
                "classes": [{"id": str(c.id), "name": c.name,
                              "class_index": c.class_index} for c in saved]}

    # Images
    async def upload_images(self, ctx: Any, dataset_id: uuid.UUID,
                             images: list[dict], split: str = "train") -> dict:
        ds = await self._dataset_repo.find_by_id(ctx, dataset_id)
        if ds is None:
            raise DatasetNotFoundError(f"dataset {dataset_id} not found")
        image_ids = []
        for img in images:
            row = ImageModel(tenant_id=ctx.tenant_id, dataset_id=dataset_id,
                              uri=img["uri"], content_hash=img["content_hash"],
                              width=img.get("width", 0), height=img.get("height", 0),
                              size_bytes=img.get("size_bytes", 0), split=split)
            saved = await self._image_repo.save(ctx, row)
            image_ids.append(saved.id)
        ds.image_count = await self._image_repo.count_by_dataset(ctx, dataset_id, None)
        if ds.image_count > 0:
            ds.status = DatasetStatus.READY.value
        await self._dataset_repo.update(ctx, ds)
        await self._bus.publish(ImagesUploaded(
            dataset_id=dataset_id, tenant_id=ctx.tenant_id,
            image_ids=tuple(image_ids), count=len(image_ids)))
        return {"dataset_id": str(dataset_id), "uploaded": len(image_ids)}

    # Annotations
    async def create_annotations(self, ctx: Any, image_id: uuid.UUID,
                                  annotations: list[dict]) -> dict:
        img = await self._image_repo.find_by_id(ctx, image_id)
        if img is None:
            raise DatasetNotFoundError(f"image {image_id} not found")
        rows = []
        for a in annotations:
            bbox = BBox(x_center=float(a["x_center"]), y_center=float(a["y_center"]),
                         width=float(a["width"]), height=float(a["height"]))
            rows.append(AnnotationModel(
                tenant_id=ctx.tenant_id, image_id=image_id,
                class_id=uuid.UUID(a["class_id"]),
                x_center=bbox.x_center, y_center=bbox.y_center,
                width=bbox.width, height=bbox.height,
                confidence=Decimal(str(a.get("confidence", 1.0))),
                is_hard=bool(a.get("is_hard", False)),
                source=a.get("source", "manual")))
        saved = await self._annotation_repo.bulk_create(ctx, rows)
        img.annotation_count = len(saved)
        await self._image_repo.save(ctx, img)
        await self._bus.publish(AnnotationsCreated(
            image_id=image_id, tenant_id=ctx.tenant_id, count=len(saved)))
        return {"image_id": str(image_id), "created": len(saved)}

    # Training
    async def start_training(self, ctx: Any, dataset_id: uuid.UUID,
                              config: TrainConfig, aug_config: AugConfig | None = None) -> dict:
        ds = await self._dataset_repo.find_by_id(ctx, dataset_id)
        if ds is None:
            raise DatasetNotFoundError(f"dataset {dataset_id} not found")
        aug_cfg = aug_config or AugConfig()
        tr = TrainingModel(
            tenant_id=ctx.tenant_id, dataset_id=dataset_id,
            model_type=config.model_type, epochs=config.epochs,
            batch_size=config.batch_size, imgsz=config.imgsz,
            lr0=Decimal(str(config.lr0)), device=config.device,
            patience=config.patience, optimizer=config.optimizer,
            aug_config_json=aug_cfg.to_dict(),
            status=TrainingStatus.PENDING.value,
            started_at=datetime.now(UTC))
        saved_tr = await self._training_repo.create(ctx, tr)
        await self._training_repo.update_status(ctx, saved_tr.id,
                                                  TrainingStatus.RUNNING.value)
        await self._bus.publish(TrainingStarted(
            training_id=saved_tr.id, tenant_id=ctx.tenant_id,
            dataset_id=dataset_id, model_type=config.model_type,
            epochs=config.epochs))
        classes = await self._class_repo.find_by_dataset(ctx, dataset_id)
        class_names = [c.name for c in classes]
        t0 = time.monotonic()
        try:
            result = await self._trainer.train(config=config, aug_config=aug_cfg,
                                                 dataset_uri=ds.root_uri,
                                                 classes=class_names)
        except Exception as exc:
            await self._training_repo.update_status(ctx, saved_tr.id,
                                                      TrainingStatus.FAILED.value)
            raise TrainingFailedError(str(exc)) from exc
        duration_ms = int((time.monotonic() - t0) * 1000)
        metrics = result.get("metrics", {})
        mAP50 = float(metrics.get("mAP50", 0.0))
        mAP50_95 = float(metrics.get("mAP50_95", 0.0))
        model = ModelModel(
            tenant_id=ctx.tenant_id, training_id=saved_tr.id,
            name=result.get("name", f"yolo-{saved_tr.id}"), version=1,
            weights_uri=result.get("weights_uri", ""),
            weights_hash=hash_bytes(str(result.get("weights_uri", "")).encode()),
            format="pt", mAP50=Decimal(str(mAP50)),
            mAP50_95=Decimal(str(mAP50_95)),
            precision_=Decimal(str(metrics.get("precision", 0.0))),
            recall_=Decimal(str(metrics.get("recall", 0.0))),
            metrics_json=metrics, is_active=True)
        saved_model = await self._model_repo.save(ctx, model)
        await self._training_repo.set_best_model(ctx, saved_tr.id, saved_model.id)
        await self._training_repo.update_status(ctx, saved_tr.id,
                                                  TrainingStatus.SUCCESS.value)
        await self._bus.publish(TrainingCompleted(
            training_id=saved_tr.id, model_id=saved_model.id,
            tenant_id=ctx.tenant_id, mAP50=mAP50, mAP50_95=mAP50_95,
            duration_ms=duration_ms))
        return {"training_id": str(saved_tr.id), "model_id": str(saved_model.id),
                "status": TrainingStatus.SUCCESS.value,
                "mAP50": mAP50, "mAP50_95": mAP50_95,
                "duration_ms": duration_ms}

    async def get_training_status(self, ctx: Any, training_id: uuid.UUID) -> dict:
        tr = await self._training_repo.find_by_id(ctx, training_id)
        if tr is None:
            raise DatasetNotFoundError(f"training {training_id} not found")
        return {"id": str(tr.id), "dataset_id": str(tr.dataset_id),
                "model_type": tr.model_type, "epochs": tr.epochs,
                "status": tr.status, "progress": tr.progress,
                "best_model_id": str(tr.best_model_id) if tr.best_model_id else None,
                "error_message": tr.error_message,
                "started_at": tr.started_at.isoformat() if tr.started_at else None,
                "finished_at": tr.finished_at.isoformat() if tr.finished_at else None}

    # Models
    async def list_models(self, ctx: Any, only_active: bool = True) -> list[dict]:
        rows = (await self._model_repo.find_active(ctx) if only_active
                else await self._model_repo.find_deployed(ctx))
        return [{"id": str(r.id), "name": r.name, "version": r.version,
                 "format": r.format, "mAP50": str(r.mAP50),
                 "mAP50_95": str(r.mAP50_95), "is_active": r.is_active,
                 "is_deployed": r.is_deployed} for r in rows]

    async def export_model(self, ctx: Any, model_id: uuid.UUID,
                            format_: str = "onnx", imgsz: int = 640,
                            opset: int = 17) -> dict:
        m = await self._model_repo.find_by_id(ctx, model_id)
        if m is None:
            raise ModelNotFoundError(f"model {model_id} not found")
        result = await self._exporter.export(
            model_id=model_id, weights_uri=m.weights_uri,
            format=format_, imgsz=imgsz, opset=opset)
        m.format = format_
        m.export_uri = result.get("export_uri", "")
        await self._model_repo.update(ctx, m)
        await self._bus.publish(ModelExported(
            model_id=model_id, tenant_id=ctx.tenant_id,
            format=format_, export_uri=m.export_uri))
        return {"model_id": str(model_id), "format": format_,
                "export_uri": m.export_uri}

    # Inference
    async def detect(self, ctx: Any, model_id: uuid.UUID, image_bytes: bytes,
                      conf: float = 0.25, iou: float = 0.45,
                      source: str = "api") -> dict:
        m = await self._model_repo.find_by_id(ctx, model_id)
        if m is None:
            raise ModelNotFoundError(f"model {model_id} not found")
        image_hash = hash_bytes(image_bytes)
        ck = image_cache_key(image_hash, str(model_id), conf, iou)
        cached = await self._cache.get(ck)
        if cached:
            return cached
        t0 = time.monotonic()
        detections: list[Detection] = []
        try:
            detections = await self._detector.detect(
                model_id=model_id, image_bytes=image_bytes,
                conf=conf, iou=iou)
        except Exception as exc:
            log.warning(f"detector.failed: {exc}")
        latency_ms = int((time.monotonic() - t0) * 1000)
        det_json = [d.to_dict() for d in detections]
        inf_row = InferenceModel(
            tenant_id=ctx.tenant_id, model_id=model_id,
            image_hash=image_hash, detections_json=det_json,
            detection_count=len(detections), latency_ms=latency_ms,
            source=source)
        saved = await self._inference_repo.create(ctx, inf_row)
        response = {"inference_id": str(saved.id), "model_id": str(model_id),
                    "image_hash": image_hash, "detections": det_json,
                    "detection_count": len(detections), "latency_ms": latency_ms}
        await self._cache.set(ck, response, ttl=300)
        await self._bus.publish(InferenceServed(
            inference_id=saved.id, model_id=model_id,
            tenant_id=ctx.tenant_id, detection_count=len(detections),
            latency_ms=latency_ms))
        return response

    async def detect_batch(self, ctx: Any, model_id: uuid.UUID,
                            images: list[bytes], conf: float = 0.25,
                            iou: float = 0.45) -> dict:
        if len(images) > 32:
            raise TrainingFailedError("batch size exceeds 32")
        results = []
        for img in images:
            try:
                r = await self.detect(ctx, model_id, img, conf, iou,
                                       source=InferenceSource.BATCH.value)
                results.append(r)
            except Exception as exc:
                results.append({"error": str(exc)})
        return {"model_id": str(model_id), "total": len(images),
                "results": results}
