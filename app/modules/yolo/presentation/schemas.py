"""YOLO Pydantic v2 schemas"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


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
    items: list[DatasetResponse]; total: int; page: int; size: int
    model_config = ConfigDict(extra="forbid")


class ClassDefineItem(BaseModel):
    name: str; class_index: int; color: str = "#FF0000"
    model_config = ConfigDict(extra="forbid")


class ClassesDefineRequest(BaseModel):
    classes: list[ClassDefineItem] = Field(..., min_length=1)
    model_config = ConfigDict(extra="forbid")


class ClassesResponse(BaseModel):
    dataset_id: str; class_count: int
    classes: list[dict[str, Any]]
    model_config = ConfigDict(extra="forbid")


class ImageUploadItem(BaseModel):
    uri: str; content_hash: str
    width: int = 0; height: int = 0; size_bytes: int = 0
    model_config = ConfigDict(extra="forbid")


class ImagesUploadRequest(BaseModel):
    images: list[ImageUploadItem] = Field(..., min_length=1, max_length=1000)
    split: str = "train"
    model_config = ConfigDict(extra="forbid")


class ImagesUploadResponse(BaseModel):
    dataset_id: str; uploaded: int
    model_config = ConfigDict(extra="forbid")


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
    mAP50: float = 0.0; mAP50_95: float = 0.0; duration_ms: int = 0
    model_config = ConfigDict(extra="forbid")


class TrainingStatusResponse(BaseModel):
    id: str; dataset_id: str; model_type: str
    epochs: int; status: str; progress: int = 0
    best_model_id: str | None = None
    error_message: str = ""
    started_at: str | None = None
    finished_at: str | None = None
    model_config = ConfigDict(extra="forbid")


class ModelResponse(BaseModel):
    id: str; name: str; version: int; format: str = "pt"
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


class DetectRequest(BaseModel):
    model_id: str
    conf: float = Field(default=0.25, ge=0.0, le=1.0)
    iou: float = Field(default=0.45, ge=0.0, le=1.0)
    image_base64: str
    model_config = ConfigDict(extra="forbid")


class DetectResponse(BaseModel):
    inference_id: str; model_id: str; image_hash: str = ""
    detections: list[dict[str, Any]] = Field(default_factory=list)
    detection_count: int = 0; latency_ms: int = 0
    model_config = ConfigDict(extra="forbid")


class BatchDetectRequest(BaseModel):
    model_id: str
    conf: float = Field(default=0.25, ge=0.0, le=1.0)
    iou: float = Field(default=0.45, ge=0.0, le=1.0)
    images_base64: list[str] = Field(..., min_length=1, max_length=32)
    model_config = ConfigDict(extra="forbid")


class BatchDetectResponse(BaseModel):
    model_id: str; total: int; results: list[dict[str, Any]]
    model_config = ConfigDict(extra="forbid")


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
