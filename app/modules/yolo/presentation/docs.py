"""YOLO OpenAPI examples"""
from __future__ import annotations

RESPONSE_DATASET_201 = {
    "description": "Dataset created",
    "content": {"application/json": {"example": {
        "id": "uuid", "name": "coco-subset", "format": "yolo",
        "status": "DRAFT", "version": 1}}}}
RESPONSE_TRAIN_201 = {
    "description": "Training started",
    "content": {"application/json": {"example": {
        "training_id": "uuid", "model_id": "uuid", "status": "SUCCESS",
        "mAP50": 0.85, "mAP50_95": 0.62, "duration_ms": 45000}}}}
RESPONSE_DETECT_200 = {
    "description": "Detection succeeded",
    "content": {"application/json": {"example": {
        "inference_id": "uuid", "model_id": "uuid",
        "detections": [{"bbox": {"x_center": 0.5, "y_center": 0.5,
                                  "width": 0.2, "height": 0.3},
                         "class_id": 0, "class_name": "person",
                         "confidence": 0.92}],
        "detection_count": 1, "latency_ms": 45}}}}
RESPONSE_ERROR_400 = {"description": "Domain error",
    "content": {"application/json": {"example": {
        "detail": "invalid bbox", "code": "INVALID_BBOX"}}}}
RESPONSE_ERROR_404 = {"description": "Not found",
    "content": {"application/json": {"example": {
        "detail": "model not found", "code": "MODEL_NOT_FOUND"}}}}
RESPONSE_ERROR_500 = {"description": "Server error",
    "content": {"application/json": {"example": {
        "detail": "training failed", "code": "TRAINING_FAILED"}}}}
RESPONSE_ERROR_503 = {"description": "GPU unavailable",
    "content": {"application/json": {"example": {
        "detail": "no GPU available", "code": "GPU_UNAVAILABLE"}}}}
