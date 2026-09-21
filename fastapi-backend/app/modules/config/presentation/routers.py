"""
Presentation Routers — HTTP endpoints ของ config
GET/PUT/DELETE/LIST พร้อม mask secret
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..application.exceptions import (
    ConfigException,
    ConfigKeyNotFoundException,
)
from ..application.use_cases import ConfigUseCases
from ..domain.enums import ConfigScope
from .dependencies import get_config_use_cases
from .schemas import (
    ConfigEntrySchema,
    ConfigListQuery,
    ConfigSetRequest,
    ConfigTypedResponse,
)

router = APIRouter(
    prefix="/api/v1/config",
    tags=["Config"],
)


@router.get(
    "/{key}/",
    response_model=ConfigEntrySchema,
    summary="Get effective config",
    description="ดึงค่าที่มีผลจริง (USER > TENANT > GLOBAL)",
)
async def get_config(
    key: str,
    user_id: str | None = Query(None, description="User ID for USER scope override"),
    use_cases: ConfigUseCases = Depends(get_config_use_cases),
) -> ConfigEntrySchema:
    """
    Get effective config — ดึงค่าที่มีผลจริง
    Secret จะถูก mask เป็น '***'
    """
    try:
        entry = await use_cases.get_effective(key, user_id=user_id)
        return ConfigEntrySchema.model_validate(entry.mask())
    except ConfigKeyNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConfigException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{key}/typed/",
    response_model=ConfigTypedResponse,
    summary="Get effective config with typed value",
)
async def get_config_typed(
    key: str,
    user_id: str | None = Query(None),
    use_cases: ConfigUseCases = Depends(get_config_use_cases),
) -> ConfigTypedResponse:
    """ดึงค่า config พร้อม typed value (secret จะไม่ถูกถอดรหัสผ่าน API นี้)"""
    try:
        entry = await use_cases.get_effective(key, user_id=user_id)
        if entry.is_secret:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Secret value cannot be returned via API",
            )
        return ConfigTypedResponse(
            key=entry.key,
            value=entry.typed_value(),
            value_type=entry.value_type,
            scope=entry.scope,
            scope_id=entry.scope_id,
            is_secret=entry.is_secret,
        )
    except ConfigKeyNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConfigException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{key}/",
    response_model=ConfigEntrySchema,
    summary="Set config",
)
async def set_config(
    key: str,
    payload: ConfigSetRequest,
    use_cases: ConfigUseCases = Depends(get_config_use_cases),
) -> ConfigEntrySchema:
    """ตั้งค่า config (secret จะถูก encrypt ก่อนเก็บ)"""
    try:
        entry = await use_cases.set(
            key=key,
            value=payload.value,
            value_type=payload.value_type,
            scope=payload.scope,
            scope_id=payload.scope_id,
            is_secret=payload.is_secret,
            description=payload.description,
        )
        return ConfigEntrySchema.model_validate(entry.mask())
    except ConfigException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/",
    response_model=list[ConfigEntrySchema],
    summary="List configs",
)
async def list_config(
    query: ConfigListQuery = Depends(),
    use_cases: ConfigUseCases = Depends(get_config_use_cases),
) -> list[ConfigEntrySchema]:
    """แสดงรายการ config ตาม scope (secret จะถูก mask)"""
    try:
        entries = await use_cases.list(query.scope, query.scope_id)
        return [ConfigEntrySchema.model_validate(e) for e in entries]
    except ConfigException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{key}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete config",
)
async def delete_config(
    key: str,
    scope: str = Query(ConfigScope.TENANT.value),
    scope_id: str = Query(""),
    use_cases: ConfigUseCases = Depends(get_config_use_cases),
) -> None:
    """ลบ config entry"""
    try:
        deleted = await use_cases.delete(key, scope, scope_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Config not found: {key}",
            )
    except ConfigException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


__all__ = ["router"]
