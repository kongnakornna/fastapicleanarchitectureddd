"""Plant growth router"""
from __future__ import annotations
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.modules.yolo.application.plant_growth_use_case import PlantGrowthUseCase
from app.modules.yolo.presentation.dependencies import get_ctx
from app.modules.yolo.presentation.schemas_plant_growth import (
    GrowthAssessmentResponse, HarvestPredictionResponse,
)

router = APIRouter(prefix="/yolo/plant-growth", tags=["yolo"])

_uc_holder: dict = {"uc": None}


async def _get_uc() -> PlantGrowthUseCase:
    if _uc_holder["uc"] is None:
        raise HTTPException(500, "PlantGrowthUseCase not wired")
    return _uc_holder["uc"]


def set_use_case(uc: PlantGrowthUseCase) -> None:
    _uc_holder["uc"] = uc


@router.post("/assess", response_model=GrowthAssessmentResponse,
              summary="Assess plant growth", operation_id="yolo_assess_growth")
async def assess(
    model_id: str = Form(...),
    field_id: str = Form(""),
    plant_id: str = Form(""),
    px_per_cm: float = Form(0.0),
    image: UploadFile = File(...),
    uc: Annotated[PlantGrowthUseCase, Depends(_get_uc)] = None,  # type: ignore
) -> GrowthAssessmentResponse:
    ctx = await get_ctx()
    raw = await image.read()
    result = await uc.assess_growth(
        ctx, uuid.UUID(model_id), raw,
        uuid.UUID(field_id) if field_id else None,
        uuid.UUID(plant_id) if plant_id else None,
        px_per_cm if px_per_cm > 0 else None)
    return GrowthAssessmentResponse(**result)


@router.get("/fields/{field_id}/timeline", summary="Field timeline",
             operation_id="yolo_growth_timeline")
async def timeline(
    field_id: uuid.UUID, days: int = 30,
    uc: Annotated[PlantGrowthUseCase, Depends(_get_uc)] = None,  # type: ignore
) -> dict:
    ctx = await get_ctx()
    return await uc.get_field_timeline(ctx, field_id, days)


@router.get("/fields/{field_id}/predict-harvest",
             response_model=HarvestPredictionResponse,
             summary="Predict harvest", operation_id="yolo_predict_harvest")
async def predict_harvest(
    field_id: uuid.UUID,
    uc: Annotated[PlantGrowthUseCase, Depends(_get_uc)],
) -> HarvestPredictionResponse:
    ctx = await get_ctx()
    return HarvestPredictionResponse(**await uc.predict_harvest(ctx, field_id))
