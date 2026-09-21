from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.modules.purchaseorder.domain.entities.purchase_order_detail import (
    PurchaseOrderDetail,
)
from app.modules.purchaseorder.domain.entities.purchase_order_header import (
    PurchaseOrderHeader,
)
from app.modules.purchaseorder.domain.entities.purchase_order_status_history import (
    PurchaseOrderStatusHistory,
)
from app.modules.purchaseorder.infrastructure.purchase_order_repository import (
    PurchaseOrderRepository,
)

VALID_TRANSITIONS: dict[str, str] = {
    "draft": "sent",
    "sent": "confirmed",
    "confirmed": "received",
}


class PurchaseOrderUseCase:
    def __init__(self, repository: PurchaseOrderRepository) -> None:
        self._repo = repository

    async def create_order(
        self, header_data: dict, items: list[dict]
    ) -> PurchaseOrderHeader:
        header = PurchaseOrderHeader(**header_data)
        self._recalculate_totals(header, items)
        await self._repo.create(header)

        for item_data in items:
            detail = PurchaseOrderDetail(po_header_id=header.id, **item_data)
            self._recalculate_detail(detail)
            await self._repo.create_detail(detail)

        return header

    async def get_orders(
        self,
        page: int = 1,
        page_size: int = 10,
        supplier_id: UUID | None = None,
        status: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[PurchaseOrderHeader], int]:
        return await self._repo.find_all_paginated(
            page=page,
            page_size=page_size,
            supplier_id=supplier_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

    async def get_order(self, order_id: UUID) -> PurchaseOrderHeader | None:
        return await self._repo.find_by_id(order_id)

    async def update_order(
        self, order_id: UUID, values: dict, items: list[dict] | None = None
    ) -> PurchaseOrderHeader | None:
        header = await self._repo.find_by_id(order_id)
        if not header or header.status != "draft":
            return None

        for key, value in values.items():
            if value is not None and hasattr(header, key):
                setattr(header, key, value)

        if items is not None:
            existing_details = await self._repo.find_details_by_header_id(order_id)
            for detail in existing_details:
                detail.is_active = False
                await self._repo.update_detail(detail)

            for item_data in items:
                detail = PurchaseOrderDetail(po_header_id=header.id, **item_data)
                self._recalculate_detail(detail)
                await self._repo.create_detail(detail)

        details = await self._repo.find_details_by_header_id(order_id)
        self._recalculate_header_totals(header, details)
        return await self._repo.update(header)

    async def delete_order(self, order_id: UUID) -> bool:
        header = await self._repo.find_by_id(order_id)
        if not header or header.status != "draft":
            return False
        return await self._repo.delete(order_id)

    async def send_order(
        self, order_id: UUID, changed_by: UUID | None = None
    ) -> PurchaseOrderHeader | None:
        header = await self._repo.find_by_id(order_id)
        if not header or header.status != "draft":
            return None
        await self._create_history(header.id, header.status, "sent", changed_by)
        header.status = "sent"
        header.sent_at = datetime.utcnow()
        return await self._repo.update(header)

    async def confirm_order(
        self, order_id: UUID, changed_by: UUID | None = None
    ) -> PurchaseOrderHeader | None:
        header = await self._repo.find_by_id(order_id)
        if not header or header.status != "sent":
            return None
        await self._create_history(header.id, header.status, "confirmed", changed_by)
        header.status = "confirmed"
        header.confirmed_at = datetime.utcnow()
        return await self._repo.update(header)

    async def receive_order(
        self,
        order_id: UUID,
        receive_items: list[dict],
        changed_by: UUID | None = None,
    ) -> PurchaseOrderHeader | None:
        header = await self._repo.find_by_id(order_id)
        if not header or header.status != "confirmed":
            return None

        for item in receive_items:
            detail = await self._repo.find_detail_by_id(item["detail_id"])
            if detail and detail.po_header_id == order_id:
                detail.quantity_received = item["received_quantity"]
                self._recalculate_detail(detail)
                await self._repo.update_detail(detail)

        await self._create_history(header.id, header.status, "received", changed_by)
        header.status = "received"
        header.actual_delivery_date = datetime.utcnow().date()

        details = await self._repo.find_details_by_header_id(order_id)
        self._recalculate_header_totals(header, details)
        return await self._repo.update(header)

    async def cancel_order(
        self,
        order_id: UUID,
        changed_by: UUID | None = None,
        reason: str | None = None,
    ) -> PurchaseOrderHeader | None:
        header = await self._repo.find_by_id(order_id)
        if not header or header.status in ("received", "cancelled"):
            return None
        await self._create_history(
            header.id, header.status, "cancelled", changed_by, reason
        )
        header.status = "cancelled"
        return await self._repo.update(header)

    async def get_status_history(
        self, order_id: UUID
    ) -> list[PurchaseOrderStatusHistory]:
        return await self._repo.find_status_history_by_header_id(order_id)

    # ── internal helpers ────────────────────────────────────────────────

    async def _create_history(
        self,
        header_id: UUID,
        from_status: str,
        to_status: str,
        changed_by: UUID | None = None,
        reason: str | None = None,
    ) -> PurchaseOrderStatusHistory:
        history = PurchaseOrderStatusHistory(
            po_header_id=header_id,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            changed_at=datetime.utcnow(),
            reason=reason,
        )
        return await self._repo.create_status_history(history)

    def _recalculate_detail(self, detail: PurchaseOrderDetail) -> None:
        detail.total_price = detail.quantity_ordered * detail.unit_price
        detail.net_price = detail.total_price - detail.discount

    def _recalculate_header_totals(
        self, header: PurchaseOrderHeader, details: list[PurchaseOrderDetail] | None = None
    ) -> None:
        if details is not None:
            header.subtotal = sum(d.net_price for d in details if d.is_active)
        header.tax_amount = header.subtotal * header.tax_rate / 100
        if header.discount_type == "percentage":
            discount = header.subtotal * header.discount_value / 100
        else:
            discount = header.discount_value
        header.total = header.subtotal + header.tax_amount - discount + header.shipping_cost

    def _recalculate_totals(
        self, header: PurchaseOrderHeader, items: list[dict]
    ) -> None:
        subtotal = 0.0
        for item_data in items:
            qty = item_data.get("quantity_ordered", 0)
            price = item_data.get("unit_price", 0)
            disc = item_data.get("discount", 0)
            subtotal += qty * price - disc
        header.subtotal = subtotal
        header.tax_amount = subtotal * header.tax_rate / 100
        if header.discount_type == "percentage":
            discount = subtotal * header.discount_value / 100
        else:
            discount = header.discount_value
        header.total = subtotal + header.tax_amount - discount + header.shipping_cost
