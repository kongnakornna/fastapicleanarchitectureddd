"""structured_outputs mappers — ORM → dict"""
from __future__ import annotations
from typing import Any


def schema_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "description": row.description or "",
        "strategy": row.strategy,
        "strict": bool(row.strict),
        "version": row.version,
    }


def request_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "schema_id": str(row.schema_id),
        "model": row.model,
        "prompt": (row.prompt or "")[:200],
        "max_repairs": int(row.max_repairs or 0),
    }


def output_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "request_id": str(row.request_id),
        "is_valid": bool(row.is_valid),
        "attempts": int(row.attempts or 0),
        "tokens_used": int(row.tokens_used or 0),
    }


def validation_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "output_id": str(row.output_id),
        "attempt": int(row.attempt or 1),
        "passed": bool(row.passed),
        "errors_json": row.errors_json or "[]",
    }


def repair_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "output_id": str(row.output_id),
        "attempt": int(row.attempt or 1),
        "feedback": row.feedback or "",
    }
