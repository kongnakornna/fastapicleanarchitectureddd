from __future__ import annotations

from uuid import UUID

from app.modules.items.domain.entities.item import Item
from app.modules.items.infrastructure.item_repository import ItemRepository


class ItemUseCase:
    def __init__(self, item_repository: ItemRepository) -> None:
        self._item_repo = item_repository

    async def get_items(
        self, owner_id: UUID | None = None, page: int = 1, page_size: int = 10
    ) -> tuple[list[Item], int]:
        if owner_id:
            return await self._item_repo.find_by_owner_id(owner_id, page, page_size)
        return await self._item_repo.find_all_paginated(page, page_size)

    async def get_item(self, item_id: UUID) -> Item | None:
        return await self._item_repo.find_by_id(item_id)

    async def create_item(self, item: Item) -> Item:
        return await self._item_repo.create(item)

    async def update_item(self, item_id: UUID, values: dict) -> Item | None:
        item = await self._item_repo.find_by_id(item_id)
        if not item:
            return None
        for key, value in values.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        return await self._item_repo.update(item)

    async def delete_item(self, item_id: UUID) -> bool:
        return await self._item_repo.delete(item_id)

    async def count(self) -> int:
        return await self._item_repo.count()

    async def count_by_owner_id(self, owner_id: UUID) -> int:
        return await self._item_repo.count_by_owner_id(owner_id)
