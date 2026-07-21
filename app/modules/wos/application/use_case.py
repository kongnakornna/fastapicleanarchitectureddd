from __future__ import annotations

from uuid import UUID

from app.modules.wos.domain.entities.order import WosOrder
from app.modules.wos.infrastructure.order_repository import WosOrderRepository

VALID_STATUSES = ("pending", "confirmed", "shipped", "delivered", "cancelled")
STATUS_TRANSITIONS: dict[str, tuple[str, ...]] = {
    "pending": ("confirmed", "cancelled"),
    "confirmed": ("shipped", "cancelled"),
    "shipped": ("delivered",),
    "delivered": (),
    "cancelled": (),
}


class WosUseCase:
    def __init__(self, order_repository: WosOrderRepository) -> None:
        self._order_repo = order_repository

    async def get_orders(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[WosOrder], int]:
        return await self._order_repo.find_all_paginated(page, page_size)

    async def get_order(self, order_id: UUID) -> WosOrder | None:
        return await self._order_repo.find_by_id(order_id)

    async def get_by_order_number(self, order_number: str) -> WosOrder | None:
        return await self._order_repo.find_by_order_number(order_number)

    async def create_order(self, order: WosOrder) -> WosOrder:
        return await self._order_repo.create(order)

    async def update_order_status(self, order_id: UUID, new_status: str) -> WosOrder | None:
        if new_status not in VALID_STATUSES:
            return None
        order = await self._order_repo.find_by_id(order_id)
        if not order:
            return None
        allowed = STATUS_TRANSITIONS.get(order.status, ())
        if new_status not in allowed:
            return None
        return await self._order_repo.update_status(order, new_status)

    async def count(self) -> int:
        return await self._order_repo.count()
