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
