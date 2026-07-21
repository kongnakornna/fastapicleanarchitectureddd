from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.wos.application.use_case import WosUseCase
from app.modules.wos.domain.entities.order import WosOrder
from app.modules.wos.infrastructure.order_repository import WosOrderRepository
from app.modules.wos.presentation.schemas import (
    PaginatedWosOrdersResponse,
    WosOrderCreateRequest,
    WosOrderResponse,
)

router = APIRouter(prefix="/wos", tags=["WOS"])


async def get_wos_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> WosUseCase:
    return WosUseCase(order_repository=WosOrderRepository(session))


def _order_to_response(order: WosOrder) -> WosOrderResponse:
    return WosOrderResponse(
        id=str(order.id),
        order_number=order.order_number,
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        customer_phone=order.customer_phone,
        items=order.items,
        total_amount=order.total_amount,
        status=order.status,
        notes=order.notes,
        created_at=order.created_at.isoformat() if order.created_at else "",
        updated_at=order.updated_at.isoformat() if order.updated_at else "",
    )


@router.get("/orders")
async def get_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    use_case: WosUseCase = Depends(get_wos_use_case),
) -> PaginatedWosOrdersResponse:
    orders, total = await use_case.get_orders(page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedWosOrdersResponse(
        items=[_order_to_response(o) for o in orders],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/orders")
async def create_order(
    payload: WosOrderCreateRequest,
    use_case: WosUseCase = Depends(get_wos_use_case),
) -> WosOrderResponse:
    import random
    import string
    import time

    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    order_number = f"WOS-{int(time.time())}-{suffix}"
    order = WosOrder(
        order_number=order_number,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        customer_phone=payload.customer_phone,
        items=payload.items,
        total_amount=payload.total_amount,
        status="pending",
        notes=payload.notes,
    )
    result = await use_case.create_order(order)
    return _order_to_response(result)


@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    use_case: WosUseCase = Depends(get_wos_use_case),
) -> WosOrderResponse:
    from uuid import UUID

    order = await use_case.get_order(UUID(order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _order_to_response(order)


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str = Query(..., min_length=1, max_length=20),
    use_case: WosUseCase = Depends(get_wos_use_case),
) -> WosOrderResponse:
    from uuid import UUID

    order = await use_case.update_order_status(UUID(order_id), status)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found or invalid status transition",
        )
    return _order_to_response(order)
