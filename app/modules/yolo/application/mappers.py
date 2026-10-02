"""YOLO mappers"""
from __future__ import annotations
from typing import Any


def dataset_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "name": row.name, "format": row.format,
            "root_uri": row.root_uri, "image_count": row.image_count,
            "class_count": row.class_count, "status": row.status,
            "version": row.version}


def image_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "dataset_id": str(row.dataset_id),
            "uri": row.uri, "content_hash": row.content_hash,
            "width": row.width, "height": row.height,
            "split": row.split, "annotation_count": row.annotation_count}


def training_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "dataset_id": str(row.dataset_id),
            "model_type": row.model_type, "epochs": row.epochs,
            "batch_size": row.batch_size, "imgsz": row.imgsz,
            "status": row.status, "progress": row.progress}


def model_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "name": row.name, "version": row.version,
            "format": row.format, "mAP50": str(row.mAP50),
            "mAP50_95": str(row.mAP50_95), "is_active": row.is_active}
