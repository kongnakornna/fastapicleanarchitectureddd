"""Plant disease router"""
from __future__ import annotations
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.modules.yolo.application.plant_disease_use_case import PlantDiseaseUseCase
from app.modules.yolo.presentation.dependencies import get_ctx
from app.modules.yolo.presentation.schemas_plant_disease import (
    DiagnosisResponse, DiseaseCatalogItem, TreatmentPlanResponse,
)

router = APIRouter(prefix="/yolo/plant-disease", tags=["yolo"])

_uc_holder: dict = {"uc": None}


async def _get_uc() -> PlantDiseaseUseCase:
    if _uc_holder["uc"] is None:
        raise HTTPException(500, "PlantDiseaseUseCase not wired")
    return _uc_holder["uc"]


def set_use_case(uc: PlantDiseaseUseCase) -> None:
    _uc_holder["uc"] = uc


@router.post("/diagnose", response_model=DiagnosisResponse,
              summary="Diagnose plant disease", operation_id="yolo_diagnose")
async def diagnose(
    model_id: str = Form(...),
    dataset_id: str = Form(""),
    plant_species: str = Form(""),
    image: UploadFile = File(...),
    uc: Annotated[PlantDiseaseUseCase, Depends(_get_uc)] = None,  # type: ignore
) -> DiagnosisResponse:
    ctx = await get_ctx()
    raw = await image.read()
    ds_id = uuid.UUID(dataset_id) if dataset_id else None
    try:
        result = await uc.diagnose_image(ctx, uuid.UUID(model_id), raw,
                                           ds_id, plant_species or None)
        return DiagnosisResponse(**result)
    except ValueError as e:
        raise HTTPException(422, detail=str(e)) from e


@router.get("/catalog", response_model=list[DiseaseCatalogItem],
             summary="Disease catalog", operation_id="yolo_disease_catalog")
async def catalog(
    uc: Annotated[PlantDiseaseUseCase, Depends(_get_uc)],
    pathogen_type: str | None = None,
) -> list[DiseaseCatalogItem]:
    ctx = await get_ctx()
    return [DiseaseCatalogItem(**i)
            for i in await uc.get_catalog(ctx, pathogen_type)]


@router.get("/treatment/{disease_code}", response_model=TreatmentPlanResponse,
             summary="Get treatment plan", operation_id="yolo_treatment_plan")
async def treatment(
    disease_code: str,
    uc: Annotated[PlantDiseaseUseCase, Depends(_get_uc)],
) -> TreatmentPlanResponse:
    ctx = await get_ctx()
    try:
        return TreatmentPlanResponse(
            **await uc.get_treatment_plan(ctx, disease_code))
    except ValueError as e:
        raise HTTPException(404, detail=str(e)) from e
