"""123Abc routers — FastAPI endpoints"""
from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from ..application.exceptions import (
    DuplicateCodeError as AppDuplicateCodeError,
    123AbcNotFoundError as AppNotFoundError,
)
from ..application.use_cases import (
    Create123AbcUseCase,
    Delete123AbcUseCase,
    Get123AbcUseCase,
    List123AbcUseCase,
    Update123AbcUseCase,
)
from ..domain.exceptions import DomainError
from .dependencies import (
    get_create_uc, get_delete_uc, get_get_uc, get_list_uc, get_update_uc,
)
from .docs import (
    RESPONSE_CREATE_201,
    RESPONSE_ERROR_400,
    RESPONSE_ERROR_404,
    RESPONSE_ERROR_409,
    RESPONSE_ERROR_422,
)
from .schemas import (
    123AbcCreateRequest,
    123AbcListResponse,
    123AbcResponse,
    123AbcUpdateRequest,
)

log = structlog.get_logger()

router = APIRouter(prefix="/123abc", tags=["123Abc"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง 123abc",
    operation_id="create_123abc",
    response_model=123AbcResponse,
    responses={
        201: RESPONSE_CREATE_201,
        400: RESPONSE_ERROR_400,
        409: RESPONSE_ERROR_409,
        422: RESPONSE_ERROR_422,
    },
)
async def create_123abc(
    payload: 123AbcCreateRequest,
    idem_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
    uc: Annotated[Create123AbcUseCase, Depends(get_create_uc)],
) -> 123AbcResponse:
    """TH: สร้าง entity ใหม่ (idempotent) | EN: create entity (idempotent)"""
    log.info("http.create.start", code=payload.code, idem=idem_key[:8])
    try:
        entity = await uc.execute(
            code=payload.code, name=payload.name,
            amount=payload.amount, idempotency_key=idem_key,
        )
    except AppDuplicateCodeError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e
    except DomainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return 123AbcResponse.model_validate(entity, from_attributes=True)


@router.get(
    "/",
    summary="รายการ 123abc",
    operation_id="list_123abc",
    response_model=123AbcListResponse,
)
async def list_123abc(
    uc: Annotated[List123AbcUseCase, Depends(get_list_uc)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> 123AbcListResponse:
    """TH: list + filter + paginate | EN: list + filter + paginate"""
    items, total = await uc.execute(
        status=status_filter, q=q, limit=limit, offset=offset
    )
    return 123AbcListResponse(
        items=[123AbcResponse.model_validate(x, from_attributes=True) for x in items],
        total=total, limit=limit, offset=offset,
    )


@router.get(
    "/{entity_id}",
    summary="ดู 123abc ตาม id",
    operation_id="get_123abc",
    response_model=123AbcResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def get_123abc(
    entity_id: uuid.UUID,
    uc: Annotated[Get123AbcUseCase, Depends(get_get_uc)],
) -> 123AbcResponse:
    try:
        entity = await uc.execute(entity_id=entity_id)
    except AppNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return 123AbcResponse.model_validate(entity, from_attributes=True)


@router.patch(
    "/{entity_id}",
    summary="แก้ไข 123abc",
    operation_id="update_123abc",
    response_model=123AbcResponse,
    responses={404: RESPONSE_ERROR_404, 409: RESPONSE_ERROR_409},
)
async def update_123abc(
    entity_id: uuid.UUID,
    payload: 123AbcUpdateRequest,
    uc: Annotated[Update123AbcUseCase, Depends(get_update_uc)],
) -> 123AbcResponse:
    try:
        entity = await uc.execute(
            entity_id=entity_id, **payload.model_dump(exclude_unset=True)
        )
    except AppNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DomainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return 123AbcResponse.model_validate(entity, from_attributes=True)


@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ลบ 123abc (soft delete)",
    operation_id="delete_123abc",
    responses={404: RESPONSE_ERROR_404},
)
async def delete_123abc(
    entity_id: uuid.UUID,
    uc: Annotated[Delete123AbcUseCase, Depends(get_delete_uc)],
) -> None:
    try:
        await uc.execute(entity_id=entity_id)
    except AppNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e