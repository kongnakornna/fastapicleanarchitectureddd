"""Settings router"""
from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.yolo.application.settings_use_case import SettingsUseCase
from app.modules.yolo.domain.settings import SettingsPatch
from app.modules.yolo.presentation.dependencies import get_ctx
from app.modules.yolo.presentation.schemas_settings import (
    SettingsPatchRequest, SettingsResponse, SettingsValidateResponse,
)

router = APIRouter(prefix="/yolo/settings", tags=["yolo"])

_uc_holder: dict = {"uc": None}


async def _get_uc() -> SettingsUseCase:
    if _uc_holder["uc"] is None:
        raise HTTPException(500, "SettingsUseCase not wired")
    return _uc_holder["uc"]


def set_use_case(uc: SettingsUseCase) -> None:
    _uc_holder["uc"] = uc


@router.get("", response_model=SettingsResponse,
             summary="Get YOLO settings", operation_id="yolo_get_settings")
async def get_settings(
    uc: Annotated[SettingsUseCase, Depends(_get_uc)],
) -> SettingsResponse:
    ctx = await get_ctx()
    return SettingsResponse(**await uc.get_settings(ctx))


@router.patch("", response_model=SettingsResponse,
               summary="Update YOLO settings", operation_id="yolo_update_settings")
async def update_settings(
    payload: SettingsPatchRequest,
    uc: Annotated[SettingsUseCase, Depends(_get_uc)],
) -> SettingsResponse:
    ctx = await get_ctx()
    try:
        patch = SettingsPatch(**payload.model_dump())
        return SettingsResponse(**await uc.update_settings(ctx, patch))
    except ValueError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                              detail=str(e)) from e


@router.post("/reset", response_model=SettingsResponse,
              summary="Reset to defaults", operation_id="yolo_reset_settings")
async def reset_settings(
    uc: Annotated[SettingsUseCase, Depends(_get_uc)],
) -> SettingsResponse:
    ctx = await get_ctx()
    return SettingsResponse(**await uc.reset_to_defaults(ctx))


@router.post("/validate", response_model=SettingsValidateResponse,
              summary="Validate settings patch", operation_id="yolo_validate_settings")
async def validate_settings(
    payload: SettingsPatchRequest,
    uc: Annotated[SettingsUseCase, Depends(_get_uc)],
) -> SettingsValidateResponse:
    ctx = await get_ctx()
    patch = SettingsPatch(**payload.model_dump())
    return SettingsValidateResponse(**await uc.validate_settings(ctx, patch))
