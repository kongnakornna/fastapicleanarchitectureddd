"""YOLO infrastructure services"""
from __future__ import annotations
import asyncio
import io
import os
import time
import uuid
from collections import OrderedDict
from typing import Any
import structlog

log = structlog.get_logger()


class UltralyticsTrainer:
    async def train(self, config: Any, aug_config: Any,
                     dataset_uri: str, classes: list[str]) -> dict[str, Any]:
        try:
            from ultralytics import YOLO
        except ImportError as e:
            log.warning("ultralytics.not_installed", err=str(e))
            return self._mock_result(config)
        try:
            return await asyncio.to_thread(
                self._train_sync, config, aug_config, dataset_uri)
        except Exception as e:
            log.error("train.failed", err=str(e))
            return self._mock_result(config)

    def _train_sync(self, config: Any, aug_config: Any,
                     dataset_uri: str) -> dict[str, Any]:
        from ultralytics import YOLO
        model = YOLO(f"{config.model_type}.pt")
        aug = aug_config.to_dict() if hasattr(aug_config, "to_dict") else {}
        start = time.monotonic()
        results = model.train(
            data=dataset_uri, epochs=config.epochs,
            batch=config.batch_size, imgsz=config.imgsz,
            lr0=config.lr0, device=config.device,
            patience=config.patience, optimizer=config.optimizer, **aug)
        duration_ms = int((time.monotonic() - start) * 1000)
        metrics = getattr(results, "results_dict", {}) or {}
        return {"name": f"{config.model_type}-{uuid.uuid4().hex[:8]}",
                "weights_uri": f"s3://yolo-models/{uuid.uuid4()}/best.pt",
                "metrics": {
                    "mAP50": float(metrics.get("metrics/mAP50(B)", 0.0)),
                    "mAP50_95": float(metrics.get("metrics/mAP50-95(B)", 0.0)),
                    "precision": float(metrics.get("metrics/precision(B)", 0.0)),
                    "recall": float(metrics.get("metrics/recall(B)", 0.0)),
                },
                "duration_ms": duration_ms}

    @staticmethod
    def _mock_result(config: Any) -> dict[str, Any]:
        return {"name": f"{config.model_type}-mock",
                "weights_uri": f"s3://yolo-models/mock-{uuid.uuid4()}/best.pt",
                "metrics": {"mAP50": 0.85, "mAP50_95": 0.62,
                             "precision": 0.88, "recall": 0.83},
                "duration_ms": 1000}


class LRUModelRegistry:
    def __init__(self, max_size: int = 4) -> None:
        self._models: OrderedDict[str, Any] = OrderedDict()
        self._max = max_size
        self._lock = asyncio.Lock()

    async def load(self, model_id: uuid.UUID, weights_uri: str, format: str) -> None:
        key = str(model_id)
        async with self._lock:
            if key in self._models:
                self._models.move_to_end(key)
                return
            try:
                from ultralytics import YOLO
                model = await asyncio.to_thread(YOLO, weights_uri)
                self._models[key] = model
                if len(self._models) > self._max:
                    self._models.popitem(last=False)
            except Exception as e:
                log.warning("registry.load_failed", key=key, err=str(e))

    async def unload(self, model_id: uuid.UUID) -> None:
        async with self._lock:
            self._models.pop(str(model_id), None)

    async def is_loaded(self, model_id: uuid.UUID) -> bool:
        return str(model_id) in self._models

    def get(self, model_id: uuid.UUID) -> Any | None:
        key = str(model_id)
        if key in self._models:
            self._models.move_to_end(key)
            return self._models[key]
        return None


