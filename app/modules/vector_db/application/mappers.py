"""vector_db mappers — ORM → dict"""
from __future__ import annotations
from typing import Any


def collection_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "name": row.name,
        "dimension": row.dimension,
        "metric": row.metric, "backend": row.backend,
        "is_active": bool(row.is_active),
    }


def vector_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "collection_id": str(row.collection_id),
        "source_id": row.source_id,
        "norm": float(row.norm or 0.0),
    }


def index_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "collection_id": str(row.collection_id),
        "name": row.name, "index_type": row.index_type,
        "build_status": row.build_status,
        "size_bytes": row.size_bytes or 0,
    }


def stats_to_dict(row: Any) -> dict[str, Any]:
    return {
        "collection_id": str(row.collection_id),
        "vector_count": row.vector_count or 0,
        "size_bytes": row.size_bytes or 0,
        "avg_latency_ms": float(row.avg_latency_ms or 0.0),
    }
