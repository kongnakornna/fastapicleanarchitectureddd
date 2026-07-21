from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.wos.domain.entities.order import WosOrder


class WosOrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, order_id: UUID) -> WosOrder | None:
        result = await self._session.execute(
            select(WosOrder).where(WosOrder.id == order_id)
        )
        return result.scalar_one_or_none()

    async def find_by_order_number(self, order_number: str) -> WosOrder | None:
        result = await self._session.execute(
            select(WosOrder).where(WosOrder.order_number == order_number)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[WosOrder], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(WosOrder).where(WosOrder.is_active.is_(True))
        )
        total = count_result.scalar() or 0
        query = (
            select(WosOrder)
            .where(WosOrder.is_active.is_(True))
            .order_by(WosOrder.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def update_status(self, order: WosOrder, status: str) -> WosOrder:
        order.status = status
        await self._session.flush()
        return order

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(WosOrder).where(WosOrder.is_active.is_(True))
        )
        return result.scalar() or 0

    async def create(self, order: WosOrder) -> WosOrder:
        self._session.add(order)
        await self._session.flush()
        return order

    async def update(self, order: WosOrder) -> WosOrder:
        await self._session.flush()
        return order

    async def delete(self, order_id: UUID) -> bool:
        order = await self.find_by_id(order_id)
        if order:
            order.is_active = False
            await self._session.flush()
            return True
        return False
