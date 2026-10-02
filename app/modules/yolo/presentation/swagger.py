"""YOLO OpenAPI metadata"""
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
                    "YOLO Object Detection Platform (Ultralytics YOLOv8/v11)\n\n"
                    "• Dataset registry + YOLO/COCO import\n"
                    "• Image upload + S3 storage\n"
                    "• Bounding box annotations\n"
                    "• Albumentations augmentation\n"
                    "• YOLO training (Ultralytics)\n"
                    "• COCO metrics (mAP@50, mAP@50-95)\n"
                    "• ONNX / TensorRT export\n"
                    "• Real-time + batch + video inference\n"
                    "• Settings, Report, Category, Counting\n"
                    "• Plant Disease, Plant Growth"
                ),
                "externalDocs": {
                    "description": "YOLO Module README",
                    "url": "/docs/README_yolo.md"}})
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "yolo")
        info.setdefault("x-layer", "5-Intel")
        info.setdefault("x-prefix", "yolo")
        info.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
