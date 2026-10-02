"""Unit tests for category tree"""
from __future__ import annotations
import uuid
from dataclasses import dataclass
import pytest
from app.modules.yolo.domain.category import CategoryTree

pytestmark = pytest.mark.unit


@dataclass
class _Cat:
    id: uuid.UUID
    parent_id: uuid.UUID | None
    slug: str
    name_th: str
    sort_order: int = 0

    def to_dict(self):
        return {"id": str(self.id),
                "parent_id": str(self.parent_id) if self.parent_id else None,
                "slug": self.slug, "name_th": self.name_th}


def test_tree_children():
    root = _Cat(uuid.uuid4(), None, "root", "Root")
    child = _Cat(uuid.uuid4(), root.id, "child", "Child")
    tree = CategoryTree([root, child])
    assert len(tree.children(None)) == 1
    assert len(tree.children(root.id)) == 1


def test_tree_ancestors():
    r = _Cat(uuid.uuid4(), None, "r", "R")
    c1 = _Cat(uuid.uuid4(), r.id, "c1", "C1")
    c2 = _Cat(uuid.uuid4(), c1.id, "c2", "C2")
    tree = CategoryTree([r, c1, c2])
    ancestors = tree.ancestors(c2.id)
    assert len(ancestors) == 2


def test_tree_depth():
    r = _Cat(uuid.uuid4(), None, "r", "R")
    c1 = _Cat(uuid.uuid4(), r.id, "c1", "C1")
    tree = CategoryTree([r, c1])
    assert tree.depth(r.id) == 0
    assert tree.depth(c1.id) == 1
