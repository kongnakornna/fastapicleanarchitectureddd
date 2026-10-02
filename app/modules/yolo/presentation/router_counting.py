"""Counting router"""
from __future__ import annotations
import base64
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.modules.yolo.application.counting_use_case import CountingUseCase
from app.modules.yolo.domain.applications.counting import CountingConfig
from app.modules.yolo.presentation.dependencies import get_ctx
from app.modules.yolo.presentation.schemas_counting import (
    BatchCountingResponse, CountingResultResponse,
)

router = APIRouter(prefix="/yolo/counting", tags=["yolo"])

_uc_holder: dict = {"uc": None}


async def _get_uc() -> CountingUseCase:
    if _uc_holder["uc"] is None:
        raise HTTPException(500, "CountingUseCase not wired")
    return _uc_holder["uc"]


def set_use_case(uc: CountingUseCase) -> None:
    _uc_holder["uc"] = uc


@router.post("/image", response_model=CountingResultResponse,
              summary="Count products", operation_id="yolo_count_image")
async def count_image(
    model_id: str = Form(...),
    mode: str = Form("shelf"),
    min_confidence: float = Form(0.5),
    image: UploadFile = File(...),
    uc: Annotated[CountingUseCase, Depends(_get_uc)] = None,  # type: ignore
) -> CountingResultResponse:
    ctx = await get_ctx()
    try:
        config = CountingConfig(mode=mode, min_confidence=min_confidence)
        raw = await image.read()
        result = await uc.count_image(ctx, uuid.UUID(model_id), raw, config)
        return CountingResultResponse(**result)
    except ValueError as e:
        raise HTTPException(422, detail=str(e)) from e


@router.post("/batch", response_model=BatchCountingResponse,
              summary="Count batch", operation_id="yolo_count_batch")
async def count_batch(
    payload: dict,
    uc: Annotated[CountingUseCase, Depends(_get_uc)],
) -> BatchCountingResponse:
    ctx = await get_ctx()
    config = CountingConfig(**payload.get("config", {}))
    images = [base64.b64decode(b) for b in payload.get("images_base64", [])]
    result = await uc.count_batch(
        ctx, uuid.UUID(payload["model_id"]), images, config)
    return BatchCountingResponse(**result)
