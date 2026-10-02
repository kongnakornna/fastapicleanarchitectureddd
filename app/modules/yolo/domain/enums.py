"""YOLO enums"""
from __future__ import annotations
from enum import StrEnum


class DatasetFormat(StrEnum):
    YOLO = "yolo"; COCO = "coco"; ROBOFLOW = "roboflow"; LABELIMG = "labelimg"


class DatasetStatus(StrEnum):
    DRAFT = "DRAFT"; READY = "READY"; TRAINING = "TRAINING"; ARCHIVED = "ARCHIVED"


class ModelType(StrEnum):
    YOLOV8N = "yolov8n"; YOLOV8S = "yolov8s"; YOLOV8M = "yolov8m"
    YOLOV8L = "yolov8l"; YOLOV8X = "yolov8x"
    YOLO11N = "yolo11n"; YOLO11S = "yolo11s"; YOLO11M = "yolo11m"
    YOLO11L = "yolo11l"; YOLO11X = "yolo11x"


class ModelFormat(StrEnum):
    PYTORCH = "pt"; ONNX = "onnx"; TENSORRT = "engine"
    TORCHSCRIPT = "torchscript"; COREML = "coreml"


class TrainingStatus(StrEnum):
    PENDING = "PENDING"; RUNNING = "RUNNING"; SUCCESS = "SUCCESS"
    FAILED = "FAILED"; CANCELLED = "CANCELLED"


class ImageSplit(StrEnum):
    TRAIN = "train"; VAL = "val"; TEST = "test"


class InferenceSource(StrEnum):
    API = "api"; BATCH = "batch"; STREAM = "stream"; UPLOAD = "upload"
