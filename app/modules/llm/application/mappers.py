"""llm mappers — ORM ↔ domain"""
from __future__ import annotations
from typing import Any


def provider_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "name": row.name,
        "provider_type": row.provider_type,
        "base_url": row.base_url, "is_active": row.is_active,
    }


def model_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "provider_id": str(row.provider_id),
        "name": row.name, "display_name": row.display_name,
        "context_window": row.context_window,
        "max_output_tokens": row.max_output_tokens,
        "supports_streaming": row.supports_streaming,
        "supports_tools": row.supports_tools,
    }


def conversation_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "user_id": str(row.user_id),
        "title": row.title, "model_id": str(row.model_id),
        "status": row.status, "message_count": row.message_count,
        "total_tokens": row.total_tokens,
    }


def message_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "role": row.role,
        "content": row.content, "tokens_input": row.tokens_input,
        "tokens_output": row.tokens_output,
        "finish_reason": row.finish_reason,
    }
