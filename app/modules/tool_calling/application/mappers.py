"""tool_calling mappers — ORM → dict"""
from __future__ import annotations
from typing import Any


def tool_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "description": row.description or "",
        "kind": row.kind,
        "risk_level": row.risk_level,
        "visibility": row.visibility,
        "timeout_seconds": row.timeout_seconds,
        "is_active": row.is_active,
    }


def invocation_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "tool_id": str(row.tool_id),
        "tool_name": row.tool_name or "",
        "status": row.status,
        "latency_ms": row.latency_ms or 0,
        "error_code": row.error_code or "",
    }


def permission_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "tool_id": str(row.tool_id),
        "role": row.role,
        "allowed": row.allowed,
    }
