"""relationships — build parent/child/prev/next from node list"""
from __future__ import annotations
import uuid
from typing import Any


def build_node_relationships(
    node_ids: list[uuid.UUID],
) -> list[dict[str, Any]]:
    """TH: สร้าง prev/next | EN: build prev/next relationships"""
    out: list[dict[str, Any]] = []
    n = len(node_ids)
    for i, nid in enumerate(node_ids):
        out.append({
            "id": nid,
            "prev_id": str(node_ids[i - 1]) if i > 0 else None,
            "next_id": str(node_ids[i + 1]) if i < n - 1 else None,
        })
    return out
