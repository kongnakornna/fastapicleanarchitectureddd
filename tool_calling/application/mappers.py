"""tool_calling mappers"""
from __future__ import annotations
from typing import Any


def tool_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "name": row.name,
        "description": row.description or "", "kind": row.kind,
        "risk_level": row.risk_level, "visibility": row.visibility,
        "timeout_seconds": row.timeout_seconds, "is_active": row.is_active,
    }
