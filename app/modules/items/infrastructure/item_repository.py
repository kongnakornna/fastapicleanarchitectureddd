from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.items.domain.entities.item import Item


class ItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, item_id: UUID) -> Item | None:
        result = await self._session.execute(
            select(Item).where(Item.id == item_id)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Item], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Item).where(Item.is_active.is_(True))
        )
        total = count_result.scalar() or 0
        query = (
            select(Item)
            .where(Item.is_active.is_(True))
            .order_by(Item.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def find_by_owner_id(
        self, owner_id: UUID, page: int = 1, page_size: int = 10
    ) -> tuple[list[Item], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Item).where(
                Item.owner_id == owner_id,
                Item.is_active.is_(True),
            )
        )
        total = count_result.scalar() or 0
        query = (
            select(Item)
            .where(Item.owner_id == owner_id, Item.is_active.is_(True))
            .order_by(Item.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Item).where(Item.is_active.is_(True))
        )
        return result.scalar() or 0

    async def count_by_owner_id(self, owner_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Item).where(
                Item.owner_id == owner_id,
                Item.is_active.is_(True),
            )
        )
        return result.scalar() or 0

    async def create(self, item: Item) -> Item:
        self._session.add(item)
        await self._session.flush()
        return item

    async def update(self, item: Item) -> Item:
        await self._session.flush()
        return item

    async def delete(self, item_id: UUID) -> bool:
        item = await self.find_by_id(item_id)
        if item:
            item.is_active = False
            await self._session.flush()
            return True
        return False
