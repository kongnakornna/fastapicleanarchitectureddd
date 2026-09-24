"""llamaindex mappers — ORM → dict"""
from __future__ import annotations
from typing import Any


def index_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "index_type": row.index_type,
        "embed_model": row.embed_model,
        "storage_kind": row.storage_kind,
        "is_active": bool(row.is_active),
    }


def node_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "index_id": str(row.index_id),
        "node_type": row.node_type,
        "ordinal": int(row.ordinal or 0),
        "content": (row.content or "")[:200],
    }


def query_engine_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "index_id": str(row.index_id),
        "name": row.name,
        "retriever_type": row.retriever_type,
        "top_k": int(row.top_k or 5),
        "response_mode": row.response_mode,
        "similarity_top_k": int(row.similarity_top_k or 5),
    }


def document_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "index_id": str(row.index_id),
        "source_uri": row.source_uri or "",
        "mime_type": row.mime_type or "",
        "title": row.title or "",
        "hash": row.hash or "",
        "status": row.status,
    }


def run_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "query_engine_id": str(row.query_engine_id),
        "query": (row.query or "")[:200],
        "answer": (row.answer or "")[:200],
        "latency_ms": int(row.latency_ms or 0),
        "tokens_used": int(row.tokens_used or 0),
    }
