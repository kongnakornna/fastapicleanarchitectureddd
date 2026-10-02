"""YOLO domain exceptions"""
from __future__ import annotations


class YOLOError(Exception):
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
