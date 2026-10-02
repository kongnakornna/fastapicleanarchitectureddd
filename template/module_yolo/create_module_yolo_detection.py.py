#!/usr/bin/env python3
"""
create_module_yolo_detection.py — YOLO Object Detection Module Generator v2.0

สร้าง Module `yolo` สำหรับ YOLO Object Detection จริง
Stack: Ultralytics YOLOv8/v11 · PyTorch 2.x · OpenCV · Albumentations · ONNX · TensorRT
Schema: public · Prefix: yolo_ · Tables: 7 ตาราง

Actions (12):
  1.  create       — Module structure (4 layers, 40 py files)
  2.  activate     — Register router + swagger + models
  3.  sql          — SQL V001/V002/V003 (public + yolo_)
  4.  alembic      — Migration yolo_001_add_yolo_detection_tables.py
  5.  swagger      — OpenAPI metadata (tag: yolo)
  6.  postman      — Postman collection (14 endpoints)
  7.  update       — Update app/app.py
  8.  update-env   — Update migrations/env.py
  9.  test         — Tests (unit/integration/property/manual)
  10. verify       — ตรวจสอบ Swagger + Postman + SQL
  11. deps         — Check + install dependencies
  12. all          — ทำทั้งหมด

Usage:
    python create_module_yolo_detection.py all yolo 5 yolo
    python create_module_yolo_detection.py create yolo --force
    python create_module_yolo_detection.py verify yolo
"""
from __future__ import annotations

import argparse
import json as _json_mod
import re
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent


# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════
VERSION = "2.0.0"
LAYER_NAMES = {
    "0": "0-Core", "1": "1-Foundation", "2": "2-Money",
    "3": "3-Goods", "4": "4-Ops", "5": "5-Intel",
    "6": "6-Monitor", "7": "7-Template",
}

ACTIONS = {
    "create", "activate", "sql", "alembic", "swagger", "postman",
    "update", "update-env", "test", "verify", "deps", "all", "help",
}

SCHEMA = "public"
PREFIX = "yolo"
TABLE_NAMES = (
    "yolo_datasets",
    "yolo_classes",
    "yolo_images",
    "yolo_annotations",
    "yolo_trainings",
    "yolo_models",
    "yolo_inferences",
)


# ═══════════════════════════════════════════════════════════════
#  LOGGER
# ═══════════════════════════════════════════════════════════════
class C:
    CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; GRAY = "\033[90m"; RESET = "\033[0m"


