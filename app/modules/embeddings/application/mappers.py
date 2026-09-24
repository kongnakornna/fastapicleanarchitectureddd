"""embeddings mappers — ORM → dict"""
from __future__ import annotations
from typing import Any


def provider_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "name": row.name,
        "provider_type": row.provider_type,
        "base_url": row.base_url or "",
        "priority": row.priority or 100,
        "is_active": bool(row.is_active),
    }


def model_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "name": row.name,
        "display_name": row.display_name or "",
        "dimension": row.dimension,
        "max_tokens": row.max_tokens or 8192,
        "normalize": bool(row.normalize),
        "is_active": bool(row.is_active),
    }


def vector_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "model_id": str(row.model_id),
        "source_hash": row.source_hash,
        "dimension": row.dimension,
    }


def batch_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "model_id": str(row.model_id),
        "total": row.total or 0,
        "completed": row.completed or 0,
        "failed": row.failed or 0,
        "status": row.status,
    }