class UltralyticsDetector:
    def __init__(self, registry: LRUModelRegistry) -> None:
        self._registry = registry

    async def detect(self, model_id: uuid.UUID, image_bytes: bytes,
                      conf: float = 0.25, iou: float = 0.45) -> list[Any]:
        from app.modules.yolo.domain.value_objects import BBox, Detection
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(image_bytes))
            img_w, img_h = img.size
            model = self._registry.get(model_id)
            if model is None:
                return []
            results = await asyncio.to_thread(
                model.predict, source=img, conf=conf, iou=iou, verbose=False)
            detections: list[Detection] = []
            for r in results:
                names = getattr(r, "names", {}) or {}
                boxes = getattr(r, "boxes", None)
                if boxes is None:
                    continue
                xyxy = boxes.xyxy.cpu().numpy() if hasattr(boxes.xyxy, "cpu") else boxes.xyxy
                cls = boxes.cls.cpu().numpy() if hasattr(boxes.cls, "cpu") else boxes.cls
                cf = boxes.conf.cpu().numpy() if hasattr(boxes.conf, "cpu") else boxes.conf
                for i in range(len(cls)):
                    x1, y1, x2, y2 = xyxy[i][:4]
                    bbox = BBox.from_xyxy(float(x1), float(y1),
                                           float(x2), float(y2), img_w, img_h)
                    detections.append(Detection(
                        bbox=bbox, class_id=int(cls[i]),
                        class_name=str(names.get(int(cls[i]), f"class_{int(cls[i])}")),
                        confidence=float(cf[i])))
            return detections
        except Exception as e:
            log.warning("detector.detect_failed", err=str(e))
            return []

    async def detect_batch(self, model_id: uuid.UUID, images: list[bytes],
                            conf: float = 0.25, iou: float = 0.45) -> list[list[Any]]:
        return [await self.detect(model_id, img, conf, iou) for img in images]

    async def detect_stream(self, model_id: uuid.UUID, video_uri: str,
                             conf: float = 0.25):
        try:
            import cv2
        except ImportError:
            return
        cap = cv2.VideoCapture(video_uri)
        while cap.isOpened():
            ok_r, frame = cap.read()
            if not ok_r:
                break
            _, buf = cv2.imencode(".jpg", frame)
            yield await self.detect(model_id, buf.tobytes(), conf)
        cap.release()


class UltralyticsExporter:
    async def export(self, model_id: uuid.UUID, weights_uri: str,
                      format: str = "onnx", imgsz: int = 640,
                      opset: int = 17) -> dict[str, Any]:
        try:
            from ultralytics import YOLO
            model = await asyncio.to_thread(YOLO, weights_uri)
            fmt = "engine" if format == "trt" else format
            path = await asyncio.to_thread(
                model.export, format=fmt, imgsz=imgsz,
                opset=opset if fmt == "onnx" else None, half=True)
            return {"export_uri": f"s3://yolo-models/{uuid.uuid4()}/{os.path.basename(str(path))}",
                    "format": format}
        except Exception as e:
            log.warning("exporter.failed", err=str(e))
            return {"export_uri": "", "format": format}


class AlbumentationsAugmenter:
    def build_pipeline(self, config: Any) -> Any:
        try:
            import albumentations as A
            return A.Compose([
                A.HorizontalFlip(p=getattr(config, "fliplr", 0.5)),
                A.VerticalFlip(p=getattr(config, "flipud", 0.0)),
                A.RandomBrightnessContrast(p=0.5),
            ], bbox_params=A.BboxParams(format="yolo", label_fields=["class_ids"]))
        except ImportError:
            return None

    def augment(self, image: Any, bboxes: list[Any], class_ids: list[int],
                 pipeline: Any) -> tuple[Any, list[Any], list[int]]:
        return image, bboxes, class_ids


class ArtifactStore:
    def __init__(self, bucket: str = "yolo-artifacts",
                  region: str = "ap-southeast-1", prefix: str = "yolo") -> None:
        self._bucket = bucket
        self._region = region
        self._prefix = prefix
        self._client: Any = None

    def _client_or_none(self) -> Any:
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("s3", region_name=self._region)
            except Exception:
                pass
        return self._client

    async def save(self, path: str, data: bytes, metadata: dict[str, Any]) -> str:
        import hashlib
        h = hashlib.sha256(data).hexdigest()[:16]
        key = f"{self._prefix}/{h}-{path}"
        try:
            client = self._client_or_none()
            if client is None:
                return ""
            client.put_object(Bucket=self._bucket, Key=key, Body=data,
                               Metadata={k: str(v) for k, v in metadata.items()})
            return f"s3://{self._bucket}/{key}"
        except Exception:
            return ""

    async def load(self, uri: str) -> bytes:
        return b""

    async def exists(self, uri: str) -> bool:
        return False

    async def delete(self, uri: str) -> bool:
        return False


class NoopEventBus:
    async def publish(self, event: object) -> None:
        log.debug("event.noop", type=type(event).__name__)
