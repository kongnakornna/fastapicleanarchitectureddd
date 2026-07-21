from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.purchaseorder.domain.entities.purchase_order_detail import (
    PurchaseOrderDetail,
)
from app.modules.purchaseorder.domain.entities.purchase_order_header import (
    PurchaseOrderHeader,
)
from app.modules.purchaseorder.domain.entities.purchase_order_status_history import (
    PurchaseOrderStatusHistory,
)


class PurchaseOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Header ──────────────────────────────────────────────────────────

    async def find_by_id(self, po_id: UUID) -> PurchaseOrderHeader | None:
        result = await self._session.execute(
            select(PurchaseOrderHeader).where(PurchaseOrderHeader.id == po_id)
        )
        return result.scalar_one_or_none()

    async def find_detail_by_id(self, detail_id: UUID) -> PurchaseOrderDetail | None:
        result = await self._session.execute(
            select(PurchaseOrderDetail).where(PurchaseOrderDetail.id == detail_id)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        supplier_id: UUID | None = None,
        status: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[PurchaseOrderHeader], int]:
        base = (
            select(PurchaseOrderHeader)
            .where(PurchaseOrderHeader.is_active.is_(True))
        )
        if supplier_id:
            base = base.where(PurchaseOrderHeader.supplier_id == supplier_id)
        if status:
            base = base.where(PurchaseOrderHeader.status == status)
        if date_from:
            base = base.where(PurchaseOrderHeader.po_date >= date_from)
        if date_to:
            base = base.where(PurchaseOrderHeader.po_date <= date_to)

        count_result = await self._session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = count_result.scalar() or 0

        query = (
            base.order_by(PurchaseOrderHeader.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, header: PurchaseOrderHeader) -> PurchaseOrderHeader:
        self._session.add(header)
        await self._session.flush()
        return header

    async def update(self, header: PurchaseOrderHeader) -> PurchaseOrderHeader:
        await self._session.flush()
        return header

    async def delete(self, po_id: UUID) -> bool:
        header = await self.find_by_id(po_id)
        if header:
            header.is_active = False
            await self._session.flush()
            return True
        return False

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(PurchaseOrderHeader)
            .where(PurchaseOrderHeader.is_active.is_(True))
        )
        return result.scalar() or 0

    # ── Detail ──────────────────────────────────────────────────────────

    async def find_details_by_header_id(
        self, header_id: UUID
    ) -> list[PurchaseOrderDetail]:
        result = await self._session.execute(
            select(PurchaseOrderDetail).where(
                PurchaseOrderDetail.po_header_id == header_id,
                PurchaseOrderDetail.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def create_detail(self, detail: PurchaseOrderDetail) -> PurchaseOrderDetail:
        self._session.add(detail)
        await self._session.flush()
        return detail

    async def update_detail(self, detail: PurchaseOrderDetail) -> PurchaseOrderDetail:
        await self._session.flush()
        return detail

    # ── Status History ──────────────────────────────────────────────────

    async def find_status_history_by_header_id(
        self, header_id: UUID
    ) -> list[PurchaseOrderStatusHistory]:
        result = await self._session.execute(
            select(PurchaseOrderStatusHistory)
            .where(PurchaseOrderStatusHistory.po_header_id == header_id)
            .order_by(PurchaseOrderStatusHistory.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_status_history(
        self, history: PurchaseOrderStatusHistory
    ) -> PurchaseOrderStatusHistory:
        self._session.add(history)
        await self._session.flush()
        return history
