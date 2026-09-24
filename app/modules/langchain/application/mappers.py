"""langchain mappers — ORM → dict"""
from __future__ import annotations
from typing import Any


def chain_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "chain_type": row.chain_type,
        "version": row.version,
        "is_active": bool(row.is_active),
    }


def agent_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "agent_type": row.agent_type,
        "model": row.model,
        "max_iterations": int(row.max_iterations or 10),
        "is_active": bool(row.is_active),
    }


def memory_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "conversation_id": str(row.conversation_id),
        "memory_type": row.memory_type,
        "size_bytes": int(row.size_bytes or 0),
    }


def run_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "kind": row.kind,
        "target_id": str(row.target_id),
        "status": row.status,
        "latency_ms": int(row.latency_ms or 0),
        "tokens_used": int(row.tokens_used or 0),
        "cost_usd": str(row.cost_usd or "0"),
    }


def trace_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "run_id": str(row.run_id),
        "step": int(row.step or 0),
        "kind": row.kind,
        "latency_ms": int(row.latency_ms or 0),
    }
