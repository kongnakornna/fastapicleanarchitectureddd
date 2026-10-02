"""Report router"""
from __future__ import annotations
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from app.modules.yolo.application.report_use_case import ReportUseCase
from app.modules.yolo.presentation.dependencies import get_ctx
from app.modules.yolo.presentation.schemas_report import (
    InferenceReportResponse, TrainingReportResponse,
)

router = APIRouter(prefix="/yolo/reports", tags=["yolo"])

_uc_holder: dict = {"uc": None}


async def _get_uc() -> ReportUseCase:
    if _uc_holder["uc"] is None:
        raise HTTPException(500, "ReportUseCase not wired")
    return _uc_holder["uc"]


def set_use_case(uc: ReportUseCase) -> None:
    _uc_holder["uc"] = uc


@router.get("/training/{training_id}", response_model=TrainingReportResponse,
             summary="Training report", operation_id="yolo_report_training")
async def training_report(
    training_id: uuid.UUID,
    uc: Annotated[ReportUseCase, Depends(_get_uc)],
) -> TrainingReportResponse:
    ctx = await get_ctx()
    try:
        return TrainingReportResponse(**await uc.training_report(ctx, training_id))
    except ValueError as e:
        raise HTTPException(404, detail=str(e)) from e


@router.get("/model/{model_id}", response_model=InferenceReportResponse,
             summary="Inference report", operation_id="yolo_report_model")
async def model_report(
    model_id: uuid.UUID, period_days: int = 30,
    uc: Annotated[ReportUseCase, Depends(_get_uc)] = None,  # type: ignore
) -> InferenceReportResponse:
    ctx = await get_ctx()
    return InferenceReportResponse(
        **await uc.model_report(ctx, model_id, period_days))


@router.get("/dataset/{dataset_id}", summary="Dataset report",
             operation_id="yolo_report_dataset")
async def dataset_report(
    dataset_id: uuid.UUID,
    uc: Annotated[ReportUseCase, Depends(_get_uc)],
) -> dict:
    ctx = await get_ctx()
    try:
        return await uc.dataset_report(ctx, dataset_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e)) from e


@router.get("/summary", summary="Tenant summary",
             operation_id="yolo_report_summary")
async def tenant_summary(
    uc: Annotated[ReportUseCase, Depends(_get_uc)],
) -> dict:
    ctx = await get_ctx()
    return await uc.tenant_summary(ctx)