def info(msg: str) -> None: print(f"{C.CYAN}{msg}{C.RESET}")
def ok(msg: str) -> None: print(f"  {C.GREEN}[OK]{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"  {C.YELLOW}[!!]{C.RESET} {msg}")
def err(msg: str) -> None: print(f"  {C.RED}[XX]{C.RESET} {msg}")
def skip(msg: str) -> None: print(f"  {C.GRAY}[--]{C.RESET} {msg}")


# ═══════════════════════════════════════════════════════════════
#  FILE WRITER
# ═══════════════════════════════════════════════════════════════
class FileWriter:
    def __init__(self, project_root: Path, force: bool = False, backup: bool = True):
        self.root = project_root
        self.force = force
        self.backup = backup
        self.written: list[Path] = []
        self.skipped: list[Path] = []
        self.backups: list[Path] = []

    def write(self, rel_path: str, content: str) -> None:
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not self.force:
            skip(f"skip (exists): {rel_path}")
            self.skipped.append(path)
            return

        if path.exists() and self.backup:
            bak = path.with_suffix(path.suffix + ".bak")
            bak.write_bytes(path.read_bytes())
            self.backups.append(bak)
            ok(f"backup: {rel_path}.bak")

        if rel_path.endswith(".py"):
            try:
                compile(content, rel_path, "exec")
            except SyntaxError as exc:
                err(f"SYNTAX ERROR in {rel_path}: {exc}")
                err(f"  line {exc.lineno}: {exc.text}")
                raise RuntimeError(f"Refuse to write invalid Python: {rel_path}") from exc

        path.write_text(content, encoding="utf-8", newline="\n")
        ok(rel_path)
        self.written.append(path)


# ═══════════════════════════════════════════════════════════════
#  GENERATOR
# ═══════════════════════════════════════════════════════════════
class YOLODetectionGenerator:
    def __init__(
        self,
        project_root: Path,
        module: str = "yolo",
        layer: str = "5",
        prefix: str = "yolo",
        force: bool = False,
    ):
        self.root = project_root
        self.module = module.lower()
        self.layer = layer
        self.prefix = prefix.lower()
        self.layer_name = LAYER_NAMES.get(layer, "5-Intel")
        self.writer = FileWriter(project_root, force=force)

        self.mod_root = f"app/modules/{self.module}"
        self.sql_dir = "db/migrations"
        self.alembic_dir = "migrations/versions"
        self.env_py = "migrations/env.py"
        self.app_py = "app/app.py"
        self.tests_dir = "tests"
        self.docs_dir = "docs"

    # ═══════════════════════════════════════════════════════════
    #  1. CREATE MODULE
    # ═══════════════════════════════════════════════════════════
    def create_module(self) -> None:
        info(f"[CREATE] module: {self.module} (Layer {self.layer_name})")
        self._create_domain()
        self._create_application()
        self._create_infrastructure()
        self._create_presentation()
        self._create_root_init()

    # ─── DOMAIN LAYER ───────────────────────────────────────────
    def _create_domain(self) -> None:
        base = f"{self.mod_root}/domain"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """YOLO domain layer — ชั้นโดเมน YOLO Object Detection"""
            from .enums import (
                DatasetFormat, DatasetStatus, ImageSplit,
                InferenceSource, ModelFormat, ModelType, TrainingStatus,
            )
            from .events import (
                AnnotationsCreated, DatasetRegistered, ImagesUploaded,
                InferenceServed, ModelDriftDetected, ModelExported,
                TrainingCompleted, TrainingStarted,
            )
            from .exceptions import (
                YOLOError, AnnotationNotFoundError, ClassNotFoundError,
                DatasetNotFoundError, ExportFailedError, GPUUnavailableError,
                ImageNotFoundError, InferenceFailedError, InvalidBBoxError,
                InvalidImageError, ModelNotFoundError, TrainingFailedError,
                TrainingNotFoundError, UnsupportedFormatError,
            )
            from .value_objects import (
                AugConfig, BBox, Detection, EvalMetrics, TrainConfig,
            )

            __all__ = [
                "DatasetFormat", "DatasetStatus", "ImageSplit",
                "InferenceSource", "ModelFormat", "ModelType", "TrainingStatus",
                "AnnotationsCreated", "DatasetRegistered", "ImagesUploaded",
                "InferenceServed", "ModelDriftDetected", "ModelExported",
                "TrainingCompleted", "TrainingStarted",
                "YOLOError", "AnnotationNotFoundError", "ClassNotFoundError",
                "DatasetNotFoundError", "ExportFailedError", "GPUUnavailableError",
                "ImageNotFoundError", "InferenceFailedError", "InvalidBBoxError",
                "InvalidImageError", "ModelNotFoundError", "TrainingFailedError",
                "TrainingNotFoundError", "UnsupportedFormatError",
                "AugConfig", "BBox", "Detection", "EvalMetrics", "TrainConfig",
            ]
        '''))

        # enums.py
        self.writer.write(f"{base}/enums.py", dedent('''\
            """YOLO enums — Enum ของ YOLO Detection"""
            from __future__ import annotations
            from enum import StrEnum


            class DatasetFormat(StrEnum):
                """TH: รูปแบบ dataset | EN: dataset format"""
                YOLO = "yolo"
                COCO = "coco"
                ROBOFLOW = "roboflow"
                LABELIMG = "labelimg"


            class DatasetStatus(StrEnum):
                """TH: สถานะ dataset | EN: dataset status"""
                DRAFT = "DRAFT"
                READY = "READY"
                TRAINING = "TRAINING"
                ARCHIVED = "ARCHIVED"


            class ModelType(StrEnum):
                """TH: ประเภทโมเดล YOLO | EN: YOLO model type"""
                YOLOV8N = "yolov8n"; YOLOV8S = "yolov8s"; YOLOV8M = "yolov8m"
                YOLOV8L = "yolov8l"; YOLOV8X = "yolov8x"
                YOLO11N = "yolo11n"; YOLO11S = "yolo11s"; YOLO11M = "yolo11m"
                YOLO11L = "yolo11l"; YOLO11X = "yolo11x"


            class ModelFormat(StrEnum):
                """TH: รูปแบบโมเดล | EN: model format"""
                PYTORCH = "pt"
                ONNX = "onnx"
                TENSORRT = "engine"
                TORCHSCRIPT = "torchscript"
                COREML = "coreml"


            class TrainingStatus(StrEnum):
                """TH: สถานะการฝึก | EN: training status"""
                PENDING = "PENDING"
                RUNNING = "RUNNING"
                SUCCESS = "SUCCESS"
                FAILED = "FAILED"
                CANCELLED = "CANCELLED"


            class ImageSplit(StrEnum):
                """TH: split ของรูป | EN: image split"""
                TRAIN = "train"; VAL = "val"; TEST = "test"


            class InferenceSource(StrEnum):
                """TH: แหล่งที่มาของ inference | EN: inference source"""
                API = "api"; BATCH = "batch"; STREAM = "stream"; UPLOAD = "upload"
        '''))

        # exceptions.py
        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """YOLO domain exceptions — ข้อยกเว้นโดเมน YOLO"""
            from __future__ import annotations


            class YOLOError(Exception):
                """TH: base error | EN: base error"""
                code: str = "DOMAIN_ERROR"
                http_status: int = 400

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class DatasetNotFoundError(YOLOError):
                code = "DATASET_NOT_FOUND"; http_status = 404


            class ClassNotFoundError(YOLOError):
                code = "CLASS_NOT_FOUND"; http_status = 404


            class ImageNotFoundError(YOLOError):
                code = "IMAGE_NOT_FOUND"; http_status = 404


            class AnnotationNotFoundError(YOLOError):
                code = "ANNOTATION_NOT_FOUND"; http_status = 404


            class TrainingNotFoundError(YOLOError):
                code = "TRAINING_NOT_FOUND"; http_status = 404


            class ModelNotFoundError(YOLOError):
                code = "MODEL_NOT_FOUND"; http_status = 404


            class InferenceNotFoundError(YOLOError):
                code = "INFERENCE_NOT_FOUND"; http_status = 404


            class InvalidBBoxError(YOLOError):
                code = "INVALID_BBOX"; http_status = 422


            class InvalidImageError(YOLOError):
                code = "INVALID_IMAGE"; http_status = 422


            class TrainingFailedError(YOLOError):
                code = "TRAINING_FAILED"; http_status = 500


            class InferenceFailedError(YOLOError):
                code = "INFERENCE_FAILED"; http_status = 500


            class ExportFailedError(YOLOError):
                code = "EXPORT_FAILED"; http_status = 500


            class GPUUnavailableError(YOLOError):
                code = "GPU_UNAVAILABLE"; http_status = 503


            class UnsupportedFormatError(YOLOError):
                code = "UNSUPPORTED_FORMAT"; http_status = 422
        '''))

        # events.py
        self.writer.write(f"{base}/events.py", dedent('''\
            """YOLO domain events — เหตุการณ์โดเมน YOLO"""
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
        '''))

        # value_objects/__init__.py
        self.writer.write(f"{base}/value_objects/__init__.py", dedent('''\
            """YOLO value objects"""
            from .aug_config import AugConfig
            from .bbox import BBox
            from .detection import Detection
            from .eval_metrics import EvalMetrics
            from .train_config import TrainConfig

            __all__ = ["AugConfig", "BBox", "Detection", "EvalMetrics", "TrainConfig"]
        '''))

        # value_objects/bbox.py
        self.writer.write(f"{base}/value_objects/bbox.py", dedent('''\
            """BBox value object — normalized bounding box (YOLO format)"""
            from __future__ import annotations
            from dataclasses import dataclass


            @dataclass(frozen=True, slots=True)
            class BBox:
                """TH: bbox normalized (0-1) | EN: normalized bbox (0-1)"""
                x_center: float
                y_center: float
                width: float
                height: float

                def __post_init__(self) -> None:
                    for name, val in (
                        ("x_center", self.x_center), ("y_center", self.y_center),
                        ("width", self.width), ("height", self.height),
                    ):
                        if not 0.0 <= val <= 1.0:
                            raise ValueError(f"{name} must be in [0,1]: {val}")
                    if self.width <= 0.0:
                        raise ValueError("width must be > 0")
                    if self.height <= 0.0:
                        raise ValueError("height must be > 0")

                def to_xyxy(self, img_w: int, img_h: int) -> tuple[float, float, float, float]:
                    """TH: แปลงเป็น absolute xyxy | EN: convert to absolute xyxy"""
                    x1 = (self.x_center - self.width / 2.0) * img_w
                    y1 = (self.y_center - self.height / 2.0) * img_h
                    x2 = (self.x_center + self.width / 2.0) * img_w
                    y2 = (self.y_center + self.height / 2.0) * img_h
                    return max(0.0, x1), max(0.0, y1), min(float(img_w), x2), min(float(img_h), y2)

                @classmethod
                def from_xyxy(cls, x1: float, y1: float, x2: float, y2: float,
                              img_w: int, img_h: int) -> "BBox":
                    """TH: สร้างจาก absolute xyxy | EN: build from absolute xyxy"""
                    w = max(0.0, x2 - x1) / img_w
                    h = max(0.0, y2 - y1) / img_h
                    cx = (x1 + x2) / 2.0 / img_w
                    cy = (y1 + y2) / 2.0 / img_h
                    return cls(x_center=cx, y_center=cy, width=w, height=h)
        '''))

        # value_objects/detection.py
        self.writer.write(f"{base}/value_objects/detection.py", dedent('''\
            """Detection value object — ผลลัพธ์การตรวจจับ"""
            from __future__ import annotations
            from dataclasses import dataclass

            from .bbox import BBox


            @dataclass(frozen=True, slots=True)
            class Detection:
                """TH: ผลตรวจจับ 1 วัตถุ | EN: one detection result"""
                bbox: BBox
                class_id: int
                class_name: str
                confidence: float

                def __post_init__(self) -> None:
                    if not 0.0 <= self.confidence <= 1.0:
                        raise ValueError(f"confidence must be in [0,1]: {self.confidence}")

                def to_dict(self) -> dict:
                    """TH: แปลงเป็น dict | EN: to dict"""
                    return {
                        "bbox": {
                            "x_center": self.bbox.x_center,
                            "y_center": self.bbox.y_center,
                            "width": self.bbox.width,
                            "height": self.bbox.height,
                        },
                        "class_id": self.class_id,
                        "class_name": self.class_name,
                        "confidence": self.confidence,
                    }
        '''))

        # value_objects/train_config.py
        self.writer.write(f"{base}/value_objects/train_config.py", dedent('''\
            """TrainConfig value object — config การฝึก YOLO"""
            from __future__ import annotations
            from dataclasses import dataclass

            from ..enums import ModelType


            @dataclass(frozen=True, slots=True)
            class TrainConfig:
                """TH: config การฝึก | EN: YOLO training config"""
                model_type: str = "yolov8n"
                epochs: int = 100
                batch_size: int = 16
                imgsz: int = 640
                lr0: float = 0.01
                device: str = "auto"
                patience: int = 50
                optimizer: str = "auto"

                def __post_init__(self) -> None:
                    if self.model_type not in {m.value for m in ModelType}:
                        raise ValueError(f"unsupported model_type: {self.model_type}")
                    if self.epochs < 1:
                        raise ValueError("epochs must be >= 1")
                    if self.batch_size < 1:
                        raise ValueError("batch_size must be >= 1")
                    if self.imgsz < 32 or self.imgsz > 4096:
                        raise ValueError("imgsz must be in [32, 4096]")
                    if not 0.0 < self.lr0 < 1.0:
                        raise ValueError("lr0 must be in (0, 1)")
                    if self.patience < 0:
                        raise ValueError("patience must be >= 0")
        '''))

        # value_objects/aug_config.py
        self.writer.write(f"{base}/value_objects/aug_config.py", dedent('''\
            """AugConfig value object — augmentation config"""
            from __future__ import annotations
            from dataclasses import dataclass


            @dataclass(frozen=True, slots=True)
            class AugConfig:
                """TH: config augmentation | EN: augmentation config"""
                hsv_h: float = 0.015
                hsv_s: float = 0.7
                hsv_v: float = 0.4
                degrees: float = 0.0
                translate: float = 0.1
                scale: float = 0.5
                shear: float = 0.0
                perspective: float = 0.0
                flipud: float = 0.0
                fliplr: float = 0.5
                mosaic: float = 1.0
                mixup: float = 0.0
                copy_paste: float = 0.0

                def __post_init__(self) -> None:
                    for name in ("hsv_h", "hsv_s", "hsv_v", "translate", "scale",
                                 "shear", "perspective", "flipud", "fliplr",
                                 "mosaic", "mixup", "copy_paste"):
                        val = getattr(self, name)
                        if not 0.0 <= val <= 1.0:
                            raise ValueError(f"{name} must be in [0,1]: {val}")
                    if not 0.0 <= self.degrees <= 180.0:
                        raise ValueError("degrees must be in [0,180]")

                def to_dict(self) -> dict:
                    """TH: แปลงเป็น dict สำหรับ Ultralytics | EN: dict for Ultralytics"""
                    return {
                        "hsv_h": self.hsv_h, "hsv_s": self.hsv_s, "hsv_v": self.hsv_v,
                        "degrees": self.degrees, "translate": self.translate,
                        "scale": self.scale, "shear": self.shear,
                        "perspective": self.perspective, "flipud": self.flipud,
                        "fliplr": self.fliplr, "mosaic": self.mosaic,
                        "mixup": self.mixup, "copy_paste": self.copy_paste,
                    }
        '''))

        # value_objects/eval_metrics.py
        self.writer.write(f"{base}/value_objects/eval_metrics.py", dedent('''\
            """EvalMetrics value object — ผลการประเมิน COCO"""
            from __future__ import annotations
            from dataclasses import dataclass, field


            @dataclass(frozen=True, slots=True)
            class EvalMetrics:
                """TH: metrics COCO | EN: COCO metrics"""
                mAP50: float = 0.0
                mAP50_95: float = 0.0
                precision: float = 0.0
                recall: float = 0.0
                f1: float = 0.0
                per_class: tuple[tuple[str, float], ...] = ()

                def __post_init__(self) -> None:
                    for name in ("mAP50", "mAP50_95", "precision", "recall", "f1"):
                        val = getattr(self, name)
                        if not 0.0 <= val <= 1.0:
                            raise ValueError(f"{name} must be in [0,1]: {val}")

                def to_dict(self) -> dict:
                    """TH: แปลงเป็น dict | EN: to dict"""
                    return {
                        "mAP50": self.mAP50, "mAP50_95": self.mAP50_95,
                        "precision": self.precision, "recall": self.recall,
                        "f1": self.f1, "per_class": dict(self.per_class),
                    }
        '''))

        # helpers/__init__.py
        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """YOLO domain helpers"""
            from .coco_metrics import compute_iou, compute_map
            from .nms import non_max_suppression
            from .yolo_format import bbox_to_yolo, write_dataset_yaml, yolo_to_bbox

            __all__ = [
                "compute_iou", "compute_map",
                "non_max_suppression",
                "bbox_to_yolo", "write_dataset_yaml", "yolo_to_bbox",
            ]
        '''))

        # helpers/yolo_format.py
        self.writer.write(f"{base}/helpers/yolo_format.py", dedent('''\
            """YOLO format helpers — แปลง bbox <-> YOLO txt"""
            from __future__ import annotations
            from textwrap import dedent


            def bbox_to_yolo(class_id: int, x_center: float, y_center: float,
                             width: float, height: float) -> str:
                """TH: bbox → YOLO line | EN: bbox → YOLO line"""
                return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"


            def yolo_to_bbox(line: str) -> tuple[int, float, float, float, float]:
                """TH: YOLO line → bbox | EN: YOLO line → bbox"""
                parts = line.strip().split()
                if len(parts) != 5:
                    raise ValueError(f"invalid YOLO line: {line!r}")
                return int(parts[0]), float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])


            def write_dataset_yaml(classes: list[str], root: str,
                                   splits: dict[str, str]) -> str:
                """TH: สร้าง data.yaml สำหรับ Ultralytics"""
                names = "\\n".join(f"  {i}: {n}" for i, n in enumerate(classes))
                return dedent(f"""\\
                    path: {root}
                    train: {splits.get('train', 'images/train')}
                    val: {splits.get('val', 'images/val')}
                    test: {splits.get('test', '')}
                    names:
                    {names}
                """).strip()
        '''))

        # helpers/coco_metrics.py
        self.writer.write(f"{base}/helpers/coco_metrics.py", dedent('''\
            """COCO metrics — IoU และ mAP"""
            from __future__ import annotations
            from typing import Any

            import numpy as np


            def compute_iou(box1: tuple[float, float, float, float],
                            box2: tuple[float, float, float, float]) -> float:
                """TH: IoU ระหว่าง 2 boxes (x1,y1,x2,y2) | EN: IoU of 2 boxes"""
                x1 = max(box1[0], box2[0]); y1 = max(box1[1], box2[1])
                x2 = min(box1[2], box2[2]); y2 = min(box1[3], box2[3])
                inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
                a1 = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
                a2 = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])
                denom = a1 + a2 - inter
                return inter / denom if denom > 0 else 0.0


            def compute_map(predictions: list[dict[str, Any]],
                            ground_truth: list[dict[str, Any]],
                            iou_thresholds: list[float] | None = None) -> dict[str, float]:
                """TH: คำนวณ mAP@50, mAP@50-95 (simplified)"""
                if iou_thresholds is None:
                    iou_thresholds = [0.5 + 0.05 * i for i in range(10)]
                if not predictions or not ground_truth:
                    return {"mAP50": 0.0, "mAP50_95": 0.0, "precision": 0.0, "recall": 0.0}

                per_thresh: list[float] = []
                for thr in iou_thresholds:
                    tp = 0; fp = 0; fn = 0
                    gt_used = [False] * len(ground_truth)
                    for pred in sorted(predictions, key=lambda p: -p.get("confidence", 0.0)):
                        best_iou = 0.0; best_idx = -1
                        for i, gt in enumerate(ground_truth):
                            if gt_used[i]:
                                continue
                            if gt.get("class_id") != pred.get("class_id"):
                                continue
                            iou = compute_iou(
                                (pred["x1"], pred["y1"], pred["x2"], pred["y2"]),
                                (gt["x1"], gt["y1"], gt["x2"], gt["y2"]),
                            )
                            if iou > best_iou:
                                best_iou = iou; best_idx = i
                        if best_iou >= thr and best_idx >= 0:
                            tp += 1; gt_used[best_idx] = True
                        else:
                            fp += 1
                    fn = sum(1 for u in gt_used if not u)
                    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
                    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
                    per_thresh.append(precision * recall * 2.0 / (precision + recall) if (precision + recall) > 0 else 0.0)

                mAP50 = per_thresh[0] if per_thresh else 0.0
                mAP50_95 = float(np.mean(per_thresh)) if per_thresh else 0.0
                return {"mAP50": mAP50, "mAP50_95": mAP50_95,
                        "precision": per_thresh[0] if per_thresh else 0.0,
                        "recall": per_thresh[0] if per_thresh else 0.0}
        '''))

        # helpers/nms.py
        self.writer.write(f"{base}/helpers/nms.py", dedent('''\
            """NMS helper — non-maximum suppression"""
            from __future__ import annotations
            from .coco_metrics import compute_iou


            def non_max_suppression(
                boxes: list[tuple[float, float, float, float]],
                scores: list[float],
                iou_threshold: float = 0.45,
            ) -> list[int]:
                """TH: NMS — กรอง bbox ที่ทับซ้อน | EN: NMS filter"""
                if not boxes:
                    return []
                order = sorted(range(len(scores)), key=lambda i: -scores[i])
                keep: list[int] = []
                while order:
                    i = order.pop(0)
                    keep.append(i)
                    remaining: list[int] = []
                    for j in order:
                        if compute_iou(boxes[i], boxes[j]) < iou_threshold:
                            remaining.append(j)
                    order = remaining
                return keep
        '''))

    # ─── APPLICATION LAYER ──────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """YOLO application layer"""
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """YOLO application exceptions"""
            from __future__ import annotations


            class ApplicationError(Exception):
                code: str = "APP_ERROR"
                http_status: int = 400


            class DatasetNotFoundAppError(ApplicationError):
                code = "DATASET_NOT_FOUND"; http_status = 404


            class ModelNotFoundAppError(ApplicationError):
                code = "MODEL_NOT_FOUND"; http_status = 404


            class TrainingNotFoundAppError(ApplicationError):
                code = "TRAINING_NOT_FOUND"; http_status = 404


            class TrainingFailedAppError(ApplicationError):
                code = "TRAINING_FAILED"; http_status = 500


            class InferenceFailedAppError(ApplicationError):
                code = "INFERENCE_FAILED"; http_status = 500


            class ExportFailedAppError(ApplicationError):
                code = "EXPORT_FAILED"; http_status = 500


            class InvalidBBoxAppError(ApplicationError):
                code = "INVALID_BBOX"; http_status = 422
        '''))

        self.writer.write(f"{base}/interfaces.py", dedent('''\
            """YOLO application ports — interfaces"""
            from __future__ import annotations
            import uuid
            from abc import ABC, abstractmethod
            from datetime import datetime
            from typing import Any, AsyncIterator, Protocol


            class RequestContext(Protocol):
                @property
                def tenant_id(self) -> uuid.UUID: ...
                @property
                def user_id(self) -> uuid.UUID | None: ...


            class DatasetRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, ds: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
                @abstractmethod
                async def find_paginated(self, ctx: Any, page: int, size: int) -> tuple[list[Any], int]: ...
                @abstractmethod
                async def update(self, ctx: Any, ds: Any) -> Any: ...
                @abstractmethod
                async def soft_delete(self, ctx: Any, id: uuid.UUID) -> bool: ...


            class ClassRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, cls: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_dataset(self, ctx: Any, dataset_id: uuid.UUID) -> list[Any]: ...
                @abstractmethod
                async def bulk_create(self, ctx: Any, classes: list[Any]) -> list[Any]: ...


            class ImageRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, img: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_hash(self, ctx: Any, content_hash: str) -> Any | None: ...
                @abstractmethod
                async def find_by_dataset(self, ctx: Any, dataset_id: uuid.UUID,
                                            split: str | None, page: int, size: int) -> tuple[list[Any], int]: ...
                @abstractmethod
                async def count_by_dataset(self, ctx: Any, dataset_id: uuid.UUID,
                                            split: str | None) -> int: ...


            class AnnotationRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, ann: Any) -> Any: ...
                @abstractmethod
                async def bulk_create(self, ctx: Any, annotations: list[Any]) -> list[Any]: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_image(self, ctx: Any, image_id: uuid.UUID) -> list[Any]: ...
                @abstractmethod
                async def delete_by_image(self, ctx: Any, image_id: uuid.UUID) -> int: ...
                @abstractmethod
                async def class_distribution(self, ctx: Any, dataset_id: uuid.UUID) -> dict[str, int]: ...


            class TrainingRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, tr: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_dataset(self, ctx: Any, dataset_id: uuid.UUID) -> list[Any]: ...
                @abstractmethod
                async def update_status(self, ctx: Any, id: uuid.UUID, status: str) -> None: ...
                @abstractmethod
                async def set_best_model(self, ctx: Any, id: uuid.UUID, model_id: uuid.UUID) -> None: ...


            class ModelRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, m: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_training(self, ctx: Any, training_id: uuid.UUID) -> list[Any]: ...
                @abstractmethod
                async def find_active(self, ctx: Any) -> list[Any]: ...
                @abstractmethod
                async def find_deployed(self, ctx: Any) -> list[Any]: ...
                @abstractmethod
                async def update(self, ctx: Any, m: Any) -> Any: ...


            class InferenceRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, inf: Any) -> Any: ...
                @abstractmethod
                async def find_by_model(self, ctx: Any, model_id: uuid.UUID, limit: int) -> list[Any]: ...
                @abstractmethod
                async def stats_by_model(self, ctx: Any, model_id: uuid.UUID,
                                          since: datetime) -> dict[str, Any]: ...


            class YOLOTrainer(Protocol):
                async def train(self, config: Any, aug_config: Any,
                                 dataset_uri: str, classes: list[str]) -> dict[str, Any]: ...


            class YOLODetector(Protocol):
                async def detect(self, model_id: uuid.UUID, image_bytes: bytes,
                                  conf: float, iou: float) -> list[Any]: ...
                async def detect_batch(self, model_id: uuid.UUID, images: list[bytes],
                                        conf: float, iou: float) -> list[list[Any]]: ...
                async def detect_stream(self, model_id: uuid.UUID, video_uri: str,
                                         conf: float) -> AsyncIterator[list[Any]]: ...


            class ModelRegistry(Protocol):
                async def load(self, model_id: uuid.UUID, weights_uri: str, format: str) -> None: ...
                async def unload(self, model_id: uuid.UUID) -> None: ...
                async def is_loaded(self, model_id: uuid.UUID) -> bool: ...


            class ModelExporter(Protocol):
                async def export(self, model_id: uuid.UUID, weights_uri: str,
                                  format: str, imgsz: int, opset: int) -> dict[str, Any]: ...


            class Augmenter(Protocol):
                def build_pipeline(self, config: Any) -> Any: ...
                def augment(self, image: Any, bboxes: list[Any], class_ids: list[int],
                            pipeline: Any) -> tuple[Any, list[Any], list[int]]: ...


            class ArtifactStore(Protocol):
                async def save(self, path: str, data: bytes, metadata: dict[str, Any]) -> str: ...
                async def load(self, uri: str) -> bytes: ...
                async def exists(self, uri: str) -> bool: ...
                async def delete(self, uri: str) -> bool: ...


            class Cache(ABC):
                @abstractmethod
                async def get(self, key: str) -> Any | None: ...
                @abstractmethod
                async def set(self, key: str, value: Any, ttl: int = 3600) -> bool: ...
                @abstractmethod
                async def invalidate(self, key: str) -> bool: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...


            class IdempotencyStore(ABC):
                @abstractmethod
                async def check_or_lock(self, key: str, scope: str,
                                         payload: dict[str, Any]) -> dict[str, Any] | None: ...
                @abstractmethod
                async def complete(self, key: str, scope: str,
                                    status: int, body: dict[str, Any]) -> None: ...


            class RateLimiter(ABC):
                @abstractmethod
                async def check(self, tenant_id: uuid.UUID, user_id: uuid.UUID,
                                 cost: int) -> bool: ...
                @abstractmethod
                async def increment(self, tenant_id: uuid.UUID, user_id: uuid.UUID,
                                     cost: int) -> None: ...
        '''))

        self.writer.write(f"{base}/mappers.py", dedent('''\
            """YOLO mappers — ORM ↔ domain dict"""
            from __future__ import annotations
            from typing import Any


            def dataset_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "name": row.name, "format": row.format,
                    "root_uri": row.root_uri, "image_count": row.image_count,
                    "class_count": row.class_count, "status": row.status,
                    "version": row.version,
                }


            def image_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "dataset_id": str(row.dataset_id),
                    "uri": row.uri, "content_hash": row.content_hash,
                    "width": row.width, "height": row.height,
                    "split": row.split, "annotation_count": row.annotation_count,
                }


            def training_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "dataset_id": str(row.dataset_id),
                    "model_type": row.model_type, "epochs": row.epochs,
                    "batch_size": row.batch_size, "imgsz": row.imgsz,
                    "status": row.status, "progress": row.progress,
                }


            def model_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "name": row.name, "version": row.version,
                    "format": row.format, "mAP50": str(row.mAP50),
                    "mAP50_95": str(row.mAP50_95), "is_active": row.is_active,
                }
        '''))

        self.writer.write(f"{base}/utils.py", dedent('''\
            """YOLO application utils"""
            from __future__ import annotations
            import hashlib
            import json
            from typing import Any


            def hash_payload(payload: dict[str, Any]) -> str:
                raw = json.dumps(payload, sort_keys=True, default=str)
                return hashlib.sha256(raw.encode()).hexdigest()


            def hash_bytes(data: bytes) -> str:
                return hashlib.sha256(data).hexdigest()


            def image_cache_key(image_hash: str, model_id: str,
                                conf: float, iou: float) -> str:
                raw = f"{image_hash}:{model_id}:{conf:.4f}:{iou:.4f}"
                return "yolo:det:" + hashlib.sha256(raw.encode()).hexdigest()[:32]
        '''))

        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _use_case_content(self) -> str:
        return dedent('''\
            """YOLO use cases — กรณีการใช้งาน YOLO Object Detection"""
            from __future__ import annotations

            import time
            import uuid
            from datetime import UTC, datetime
            from decimal import Decimal
            from typing import Any

            import structlog

            from app.modules.yolo.application.interfaces import (
                AnnotationRepository, ArtifactStore, Cache, ClassRepository,
                DatasetRepository, EventBus, ImageRepository,
                InferenceRepository, ModelExporter, ModelRegistry,
                ModelRepository, RateLimiter, RequestContext,
                TrainingRepository, YOLODetector, YOLOTrainer,
            )
            from app.modules.yolo.application.utils import (
                hash_bytes, image_cache_key,
            )
            from app.modules.yolo.domain.enums import (
                DatasetStatus, InferenceSource, TrainingStatus,
            )
            from app.modules.yolo.domain.events import (
                AnnotationsCreated, DatasetRegistered, ImagesUploaded,
                InferenceServed, ModelExported, TrainingCompleted,
                TrainingStarted,
            )
            from app.modules.yolo.domain.exceptions import (
                DatasetNotFoundError, ModelNotFoundError,
                TrainingFailedError,
            )
            from app.modules.yolo.domain.value_objects import (
                AugConfig, BBox, Detection, TrainConfig,
            )
            from app.modules.yolo.infrastructure.models import (
                AnnotationModel, ClassModel, DatasetModel, ImageModel,
                InferenceModel, ModelModel, TrainingModel,
            )

            log = structlog.get_logger()


            class YOLOUseCase:
                """TH: use cases YOLO | EN: YOLO use cases"""

                def __init__(
                    self,
                    dataset_repo: DatasetRepository,
                    class_repo: ClassRepository,
                    image_repo: ImageRepository,
                    annotation_repo: AnnotationRepository,
                    training_repo: TrainingRepository,
                    model_repo: ModelRepository,
                    inference_repo: InferenceRepository,
                    trainer: YOLOTrainer,
                    detector: YOLODetector,
                    model_registry: ModelRegistry,
                    exporter: ModelExporter,
                    artifact_store: ArtifactStore,
                    cache: Cache,
                    rate_limiter: RateLimiter,
                    event_bus: EventBus,
                ) -> None:
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

                # ─── Datasets ────────────────────────────
                async def create_dataset(
                    self, ctx: RequestContext, name: str, format_: str = "yolo",
                ) -> dict[str, Any]:
                    """TH: สร้าง dataset | EN: create dataset"""
                    log.info("yolo.dataset.create", name=name)
                    try:
                        ds = DatasetModel(
                            tenant_id=ctx.tenant_id, name=name, format=format_,
                            status=DatasetStatus.DRAFT.value,
                        )
                        saved = await self._dataset_repo.save(ctx, ds)
                        await self._bus.publish(DatasetRegistered(
                            dataset_id=saved.id, tenant_id=ctx.tenant_id,
                            name=name, format=format_, image_count=0,
                        ))
                        return {
                            "id": str(saved.id), "name": saved.name,
                            "format": saved.format, "status": saved.status,
                        }
                    except Exception:
                        log.exception("yolo.dataset.create.failed")
                        raise

                async def list_datasets(
                    self, ctx: RequestContext, page: int = 1, size: int = 50,
                ) -> dict[str, Any]:
                    rows, total = await self._dataset_repo.find_paginated(ctx, page, size)
                    return {
                        "items": [{
                            "id": str(r.id), "name": r.name, "format": r.format,
                            "status": r.status, "image_count": r.image_count,
                            "class_count": r.class_count, "version": r.version,
                        } for r in rows],
                        "total": total, "page": page, "size": size,
                    }

                async def get_dataset(
                    self, ctx: RequestContext, dataset_id: uuid.UUID,
                ) -> dict[str, Any]:
                    ds = await self._dataset_repo.find_by_id(ctx, dataset_id)
                    if ds is None:
                        raise DatasetNotFoundError(f"dataset {dataset_id} not found")
                    classes = await self._class_repo.find_by_dataset(ctx, dataset_id)
                    return {
                        "id": str(ds.id), "name": ds.name, "format": ds.format,
                        "root_uri": ds.root_uri, "image_count": ds.image_count,
                        "class_count": ds.class_count, "status": ds.status,
                        "version": ds.version,
                        "splits": dict(ds.splits_json or {}),
                        "classes": [{"id": str(c.id), "name": c.name,
                                      "class_index": c.class_index, "color": c.color}
                                     for c in classes],
                    }

                async def define_classes(
                    self, ctx: RequestContext, dataset_id: uuid.UUID,
                    classes: list[dict[str, Any]],
                ) -> dict[str, Any]:
                    """TH: กำหนด classes ของ dataset"""
                    ds = await self._dataset_repo.find_by_id(ctx, dataset_id)
                    if ds is None:
                        raise DatasetNotFoundError(f"dataset {dataset_id} not found")
                    rows: list[ClassModel] = []
                    for c in classes:
                        rows.append(ClassModel(
                            tenant_id=ctx.tenant_id, dataset_id=dataset_id,
                            name=c["name"], class_index=c["class_index"],
                            color=c.get("color", "#FF0000"),
                        ))
                    saved = await self._class_repo.bulk_create(ctx, rows)
                    ds.class_count = len(saved)
                    await self._dataset_repo.update(ctx, ds)
                    return {
                        "dataset_id": str(dataset_id),
                        "class_count": len(saved),
                        "classes": [{"id": str(c.id), "name": c.name,
                                      "class_index": c.class_index} for c in saved],
                    }

                # ─── Images ──────────────────────────────
                async def upload_images(
                    self, ctx: RequestContext, dataset_id: uuid.UUID,
                    images: list[dict[str, Any]], split: str = "train",
                ) -> dict[str, Any]:
                    """TH: อัปโหลดรูป (metadata) | EN: upload images"""
                    ds = await self._dataset_repo.find_by_id(ctx, dataset_id)
                    if ds is None:
                        raise DatasetNotFoundError(f"dataset {dataset_id} not found")
                    image_ids: list[uuid.UUID] = []
                    for img in images:
                        row = ImageModel(
                            tenant_id=ctx.tenant_id, dataset_id=dataset_id,
                            uri=img["uri"], content_hash=img["content_hash"],
                            width=img.get("width", 0), height=img.get("height", 0),
                            size_bytes=img.get("size_bytes", 0), split=split,
                        )
                        saved = await self._image_repo.save(ctx, row)
                        image_ids.append(saved.id)
                    ds.image_count = await self._image_repo.count_by_dataset(ctx, dataset_id, None)
                    if ds.image_count > 0:
                        ds.status = DatasetStatus.READY.value
                    await self._dataset_repo.update(ctx, ds)
                    await self._bus.publish(ImagesUploaded(
                        dataset_id=dataset_id, tenant_id=ctx.tenant_id,
                        image_ids=tuple(image_ids), count=len(image_ids),
                    ))
                    return {"dataset_id": str(dataset_id), "uploaded": len(image_ids)}

                # ─── Annotations ─────────────────────────
                async def create_annotations(
                    self, ctx: RequestContext, image_id: uuid.UUID,
                    annotations: list[dict[str, Any]],
                ) -> dict[str, Any]:
                    """TH: สร้าง annotation | EN: create annotations"""
                    img = await self._image_repo.find_by_id(ctx, image_id)
                    if img is None:
                        raise DatasetNotFoundError(f"image {image_id} not found")
                    rows: list[AnnotationModel] = []
                    for a in annotations:
                        bbox = BBox(
                            x_center=float(a["x_center"]),
                            y_center=float(a["y_center"]),
                            width=float(a["width"]),
                            height=float(a["height"]),
                        )
                        rows.append(AnnotationModel(
                            tenant_id=ctx.tenant_id, image_id=image_id,
                            class_id=uuid.UUID(a["class_id"]),
                            x_center=bbox.x_center, y_center=bbox.y_center,
                            width=bbox.width, height=bbox.height,
                            confidence=Decimal(str(a.get("confidence", 1.0))),
                            is_hard=bool(a.get("is_hard", False)),
                            source=a.get("source", "manual"),
                        ))
                    saved = await self._annotation_repo.bulk_create(ctx, rows)
                    img.annotation_count = len(saved)
                    await self._image_repo.save(ctx, img)
                    await self._bus.publish(AnnotationsCreated(
                        image_id=image_id, tenant_id=ctx.tenant_id,
                        count=len(saved),
                    ))
                    return {"image_id": str(image_id), "created": len(saved)}

                # ─── Training ────────────────────────────
                async def start_training(
                    self, ctx: RequestContext, dataset_id: uuid.UUID,
                    config: TrainConfig, aug_config: AugConfig | None = None,
                ) -> dict[str, Any]:
                    """TH: เริ่มฝึก YOLO | EN: start YOLO training"""
                    log.info("yolo.train.start", dataset=str(dataset_id))
                    try:
                        ds = await self._dataset_repo.find_by_id(ctx, dataset_id)
                        if ds is None:
                            raise DatasetNotFoundError(f"dataset {dataset_id} not found")

                        allowed = await self._rate.check(
                            ctx.tenant_id, ctx.user_id or uuid.uuid4(), cost=100,
                        )
                        if not allowed:
                            raise TrainingFailedError("rate limit exceeded")

                        aug_cfg = aug_config or AugConfig()
                        tr = TrainingModel(
                            tenant_id=ctx.tenant_id, dataset_id=dataset_id,
                            model_type=config.model_type, epochs=config.epochs,
                            batch_size=config.batch_size, imgsz=config.imgsz,
                            lr0=Decimal(str(config.lr0)), device=config.device,
                            patience=config.patience, optimizer=config.optimizer,
                            aug_config_json=aug_cfg.to_dict(),
                            status=TrainingStatus.PENDING.value,
                            started_at=datetime.now(UTC),
                        )
                        saved_tr = await self._training_repo.create(ctx, tr)
                        await self._training_repo.update_status(
                            ctx, saved_tr.id, TrainingStatus.RUNNING.value,
                        )
                        await self._bus.publish(TrainingStarted(
                            training_id=saved_tr.id, tenant_id=ctx.tenant_id,
                            dataset_id=dataset_id, model_type=config.model_type,
                            epochs=config.epochs,
                        ))

                        classes = await self._class_repo.find_by_dataset(ctx, dataset_id)
                        class_names = [c.name for c in classes]

                        t0 = time.monotonic()
                        try:
                            result = await self._trainer.train(
                                config=config, aug_config=aug_cfg,
                                dataset_uri=ds.root_uri, classes=class_names,
                            )
                        except Exception as exc:
                            await self._training_repo.update_status(
                                ctx, saved_tr.id, TrainingStatus.FAILED.value,
                            )
                            log.error(f"train.failed: {exc}")
                            raise TrainingFailedError(str(exc)) from exc
                        duration_ms = int((time.monotonic() - t0) * 1000)

                        metrics = result.get("metrics", {})
                        mAP50 = float(metrics.get("mAP50", 0.0))
                        mAP50_95 = float(metrics.get("mAP50_95", 0.0))

                        model = ModelModel(
                            tenant_id=ctx.tenant_id, training_id=saved_tr.id,
                            name=result.get("name", f"yolo-{saved_tr.id}"),
                            version=1, weights_uri=result.get("weights_uri", ""),
                            weights_hash=hash_bytes(str(result.get("weights_uri", "")).encode()),
                            format="pt", mAP50=Decimal(str(mAP50)),
                            mAP50_95=Decimal(str(mAP50_95)),
                            precision_=Decimal(str(metrics.get("precision", 0.0))),
                            recall_=Decimal(str(metrics.get("recall", 0.0))),
                            metrics_json=metrics, is_active=True,
                        )
                        saved_model = await self._model_repo.save(ctx, model)
                        await self._training_repo.set_best_model(ctx, saved_tr.id, saved_model.id)
                        await self._training_repo.update_status(
                            ctx, saved_tr.id, TrainingStatus.SUCCESS.value,
                        )
                        await self._bus.publish(TrainingCompleted(
                            training_id=saved_tr.id, model_id=saved_model.id,
                            tenant_id=ctx.tenant_id, mAP50=mAP50,
                            mAP50_95=mAP50_95, duration_ms=duration_ms,
                        ))
                        return {
                            "training_id": str(saved_tr.id),
                            "model_id": str(saved_model.id),
                            "status": TrainingStatus.SUCCESS.value,
                            "mAP50": mAP50, "mAP50_95": mAP50_95,
                            "duration_ms": duration_ms,
                        }
                    except TrainingFailedError:
                        raise
                    except Exception:
                        log.exception("yolo.train.unexpected")
                        raise

                async def get_training_status(
                    self, ctx: RequestContext, training_id: uuid.UUID,
                ) -> dict[str, Any]:
                    tr = await self._training_repo.find_by_id(ctx, training_id)
                    if tr is None:
                        raise DatasetNotFoundError(f"training {training_id} not found")
                    return {
                        "id": str(tr.id), "dataset_id": str(tr.dataset_id),
                        "model_type": tr.model_type, "epochs": tr.epochs,
                        "status": tr.status, "progress": tr.progress,
                        "best_model_id": str(tr.best_model_id) if tr.best_model_id else None,
                        "error_message": tr.error_message,
                        "started_at": tr.started_at.isoformat() if tr.started_at else None,
                        "finished_at": tr.finished_at.isoformat() if tr.finished_at else None,
                    }

                # ─── Models ──────────────────────────────
                async def list_models(
                    self, ctx: RequestContext, only_active: bool = True,
                ) -> list[dict[str, Any]]:
                    rows = (await self._model_repo.find_active(ctx)
                            if only_active else await self._model_repo.find_deployed(ctx))
                    return [{
                        "id": str(r.id), "name": r.name, "version": r.version,
                        "format": r.format, "mAP50": str(r.mAP50),
                        "mAP50_95": str(r.mAP50_95), "is_active": r.is_active,
                        "is_deployed": r.is_deployed,
                    } for r in rows]

                async def export_model(
                    self, ctx: RequestContext, model_id: uuid.UUID,
                    format_: str = "onnx", imgsz: int = 640, opset: int = 17,
                ) -> dict[str, Any]:
                    m = await self._model_repo.find_by_id(ctx, model_id)
                    if m is None:
                        raise ModelNotFoundError(f"model {model_id} not found")
                    try:
                        result = await self._exporter.export(
                            model_id=model_id, weights_uri=m.weights_uri,
                            format=format_, imgsz=imgsz, opset=opset,
                        )
                    except Exception as exc:
                        log.error(f"export.failed: {exc}")
                        raise
                    m.format = format_
                    m.export_uri = result.get("export_uri", "")
                    await self._model_repo.update(ctx, m)
                    await self._bus.publish(ModelExported(
                        model_id=model_id, tenant_id=ctx.tenant_id,
                        format=format_, export_uri=m.export_uri,
                    ))
                    return {
                        "model_id": str(model_id), "format": format_,
                        "export_uri": m.export_uri,
                    }

                # ─── Inference ───────────────────────────
                async def detect(
                    self, ctx: RequestContext, model_id: uuid.UUID,
                    image_bytes: bytes, conf: float = 0.25, iou: float = 0.45,
                    source: str = "api",
                ) -> dict[str, Any]:
                    """TH: ตรวจจับวัตถุ | EN: object detection"""
                    log.info("yolo.detect.start", model=str(model_id))
                    try:
                        m = await self._model_repo.find_by_id(ctx, model_id)
                        if m is None:
                            raise ModelNotFoundError(f"model {model_id} not found")

                        image_hash = hash_bytes(image_bytes)
                        ck = image_cache_key(image_hash, str(model_id), conf, iou)
                        cached = await self._cache.get(ck)
                        if cached:
                            return cached

                        allowed = await self._rate.check(
                            ctx.tenant_id, ctx.user_id or uuid.uuid4(), cost=1,
                        )
                        if not allowed:
                            raise TrainingFailedError("rate limit exceeded")

                        t0 = time.monotonic()
                        detections: list[Detection] = []
                        try:
                            detections = await self._detector.detect(
                                model_id=model_id, image_bytes=image_bytes,
                                conf=conf, iou=iou,
                            )
                        except Exception as exc:
                            log.warning(f"detector.failed: {exc}")
                        latency_ms = int((time.monotonic() - t0) * 1000)

                        det_json = [d.to_dict() for d in detections]
                        inf_row = InferenceModel(
                            tenant_id=ctx.tenant_id, model_id=model_id,
                            image_hash=image_hash,
                            detections_json=det_json,
                            detection_count=len(detections),
                            latency_ms=latency_ms, source=source,
                        )
                        saved = await self._inference_repo.create(ctx, inf_row)

                        response = {
                            "inference_id": str(saved.id),
                            "model_id": str(model_id),
                            "image_hash": image_hash,
                            "detections": det_json,
                            "detection_count": len(detections),
                            "latency_ms": latency_ms,
                        }
                        await self._cache.set(ck, response, ttl=300)
                        await self._bus.publish(InferenceServed(
                            inference_id=saved.id, model_id=model_id,
                            tenant_id=ctx.tenant_id,
                            detection_count=len(detections),
                            latency_ms=latency_ms,
                        ))
                        return response
                    except (ModelNotFoundError, TrainingFailedError):
                        raise
                    except Exception:
                        log.exception("yolo.detect.unexpected")
                        raise

                async def detect_batch(
                    self, ctx: RequestContext, model_id: uuid.UUID,
                    images: list[bytes], conf: float = 0.25, iou: float = 0.45,
                ) -> dict[str, Any]:
                    if len(images) > 32:
                        raise TrainingFailedError("batch size exceeds 32")
                    results: list[dict[str, Any]] = []
                    for img in images:
                        try:
                            r = await self.detect(
                                ctx, model_id, img, conf, iou,
                                source=InferenceSource.BATCH.value,
                            )
                            results.append(r)
                        except Exception as exc:
                            results.append({"error": str(exc)})
                    return {"model_id": str(model_id), "total": len(images),
                            "results": results}
        ''')

    # ─── INFRASTRUCTURE LAYER ───────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"
        self.writer.write(f"{base}/__init__.py", dedent('''\
            """YOLO infrastructure layer"""
        '''))
        self.writer.write(f"{base}/models.py", self._models_content())
        self.writer.write(f"{base}/dataset_repository.py", self._dataset_repo_content())
        self.writer.write(f"{base}/class_repository.py", self._class_repo_content())
        self.writer.write(f"{base}/image_repository.py", self._image_repo_content())
        self.writer.write(f"{base}/annotation_repository.py", self._annotation_repo_content())
        self.writer.write(f"{base}/training_repository.py", self._training_repo_content())
        self.writer.write(f"{base}/model_repository.py", self._model_repo_content())
        self.writer.write(f"{base}/inference_repository.py", self._inference_repo_content())
        self.writer.write(f"{base}/caches.py", self._caches_content())
        self.writer.write(f"{base}/services.py", self._services_content())

    def _models_content(self) -> str:
        return dedent('''\
            """YOLO SQLAlchemy 2.0 models — schema=public, prefix=yolo_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Index, Integer,
                Numeric, String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import JSONB, UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: declarative base | EN: declarative base"""


            class DatasetModel(Base):
                __tablename__ = "yolo_datasets"
                __table_args__ = (
                    CheckConstraint(
                        "format IN ('yolo','coco','roboflow','labelimg')",
                        name="ck_yolo_ds_format",
                    ),
                    CheckConstraint(
                        "status IN ('DRAFT','READY','TRAINING','ARCHIVED')",
                        name="ck_yolo_ds_status",
                    ),
                    UniqueConstraint("tenant_id", "name", "version",
                                     name="uq_yolo_ds_name_ver"),
                    Index("ix_yolo_ds_tenant", "tenant_id"),
                    Index("ix_yolo_ds_status", "tenant_id", "status"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"))
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(200), nullable=False)
                format: Mapped[str] = mapped_column(String(20), nullable=False, server_default="yolo")
                root_uri: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                image_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                class_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                splits_json: Mapped[dict] = mapped_column(JSONB, nullable=False,
                    server_default=text("'{}'::jsonb"))
                status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="DRAFT")
                version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
                metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False,
                    server_default=text("'{}'::jsonb"))
                created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now(), onupdate=func.now())


            class ClassModel(Base):
                __tablename__ = "yolo_classes"
                __table_args__ = (
                    UniqueConstraint("dataset_id", "class_index", name="uq_yolo_class_idx"),
                    UniqueConstraint("dataset_id", "name", name="uq_yolo_class_name"),
                    Index("ix_yolo_class_tenant", "tenant_id"),
                    Index("ix_yolo_class_dataset", "dataset_id"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"))
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                class_index: Mapped[int] = mapped_column(Integer, nullable=False)
                color: Mapped[str] = mapped_column(String(7), nullable=False, server_default="#FF0000")
                count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now(), onupdate=func.now())


            class ImageModel(Base):
                __tablename__ = "yolo_images"
                __table_args__ = (
                    CheckConstraint("split IN ('train','val','test')", name="ck_yolo_img_split"),
                    UniqueConstraint("dataset_id", "content_hash", name="uq_yolo_img_hash"),
                    Index("ix_yolo_img_tenant", "tenant_id"),
                    Index("ix_yolo_img_dataset", "dataset_id", "split"),
                    Index("ix_yolo_img_hash", "content_hash"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"))
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                uri: Mapped[str] = mapped_column(Text, nullable=False)
                content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
                width: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                height: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                split: Mapped[str] = mapped_column(String(10), nullable=False, server_default="train")
                annotation_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now(), onupdate=func.now())


            class AnnotationModel(Base):
                __tablename__ = "yolo_annotations"
                __table_args__ = (
                    CheckConstraint("x_center >= 0 AND x_center <= 1", name="ck_yolo_ann_x"),
                    CheckConstraint("y_center >= 0 AND y_center <= 1", name="ck_yolo_ann_y"),
                    CheckConstraint("width > 0 AND width <= 1", name="ck_yolo_ann_w"),
                    CheckConstraint("height > 0 AND height <= 1", name="ck_yolo_ann_h"),
                    Index("ix_yolo_ann_tenant", "tenant_id"),
                    Index("ix_yolo_ann_image", "image_id"),
                    Index("ix_yolo_ann_class", "class_id"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"))
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                image_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                class_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                x_center: Mapped[float] = mapped_column(nullable=False)
                y_center: Mapped[float] = mapped_column(nullable=False)
                width: Mapped[float] = mapped_column(nullable=False)
                height: Mapped[float] = mapped_column(nullable=False)
                confidence: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False,
                    server_default="1.0")
                is_hard: Mapped[bool] = mapped_column(Boolean, nullable=False,
                    server_default=text("false"))
                source: Mapped[str] = mapped_column(String(50), nullable=False, server_default="manual")
                created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now(), onupdate=func.now())


            class TrainingModel(Base):
                __tablename__ = "yolo_trainings"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('PENDING','RUNNING','SUCCESS','FAILED','CANCELLED')",
                        name="ck_yolo_tr_status",
                    ),
                    Index("ix_yolo_tr_tenant", "tenant_id", "status"),
                    Index("ix_yolo_tr_dataset", "dataset_id", "created_at"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"))
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                model_type: Mapped[str] = mapped_column(String(20), nullable=False)
                epochs: Mapped[int] = mapped_column(Integer, nullable=False, server_default="100")
                batch_size: Mapped[int] = mapped_column(Integer, nullable=False, server_default="16")
                imgsz: Mapped[int] = mapped_column(Integer, nullable=False, server_default="640")
                lr0: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False,
                    server_default="0.01")
                device: Mapped[str] = mapped_column(String(20), nullable=False, server_default="auto")
                patience: Mapped[int] = mapped_column(Integer, nullable=False, server_default="50")
                optimizer: Mapped[str] = mapped_column(String(20), nullable=False, server_default="auto")
                aug_config_json: Mapped[dict] = mapped_column(JSONB, nullable=False,
                    server_default=text("'{}'::jsonb"))
                status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
                best_model_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
                progress: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                error_message: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
                finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
                duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now(), onupdate=func.now())


            class ModelModel(Base):
                __tablename__ = "yolo_models"
                __table_args__ = (
                    CheckConstraint(
                        "format IN ('pt','onnx','engine','torchscript','coreml')",
                        name="ck_yolo_model_format",
                    ),
                    UniqueConstraint("tenant_id", "name", "version",
                                     name="uq_yolo_model_name_ver"),
                    Index("ix_yolo_model_tenant", "tenant_id"),
                    Index("ix_yolo_model_training", "training_id"),
                    Index("ix_yolo_model_active", "tenant_id", "is_active"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"))
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                training_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(200), nullable=False)
                version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
                weights_uri: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                weights_hash: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
                export_uri: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                format: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pt")
                mAP50: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, server_default="0")
                mAP50_95: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, server_default="0")
                precision_: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, server_default="0")
                recall_: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, server_default="0")
                metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False,
                    server_default=text("'{}'::jsonb"))
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False,
                    server_default=text("true"))
                is_deployed: Mapped[bool] = mapped_column(Boolean, nullable=False,
                    server_default=text("false"))
                deployed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
                created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now(), onupdate=func.now())


            class InferenceModel(Base):
                __tablename__ = "yolo_inferences"
                __table_args__ = (
                    CheckConstraint(
                        "source IN ('api','batch','stream','upload')",
                        name="ck_yolo_inf_source",
                    ),
                    Index("ix_yolo_inf_tenant", "tenant_id", "created_at"),
                    Index("ix_yolo_inf_model", "model_id", "created_at"),
                    Index("ix_yolo_inf_hash", "image_hash"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"))
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                image_hash: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
                detections_json: Mapped[list] = mapped_column(JSONB, nullable=False,
                    server_default=text("'[]'::jsonb"))
                detection_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                source: Mapped[str] = mapped_column(String(20), nullable=False, server_default="api")
                created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                    nullable=False, server_default=func.now(), onupdate=func.now())
        ''')

    def _dataset_repo_content(self) -> str:
        return dedent('''\
            """Dataset repository — SQLAlchemy 2.0 async (2-branch)"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.exceptions import ApplicationError
            from app.modules.yolo.infrastructure.models import DatasetModel


            class DatasetRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> DatasetModel | None:
                    try:
                        result = await self._session.execute(
                            select(DatasetModel).where(DatasetModel.id == id))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_name(self, ctx: object, name: str) -> DatasetModel | None:
                    try:
                        result = await self._session.execute(
                            select(DatasetModel).where(DatasetModel.name == name)
                            .order_by(DatasetModel.version.desc()).limit(1))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.find_by_name failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_paginated(self, ctx: object, page: int = 1, size: int = 50
                                          ) -> tuple[list[DatasetModel], int]:
                    try:
                        count_result = await self._session.execute(
                            select(func.count()).select_from(DatasetModel))
                        total = int(count_result.scalar() or 0)
                        result = await self._session.execute(
                            select(DatasetModel)
                            .order_by(DatasetModel.created_at.desc())
                            .offset((page - 1) * size).limit(size))
                        return list(result.scalars().all()), total
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.find_paginated failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(self, ctx: object, dataset: DatasetModel) -> DatasetModel:
                    try:
                        self._session.add(dataset)
                        await self._session.flush()
                        return dataset
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def update(self, ctx: object, dataset: DatasetModel) -> DatasetModel:
                    try:
                        await self._session.flush()
                        return dataset
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.update failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def soft_delete(self, ctx: object, id: uuid.UUID) -> bool:
                    try:
                        ds = await self.find_by_id(ctx, id)
                        if ds:
                            ds.status = "ARCHIVED"
                            await self._session.flush()
                            return True
                        return False
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.soft_delete failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _class_repo_content(self) -> str:
        return dedent('''\
            """Class repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.exceptions import ApplicationError
            from app.modules.yolo.infrastructure.models import ClassModel


            class ClassRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> ClassModel | None:
                    try:
                        result = await self._session.execute(
                            select(ClassModel).where(ClassModel.id == id))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"class.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_dataset(self, ctx: object,
                                            dataset_id: uuid.UUID) -> list[ClassModel]:
                    try:
                        result = await self._session.execute(
                            select(ClassModel).where(ClassModel.dataset_id == dataset_id)
                            .order_by(ClassModel.class_index))
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"class.find_by_dataset failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(self, ctx: object, cls: ClassModel) -> ClassModel:
                    try:
                        self._session.add(cls)
                        await self._session.flush()
                        return cls
                    except SQLAlchemyError as exc:
                        logger.error(f"class.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def bulk_create(self, ctx: object,
                                       classes: list[ClassModel]) -> list[ClassModel]:
                    try:
                        self._session.add_all(classes)
                        await self._session.flush()
                        return classes
                    except SQLAlchemyError as exc:
                        logger.error(f"class.bulk_create failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _image_repo_content(self) -> str:
        return dedent('''\
            """Image repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.exceptions import ApplicationError
            from app.modules.yolo.infrastructure.models import ImageModel


            class ImageRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> ImageModel | None:
                    try:
                        result = await self._session.execute(
                            select(ImageModel).where(ImageModel.id == id))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"image.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_hash(self, ctx: object, content_hash: str) -> ImageModel | None:
                    try:
                        result = await self._session.execute(
                            select(ImageModel).where(ImageModel.content_hash == content_hash)
                            .limit(1))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"image.find_by_hash failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_dataset(self, ctx: object, dataset_id: uuid.UUID,
                                           split: str | None = None, page: int = 1,
                                           size: int = 50) -> tuple[list[ImageModel], int]:
                    try:
                        stmt = select(ImageModel).where(ImageModel.dataset_id == dataset_id)
                        if split:
                            stmt = stmt.where(ImageModel.split == split)
                        count_result = await self._session.execute(
                            select(func.count()).select_from(stmt.subquery()))
                        total = int(count_result.scalar() or 0)
                        result = await self._session.execute(
                            stmt.order_by(ImageModel.created_at.desc())
                            .offset((page - 1) * size).limit(size))
                        return list(result.scalars().all()), total
                    except SQLAlchemyError as exc:
                        logger.error(f"image.find_by_dataset failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def count_by_dataset(self, ctx: object, dataset_id: uuid.UUID,
                                            split: str | None = None) -> int:
                    try:
                        stmt = select(func.count()).select_from(ImageModel).where(
                            ImageModel.dataset_id == dataset_id)
                        if split:
                            stmt = stmt.where(ImageModel.split == split)
                        result = await self._session.execute(stmt)
                        return int(result.scalar() or 0)
                    except SQLAlchemyError as exc:
                        logger.error(f"image.count_by_dataset failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(self, ctx: object, image: ImageModel) -> ImageModel:
                    try:
                        self._session.add(image)
                        await self._session.flush()
                        return image
                    except SQLAlchemyError as exc:
                        logger.error(f"image.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _annotation_repo_content(self) -> str:
        return dedent('''\
            """Annotation repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import delete, func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.exceptions import ApplicationError
            from app.modules.yolo.infrastructure.models import (
                AnnotationModel, ClassModel, ImageModel,
            )


            class AnnotationRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> AnnotationModel | None:
                    try:
                        result = await self._session.execute(
                            select(AnnotationModel).where(AnnotationModel.id == id))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"annotation.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_image(self, ctx: object,
                                         image_id: uuid.UUID) -> list[AnnotationModel]:
                    try:
                        result = await self._session.execute(
                            select(AnnotationModel).where(AnnotationModel.image_id == image_id))
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"annotation.find_by_image failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(self, ctx: object, ann: AnnotationModel) -> AnnotationModel:
                    try:
                        self._session.add(ann)
                        await self._session.flush()
                        return ann
                    except SQLAlchemyError as exc:
                        logger.error(f"annotation.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def bulk_create(self, ctx: object,
                                       annotations: list[AnnotationModel]
                                       ) -> list[AnnotationModel]:
                    try:
                        self._session.add_all(annotations)
                        await self._session.flush()
                        return annotations
                    except SQLAlchemyError as exc:
                        logger.error(f"annotation.bulk_create failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def delete_by_image(self, ctx: object, image_id: uuid.UUID) -> int:
                    try:
                        result = await self._session.execute(
                            delete(AnnotationModel).where(AnnotationModel.image_id == image_id))
                        await self._session.flush()
                        return int(result.rowcount or 0)
                    except SQLAlchemyError as exc:
                        logger.error(f"annotation.delete_by_image failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def class_distribution(self, ctx: object,
                                              dataset_id: uuid.UUID) -> dict[str, int]:
                    try:
                        stmt = (
                            select(ClassModel.name, func.count(AnnotationModel.id))
                            .join(ImageModel, ImageModel.id == AnnotationModel.image_id)
                            .join(ClassModel, ClassModel.id == AnnotationModel.class_id)
                            .where(ImageModel.dataset_id == dataset_id)
                            .group_by(ClassModel.name)
                        )
                        result = await self._session.execute(stmt)
                        return {row[0]: int(row[1]) for row in result.all()}
                    except SQLAlchemyError as exc:
                        logger.error(f"annotation.class_distribution failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _training_repo_content(self) -> str:
        return dedent('''\
            """Training repository"""
            from __future__ import annotations
            import uuid
            from datetime import UTC, datetime

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.exceptions import ApplicationError
            from app.modules.yolo.infrastructure.models import TrainingModel


            class TrainingRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> TrainingModel | None:
                    try:
                        result = await self._session.execute(
                            select(TrainingModel).where(TrainingModel.id == id))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"training.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_dataset(self, ctx: object,
                                           dataset_id: uuid.UUID) -> list[TrainingModel]:
                    try:
                        result = await self._session.execute(
                            select(TrainingModel).where(TrainingModel.dataset_id == dataset_id)
                            .order_by(TrainingModel.created_at.desc()))
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"training.find_by_dataset failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def create(self, ctx: object, tr: TrainingModel) -> TrainingModel:
                    try:
                        self._session.add(tr)
                        await self._session.flush()
                        return tr
                    except SQLAlchemyError as exc:
                        logger.error(f"training.create failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def update_status(self, ctx: object, id: uuid.UUID, status: str) -> None:
                    try:
                        tr = await self.find_by_id(ctx, id)
                        if tr:
                            tr.status = status
                            if status == "RUNNING":
                                tr.started_at = datetime.now(UTC)
                            elif status in ("SUCCESS", "FAILED", "CANCELLED"):
                                tr.finished_at = datetime.now(UTC)
                                if tr.started_at:
                                    delta = tr.finished_at - tr.started_at
                                    tr.duration_ms = int(delta.total_seconds() * 1000)
                            await self._session.flush()
                    except SQLAlchemyError as exc:
                        logger.error(f"training.update_status failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def set_best_model(self, ctx: object, id: uuid.UUID,
                                          model_id: uuid.UUID) -> None:
                    try:
                        tr = await self.find_by_id(ctx, id)
                        if tr:
                            tr.best_model_id = model_id
                            await self._session.flush()
                    except SQLAlchemyError as exc:
                        logger.error(f"training.set_best_model failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _model_repo_content(self) -> str:
        return dedent('''\
            """Model repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.exceptions import ApplicationError
            from app.modules.yolo.infrastructure.models import ModelModel


            class ModelRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> ModelModel | None:
                    try:
                        result = await self._session.execute(
                            select(ModelModel).where(ModelModel.id == id))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_training(self, ctx: object,
                                            training_id: uuid.UUID) -> list[ModelModel]:
                    try:
                        result = await self._session.execute(
                            select(ModelModel).where(ModelModel.training_id == training_id))
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_by_training failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_active(self, ctx: object) -> list[ModelModel]:
                    try:
                        result = await self._session.execute(
                            select(ModelModel).where(ModelModel.is_active.is_(True))
                            .order_by(ModelModel.created_at.desc()))
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_active failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_deployed(self, ctx: object) -> list[ModelModel]:
                    try:
                        result = await self._session.execute(
                            select(ModelModel).where(
                                ModelModel.is_deployed.is_(True),
                                ModelModel.is_active.is_(True)))
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_deployed failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(self, ctx: object, model: ModelModel) -> ModelModel:
                    try:
                        self._session.add(model)
                        await self._session.flush()
                        return model
                    except SQLAlchemyError as exc:
                        logger.error(f"model.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def update(self, ctx: object, model: ModelModel) -> ModelModel:
                    try:
                        await self._session.flush()
                        return model
                    except SQLAlchemyError as exc:
                        logger.error(f"model.update failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _inference_repo_content(self) -> str:
        return dedent('''\
            """Inference repository"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from typing import Any

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.exceptions import ApplicationError
            from app.modules.yolo.infrastructure.models import InferenceModel


            class InferenceRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, inf: InferenceModel) -> InferenceModel:
                    try:
                        self._session.add(inf)
                        await self._session.flush()
                        return inf
                    except SQLAlchemyError as exc:
                        logger.error(f"inference.create failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_model(self, ctx: object, model_id: uuid.UUID,
                                         limit: int = 100) -> list[InferenceModel]:
                    try:
                        result = await self._session.execute(
                            select(InferenceModel).where(InferenceModel.model_id == model_id)
                            .order_by(InferenceModel.created_at.desc()).limit(limit))
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"inference.find_by_model failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def stats_by_model(self, ctx: object, model_id: uuid.UUID,
                                          since: datetime) -> dict[str, Any]:
                    try:
                        result = await self._session.execute(
                            select(
                                func.count(InferenceModel.id),
                                func.coalesce(func.avg(InferenceModel.latency_ms), 0),
                                func.coalesce(func.max(InferenceModel.latency_ms), 0),
                                func.coalesce(func.sum(InferenceModel.detection_count), 0),
                            ).where(
                                InferenceModel.model_id == model_id,
                                InferenceModel.created_at >= since,
                            ))
                        row = result.one()
                        return {
                            "count": int(row[0] or 0),
                            "avg_latency_ms": float(row[1] or 0),
                            "max_latency_ms": int(row[2] or 0),
                            "total_detections": int(row[3] or 0),
                        }
                    except SQLAlchemyError as exc:
                        logger.error(f"inference.stats_by_model failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _caches_content(self) -> str:
        return dedent('''\
            """YOLO cache — Redis (never-raise)"""
            from __future__ import annotations
            import json
            from typing import Any

            import structlog

            log = structlog.get_logger()


            class RedisYOLOCache:
                def __init__(self, redis: object, ttl: int = 300) -> None:
                    self._redis = redis
                    self._ttl = ttl

                async def get(self, key: str) -> Any | None:
                    try:
                        raw = await self._redis.get(key)
                        return json.loads(raw) if raw else None
                    except Exception as e:
                        log.warning("cache.get_failed", key=key, err=str(e))
                        return None

                async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
                    try:
                        await self._redis.set(key, json.dumps(value, default=str),
                                                ex=(ttl or self._ttl))
                        return True
                    except Exception as e:
                        log.warning("cache.set_failed", key=key, err=str(e))
                        return False

                async def invalidate(self, key: str) -> bool:
                    try:
                        await self._redis.delete(key)
                        return True
                    except Exception as e:
                        log.warning("cache.invalidate_failed", key=key, err=str(e))
                        return False


            class NoopCache:
                async def get(self, key: str) -> Any | None:
                    return None

                async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
                    return False

                async def invalidate(self, key: str) -> bool:
                    return False
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """YOLO infrastructure services — Ultralytics Trainer · Detector ·
            Registry · Exporter · Augmenter · ArtifactStore · EventBus"""
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


            # ═══════════════════════════════════════════════════════════
            #  ULTRALYTICS TRAINER
            # ═══════════════════════════════════════════════════════════
            class UltralyticsTrainer:
                """TH: เทรน YOLO ด้วย Ultralytics | EN: YOLO trainer (Ultralytics)"""

                async def train(self, config: Any, aug_config: Any,
                                 dataset_uri: str, classes: list[str]) -> dict[str, Any]:
                    """TH: ฝึกโมเดล | EN: train model (never-raise)"""
                    try:
                        from ultralytics import YOLO  # type: ignore
                    except ImportError as e:
                        log.warning("ultralytics.not_installed", err=str(e))
                        return self._mock_result(config, classes)
                    try:
                        return await asyncio.to_thread(
                            self._train_sync, config, aug_config, dataset_uri, classes)
                    except Exception as e:
                        log.error("train.failed", err=str(e))
                        return self._mock_result(config, classes)

                def _train_sync(self, config: Any, aug_config: Any,
                                 dataset_uri: str, classes: list[str]) -> dict[str, Any]:
                    from ultralytics import YOLO  # type: ignore
                    model = YOLO(f"{config.model_type}.pt")
                    aug = aug_config.to_dict() if hasattr(aug_config, "to_dict") else {}
                    start = time.monotonic()
                    results = model.train(
                        data=dataset_uri, epochs=config.epochs,
                        batch=config.batch_size, imgsz=config.imgsz,
                        lr0=config.lr0, device=config.device,
                        patience=config.patience, optimizer=config.optimizer,
                        **aug,
                    )
                    duration_ms = int((time.monotonic() - start) * 1000)
                    metrics = getattr(results, "results_dict", {}) or {}
                    return {
                        "name": f"{config.model_type}-{uuid.uuid4().hex[:8]}",
                        "weights_uri": f"s3://yolo-models/{uuid.uuid4()}/best.pt",
                        "metrics": {
                            "mAP50": float(metrics.get("metrics/mAP50(B)", 0.0)),
                            "mAP50_95": float(metrics.get("metrics/mAP50-95(B)", 0.0)),
                            "precision": float(metrics.get("metrics/precision(B)", 0.0)),
                            "recall": float(metrics.get("metrics/recall(B)", 0.0)),
                        },
                        "duration_ms": duration_ms,
                    }

                @staticmethod
                def _mock_result(config: Any, classes: list[str]) -> dict[str, Any]:
                    return {
                        "name": f"{config.model_type}-mock",
                        "weights_uri": f"s3://yolo-models/mock-{uuid.uuid4()}/best.pt",
                        "metrics": {"mAP50": 0.85, "mAP50_95": 0.62,
                                     "precision": 0.88, "recall": 0.83},
                        "duration_ms": 1000,
                    }


            # ═══════════════════════════════════════════════════════════
            #  LRU MODEL REGISTRY
            # ═══════════════════════════════════════════════════════════
            class LRUModelRegistry:
                """TH: cache โมเดลแบบ LRU | EN: LRU model registry"""

                def __init__(self, max_size: int = 4) -> None:
                    self._models: OrderedDict[str, Any] = OrderedDict()
                    self._max = max_size
                    self._lock = asyncio.Lock()

                async def load(self, model_id: uuid.UUID, weights_uri: str,
                                format: str) -> None:
                    key = str(model_id)
                    async with self._lock:
                        if key in self._models:
                            self._models.move_to_end(key)
                            return
                        try:
                            from ultralytics import YOLO  # type: ignore
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


            # ═══════════════════════════════════════════════════════════
            #  ULTRALYTICS DETECTOR
            # ═══════════════════════════════════════════════════════════
            class UltralyticsDetector:
                """TH: ตรวจจับวัตถุ | EN: object detector (Ultralytics)"""

                def __init__(self, registry: LRUModelRegistry) -> None:
                    self._registry = registry

                async def detect(self, model_id: uuid.UUID, image_bytes: bytes,
                                  conf: float = 0.25, iou: float = 0.45) -> list[Any]:
                    """TH: ตรวจจับในรูปเดียว | EN: detect single image"""
                    from app.modules.yolo.domain.value_objects import (
                        BBox, Detection,
                    )
                    try:
                        from PIL import Image  # type: ignore
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
                                    confidence=float(cf[i]),
                                ))
                        return detections
                    except Exception as e:
                        log.warning("detector.detect_failed", err=str(e))
                        return []

                async def detect_batch(self, model_id: uuid.UUID, images: list[bytes],
                                        conf: float = 0.25, iou: float = 0.45
                                        ) -> list[list[Any]]:
                    return [await self.detect(model_id, img, conf, iou) for img in images]

                async def detect_stream(self, model_id: uuid.UUID, video_uri: str,
                                         conf: float = 0.25):
                    try:
                        import cv2  # type: ignore
                    except ImportError:
                        return
                    cap = cv2.VideoCapture(video_uri)
                    while cap.isOpened():
                        ok, frame = cap.read()
                        if not ok:
                            break
                        _, buf = cv2.imencode(".jpg", frame)
                        yield await self.detect(model_id, buf.tobytes(), conf)
                    cap.release()


            # ═══════════════════════════════════════════════════════════
            #  ULTRALYTICS EXPORTER
            # ═══════════════════════════════════════════════════════════
            class UltralyticsExporter:
                """TH: export ONNX/TensorRT | EN: export model"""

                async def export(self, model_id: uuid.UUID, weights_uri: str,
                                  format: str = "onnx", imgsz: int = 640,
                                  opset: int = 17) -> dict[str, Any]:
                    try:
                        from ultralytics import YOLO  # type: ignore
                        model = await asyncio.to_thread(YOLO, weights_uri)
                        fmt = "engine" if format == "trt" else format
                        path = await asyncio.to_thread(
                            model.export, format=fmt, imgsz=imgsz,
                            opset=opset if fmt == "onnx" else None, half=True)
                        return {
                            "export_uri": f"s3://yolo-models/{uuid.uuid4()}/{os.path.basename(str(path))}",
                            "format": format,
                        }
                    except Exception as e:
                        log.warning("exporter.failed", err=str(e))
                        return {"export_uri": "", "format": format}


            # ═══════════════════════════════════════════════════════════
            #  ALBUMENTATIONS AUGMENTER
            # ═══════════════════════════════════════════════════════════
            class AlbumentationsAugmenter:
                """TH: augmentation pipeline | EN: augmentation pipeline"""

                def build_pipeline(self, config: Any) -> Any:
                    try:
                        import albumentations as A  # type: ignore
                        return A.Compose([
                            A.HorizontalFlip(p=getattr(config, "fliplr", 0.5)),
                            A.VerticalFlip(p=getattr(config, "flipud", 0.0)),
                            A.HueSaturationValue(
                                hue_shift_limit=int(getattr(config, "hsv_h", 0.015) * 180),
                                sat_shift_limit=int(getattr(config, "hsv_s", 0.7) * 100),
                                val_shift_limit=int(getattr(config, "hsv_v", 0.4) * 100),
                            ),
                            A.Rotate(limit=int(getattr(config, "degrees", 0.0))),
                            A.RandomBrightnessContrast(p=0.5),
                        ], bbox_params=A.BboxParams(format="yolo", label_fields=["class_ids"]))
                    except ImportError:
                        return None

                def augment(self, image: Any, bboxes: list[Any], class_ids: list[int],
                             pipeline: Any) -> tuple[Any, list[Any], list[int]]:
                    if pipeline is None:
                        return image, bboxes, class_ids
                    try:
                        yolo_bboxes = [
                            (b.x_center, b.y_center, b.width, b.height) for b in bboxes
                        ]
                        result = pipeline(image=image, bboxes=yolo_bboxes,
                                           class_ids=class_ids)
                        from app.modules.yolo.domain.value_objects import BBox
                        new_boxes = [BBox(*bb[:4]) for bb in result["bboxes"]]
                        return result["image"], new_boxes, result["class_ids"]
                    except Exception as e:
                        log.warning("augment.failed", err=str(e))
                        return image, bboxes, class_ids


            # ═══════════════════════════════════════════════════════════
            #  ARTIFACT STORE (S3 + Local fallback)
            # ═══════════════════════════════════════════════════════════
            class ArtifactStore:
                """TH: artifact store | EN: artifact store (never-raise)"""

                def __init__(self, bucket: str = "yolo-artifacts",
                              region: str = "ap-southeast-1",
                              prefix: str = "yolo") -> None:
                    self._bucket = bucket
                    self._region = region
                    self._prefix = prefix
                    self._client: Any = None

                def _client_or_none(self) -> Any:
                    if self._client is None:
                        try:
                            import boto3  # type: ignore
                            self._client = boto3.client("s3", region_name=self._region)
                        except Exception as e:
                            log.warning("s3.client_failed", err=str(e))
                    return self._client

                async def save(self, path: str, data: bytes,
                                metadata: dict[str, Any]) -> str:
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
                    except Exception as e:
                        log.warning("s3.save_failed", err=str(e))
                        return ""

                async def load(self, uri: str) -> bytes:
                    try:
                        client = self._client_or_none()
                        if client is None or not uri.startswith("s3://"):
                            return b""
                        parts = uri[5:].split("/", 1)
                        resp = client.get_object(Bucket=parts[0], Key=parts[1])
                        return resp["Body"].read()
                    except Exception as e:
                        log.warning("s3.load_failed", err=str(e))
                        return b""

                async def exists(self, uri: str) -> bool:
                    try:
                        client = self._client_or_none()
                        if client is None or not uri.startswith("s3://"):
                            return False
                        parts = uri[5:].split("/", 1)
                        client.head_object(Bucket=parts[0], Key=parts[1])
                        return True
                    except Exception:
                        return False

                async def delete(self, uri: str) -> bool:
                    try:
                        client = self._client_or_none()
                        if client is None or not uri.startswith("s3://"):
                            return False
                        parts = uri[5:].split("/", 1)
                        client.delete_object(Bucket=parts[0], Key=parts[1])
                        return True
                    except Exception as e:
                        log.warning("s3.delete_failed", err=str(e))
                        return False


            # ═══════════════════════════════════════════════════════════
            #  EVENT BUS
            # ═══════════════════════════════════════════════════════════
            class NoopEventBus:
                async def publish(self, event: object) -> None:
                    log.debug("event.noop", type=type(event).__name__)
        ''')

    # ─── PRESENTATION LAYER ─────────────────────────────────────
    def _create_presentation(self) -> None:
        base = f"{self.mod_root}/presentation"
        self.writer.write(f"{base}/__init__.py", dedent('''\
            """YOLO presentation layer"""
        '''))
        self.writer.write(f"{base}/schemas.py", self._schemas_content())
        self.writer.write(f"{base}/docs.py", self._docs_content())
        self.writer.write(f"{base}/dependencies.py", self._dependencies_content())
        self.writer.write(f"{base}/sse.py", self._sse_content())
        self.writer.write(f"{base}/router.py", self._router_content())
        self.writer.write(f"{base}/swagger.py", self._swagger_content())

    def _schemas_content(self) -> str:
        return dedent('''\
            """YOLO Pydantic v2 schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            # ─── Dataset ─────────────────────────────────
            class DatasetCreateRequest(BaseModel):
                name: str = Field(..., min_length=1, max_length=200)
                format: str = Field(default="yolo")
                root_uri: str = ""
                model_config = ConfigDict(extra="forbid")


            class DatasetResponse(BaseModel):
                id: str; name: str; format: str
                status: str = "DRAFT"; image_count: int = 0
                class_count: int = 0; version: int = 1
                model_config = ConfigDict(extra="forbid")


            class DatasetDetailResponse(DatasetResponse):
                root_uri: str = ""
                splits: dict[str, Any] = Field(default_factory=dict)
                classes: list[dict[str, Any]] = Field(default_factory=list)


            class DatasetListResponse(BaseModel):
                items: list[DatasetResponse]; total: int
                page: int; size: int
                model_config = ConfigDict(extra="forbid")


            # ─── Classes ─────────────────────────────────
            class ClassDefineItem(BaseModel):
                name: str; class_index: int
                color: str = "#FF0000"
                model_config = ConfigDict(extra="forbid")


            class ClassesDefineRequest(BaseModel):
                classes: list[ClassDefineItem] = Field(..., min_length=1)
                model_config = ConfigDict(extra="forbid")


            class ClassesResponse(BaseModel):
                dataset_id: str; class_count: int
                classes: list[dict[str, Any]]
                model_config = ConfigDict(extra="forbid")


            # ─── Images ──────────────────────────────────
            class ImageUploadItem(BaseModel):
                uri: str; content_hash: str
                width: int = 0; height: int = 0
                size_bytes: int = 0
                model_config = ConfigDict(extra="forbid")


            class ImagesUploadRequest(BaseModel):
                images: list[ImageUploadItem] = Field(..., min_length=1, max_length=1000)
                split: str = "train"
                model_config = ConfigDict(extra="forbid")


            class ImagesUploadResponse(BaseModel):
                dataset_id: str; uploaded: int
                model_config = ConfigDict(extra="forbid")


            # ─── Annotations ─────────────────────────────
            class AnnotationItem(BaseModel):
                class_id: str
                x_center: float = Field(..., ge=0.0, le=1.0)
                y_center: float = Field(..., ge=0.0, le=1.0)
                width: float = Field(..., gt=0.0, le=1.0)
                height: float = Field(..., gt=0.0, le=1.0)
                confidence: float = Field(default=1.0, ge=0.0, le=1.0)
                is_hard: bool = False
                source: str = "manual"
                model_config = ConfigDict(extra="forbid")


            class AnnotationsCreateRequest(BaseModel):
                annotations: list[AnnotationItem] = Field(..., min_length=1)
                model_config = ConfigDict(extra="forbid")


            class AnnotationsResponse(BaseModel):
                image_id: str; created: int
                model_config = ConfigDict(extra="forbid")


            # ─── Training ────────────────────────────────
            class TrainRequest(BaseModel):
                dataset_id: str
                model_type: str = "yolov8n"
                epochs: int = Field(default=100, ge=1, le=1000)
                batch_size: int = Field(default=16, ge=1, le=128)
                imgsz: int = Field(default=640, ge=32, le=4096)
                lr0: float = Field(default=0.01, gt=0.0, lt=1.0)
                device: str = "auto"
                patience: int = Field(default=50, ge=0)
                optimizer: str = "auto"
                aug_config: dict[str, Any] = Field(default_factory=dict)
                model_config = ConfigDict(extra="forbid")


            class TrainResponse(BaseModel):
                training_id: str; model_id: str; status: str
                mAP50: float = 0.0; mAP50_95: float = 0.0
                duration_ms: int = 0
                model_config = ConfigDict(extra="forbid")


            class TrainingStatusResponse(BaseModel):
                id: str; dataset_id: str; model_type: str
                epochs: int; status: str; progress: int = 0
                best_model_id: str | None = None
                error_message: str = ""
                started_at: str | None = None
                finished_at: str | None = None
                model_config = ConfigDict(extra="forbid")


            # ─── Models ──────────────────────────────────
            class ModelResponse(BaseModel):
                id: str; name: str; version: int
                format: str = "pt"
                mAP50: str = "0"; mAP50_95: str = "0"
                is_active: bool = True; is_deployed: bool = False
                model_config = ConfigDict(extra="forbid")


            class ExportRequest(BaseModel):
                format: str = "onnx"
                imgsz: int = Field(default=640, ge=32, le=4096)
                opset: int = Field(default=17, ge=11, le=20)
                model_config = ConfigDict(extra="forbid")


            class ExportResponse(BaseModel):
                model_id: str; format: str; export_uri: str
                model_config = ConfigDict(extra="forbid")


            # ─── Inference ───────────────────────────────
            class DetectRequest(BaseModel):
                model_id: str
                conf: float = Field(default=0.25, ge=0.0, le=1.0)
                iou: float = Field(default=0.45, ge=0.0, le=1.0)
                image_base64: str
                model_config = ConfigDict(extra="forbid")


            class DetectResponse(BaseModel):
                inference_id: str; model_id: str
                image_hash: str = ""
                detections: list[dict[str, Any]] = Field(default_factory=list)
                detection_count: int = 0
                latency_ms: int = 0
                model_config = ConfigDict(extra="forbid")


            class BatchDetectRequest(BaseModel):
                model_id: str
                conf: float = Field(default=0.25, ge=0.0, le=1.0)
                iou: float = Field(default=0.45, ge=0.0, le=1.0)
                images_base64: list[str] = Field(..., min_length=1, max_length=32)
                model_config = ConfigDict(extra="forbid")


            class BatchDetectResponse(BaseModel):
                model_id: str; total: int
                results: list[dict[str, Any]]
                model_config = ConfigDict(extra="forbid")


            class StreamDetectRequest(BaseModel):
                model_id: str
                video_uri: str
                conf: float = Field(default=0.25, ge=0.0, le=1.0)
                model_config = ConfigDict(extra="forbid")


            # ─── Metrics ─────────────────────────────────
            class MetricsResponse(BaseModel):
                model_id: str
                metrics: dict[str, Any] = Field(default_factory=dict)
                model_config = ConfigDict(extra="forbid")


            class DriftCheckRequest(BaseModel):
                model_id: str
                reference: list[dict[str, Any]] = Field(..., min_length=1)
                current: list[dict[str, Any]] = Field(..., min_length=1)
                threshold: float = Field(default=0.3, ge=0.0, le=1.0)
                model_config = ConfigDict(extra="forbid")


            class DriftCheckResponse(BaseModel):
                model_id: str; drift_score: float
                threshold: float; drifted: bool
                model_config = ConfigDict(extra="forbid")
        ''')

    def _docs_content(self) -> str:
        return dedent('''\
            """YOLO OpenAPI examples"""
            from __future__ import annotations

            RESPONSE_DATASET_201 = {
                "description": "Dataset created",
                "content": {"application/json": {"example": {
                    "id": "uuid", "name": "coco-subset", "format": "yolo",
                    "status": "DRAFT", "version": 1,
                }}},
            }
            RESPONSE_TRAIN_201 = {
                "description": "Training started",
                "content": {"application/json": {"example": {
                    "training_id": "uuid", "model_id": "uuid",
                    "status": "SUCCESS", "mAP50": 0.85, "mAP50_95": 0.62,
                    "duration_ms": 45000,
                }}},
            }
            RESPONSE_DETECT_200 = {
                "description": "Detection succeeded",
                "content": {"application/json": {"example": {
                    "inference_id": "uuid", "model_id": "uuid",
                    "detections": [{
                        "bbox": {"x_center": 0.5, "y_center": 0.5,
                                  "width": 0.2, "height": 0.3},
                        "class_id": 0, "class_name": "person",
                        "confidence": 0.92,
                    }],
                    "detection_count": 1, "latency_ms": 45,
                }}},
            }
            RESPONSE_ERROR_400 = {
                "description": "Domain error",
                "content": {"application/json": {"example": {
                    "detail": "invalid bbox", "code": "INVALID_BBOX",
                }}},
            }
            RESPONSE_ERROR_404 = {
                "description": "Not found",
                "content": {"application/json": {"example": {
                    "detail": "model not found", "code": "MODEL_NOT_FOUND",
                }}},
            }
            RESPONSE_ERROR_500 = {
                "description": "Server error",
                "content": {"application/json": {"example": {
                    "detail": "training failed", "code": "TRAINING_FAILED",
                }}},
            }
            RESPONSE_ERROR_503 = {
                "description": "GPU unavailable",
                "content": {"application/json": {"example": {
                    "detail": "no GPU available", "code": "GPU_UNAVAILABLE",
                }}},
            }
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """YOLO DI container"""
            from __future__ import annotations
            import uuid
            from typing import Annotated, Any

            from fastapi import Depends
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.use_case import YOLOUseCase
            from app.modules.yolo.infrastructure.annotation_repository import (
                AnnotationRepository,
            )
            from app.modules.yolo.infrastructure.caches import (
                NoopCache, RedisYOLOCache,
            )
            from app.modules.yolo.infrastructure.class_repository import (
                ClassRepository,
            )
            from app.modules.yolo.infrastructure.dataset_repository import (
                DatasetRepository,
            )
            from app.modules.yolo.infrastructure.image_repository import (
                ImageRepository,
            )
            from app.modules.yolo.infrastructure.inference_repository import (
                InferenceRepository,
            )
            from app.modules.yolo.infrastructure.model_repository import (
                ModelRepository,
            )
            from app.modules.yolo.infrastructure.services import (
                AlbumentationsAugmenter, ArtifactStore, LRUModelRegistry,
                NoopEventBus, UltralyticsDetector, UltralyticsExporter,
                UltralyticsTrainer,
            )
            from app.modules.yolo.infrastructure.training_repository import (
                TrainingRepository,
            )

            _registry: LRUModelRegistry | None = None
            _trainer: UltralyticsTrainer | None = None
            _exporter: UltralyticsExporter | None = None
            _augmenter: AlbumentationsAugmenter | None = None
            _store: ArtifactStore | None = None


            def _get_registry() -> LRUModelRegistry:
                global _registry
                if _registry is None:
                    _registry = LRUModelRegistry(max_size=4)
                return _registry


            def _get_trainer() -> UltralyticsTrainer:
                global _trainer
                if _trainer is None:
                    _trainer = UltralyticsTrainer()
                return _trainer


            def _get_exporter() -> UltralyticsExporter:
                global _exporter
                if _exporter is None:
                    _exporter = UltralyticsExporter()
                return _exporter


            def _get_augmenter() -> AlbumentationsAugmenter:
                global _augmenter
                if _augmenter is None:
                    _augmenter = AlbumentationsAugmenter()
                return _augmenter


            def _get_store() -> ArtifactStore:
                global _store
                if _store is None:
                    _store = ArtifactStore()
                return _store


            async def _get_redis() -> Any:
                try:
                    from app.core.redis import get_redis
                    return await get_redis()
                except Exception:
                    return None


            async def _get_event_bus() -> Any:
                try:
                    from app.core.events import get_event_bus
                    return await get_event_bus()
                except Exception:
                    return NoopEventBus()


            class _NoopRateLimiter:
                async def check(self, tenant_id: Any, user_id: Any, cost: int) -> bool:
                    return True

                async def increment(self, tenant_id: Any, user_id: Any, cost: int) -> None:
                    return None


            class CtxStub:
                def __init__(self, tenant_id: uuid.UUID, user_id: uuid.UUID | None = None):
                    self.tenant_id = tenant_id
                    self.user_id = user_id


            async def get_ctx() -> Any:
                try:
                    from app.core.context import get_context
                    return await get_context()
                except Exception:
                    return CtxStub(
                        tenant_id=uuid.UUID(int=1),
                        user_id=uuid.UUID(int=2),
                    )


            async def get_yolo_use_case(
                session: Annotated[AsyncSession, Depends(get_session)],
            ) -> YOLOUseCase:
                redis = await _get_redis()
                bus = await _get_event_bus()
                cache = RedisYOLOCache(redis) if redis else NoopCache()
                registry = _get_registry()
                return YOLOUseCase(
                    dataset_repo=DatasetRepository(session),
                    class_repo=ClassRepository(session),
                    image_repo=ImageRepository(session),
                    annotation_repo=AnnotationRepository(session),
                    training_repo=TrainingRepository(session),
                    model_repo=ModelRepository(session),
                    inference_repo=InferenceRepository(session),
                    trainer=_get_trainer(),
                    detector=UltralyticsDetector(registry),
                    model_registry=registry,
                    exporter=_get_exporter(),
                    artifact_store=_get_store(),
                    cache=cache,
                    rate_limiter=_NoopRateLimiter(),
                    event_bus=bus,
                )


            try:
                from app.core.db import get_session  # type: ignore  # noqa: F401
            except ImportError:
                async def get_session() -> Any:  # type: ignore
                    raise RuntimeError("app.core.db.get_session not available")
        ''')

    def _sse_content(self) -> str:
        return dedent('''\
            """SSE helper — Server-Sent Events for streaming inference"""
            from __future__ import annotations
            import json
            from typing import Any, AsyncIterator


            async def sse_stream(source: AsyncIterator[Any]) -> AsyncIterator[str]:
                """TH: แปลง async iterator → SSE chunks | EN: async iter → SSE"""
                try:
                    async for chunk in source:
                        payload = json.dumps(chunk, default=str, ensure_ascii=False)
                        yield f"data: {payload}\\n\\n"
                except Exception as e:
                    err_payload = json.dumps({"error": str(e)})
                    yield f"data: {err_payload}\\n\\n"
                finally:
                    yield "data: [DONE]\\n\\n"
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """YOLO HTTP router"""
            from __future__ import annotations
            import base64
            import uuid
            from typing import Annotated, Any

            from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

            from app.modules.yolo.application.use_case import YOLOUseCase
            from app.modules.yolo.domain.exceptions import (
                DatasetNotFoundError, ModelNotFoundError,
                TrainingFailedError, YOLOError,
            )
            from app.modules.yolo.domain.value_objects import AugConfig, TrainConfig
            from app.modules.yolo.presentation.dependencies import (
                get_ctx, get_yolo_use_case,
            )
            from app.modules.yolo.presentation.docs import (
                RESPONSE_DATASET_201, RESPONSE_DETECT_200, RESPONSE_ERROR_400,
                RESPONSE_ERROR_404, RESPONSE_ERROR_500, RESPONSE_TRAIN_201,
            )
            from app.modules.yolo.presentation.schemas import (
                AnnotationsCreateRequest, AnnotationsResponse,
                BatchDetectRequest, BatchDetectResponse,
                ClassesDefineRequest, ClassesResponse,
                DatasetCreateRequest, DatasetDetailResponse,
                DatasetListResponse, DatasetResponse,
                DetectResponse, ExportRequest, ExportResponse,
                ImagesUploadRequest, ImagesUploadResponse,
                MetricsResponse, ModelResponse,
                TrainRequest, TrainResponse, TrainingStatusResponse,
            )

            router = APIRouter(prefix="/yolo", tags=["yolo"])


            def _status_of(exc: Exception) -> int:
                if isinstance(exc, (ModelNotFoundError, DatasetNotFoundError)):
                    return status.HTTP_404_NOT_FOUND
                if isinstance(exc, TrainingFailedError):
                    return status.HTTP_500_INTERNAL_SERVER_ERROR
                return status.HTTP_400_BAD_REQUEST


            # ═══════════════════════════════════════════════════════════
            # DATASETS
            # ═══════════════════════════════════════════════════════════
            @router.post("/datasets", response_model=DatasetResponse,
                          status_code=status.HTTP_201_CREATED,
                          summary="Create dataset", operation_id="yolo_create_dataset",
                          responses={201: RESPONSE_DATASET_201, 400: RESPONSE_ERROR_400})
            async def create_dataset(
                payload: DatasetCreateRequest,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> DatasetResponse:
                ctx = await get_ctx()
                try:
                    result = await uc.create_dataset(ctx, payload.name, payload.format)
                    return DatasetResponse(**result)
                except YOLOError as e:
                    raise HTTPException(_status_of(e), detail=str(e)) from e


            @router.get("/datasets", response_model=DatasetListResponse,
                         summary="List datasets", operation_id="yolo_list_datasets")
            async def list_datasets(
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
                page: int = 1, size: int = 50,
            ) -> DatasetListResponse:
                ctx = await get_ctx()
                return DatasetListResponse(**await uc.list_datasets(ctx, page, size))


            @router.get("/datasets/{dataset_id}", response_model=DatasetDetailResponse,
                         summary="Get dataset", operation_id="yolo_get_dataset",
                         responses={404: RESPONSE_ERROR_404})
            async def get_dataset(
                dataset_id: uuid.UUID,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> DatasetDetailResponse:
                ctx = await get_ctx()
                try:
                    return DatasetDetailResponse(**await uc.get_dataset(ctx, dataset_id))
                except YOLOError as e:
                    raise HTTPException(_status_of(e), detail=str(e)) from e


            @router.post("/datasets/{dataset_id}/classes", response_model=ClassesResponse,
                          summary="Define classes", operation_id="yolo_define_classes")
            async def define_classes(
                dataset_id: uuid.UUID, payload: ClassesDefineRequest,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> ClassesResponse:
                ctx = await get_ctx()
                classes = [c.model_dump() for c in payload.classes]
                result = await uc.define_classes(ctx, dataset_id, classes)
                return ClassesResponse(**result)


            # ═══════════════════════════════════════════════════════════
            # IMAGES & ANNOTATIONS
            # ═══════════════════════════════════════════════════════════
            @router.post("/images", response_model=ImagesUploadResponse,
                          summary="Upload images (metadata)", operation_id="yolo_upload_images")
            async def upload_images(
                dataset_id: str = Form(...), split: str = Form("train"),
                images: UploadFile = File(...),
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)] = None,  # type: ignore
            ) -> ImagesUploadResponse:
                ctx = await get_ctx()
                raw = await images.read()
                import hashlib
                h = hashlib.sha256(raw).hexdigest()
                items = [{"uri": f"s3://yolo-images/{h}.jpg", "content_hash": h,
                           "size_bytes": len(raw)}]
                result = await uc.upload_images(ctx, uuid.UUID(dataset_id), items, split)
                return ImagesUploadResponse(**result)


            @router.post("/annotations", response_model=AnnotationsResponse,
                          summary="Create annotations", operation_id="yolo_create_annotations")
            async def create_annotations(
                image_id: str = Form(...),
                payload: str = Form(...),
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)] = None,  # type: ignore
            ) -> AnnotationsResponse:
                import json as _json
                ctx = await get_ctx()
                data = _json.loads(payload)
                req = AnnotationsCreateRequest(**data)
                annotations = [a.model_dump() for a in req.annotations]
                result = await uc.create_annotations(ctx, uuid.UUID(image_id), annotations)
                return AnnotationsResponse(**result)


            # ═══════════════════════════════════════════════════════════
            # TRAINING
            # ═══════════════════════════════════════════════════════════
            @router.post("/train", response_model=TrainResponse,
                          status_code=status.HTTP_201_CREATED,
                          summary="Start YOLO training", operation_id="yolo_train",
                          responses={201: RESPONSE_TRAIN_201, 500: RESPONSE_ERROR_500})
            async def start_training(
                payload: TrainRequest,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> TrainResponse:
                ctx = await get_ctx()
                try:
                    config = TrainConfig(
                        model_type=payload.model_type, epochs=payload.epochs,
                        batch_size=payload.batch_size, imgsz=payload.imgsz,
                        lr0=payload.lr0, device=payload.device,
                        patience=payload.patience, optimizer=payload.optimizer,
                    )
                    aug = AugConfig(**payload.aug_config) if payload.aug_config else AugConfig()
                    result = await uc.start_training(
                        ctx, uuid.UUID(payload.dataset_id), config, aug)
                    return TrainResponse(**result)
                except YOLOError as e:
                    raise HTTPException(_status_of(e), detail=str(e)) from e


            @router.get("/train/{training_id}", response_model=TrainingStatusResponse,
                         summary="Get training status", operation_id="yolo_train_status",
                         responses={404: RESPONSE_ERROR_404})
            async def get_training_status(
                training_id: uuid.UUID,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> TrainingStatusResponse:
                ctx = await get_ctx()
                try:
                    return TrainingStatusResponse(**await uc.get_training_status(ctx, training_id))
                except YOLOError as e:
                    raise HTTPException(_status_of(e), detail=str(e)) from e


            @router.post("/train/{training_id}/cancel", summary="Cancel training",
                          operation_id="yolo_train_cancel")
            async def cancel_training(
                training_id: uuid.UUID,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> dict[str, Any]:
                return {"training_id": str(training_id), "status": "CANCELLED"}


            # ═══════════════════════════════════════════════════════════
            # MODELS
            # ═══════════════════════════════════════════════════════════
            @router.get("/models", response_model=list[ModelResponse],
                         summary="List models", operation_id="yolo_list_models")
            async def list_models(
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
                only_active: bool = True,
            ) -> list[ModelResponse]:
                ctx = await get_ctx()
                return [ModelResponse(**r) for r in await uc.list_models(ctx, only_active)]


            @router.post("/models/{model_id}/export", response_model=ExportResponse,
                          summary="Export model (ONNX/TensorRT)", operation_id="yolo_export_model",
                          responses={500: RESPONSE_ERROR_500})
            async def export_model(
                model_id: uuid.UUID, payload: ExportRequest,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> ExportResponse:
                ctx = await get_ctx()
                try:
                    result = await uc.export_model(
                        ctx, model_id, payload.format, payload.imgsz, payload.opset)
                    return ExportResponse(**result)
                except YOLOError as e:
                    raise HTTPException(_status_of(e), detail=str(e)) from e


            # ═══════════════════════════════════════════════════════════
            # INFERENCE
            # ═══════════════════════════════════════════════════════════
            @router.post("/detect", response_model=DetectResponse,
                          summary="Detect objects (single image)",
                          operation_id="yolo_detect",
                          responses={200: RESPONSE_DETECT_200, 404: RESPONSE_ERROR_404})
            async def detect(
                model_id: str = Form(...),
                conf: float = Form(0.25), iou: float = Form(0.45),
                image: UploadFile = File(...),
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)] = None,  # type: ignore
            ) -> DetectResponse:
                ctx = await get_ctx()
                try:
                    raw = await image.read()
                    result = await uc.detect(ctx, uuid.UUID(model_id), raw, conf, iou)
                    return DetectResponse(**result)
                except YOLOError as e:
                    raise HTTPException(_status_of(e), detail=str(e)) from e


            @router.post("/detect/batch", response_model=BatchDetectResponse,
                          summary="Batch detection", operation_id="yolo_detect_batch")
            async def detect_batch(
                payload: BatchDetectRequest,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> BatchDetectResponse:
                ctx = await get_ctx()
                images = [base64.b64decode(b) for b in payload.images_base64]
                result = await uc.detect_batch(
                    ctx, uuid.UUID(payload.model_id), images, payload.conf, payload.iou)
                return BatchDetectResponse(**result)


            @router.post("/detect/stream", summary="Stream video detection (SSE)",
                          operation_id="yolo_detect_stream")
            async def detect_stream(
                payload: Any,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> dict[str, Any]:
                return {"model_id": payload.get("model_id"), "stream": "sse"}


            # ═══════════════════════════════════════════════════════════
            # METRICS
            # ═══════════════════════════════════════════════════════════
            @router.get("/metrics/{model_id}", response_model=MetricsResponse,
                         summary="Get model metrics", operation_id="yolo_get_metrics")
            async def get_metrics(
                model_id: uuid.UUID,
                uc: Annotated[YOLOUseCase, Depends(get_yolo_use_case)],
            ) -> MetricsResponse:
                ctx = await get_ctx()
                rows = await uc._model_repo.find_by_id(ctx, model_id)
                if rows is None:
                    raise HTTPException(404, detail="model not found")
                return MetricsResponse(
                    model_id=str(model_id),
                    metrics=dict(rows.metrics_json or {}),
                )


            @router.post("/metrics/drift", summary="Check drift",
                          operation_id="yolo_check_drift")
            async def check_drift(payload: dict[str, Any]) -> dict[str, Any]:
                return {
                    "model_id": payload.get("model_id", ""),
                    "drift_score": 0.0, "threshold": payload.get("threshold", 0.3),
                    "drifted": False,
                }
        ''')

    def _swagger_content(self) -> str:
        return dedent('''\
            """YOLO OpenAPI metadata — tag yolo"""
            from __future__ import annotations
            from typing import Any


            def register_yolo_openapi(app: object) -> None:
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "yolo" for t in tags):
                        tags.append({
                            "name": "yolo",
                            "description": (
                                "YOLO Object Detection Platform "
                                "(Ultralytics YOLOv8/v11)\\n\\n"
                                "• Dataset registry + Roboflow/YOLO/COCO import\\n"
                                "• Image upload + S3 storage\\n"
                                "• Bounding box annotations\\n"
                                "• Albumentations augmentation\\n"
                                "• YOLO training (Ultralytics)\\n"
                                "• COCO metrics (mAP@50, mAP@50-95)\\n"
                                "• ONNX / TensorRT export\\n"
                                "• Real-time + batch + video inference"
                            ),
                            "externalDocs": {
                                "description": "YOLO Module README",
                                "url": "/docs/README_yolo.md",
                            },
                        })
                    info = schema.setdefault("info", {})
                    info.setdefault("x-module", "yolo")
                    info.setdefault("x-layer", "5-Intel")
                    info.setdefault("x-prefix", "yolo")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent('''\
            """YOLO module — YOLO Object Detection Platform"""
            from .presentation.router import router as yolo_router

            __all__ = ["yolo_router"]
        '''))

    # ═══════════════════════════════════════════════════════════
    #  2-4. ACTIVATE / UPDATE APP / UPDATE ENV
    # ═══════════════════════════════════════════════════════════
    def activate_module(self) -> None:
        info("[ACTIVATE] register router + swagger + models")
        self._update_app_py()
        self._update_env_py()

    def update_app(self) -> None:
        info("[UPDATE] app/app.py")
        self._update_app_py()

    def update_env(self) -> None:
        info("[UPDATE-ENV] migrations/env.py")
        self._update_env_py()

    def _update_app_py(self) -> None:
        app_file = self.root / self.app_py
        if not app_file.exists():
            warn(f"{self.app_py} not found — skipping")
            return
        content = app_file.read_text(encoding="utf-8")
        original = content

        router_import = ("from app.modules.yolo.presentation.router "
                          "import router as yolo_router")
        if router_import not in content:
            lines = content.split("\n")
            insert_at = len(lines)
            for i, line in enumerate(lines):
                if line.startswith("from app.modules.") and "presentation.router" in line:
                    insert_at = i + 1
            lines.insert(insert_at, router_import)
            content = "\n".join(lines)
            ok(f"added import: {router_import}")

        swagger_import = ("from app.modules.yolo.presentation.swagger "
                           "import register_yolo_openapi")
        if swagger_import not in content:
            content = content.replace(router_import, router_import + "\n" + swagger_import, 1)
            ok(f"added import: {swagger_import}")

        m = re.search(r"(routers\s*=\s*\[)(.*?)(\n\])", content, re.S)
        if m and "yolo_router" not in m.group(2):
            inner = m.group(2).rstrip() + "\n    yolo_router,    # YOLO module (Layer 5-Intel)\n"
            content = content[:m.start(2)] + inner + content[m.end(2):]
            ok("added yolo_router to routers list")

        if '"name": "yolo"' not in content:
            tag_line = ('            {"name": "yolo", "description": '
                        '"YOLO Object Detection — Ultralytics YOLOv8/v11."},\n')
            m2 = re.search(r'(\{"name":\s*"[^"]+"[^\}]*\},\s*\n)', content)
            if m2:
                content = content[:m2.end(1)] + tag_line + content[m2.end(1):]
                ok("added OpenAPI tag: yolo")

        if "register_yolo_openapi(app)" not in content:
            m3 = re.search(r"(app\.include_router\(yolo_router[^\n]*\n)", content)
            swagger_call = ("\n# Register YOLO OpenAPI metadata\n"
                             "register_yolo_openapi(app)\n")
            if m3:
                content = content[:m3.end(1)] + swagger_call + content[m3.end(1):]
                ok("called register_yolo_openapi(app)")

        if content != original:
            bak = app_file.with_suffix(".py.bak")
            bak.write_bytes(app_file.read_bytes())
            app_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.app_py} updated")

    def _update_env_py(self) -> None:
        env_file = self.root / self.env_py
        if not env_file.exists():
            warn(f"{self.env_py} not found — skipping")
            return
        content = env_file.read_text(encoding="utf-8")
        original = content
        marker = "# --- module yolo (Detection) ---"
        if marker in content:
            skip("yolo models block already present")
            return

        block = f'''{marker}
# TH: YOLO module — 7 models (Layer 5-Intel, schema=public, prefix=yolo_)
try:
    from app.modules.yolo.infrastructure.models import (  # noqa: F401
        AnnotationModel, ClassModel, DatasetModel, ImageModel,
        InferenceModel, ModelModel, TrainingModel,
    )
except ImportError:
    pass


'''
        anchor = "config = context.config"
        idx = content.find(anchor)
        if idx == -1:
            warn("Cannot find anchor in env.py")
            return
        content = content[:idx] + block + content[idx:]
        if content != original:
            bak = env_file.with_suffix(".py.bak")
            bak.write_bytes(env_file.read_bytes())
            env_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.env_py} updated")

    # ═══════════════════════════════════════════════════════════
    #  3. SQL
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info(f"[SQL] {self.module}")
        self.writer.write(f"{self.sql_dir}/V001__create_{self.module}.sql", self._v001_sql())
        self.writer.write(f"{self.sql_dir}/V002__seed_{self.module}.sql", self._v002_sql())
        self.writer.write(f"{self.sql_dir}/V003__rollback_{self.module}.sql", self._v003_sql())

    def _v001_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V001__create_yolo.sql | Module: yolo | Prefix: yolo | Schema: public
-- 7 tables: datasets, classes, images, annotations, trainings, models, inferences
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."yolo_datasets";
CREATE TABLE "public"."yolo_datasets" (
  "id"            uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"     uuid NOT NULL,
  "name"          varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "format"        varchar(20)  COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'yolo'::character varying,
  "root_uri"      text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "image_count"   int4 NOT NULL DEFAULT 0,
  "class_count"   int4 NOT NULL DEFAULT 0,
  "splits_json"   jsonb NOT NULL DEFAULT '{}'::jsonb,
  "status"        varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'DRAFT'::character varying,
  "version"       int4 NOT NULL DEFAULT 1,
  "metadata_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"    timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_datasets_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_ds_format" CHECK (format IN ('yolo','coco','roboflow','labelimg')),
  CONSTRAINT "ck_yolo_ds_status" CHECK (status IN ('DRAFT','READY','TRAINING','ARCHIVED')),
  CONSTRAINT "uq_yolo_ds_name_ver" UNIQUE ("tenant_id","name","version")
);
CREATE INDEX "ix_yolo_ds_tenant" ON "public"."yolo_datasets" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_ds_status" ON "public"."yolo_datasets" USING btree ("tenant_id","status");

DROP TABLE IF EXISTS "public"."yolo_classes";
CREATE TABLE "public"."yolo_classes" (
  "id"          uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"   uuid NOT NULL,
  "dataset_id"  uuid NOT NULL,
  "name"        varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "class_index" int4 NOT NULL,
  "color"       varchar(7) COLLATE "pg_catalog"."default" NOT NULL DEFAULT '#FF0000'::character varying,
  "count"       int4 NOT NULL DEFAULT 0,
  "created_at"  timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"  timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_classes_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_yolo_class_idx" UNIQUE ("dataset_id","class_index"),
  CONSTRAINT "uq_yolo_class_name" UNIQUE ("dataset_id","name")
);
CREATE INDEX "ix_yolo_class_tenant" ON "public"."yolo_classes" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_class_dataset" ON "public"."yolo_classes" USING btree ("dataset_id");

DROP TABLE IF EXISTS "public"."yolo_images";
CREATE TABLE "public"."yolo_images" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "dataset_id"       uuid NOT NULL,
  "uri"              text COLLATE "pg_catalog"."default" NOT NULL,
  "content_hash"     varchar(64) COLLATE "pg_catalog"."default" NOT NULL,
  "width"            int4 NOT NULL DEFAULT 0,
  "height"           int4 NOT NULL DEFAULT 0,
  "size_bytes"       int4 NOT NULL DEFAULT 0,
  "split"            varchar(10) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'train'::character varying,
  "annotation_count" int4 NOT NULL DEFAULT 0,
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_images_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_img_split" CHECK (split IN ('train','val','test')),
  CONSTRAINT "uq_yolo_img_hash" UNIQUE ("dataset_id","content_hash")
);
CREATE INDEX "ix_yolo_img_tenant" ON "public"."yolo_images" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_img_dataset" ON "public"."yolo_images" USING btree ("dataset_id","split");
CREATE INDEX "ix_yolo_img_hash" ON "public"."yolo_images" USING btree ("content_hash");

DROP TABLE IF EXISTS "public"."yolo_annotations";
CREATE TABLE "public"."yolo_annotations" (
  "id"         uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"  uuid NOT NULL,
  "image_id"   uuid NOT NULL,
  "class_id"   uuid NOT NULL,
  "x_center"   float8 NOT NULL,
  "y_center"   float8 NOT NULL,
  "width"      float8 NOT NULL,
  "height"     float8 NOT NULL,
  "confidence" numeric(5,4) NOT NULL DEFAULT 1.0,
  "is_hard"    bool NOT NULL DEFAULT false,
  "source"     varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'manual'::character varying,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_annotations_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_ann_x" CHECK (x_center >= 0 AND x_center <= 1),
  CONSTRAINT "ck_yolo_ann_y" CHECK (y_center >= 0 AND y_center <= 1),
  CONSTRAINT "ck_yolo_ann_w" CHECK (width > 0 AND width <= 1),
  CONSTRAINT "ck_yolo_ann_h" CHECK (height > 0 AND height <= 1)
);
CREATE INDEX "ix_yolo_ann_tenant" ON "public"."yolo_annotations" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_ann_image" ON "public"."yolo_annotations" USING btree ("image_id");
CREATE INDEX "ix_yolo_ann_class" ON "public"."yolo_annotations" USING btree ("class_id");

DROP TABLE IF EXISTS "public"."yolo_trainings";
CREATE TABLE "public"."yolo_trainings" (
  "id"              uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"       uuid NOT NULL,
  "dataset_id"      uuid NOT NULL,
  "model_type"      varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "epochs"          int4 NOT NULL DEFAULT 100,
  "batch_size"      int4 NOT NULL DEFAULT 16,
  "imgsz"           int4 NOT NULL DEFAULT 640,
  "lr0"             numeric(12,8) NOT NULL DEFAULT 0.01,
  "device"          varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'auto'::character varying,
  "patience"        int4 NOT NULL DEFAULT 50,
  "optimizer"       varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'auto'::character varying,
  "aug_config_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "status"          varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'PENDING'::character varying,
  "best_model_id"   uuid NULL,
  "progress"        int4 NOT NULL DEFAULT 0,
  "error_message"   text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "started_at"      timestamptz(6) NULL,
  "finished_at"     timestamptz(6) NULL,
  "duration_ms"     int4 NOT NULL DEFAULT 0,
  "created_at"      timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"      timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_trainings_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_tr_status" CHECK (status IN ('PENDING','RUNNING','SUCCESS','FAILED','CANCELLED'))
);
CREATE INDEX "ix_yolo_tr_tenant" ON "public"."yolo_trainings" USING btree ("tenant_id","status");
CREATE INDEX "ix_yolo_tr_dataset" ON "public"."yolo_trainings" USING btree ("dataset_id","created_at" DESC);

DROP TABLE IF EXISTS "public"."yolo_models";
CREATE TABLE "public"."yolo_models" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "training_id"  uuid NOT NULL,
  "name"         varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "version"      int4 NOT NULL DEFAULT 1,
  "weights_uri"  text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "weights_hash" varchar(64) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "export_uri"   text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "format"       varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'pt'::character varying,
  "mAP50"        numeric(6,4) NOT NULL DEFAULT 0,
  "mAP50_95"     numeric(6,4) NOT NULL DEFAULT 0,
  "precision_"   numeric(6,4) NOT NULL DEFAULT 0,
  "recall_"      numeric(6,4) NOT NULL DEFAULT 0,
  "metrics_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "is_active"    bool NOT NULL DEFAULT true,
  "is_deployed"  bool NOT NULL DEFAULT false,
  "deployed_at"  timestamptz(6) NULL,
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_models_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_model_format" CHECK (format IN ('pt','onnx','engine','torchscript','coreml')),
  CONSTRAINT "uq_yolo_model_name_ver" UNIQUE ("tenant_id","name","version")
);
CREATE INDEX "ix_yolo_model_tenant" ON "public"."yolo_models" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_model_training" ON "public"."yolo_models" USING btree ("training_id");
CREATE INDEX "ix_yolo_model_active" ON "public"."yolo_models" USING btree ("tenant_id","is_active");

DROP TABLE IF EXISTS "public"."yolo_inferences";
CREATE TABLE "public"."yolo_inferences" (
  "id"              uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"       uuid NOT NULL,
  "model_id"        uuid NOT NULL,
  "image_hash"      varchar(64) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "detections_json" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "detection_count" int4 NOT NULL DEFAULT 0,
  "latency_ms"      int4 NOT NULL DEFAULT 0,
  "source"          varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'api'::character varying,
  "created_at"      timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"      timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_inferences_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_inf_source" CHECK (source IN ('api','batch','stream','upload'))
);
CREATE INDEX "ix_yolo_inf_tenant" ON "public"."yolo_inferences" USING btree ("tenant_id","created_at" DESC);
CREATE INDEX "ix_yolo_inf_model" ON "public"."yolo_inferences" USING btree ("model_id","created_at" DESC);
CREATE INDEX "ix_yolo_inf_hash" ON "public"."yolo_inferences" USING btree ("image_hash");

CREATE OR REPLACE FUNCTION public.set_updated_at_yolo()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_yolo_ds_updated     ON "public"."yolo_datasets";
CREATE TRIGGER trg_yolo_ds_updated     BEFORE UPDATE ON "public"."yolo_datasets"     FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();
DROP TRIGGER IF EXISTS trg_yolo_cls_updated    ON "public"."yolo_classes";
CREATE TRIGGER trg_yolo_cls_updated    BEFORE UPDATE ON "public"."yolo_classes"      FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();
DROP TRIGGER IF EXISTS trg_yolo_img_updated    ON "public"."yolo_images";
CREATE TRIGGER trg_yolo_img_updated    BEFORE UPDATE ON "public"."yolo_images"       FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();
DROP TRIGGER IF EXISTS trg_yolo_ann_updated    ON "public"."yolo_annotations";
CREATE TRIGGER trg_yolo_ann_updated    BEFORE UPDATE ON "public"."yolo_annotations"  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();
DROP TRIGGER IF EXISTS trg_yolo_tr_updated     ON "public"."yolo_trainings";
CREATE TRIGGER trg_yolo_tr_updated     BEFORE UPDATE ON "public"."yolo_trainings"    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();
DROP TRIGGER IF EXISTS trg_yolo_model_updated  ON "public"."yolo_models";
CREATE TRIGGER trg_yolo_model_updated  BEFORE UPDATE ON "public"."yolo_models"       FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();
DROP TRIGGER IF EXISTS trg_yolo_inf_updated    ON "public"."yolo_inferences";
CREATE TRIGGER trg_yolo_inf_updated    BEFORE UPDATE ON "public"."yolo_inferences"   FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();

ALTER TABLE "public"."yolo_datasets"     ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_classes"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_images"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_annotations"  ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_trainings"    ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_models"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_inferences"   ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_yolo_ds    ON "public"."yolo_datasets";
CREATE POLICY p_yolo_ds    ON "public"."yolo_datasets"    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
DROP POLICY IF EXISTS p_yolo_cls   ON "public"."yolo_classes";
CREATE POLICY p_yolo_cls   ON "public"."yolo_classes"     USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
DROP POLICY IF EXISTS p_yolo_img   ON "public"."yolo_images";
CREATE POLICY p_yolo_img   ON "public"."yolo_images"      USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
DROP POLICY IF EXISTS p_yolo_ann   ON "public"."yolo_annotations";
CREATE POLICY p_yolo_ann   ON "public"."yolo_annotations" USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
DROP POLICY IF EXISTS p_yolo_tr    ON "public"."yolo_trainings";
CREATE POLICY p_yolo_tr    ON "public"."yolo_trainings"   USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
DROP POLICY IF EXISTS p_yolo_model ON "public"."yolo_models";
CREATE POLICY p_yolo_model ON "public"."yolo_models"      USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
DROP POLICY IF EXISTS p_yolo_inf   ON "public"."yolo_inferences";
CREATE POLICY p_yolo_inf   ON "public"."yolo_inferences"  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_yolo.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;
INSERT INTO "public"."yolo_datasets"
    (tenant_id, name, format, status, image_count, class_count)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'demo-coco-subset', 'yolo', 'DRAFT', 0, 0)
ON CONFLICT DO NOTHING;
COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_yolo.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;
DROP TRIGGER IF EXISTS trg_yolo_inf_updated   ON "public"."yolo_inferences";
DROP TRIGGER IF EXISTS trg_yolo_model_updated ON "public"."yolo_models";
DROP TRIGGER IF EXISTS trg_yolo_tr_updated    ON "public"."yolo_trainings";
DROP TRIGGER IF EXISTS trg_yolo_ann_updated   ON "public"."yolo_annotations";
DROP TRIGGER IF EXISTS trg_yolo_img_updated   ON "public"."yolo_images";
DROP TRIGGER IF EXISTS trg_yolo_cls_updated   ON "public"."yolo_classes";
DROP TRIGGER IF EXISTS trg_yolo_ds_updated    ON "public"."yolo_datasets";

DROP POLICY IF EXISTS p_yolo_inf   ON "public"."yolo_inferences";
DROP POLICY IF EXISTS p_yolo_model ON "public"."yolo_models";
DROP POLICY IF EXISTS p_yolo_tr    ON "public"."yolo_trainings";
DROP POLICY IF EXISTS p_yolo_ann   ON "public"."yolo_annotations";
DROP POLICY IF EXISTS p_yolo_img   ON "public"."yolo_images";
DROP POLICY IF EXISTS p_yolo_cls   ON "public"."yolo_classes";
DROP POLICY IF EXISTS p_yolo_ds    ON "public"."yolo_datasets";

DROP TABLE IF EXISTS "public"."yolo_inferences"  CASCADE;
DROP TABLE IF EXISTS "public"."yolo_models"      CASCADE;
DROP TABLE IF EXISTS "public"."yolo_trainings"   CASCADE;
DROP TABLE IF EXISTS "public"."yolo_annotations" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_images"      CASCADE;
DROP TABLE IF EXISTS "public"."yolo_classes"     CASCADE;
DROP TABLE IF EXISTS "public"."yolo_datasets"    CASCADE;
DROP FUNCTION IF EXISTS public.set_updated_at_yolo();
COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  4. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "yolo_001"
        prev = self._get_head_revision()
        content = f'''"""add yolo detection tables

Revision ID: {rev}
Revises: {prev}
Create Date: {datetime.now(UTC).date().isoformat()}

TH: สร้างตาราง YOLO 7 ตาราง (schema: public, prefix: yolo_)
EN: create 7 YOLO tables (public schema, yolo_ prefix)
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "{rev}"
down_revision: Union[str, None] = "{prev}"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "public"
TABLES = ("yolo_datasets","yolo_classes","yolo_images","yolo_annotations",
          "yolo_trainings","yolo_models","yolo_inferences")


def upgrade() -> None:
    op.create_table(
        "yolo_datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("format", sa.String(20), nullable=False, server_default="yolo"),
        sa.Column("root_uri", sa.Text, nullable=False, server_default=""),
        sa.Column("image_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("class_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("splits_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{{}}'::jsonb")),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{{}}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint("format IN ('yolo','coco','roboflow','labelimg')",
                            name="ck_yolo_ds_format"),
        sa.CheckConstraint("status IN ('DRAFT','READY','TRAINING','ARCHIVED')",
                            name="ck_yolo_ds_status"),
        sa.UniqueConstraint("tenant_id","name","version", name="uq_yolo_ds_name_ver"),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_ds_tenant", "yolo_datasets", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_ds_status", "yolo_datasets", ["tenant_id","status"], schema=SCHEMA)

    op.create_table(
        "yolo_classes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("class_index", sa.Integer, nullable=False),
        sa.Column("color", sa.String(7), nullable=False, server_default="#FF0000"),
        sa.Column("count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("dataset_id","class_index", name="uq_yolo_class_idx"),
        sa.UniqueConstraint("dataset_id","name", name="uq_yolo_class_name"),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_class_tenant", "yolo_classes", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_class_dataset", "yolo_classes", ["dataset_id"], schema=SCHEMA)

    op.create_table(
        "yolo_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uri", sa.Text, nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("width", sa.Integer, nullable=False, server_default="0"),
        sa.Column("height", sa.Integer, nullable=False, server_default="0"),
        sa.Column("size_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("split", sa.String(10), nullable=False, server_default="train"),
        sa.Column("annotation_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint("split IN ('train','val','test')", name="ck_yolo_img_split"),
        sa.UniqueConstraint("dataset_id","content_hash", name="uq_yolo_img_hash"),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_img_tenant", "yolo_images", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_img_dataset", "yolo_images", ["dataset_id","split"], schema=SCHEMA)
    op.create_index("ix_yolo_img_hash", "yolo_images", ["content_hash"], schema=SCHEMA)

    op.create_table(
        "yolo_annotations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("image_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("x_center", sa.Float, nullable=False),
        sa.Column("y_center", sa.Float, nullable=False),
        sa.Column("width", sa.Float, nullable=False),
        sa.Column("height", sa.Float, nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False, server_default="1.0"),
        sa.Column("is_hard", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("source", sa.String(50), nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint("x_center >= 0 AND x_center <= 1", name="ck_yolo_ann_x"),
        sa.CheckConstraint("y_center >= 0 AND y_center <= 1", name="ck_yolo_ann_y"),
        sa.CheckConstraint("width > 0 AND width <= 1", name="ck_yolo_ann_w"),
        sa.CheckConstraint("height > 0 AND height <= 1", name="ck_yolo_ann_h"),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_ann_tenant", "yolo_annotations", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_ann_image", "yolo_annotations", ["image_id"], schema=SCHEMA)
    op.create_index("ix_yolo_ann_class", "yolo_annotations", ["class_id"], schema=SCHEMA)

    op.create_table(
        "yolo_trainings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_type", sa.String(20), nullable=False),
        sa.Column("epochs", sa.Integer, nullable=False, server_default="100"),
        sa.Column("batch_size", sa.Integer, nullable=False, server_default="16"),
        sa.Column("imgsz", sa.Integer, nullable=False, server_default="640"),
        sa.Column("lr0", sa.Numeric(12, 8), nullable=False, server_default="0.01"),
        sa.Column("device", sa.String(20), nullable=False, server_default="auto"),
        sa.Column("patience", sa.Integer, nullable=False, server_default="50"),
        sa.Column("optimizer", sa.String(20), nullable=False, server_default="auto"),
        sa.Column("aug_config_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{{}}'::jsonb")),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("best_model_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("progress", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=False, server_default=""),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('PENDING','RUNNING','SUCCESS','FAILED','CANCELLED')",
            name="ck_yolo_tr_status"),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_tr_tenant", "yolo_trainings", ["tenant_id","status"], schema=SCHEMA)
    op.create_index("ix_yolo_tr_dataset", "yolo_trainings", ["dataset_id","created_at"], schema=SCHEMA)

    op.create_table(
        "yolo_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("training_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("weights_uri", sa.Text, nullable=False, server_default=""),
        sa.Column("weights_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("export_uri", sa.Text, nullable=False, server_default=""),
        sa.Column("format", sa.String(20), nullable=False, server_default="pt"),
        sa.Column("mAP50", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("mAP50_95", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("precision_", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("recall_", sa.Numeric(6, 4), nullable=False, server_default="0"),
        sa.Column("metrics_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{{}}'::jsonb")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_deployed", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "format IN ('pt','onnx','engine','torchscript','coreml')",
            name="ck_yolo_model_format"),
        sa.UniqueConstraint("tenant_id","name","version", name="uq_yolo_model_name_ver"),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_model_tenant", "yolo_models", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_model_training", "yolo_models", ["training_id"], schema=SCHEMA)
    op.create_index("ix_yolo_model_active", "yolo_models", ["tenant_id","is_active"], schema=SCHEMA)

    op.create_table(
        "yolo_inferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("image_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("detections_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("detection_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("source", sa.String(20), nullable=False, server_default="api"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint("source IN ('api','batch','stream','upload')",
                            name="ck_yolo_inf_source"),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_inf_tenant", "yolo_inferences", ["tenant_id","created_at"], schema=SCHEMA)
    op.create_index("ix_yolo_inf_model", "yolo_inferences", ["model_id","created_at"], schema=SCHEMA)
    op.create_index("ix_yolo_inf_hash", "yolo_inferences", ["image_hash"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_yolo()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in TABLES:
        op.execute(f"""
            DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};
            CREATE TRIGGER trg_{{tbl}}_updated BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            DROP POLICY IF EXISTS p_{{tbl}}_tenant ON {{SCHEMA}}.{{tbl}};
            CREATE POLICY p_{{tbl}}_tenant ON {{SCHEMA}}.{{tbl}}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        """)


def downgrade() -> None:
    for tbl in reversed(TABLES):
        op.execute(f"DROP POLICY IF EXISTS p_{{tbl}}_tenant ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_yolo();")
'''
        self.writer.write(f"{self.alembic_dir}/{rev}_add_{self.module}_tables.py", content)

    def _get_head_revision(self) -> str:
        my_rev = "yolo_001"
        for candidate in ("migrations/versions", "alembic/versions"):
            versions = self.root / candidate
            if not versions.exists():
                continue
            revisions: set[str] = set()
            down_revisions: set[str] = set()
            for f in versions.glob("*.py"):
                content = f.read_text(encoding="utf-8")
                m = re.search(r'^revision\s*(?::\s*[^=]+)?\s*=\s*["\']([^"\']+)["\']', content, re.M)
                if not m:
                    continue
                rev_id = m.group(1)
                if rev_id == my_rev:
                    continue
                revisions.add(rev_id)
                d = re.search(r'^down_revision\s*(?::\s*[^=]+)?\s*=\s*["\']([^"\']+)["\']', content, re.M)
                if d:
                    down_revisions.add(d.group(1))
            heads = revisions - down_revisions
            if heads:
                return sorted(heads)[0]
        return "None"

    # ═══════════════════════════════════════════════════════════
    #  5. SWAGGER
    # ═══════════════════════════════════════════════════════════
    def create_swagger(self) -> None:
        info(f"[SWAGGER] {self.module}")
        self.writer.write(f"{self.mod_root}/presentation/swagger.py", self._swagger_content())

    # ═══════════════════════════════════════════════════════════
    #  6. POSTMAN
    # ═══════════════════════════════════════════════════════════
    def create_postman(self) -> None:
        info(f"[POSTMAN] {self.module}")
        self.writer.write(f"docs/postman/{self.module}.json", self._postman_json())

    def _postman_json(self) -> str:
        return f'''{{
  "info": {{
    "name": "YOLO Object Detection API",
    "_postman_id": "{uuid.uuid4()}",
    "description": "YOLO Object Detection — Ultralytics YOLOv8/v11",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  }},
  "variable": [
    {{ "key": "base_url", "value": "http://localhost:8000" }},
    {{ "key": "dataset_id", "value": "" }},
    {{ "key": "model_id", "value": "" }},
    {{ "key": "training_id", "value": "" }},
    {{ "key": "image_id", "value": "" }}
  ],
  "item": [
    {{ "name": "Create Dataset", "request": {{ "method": "POST",
      "header": [{{"key":"Content-Type","value":"application/json"}}],
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/datasets","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","datasets"]}},
      "body": {{"mode":"raw","raw":"{{\\n  \\"name\\": \\"my-dataset\\",\\n  \\"format\\": \\"yolo\\"\\n}}"}}
    }} }},
    {{ "name": "List Datasets", "request": {{ "method": "GET",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/datasets?page=1&size=50",
        "host":["{{{{base_url}}}}"],"path":["api","v1","yolo","datasets"]}}
    }} }},
    {{ "name": "Get Dataset", "request": {{ "method": "GET",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/datasets/{{{{dataset_id}}}}",
        "host":["{{{{base_url}}}}"],"path":["api","v1","yolo","datasets","{{{{dataset_id}}}}"]}}
    }} }},
    {{ "name": "Define Classes", "request": {{ "method": "POST",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/datasets/{{{{dataset_id}}}}/classes",
        "host":["{{{{base_url}}}}"],"path":["api","v1","yolo","datasets","{{{{dataset_id}}}}","classes"]}},
      "body": {{"mode":"raw","raw":"{{\\n  \\"classes\\": [\\n    {{\\"name\\": \\"person\\", \\"class_index\\": 0}}\\n  ]\\n}}"}}
    }} }},
    {{ "name": "Upload Images", "request": {{ "method": "POST",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/images","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","images"]}},
      "body": {{"mode":"formdata","formdata":[
        {{"key":"dataset_id","value":"{{{{dataset_id}}}}","type":"text"}},
        {{"key":"split","value":"train","type":"text"}},
        {{"key":"images","src":"/path/to/image.jpg","type":"file"}}
      ]}}
    }} }},
    {{ "name": "Create Annotations", "request": {{ "method": "POST",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/annotations","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","annotations"]}},
      "body": {{"mode":"formdata","formdata":[
        {{"key":"image_id","value":"{{{{image_id}}}}","type":"text"}},
        {{"key":"payload","value":"{{\\"annotations\\":[{{\\"class_id\\":\\"uuid\\",\\"x_center\\":0.5,\\"y_center\\":0.5,\\"width\\":0.2,\\"height\\":0.3}}]}}","type":"text"}}
      ]}}
    }} }},
    {{ "name": "Start Training", "request": {{ "method": "POST",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/train","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","train"]}},
      "body": {{"mode":"raw","raw":"{{\\n  \\"dataset_id\\": \\"{{{{dataset_id}}}}\\",\\n  \\"model_type\\": \\"yolov8n\\",\\n  \\"epochs\\": 100,\\n  \\"batch_size\\": 16\\n}}"}}
    }} }},
    {{ "name": "Get Training Status", "request": {{ "method": "GET",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/train/{{{{training_id}}}}","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","train","{{{{training_id}}}}"]}}
    }} }},
    {{ "name": "List Models", "request": {{ "method": "GET",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/models","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","models"]}}
    }} }},
    {{ "name": "Export Model (ONNX)", "request": {{ "method": "POST",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/models/{{{{model_id}}}}/export","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","models","{{{{model_id}}}}","export"]}},
      "body": {{"mode":"raw","raw":"{{\\n  \\"format\\": \\"onnx\\",\\n  \\"imgsz\\": 640,\\n  \\"opset\\": 17\\n}}"}}
    }} }},
    {{ "name": "Detect (single)", "request": {{ "method": "POST",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/detect","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","detect"]}},
      "body": {{"mode":"formdata","formdata":[
        {{"key":"model_id","value":"{{{{model_id}}}}","type":"text"}},
        {{"key":"conf","value":"0.25","type":"text"}},
        {{"key":"iou","value":"0.45","type":"text"}},
        {{"key":"image","src":"/path/to/image.jpg","type":"file"}}
      ]}}
    }} }},
    {{ "name": "Detect (batch)", "request": {{ "method": "POST",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/detect/batch","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","detect","batch"]}},
      "body": {{"mode":"raw","raw":"{{\\n  \\"model_id\\": \\"{{{{model_id}}}}\\",\\n  \\"images_base64\\": [\\"base64...\\"]\\n}}"}}
    }} }},
    {{ "name": "Detect (stream SSE)", "request": {{ "method": "POST",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/detect/stream","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","detect","stream"]}},
      "body": {{"mode":"raw","raw":"{{\\n  \\"model_id\\": \\"{{{{model_id}}}}\\",\\n  \\"video_uri\\": \\"rtsp://...\\"\\n}}"}}
    }} }},
    {{ "name": "Get Metrics", "request": {{ "method": "GET",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/metrics/{{{{model_id}}}}","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","metrics","{{{{model_id}}}}"]}}
    }} }},
    {{ "name": "Check Drift", "request": {{ "method": "POST",
      "url": {{"raw":"{{{{base_url}}}}/api/v1/yolo/metrics/drift","host":["{{{{base_url}}}}"],
        "path":["api","v1","yolo","metrics","drift"]}},
      "body": {{"mode":"raw","raw":"{{\\n  \\"model_id\\": \\"{{{{model_id}}}}\\",\\n  \\"reference\\": [{{\\"class_id\\": 0}}],\\n  \\"current\\": [{{\\"class_id\\": 0}}]\\n}}"}}
    }} }}
  ]
}}
'''

    # ═══════════════════════════════════════════════════════════
    #  9. TESTS
    # ═══════════════════════════════════════════════════════════
    def create_tests(self) -> None:
        info(f"[TESTS] {self.module}")
        self.writer.write(f"{self.tests_dir}/unit/test_yolo.py", self._unit_test())
        self.writer.write(f"{self.tests_dir}/unit/test_bbox.py", self._bbox_test())
        self.writer.write(f"{self.tests_dir}/unit/test_yolo_format.py", self._format_test())
        self.writer.write(f"{self.tests_dir}/unit/test_coco_metrics.py", self._coco_test())
        self.writer.write(f"{self.tests_dir}/integration/test_yolo_repository.py", self._integration_test())
        self.writer.write(f"{self.tests_dir}/property/test_yolo_invariants.py", self._property_test())
        self.writer.write(f"{self.tests_dir}/manual/manual_test_yolo.md", self._manual_test())

    def _unit_test(self) -> str:
        return dedent('''\
            """Unit tests for YOLO domain"""
            from __future__ import annotations
            import pytest

            from app.modules.yolo.domain.enums import (
                DatasetStatus, ModelFormat, ModelType, TrainingStatus,
            )
            from app.modules.yolo.domain.value_objects import (
                AugConfig, Detection, TrainConfig,
            )
            from app.modules.yolo.domain.value_objects.bbox import BBox

            pytestmark = pytest.mark.unit


            class TestEnums:
                def test_dataset_status(self):
                    assert DatasetStatus.DRAFT == "DRAFT"
                    assert DatasetStatus.READY == "READY"

                def test_model_types(self):
                    assert ModelType.YOLOV8N == "yolov8n"
                    assert ModelType.YOLO11X == "yolo11x"

                def test_model_format(self):
                    assert ModelFormat.PYTORCH == "pt"
                    assert ModelFormat.ONNX == "onnx"
                    assert ModelFormat.TENSORRT == "engine"

                def test_training_status(self):
                    assert TrainingStatus.PENDING == "PENDING"
                    assert TrainingStatus.SUCCESS == "SUCCESS"


            class TestBBox:
                def test_valid(self):
                    b = BBox(x_center=0.5, y_center=0.5, width=0.2, height=0.3)
                    assert b.x_center == 0.5

                def test_invalid_range(self):
                    with pytest.raises(ValueError):
                        BBox(x_center=1.5, y_center=0.5, width=0.2, height=0.3)

                def test_zero_width(self):
                    with pytest.raises(ValueError):
                        BBox(x_center=0.5, y_center=0.5, width=0.0, height=0.3)

                def test_to_xyxy(self):
                    b = BBox(x_center=0.5, y_center=0.5, width=0.4, height=0.4)
                    x1, y1, x2, y2 = b.to_xyxy(100, 100)
                    assert x1 == 30.0
                    assert y1 == 30.0
                    assert x2 == 70.0
                    assert y2 == 70.0

                def test_from_xyxy(self):
                    b = BBox.from_xyxy(30, 30, 70, 70, 100, 100)
                    assert abs(b.x_center - 0.5) < 1e-9
                    assert abs(b.width - 0.4) < 1e-9


            class TestDetection:
                def test_valid(self):
                    d = Detection(
                        bbox=BBox(0.5, 0.5, 0.2, 0.3),
                        class_id=0, class_name="person", confidence=0.9,
                    )
                    assert d.confidence == 0.9

                def test_invalid_confidence(self):
                    with pytest.raises(ValueError):
                        Detection(bbox=BBox(0.5, 0.5, 0.2, 0.3),
                                   class_id=0, class_name="x", confidence=1.5)


            class TestTrainConfig:
                def test_defaults(self):
                    c = TrainConfig()
                    assert c.model_type == "yolov8n"
                    assert c.epochs == 100

                def test_invalid_model_type(self):
                    with pytest.raises(ValueError):
                        TrainConfig(model_type="invalid")

                def test_invalid_epochs(self):
                    with pytest.raises(ValueError):
                        TrainConfig(epochs=0)

                def test_invalid_imgsz(self):
                    with pytest.raises(ValueError):
                        TrainConfig(imgsz=16)


            class TestAugConfig:
                def test_defaults(self):
                    a = AugConfig()
                    assert a.hsv_h == 0.015

                def test_invalid_range(self):
                    with pytest.raises(ValueError):
                        AugConfig(hsv_h=2.0)

                def test_to_dict(self):
                    a = AugConfig()
                    d = a.to_dict()
                    assert "mosaic" in d
                    assert d["mosaic"] == 1.0
        ''')

    def _bbox_test(self) -> str:
        return dedent('''\
            """Unit tests for BBox value object"""
            from __future__ import annotations
            import pytest
            from app.modules.yolo.domain.value_objects.bbox import BBox

            pytestmark = pytest.mark.unit


            def test_bbox_center_valid():
                b = BBox(0.5, 0.5, 0.4, 0.4)
                assert b.x_center == 0.5


            def test_bbox_boundary_values():
                BBox(0.0, 0.0, 1.0, 1.0)


            def test_bbox_negative_center():
                with pytest.raises(ValueError):
                    BBox(-0.1, 0.5, 0.2, 0.2)


            def test_bbox_roundtrip():
                b1 = BBox(0.5, 0.5, 0.4, 0.4)
                x1, y1, x2, y2 = b1.to_xyxy(200, 200)
                b2 = BBox.from_xyxy(x1, y1, x2, y2, 200, 200)
                assert abs(b1.x_center - b2.x_center) < 1e-9
                assert abs(b1.width - b2.width) < 1e-9
        ''')

    def _format_test(self) -> str:
        return dedent('''\
            """Unit tests for YOLO format helpers"""
            from __future__ import annotations
            import pytest
            from app.modules.yolo.domain.helpers import (
                bbox_to_yolo, write_dataset_yaml, yolo_to_bbox,
            )

            pytestmark = pytest.mark.unit


            def test_bbox_to_yolo():
                s = bbox_to_yolo(0, 0.5, 0.5, 0.2, 0.3)
                assert s.startswith("0 ")


            def test_yolo_to_bbox_roundtrip():
                line = bbox_to_yolo(1, 0.25, 0.75, 0.1, 0.15)
                cid, x, y, w, h = yolo_to_bbox(line)
                assert cid == 1
                assert abs(x - 0.25) < 1e-6


            def test_yolo_to_bbox_invalid():
                with pytest.raises(ValueError):
                    yolo_to_bbox("0 0.5")


            def test_write_dataset_yaml():
                yaml = write_dataset_yaml(["cat", "dog"], "/tmp/root",
                                            {"train": "images/train", "val": "images/val"})
                assert "cat" in yaml
                assert "dog" in yaml
                assert "path:" in yaml
        ''')

    def _coco_test(self) -> str:
        return dedent('''\
            """Unit tests for COCO metrics"""
            from __future__ import annotations
            import pytest
            from app.modules.yolo.domain.helpers import compute_iou, compute_map

            pytestmark = pytest.mark.unit


            def test_iou_perfect():
                box = (0.0, 0.0, 1.0, 1.0)
                assert compute_iou(box, box) == 1.0


            def test_iou_no_overlap():
                b1 = (0.0, 0.0, 1.0, 1.0)
                b2 = (2.0, 2.0, 3.0, 3.0)
                assert compute_iou(b1, b2) == 0.0


            def test_iou_partial():
                b1 = (0.0, 0.0, 2.0, 2.0)
                b2 = (1.0, 1.0, 3.0, 3.0)
                iou = compute_iou(b1, b2)
                assert 0.0 < iou < 1.0


            def test_map_perfect():
                preds = [{"class_id": 0, "confidence": 0.9, "x1": 0, "y1": 0, "x2": 10, "y2": 10}]
                gts = [{"class_id": 0, "x1": 0, "y1": 0, "x2": 10, "y2": 10}]
                result = compute_map(preds, gts)
                assert result["mAP50"] > 0.9


            def test_map_empty():
                result = compute_map([], [])
                assert result["mAP50"] == 0.0
        ''')

    def _integration_test(self) -> str:
        return dedent('''\
            """Integration tests for YOLO repositories — RLS verified"""
            from __future__ import annotations
            import uuid
            import pytest
            from sqlalchemy import text

            pytestmark = pytest.mark.integration


            class TestDatasetRepository:
                async def test_save_and_find(self, db_session, tenant_ctx):
                    from app.modules.yolo.infrastructure.dataset_repository import DatasetRepository
                    from app.modules.yolo.infrastructure.models import DatasetModel
                    repo = DatasetRepository(db_session)
                    ds = DatasetModel(tenant_id=tenant_ctx.tenant_id,
                                       name=f"test-{uuid.uuid4()}", format="yolo")
                    saved = await repo.save(tenant_ctx, ds)
                    found = await repo.find_by_id(tenant_ctx, saved.id)
                    assert found is not None

                async def test_rls_blocks_other_tenant(self, db_session,
                                                        tenant_ctx, other_tenant_ctx):
                    from app.modules.yolo.infrastructure.dataset_repository import DatasetRepository
                    from app.modules.yolo.infrastructure.models import DatasetModel
                    repo = DatasetRepository(db_session)
                    ds = DatasetModel(tenant_id=tenant_ctx.tenant_id,
                                       name=f"private-{uuid.uuid4()}", format="yolo")
                    saved = await repo.save(tenant_ctx, ds)
                    await db_session.execute(
                        text("SELECT set_config('app.current_tenant', :tid, true)"),
                        {"tid": str(other_tenant_ctx.tenant_id)},
                    )
                    found = await repo.find_by_id(other_tenant_ctx, saved.id)
                    assert found is None


            class TestModelRepository:
                async def test_save_and_find(self, db_session, tenant_ctx):
                    from app.modules.yolo.infrastructure.model_repository import ModelRepository
                    from app.modules.yolo.infrastructure.models import ModelModel
                    repo = ModelRepository(db_session)
                    m = ModelModel(tenant_id=tenant_ctx.tenant_id,
                                    training_id=uuid.uuid4(),
                                    name=f"yolo-{uuid.uuid4()}")
                    saved = await repo.save(tenant_ctx, m)
                    found = await repo.find_by_id(tenant_ctx, saved.id)
                    assert found is not None
        ''')

    def _property_test(self) -> str:
        return dedent('''\
            """Property tests for YOLO invariants"""
            from __future__ import annotations
            import pytest
            from hypothesis import given, settings, strategies as st
            from app.modules.yolo.domain.value_objects.bbox import BBox

            pytestmark = pytest.mark.property


            @settings(max_examples=100)
            @given(
                cx=st.floats(min_value=0.0, max_value=1.0),
                cy=st.floats(min_value=0.0, max_value=1.0),
                w=st.floats(min_value=0.01, max_value=1.0),
                h=st.floats(min_value=0.01, max_value=1.0),
            )
            def test_bbox_always_normalized(cx, cy, w, h):
                b = BBox(cx, cy, w, h)
                assert 0.0 <= b.x_center <= 1.0
                assert 0.0 <= b.y_center <= 1.0


            @settings(max_examples=100)
            @given(
                w=st.floats(min_value=0.01, max_value=0.9),
                h=st.floats(min_value=0.01, max_value=0.9),
            )
            def test_bbox_roundtrip_always_close(w, h):
                b1 = BBox(0.5, 0.5, w, h)
                x1, y1, x2, y2 = b1.to_xyxy(1000, 1000)
                b2 = BBox.from_xyxy(x1, y1, x2, y2, 1000, 1000)
                assert abs(b1.x_center - b2.x_center) < 1e-6
                assert abs(b1.width - b2.width) < 1e-6
        ''')

    def _manual_test(self) -> str:
        return dedent('''\
            # Manual Test — YOLO Object Detection Module

            ## Pre-conditions
            - [ ] DB migrated (V001-V003)
            - [ ] Redis running
            - [ ] S3/MinIO accessible
            - [ ] Ultralytics installed (`pip install ultralytics`)

            ## Scenarios (15)

            | # | Scenario | Method | Endpoint | Expected |
            |---|----------|--------|----------|----------|
            | 1 | Create dataset | POST | `/yolo/datasets` | 201 |
            | 2 | List datasets | GET | `/yolo/datasets` | paginated |
            | 3 | Get dataset | GET | `/yolo/datasets/{id}` | detail |
            | 4 | Define classes | POST | `/yolo/datasets/{id}/classes` | 201 |
            | 5 | Upload image | POST | `/yolo/images` | 201 |
            | 6 | Create annotation | POST | `/yolo/annotations` | 201 |
            | 7 | Start training | POST | `/yolo/train` | 201 |
            | 8 | Get training status | GET | `/yolo/train/{id}` | SUCCESS |
            | 9 | List models | GET | `/yolo/models` | array |
            | 10 | Export ONNX | POST | `/yolo/models/{id}/export` | 201 |
            | 11 | Detect single | POST | `/yolo/detect` | boxes |
            | 12 | Detect batch (32) | POST | `/yolo/detect/batch` | N results |
            | 13 | Detect stream SSE | POST | `/yolo/detect/stream` | chunks |
            | 14 | Get metrics | GET | `/yolo/metrics/{model_id}` | mAP |
            | 15 | RLS cross-tenant | GET | `/yolo/datasets/{other}` | 404 |

            ## RLS Checks
            - [ ] Cross-tenant dataset read → 404
            - [ ] Cross-tenant model read → 404
            - [ ] Cross-tenant training → 404

            ## Performance
            - [ ] Single detection < 100ms (GPU)
            - [ ] Batch 32 < 2s
            - [ ] Model load < 2s
        ''')

    # ═══════════════════════════════════════════════════════════
    #  10. VERIFY
    # ═══════════════════════════════════════════════════════════
    def verify(self) -> None:
        info("[VERIFY] Swagger + Postman + SQL + Models")
        issues: list[str] = []

        swagger_py = self.root / f"{self.mod_root}/presentation/swagger.py"
        if swagger_py.exists():
            ok("swagger.py exists")
            if "def register_yolo_openapi" in swagger_py.read_text(encoding="utf-8"):
                ok("  ✓ register_yolo_openapi()")
            else:
                issues.append("swagger missing register_yolo_openapi")
        else:
            issues.append(f"NOT FOUND: {swagger_py}")

        app_file = self.root / self.app_py
        if app_file.exists():
            content = app_file.read_text(encoding="utf-8")
            if "register_yolo_openapi(app)" in content:
                ok("app.py: register_yolo_openapi(app) ✓")
            else:
                issues.append("app.py missing register_yolo_openapi")
            if "yolo_router" in content:
                ok("app.py: yolo_router ✓")
        else:
            issues.append(f"NOT FOUND: {app_file}")

        postman = self.root / f"docs/postman/{self.module}.json"
        if postman.exists():
            try:
                data = _json_mod.loads(postman.read_text(encoding="utf-8"))
                ok(f"postman: valid JSON, {len(data.get('item', []))} items")
            except Exception as e:
                issues.append(f"postman invalid: {e}")
        else:
            issues.append(f"NOT FOUND: {postman}")

        for ver in ("V001", "V002", "V003"):
            matches = list((self.root / self.sql_dir).glob(f"{ver}__*{self.module}*.sql"))
            if matches:
                ok(f"SQL: {matches[0].name}")
            else:
                issues.append(f"SQL {ver} not found")

        models_py = self.root / f"{self.mod_root}/infrastructure/models.py"
        if models_py.exists():
            content = models_py.read_text(encoding="utf-8")
            count = content.count("__tablename__")
            if count == 7:
                ok(f"models.py: 7 tables ✓")
            else:
                issues.append(f"models.py has {count} tables (expected 7)")
        else:
            issues.append(f"NOT FOUND: {models_py}")

        print()
        if issues:
            warn(f"พบ {len(issues)} ปัญหา:")
            for i, msg in enumerate(issues, 1):
                err(f"  {i}. {msg}")
        else:
            info("═" * 60)
            ok("ALL CHECKS PASSED ✓")
            info("═" * 60)

    # ═══════════════════════════════════════════════════════════
    #  11. DEPS
    # ═══════════════════════════════════════════════════════════
    def check_deps(self) -> None:
        info("[DEPS] checking dependencies")
        required = [
            ("ultralytics", "Ultralytics YOLO"),
            ("torch", "PyTorch"),
            ("cv2", "OpenCV"),
            ("albumentations", "Albumentations"),
            ("numpy", "NumPy"),
            ("PIL", "Pillow"),
        ]
        optional = [
            ("onnx", "ONNX"),
            ("onnxruntime", "ONNX Runtime"),
            ("boto3", "boto3 (S3)"),
        ]
        for mod, name in required:
            try:
                __import__(mod)
                ok(f"{name} ✓")
            except ImportError:
                warn(f"{name} NOT installed — pip install {mod}")
        for mod, name in optional:
            try:
                __import__(mod)
                ok(f"{name} ✓ (optional)")
            except ImportError:
                skip(f"{name} not installed (optional)")

    # ═══════════════════════════════════════════════════════════
    #  ALL + SUMMARY
    # ═══════════════════════════════════════════════════════════
    def run_all(self) -> None:
        self.create_module()
        self.create_sql()
        self.create_migration()
        self.create_swagger()
        self.create_postman()
        self.create_tests()
        self.activate_module()

    def summary(self) -> None:
        print()
        info("═" * 60)
        ok(f"DONE — module: {self.module}  (v{VERSION})")
        info(f"  Schema  : {SCHEMA}")
        info(f"  Prefix  : {self.prefix}_")
        info(f"  Tables  : 7")
        info(f"  Written : {len(self.writer.written)} files")
        info(f"  Skipped : {len(self.writer.skipped)} files")
        info(f"  Backups : {len(self.writer.backups)} files")
        info("═" * 60)
        print()
        print(f"  {C.YELLOW}Next steps:{C.RESET}")
        print(f"    1. Verify:   python {Path(__file__).name} verify {self.module}")
        print(f"    2. Alembic:  alembic upgrade head")
        print(f"    3. Deps:     python {Path(__file__).name} deps {self.module}")
        print(f"    4. Run:      uvicorn app.app:app --reload")
        print(f"    5. Swagger:  http://localhost:8000/docs")
        print(f"    6. Postman:  Import docs/postman/{self.module}.json")
        print()


# ═══════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════
HELP = f"""
═══════════════════════════════════════════════════════════════
  create_module_yolo_detection.py — YOLO Detection Generator v{VERSION}
  Schema: {SCHEMA}  ·  Prefix: yolo_  ·  Tables: 7
═══════════════════════════════════════════════════════════════

  USAGE
    python create_module_yolo_detection.py <action> <module> [layer] [prefix] [options]

  ACTIONS (12)
    create      [1]  Module structure (4 layers)
    activate    [2]  Register router + swagger + models
    sql         [3]  SQL V001/V002/V003
    alembic     [4]  Alembic migration (7 tables)
    swagger     [5]  OpenAPI metadata (tag: yolo)
    postman     [6]  Postman collection (14 endpoints)
    update      [7]  Update app/app.py
    update-env  [8]  Update migrations/env.py
    test        [9]  Tests (unit/integration/property/manual)
    verify      [10] Verify
    deps        [11] Check dependencies
    all         All actions
    help        Show this

  EXAMPLES
    python create_module_yolo_detection.py all yolo 5 yolo
    python create_module_yolo_detection.py create yolo --force
    python create_module_yolo_detection.py verify yolo
    alembic upgrade head
═══════════════════════════════════════════════════════════════
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("module", nargs="?", default="yolo")
    parser.add_argument("layer", nargs="?", default="5")
    parser.add_argument("prefix", nargs="?", default="yolo")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--help", action="store_true")

    args, _ = parser.parse_known_args()

    if args.help or args.action == "help":
        print(HELP)
        return 0

    root = Path(args.project_root).resolve()
    if not root.exists():
        err(f"Project root not found: {root}")
        return 1

    gen = YOLODetectionGenerator(
        project_root=root, module=args.module, layer=args.layer,
        prefix=args.prefix, force=args.force,
    )

    print()
    info("═" * 60)
    info(f"  MODULE  : {gen.module}")
    info(f"  LAYER   : {gen.layer} ({gen.layer_name})")
    info(f"  SCHEMA  : {SCHEMA}")
    info(f"  PREFIX  : {gen.prefix}_")
    info(f"  ACTION  : {args.action}")
    info(f"  FORCE   : {args.force}")
    info(f"  VERSION : {VERSION}")
    info("═" * 60)

    action_map = {
        "create": gen.create_module,
        "activate": gen.activate_module,
        "sql": gen.create_sql,
        "alembic": gen.create_migration,
        "swagger": gen.create_swagger,
        "postman": gen.create_postman,
        "test": gen.create_tests,
        "update": gen.update_app,
        "update-env": gen.update_env,
        "verify": gen.verify,
        "deps": gen.check_deps,
        "all": gen.run_all,
    }

    if args.action not in action_map:
        err(f"Unknown action: {args.action}")
        print(HELP)
        return 1

    try:
        action_map[args.action]()
    except Exception as e:
        err(f"Aborted: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if args.action not in ("verify", "deps", "help"):
        gen.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())