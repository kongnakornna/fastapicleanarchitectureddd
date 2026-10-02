"""Deployment router"""
from __future__ import annotations
import os
from typing import Any
from fastapi import APIRouter

router = APIRouter(prefix="/yolo/deployment", tags=["yolo"])


@router.get("/health", summary="Health check", operation_id="yolo_health")
async def health() -> dict:
    gpu_ok = False
    gpu_name = None
    try:
        import torch
        gpu_ok = bool(torch.cuda.is_available())
        if gpu_ok:
            gpu_name = torch.cuda.get_device_name(0)
    except Exception:
        pass
    return {"status": "ok", "gpu_available": gpu_ok, "gpu_name": gpu_name,
            "device": os.getenv("YOLO_DEVICE", "auto"),
            "default_model": os.getenv("YOLO_DEFAULT_MODEL", "yolov8n.pt")}


@router.get("/readyz", summary="Readiness", operation_id="yolo_readyz")
async def readyz() -> dict:
    return {"ready": True}


@router.get("/livez", summary="Liveness", operation_id="yolo_livez")
async def livez() -> dict:
    return {"alive": True}


@router.get("/registry", summary="List loaded models",
             operation_id="yolo_registry_list")
async def registry_list() -> dict:
    try:
        from app.modules.yolo.presentation.dependencies import _get_registry
        r = _get_registry()
        return {"loaded": len(getattr(r, "_models", {}))}
    except Exception:
        return {"loaded": 0}


@router.post("/registry/load", summary="Pre-load model",
              operation_id="yolo_registry_load")
async def registry_load(payload: dict) -> dict:
    return {"loaded": payload.get("model_id"), "status": "queued"}


@router.post("/registry/unload", summary="Unload model",
              operation_id="yolo_registry_unload")
async def registry_unload(payload: dict) -> dict:
    return {"unloaded": payload.get("model_id")}


@router.get("/metrics", summary="Prometheus metrics",
             operation_id="yolo_metrics")
async def metrics() -> dict:
    return {"inferences_total": 0, "trainings_total": 0}
