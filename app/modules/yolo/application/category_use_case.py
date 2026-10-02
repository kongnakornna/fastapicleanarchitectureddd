"""Category use case"""
from __future__ import annotations
import uuid
from typing import Any
import structlog
from app.modules.yolo.domain.category import CategoryTree

log = structlog.get_logger()


class CategoryUseCase:
    def __init__(self, repo: Any) -> None:
        self._repo = repo

    async def create_category(self, ctx: Any, payload: dict) -> dict:
        row = await self._repo.create(ctx, payload)
        return self._to_dict(row)

    async def get_category(self, ctx: Any, category_id: uuid.UUID) -> dict:
        row = await self._repo.find_by_id(ctx, category_id)
        if row is None:
            raise ValueError(f"category {category_id} not found")
        return self._to_dict(row)

    async def list_categories(self, ctx: Any,
                                parent_id: uuid.UUID | None = None) -> list[dict]:
        rows = await self._repo.find_children(ctx, parent_id)
        return [self._to_dict(r) for r in rows]

    async def get_tree(self, ctx: Any, root_id: uuid.UUID | None = None) -> dict:
        all_rows = await self._repo.find_all(ctx)
        tree = CategoryTree(all_rows)
        if tree.has_cycle():
            raise ValueError("category tree contains cycle")
        return {"root_id": str(root_id) if root_id else None,
                "items": tree.to_nested(root_id)}

    async def update_category(self, ctx: Any, category_id: uuid.UUID,
                                payload: dict) -> dict:
        row = await self._repo.update(ctx, category_id, payload)
        if row is None:
            raise ValueError(f"category {category_id} not found")
        return self._to_dict(row)

    async def move_category(self, ctx: Any, category_id: uuid.UUID,
                              new_parent_id: uuid.UUID | None) -> dict:
        all_rows = await self._repo.find_all(ctx)
        tree = CategoryTree(all_rows)
        if new_parent_id:
            descendants = {d.id for d in tree.descendants(category_id)}
            if new_parent_id in descendants or new_parent_id == category_id:
                raise ValueError("cannot move under own descendant")
        row = await self._repo.update(ctx, category_id,
                                        {"parent_id": new_parent_id})
        return self._to_dict(row)

    async def delete_category(self, ctx: Any, category_id: uuid.UUID,
                                cascade: bool = False) -> dict:
        if not cascade:
            children = await self._repo.find_children(ctx, category_id)
            if children:
                raise ValueError("category has children; use cascade=true")
        await self._repo.delete(ctx, category_id, cascade=cascade)
        return {"deleted": str(category_id), "cascade": cascade}

    @staticmethod
    def _to_dict(row: Any) -> dict:
        if hasattr(row, "to_dict"):
            return row.to_dict()
        return {"id": str(row.id),
                "parent_id": str(row.parent_id) if row.parent_id else None,
                "slug": row.slug, "name_th": row.name_th,
                "name_en": row.name_en, "description": row.description,
                "color": row.color, "sort_order": row.sort_order,
                "is_active": row.is_active}
