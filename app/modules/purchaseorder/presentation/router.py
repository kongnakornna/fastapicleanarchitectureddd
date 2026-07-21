from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.purchaseorder.application.use_case import PurchaseOrderUseCase
from app.modules.purchaseorder.domain.entities.purchase_order_header import (
    PurchaseOrderHeader,
)
from app.modules.purchaseorder.infrastructure.purchase_order_repository import (
    PurchaseOrderRepository,
)
from app.modules.purchaseorder.presentation.schemas import (
    PaginatedPurchaseOrdersResponse,
    PurchaseOrderCreateRequest,
    PurchaseOrderDetailResponse,
    PurchaseOrderReceiveRequest,
    PurchaseOrderResponse,
    PurchaseOrderStatusHistoryResponse,
    PurchaseOrderStatusRequest,
    PurchaseOrderUpdateRequest,
)

router = APIRouter(prefix="/purchase-order", tags=["PurchaseOrder"])


async def get_purchase_order_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> PurchaseOrderUseCase:
    return PurchaseOrderUseCase(repository=PurchaseOrderRepository(session))


def _header_to_response(
    header: PurchaseOrderHeader,
    details: list | None = None,
    history: list | None = None,
) -> PurchaseOrderResponse:
    return PurchaseOrderResponse(
        id=header.id,
        po_no=header.po_no,
        quotation_id=header.quotation_id,
        job_id=header.job_id,
        supplier_id=header.supplier_id,
        po_date=header.po_date,
        expected_delivery_date=header.expected_delivery_date,
        actual_delivery_date=header.actual_delivery_date,
        status=header.status,
        subtotal=header.subtotal,
        tax_rate=header.tax_rate,
        tax_amount=header.tax_amount,
        discount_type=header.discount_type,
        discount_value=header.discount_value,
        total=header.total,
        currency=header.currency,
        exchange_rate=header.exchange_rate,
        shipping_cost=header.shipping_cost,
        payment_terms=header.payment_terms,
        delivery_address=header.delivery_address,
        notes=header.notes,
        terms_and_conditions=header.terms_and_conditions,
        sent_at=header.sent_at,
        confirmed_at=header.confirmed_at,
        received_by=header.received_by,
        is_active=header.is_active,
        created_at=header.created_at,
        updated_at=header.updated_at,
        items=[PurchaseOrderDetailResponse.model_validate(d) for d in (details or [])],
        status_history=[
            PurchaseOrderStatusHistoryResponse.model_validate(h)
            for h in (history or [])
        ],
    )


@router.post("/")
async def create_purchase_order(
    payload: PurchaseOrderCreateRequest,
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> PurchaseOrderResponse:
    header_data = payload.model_dump(exclude={"items"})
    items = [i.model_dump() for i in payload.items]
    header = await use_case.create_order(header_data, items)
    details = await use_case._repo.find_details_by_header_id(header.id)
    return _header_to_response(header, details)


@router.get("/")
async def get_purchase_orders(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    supplier_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> PaginatedPurchaseOrdersResponse:
    from uuid import UUID

    sup_id = UUID(supplier_id) if supplier_id else None
    headers, total = await use_case.get_orders(
        page=page,
        page_size=per_page,
        supplier_id=sup_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    total_pages = (total + per_page - 1) // per_page
    items = []
    for h in headers:
        details = await use_case._repo.find_details_by_header_id(h.id)
        items.append(_header_to_response(h, details))
    return PaginatedPurchaseOrdersResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/{po_id}")
async def get_purchase_order(
    po_id: str,
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> PurchaseOrderResponse:
    from uuid import UUID

    header = await use_case.get_order(UUID(po_id))
    if not header:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    details = await use_case._repo.find_details_by_header_id(header.id)
    history = await use_case.get_status_history(header.id)
    return _header_to_response(header, details, history)


@router.put("/{po_id}")
async def update_purchase_order(
    po_id: str,
    payload: PurchaseOrderUpdateRequest,
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> PurchaseOrderResponse:
    from uuid import UUID

    values = payload.model_dump(exclude={"items"}, exclude_none=True)
    items = [i.model_dump() for i in payload.items] if payload.items is not None else None
    header = await use_case.update_order(UUID(po_id), values, items)
    if not header:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found or not in DRAFT status",
        )
    details = await use_case._repo.find_details_by_header_id(header.id)
    return _header_to_response(header, details)


@router.delete("/{po_id}")
async def delete_purchase_order(
    po_id: str,
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> dict[str, bool]:
    from uuid import UUID

    success = await use_case.delete_order(UUID(po_id))
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found or not in DRAFT status",
        )
    return {"success": True}


@router.post("/{po_id}/send")
async def send_purchase_order(
    po_id: str,
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> PurchaseOrderResponse:
    from uuid import UUID

    header = await use_case.send_order(UUID(po_id))
    if not header:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found or not in DRAFT status",
        )
    details = await use_case._repo.find_details_by_header_id(header.id)
    return _header_to_response(header, details)


@router.put("/{po_id}/confirm")
async def confirm_purchase_order(
    po_id: str,
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> PurchaseOrderResponse:
    from uuid import UUID

    header = await use_case.confirm_order(UUID(po_id))
    if not header:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found or not in SENT status",
        )
    details = await use_case._repo.find_details_by_header_id(header.id)
    return _header_to_response(header, details)


@router.post("/{po_id}/receive")
async def receive_purchase_order(
    po_id: str,
    payload: PurchaseOrderReceiveRequest,
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> PurchaseOrderResponse:
    from uuid import UUID

    receive_items = [i.model_dump() for i in payload.items]
    header = await use_case.receive_order(UUID(po_id), receive_items)
    if not header:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found or not in CONFIRMED status",
        )
    details = await use_case._repo.find_details_by_header_id(header.id)
    return _header_to_response(header, details)


@router.put("/{po_id}/cancel")
async def cancel_purchase_order(
    po_id: str,
    payload: PurchaseOrderStatusRequest | None = None,
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> PurchaseOrderResponse:
    from uuid import UUID

    reason = payload.reason if payload else None
    header = await use_case.cancel_order(UUID(po_id), reason=reason)
    if not header:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found or already received/cancelled",
        )
    details = await use_case._repo.find_details_by_header_id(header.id)
    return _header_to_response(header, details)


@router.get("/{po_id}/history")
async def get_purchase_order_history(
    po_id: str,
    use_case: PurchaseOrderUseCase = Depends(get_purchase_order_use_case),
) -> list[PurchaseOrderStatusHistoryResponse]:
    from uuid import UUID

    history = await use_case.get_status_history(UUID(po_id))
    return [PurchaseOrderStatusHistoryResponse.model_validate(h) for h in history]
