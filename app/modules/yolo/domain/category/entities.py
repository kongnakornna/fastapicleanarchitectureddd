"""Category entities"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class Category:
    id: uuid.UUID
    tenant_id: uuid.UUID
    parent_id: uuid.UUID | None
    slug: str
    name_th: str
    name_en: str
    description: str = ""
    icon: str | None = None
    color: str = "#3B82F6"
    sort_order: int = 0
    is_active: bool = True
    class_count: int = 0
    extra_json: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {"id": str(self.id),
                "parent_id": str(self.parent_id) if self.parent_id else None,
                "slug": self.slug, "name_th": self.name_th,
                "name_en": self.name_en, "description": self.description,
                "icon": self.icon, "color": self.color,
                "sort_order": self.sort_order, "is_active": self.is_active,
                "class_count": self.class_count}


class CategoryTree:
    def __init__(self, categories: list[Any]) -> None:
        self._by_parent: dict[uuid.UUID | None, list[Any]] = {}
        self._by_id: dict[uuid.UUID, Any] = {}
        for c in categories:
            self._by_parent.setdefault(c.parent_id, []).append(c)
            self._by_id[c.id] = c

    def children(self, parent_id: uuid.UUID | None) -> list[Any]:
        items = list(self._by_parent.get(parent_id, []))
        items.sort(key=lambda c: (c.sort_order, c.name_th))
        return items

    def ancestors(self, category_id: uuid.UUID) -> list[Any]:
        result: list[Any] = []
        current = self._by_id.get(category_id)
        while current and current.parent_id:
            parent = self._by_id.get(current.parent_id)
            if parent is None:
                break
            result.append(parent)
            current = parent
        return list(reversed(result))

    def descendants(self, category_id: uuid.UUID) -> list[Any]:
        result: list[Any] = []
        stack = [category_id]
        while stack:
            cid = stack.pop()
            for child in self._by_parent.get(cid, []):
                result.append(child)
                stack.append(child.id)
        return result

    def depth(self, category_id: uuid.UUID) -> int:
        return len(self.ancestors(category_id))

    def to_nested(self, parent_id: uuid.UUID | None = None) -> list[dict]:
        result: list[dict] = []
        for c in self.children(parent_id):
            node = c.to_dict() if hasattr(c, "to_dict") else dict(c)
            node["children"] = self.to_nested(c.id)
            result.append(node)
        return result

    def has_cycle(self) -> bool:
        for c in self._by_id.values():
            seen: set[uuid.UUID] = set()
            current = c
            while current and current.parent_id:
                if current.id in seen:
                    return True
                seen.add(current.id)
                current = self._by_id.get(current.parent_id)
        return False
