"""Money routers — FastAPI endpoints"""
from __future__ import annotations

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from ..application.exceptions import (
    DuplicateCodeError as AppDuplicateCodeError,
    MoneyNotFoundError as AppNotFoundError,
)
from ..application.use_cases import (
    CreateMoneyUseCase,
    DeleteMoneyUseCase,
    GetMoneyUseCase,
    ListMoneyUseCase,
    UpdateMoneyUseCase,
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
    MoneyCreateRequest,
    MoneyListResponse,
    MoneyResponse,
    MoneyUpdateRequest,
)

log = structlog.get_logger()

router = APIRouter(prefix="/money", tags=["Money"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="สร้าง money",
    operation_id="create_money",
    response_model=MoneyResponse,
    responses={
        201: RESPONSE_CREATE_201,
        400: RESPONSE_ERROR_400,
        409: RESPONSE_ERROR_409,
        422: RESPONSE_ERROR_422,
    },
)
async def create_money(
    payload: MoneyCreateRequest,
    idem_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
    uc: Annotated[CreateMoneyUseCase, Depends(get_create_uc)],
) -> MoneyResponse:
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
    return MoneyResponse.model_validate(entity, from_attributes=True)


@router.get(
    "/",
    summary="รายการ money",
    operation_id="list_money",
    response_model=MoneyListResponse,
)
async def list_money(
    uc: Annotated[ListMoneyUseCase, Depends(get_list_uc)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> MoneyListResponse:
    """TH: list + filter + paginate | EN: list + filter + paginate"""
    items, total = await uc.execute(
        status=status_filter, q=q, limit=limit, offset=offset
    )
    return MoneyListResponse(
        items=[MoneyResponse.model_validate(x, from_attributes=True) for x in items],
        total=total, limit=limit, offset=offset,
    )


@router.get(
    "/{entity_id}",
    summary="ดู money ตาม id",
    operation_id="get_money",
    response_model=MoneyResponse,
    responses={404: RESPONSE_ERROR_404},
)
async def get_money(
    entity_id: uuid.UUID,
    uc: Annotated[GetMoneyUseCase, Depends(get_get_uc)],
) -> MoneyResponse:
    try:
        entity = await uc.execute(entity_id=entity_id)
    except AppNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return MoneyResponse.model_validate(entity, from_attributes=True)


@router.patch(
    "/{entity_id}",
    summary="แก้ไข money",
    operation_id="update_money",
    response_model=MoneyResponse,
    responses={404: RESPONSE_ERROR_404, 409: RESPONSE_ERROR_409},
)
async def update_money(
    entity_id: uuid.UUID,
    payload: MoneyUpdateRequest,
    uc: Annotated[UpdateMoneyUseCase, Depends(get_update_uc)],
) -> MoneyResponse:
    try:
        entity = await uc.execute(
            entity_id=entity_id, **payload.model_dump(exclude_unset=True)
        )
    except AppNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DomainError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return MoneyResponse.model_validate(entity, from_attributes=True)


@router.delete(
    "/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ลบ money (soft delete)",
    operation_id="delete_money",
    responses={404: RESPONSE_ERROR_404},
)
async def delete_money(
    entity_id: uuid.UUID,
    uc: Annotated[DeleteMoneyUseCase, Depends(get_delete_uc)],
) -> None:
    try:
        await uc.execute(entity_id=entity_id)
    except AppNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e)) from e