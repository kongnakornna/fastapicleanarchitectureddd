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
