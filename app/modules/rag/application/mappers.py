"""rag mappers — ORM → dict"""
from __future__ import annotations
from typing import Any


def document_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "source_uri": row.source_uri or "",
        "mime_type": row.mime_type or "",
        "title": row.title or "",
        "status": row.status,
        "size_bytes": row.size_bytes or 0,
        "chunk_count": row.chunk_count or 0,
    }


def chunk_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "document_id": str(row.document_id),
        "ordinal": row.ordinal or 0,
        "content": row.content or "",
        "token_count": row.token_count or 0,
    }


def pipeline_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "name": row.name,
        "chunker_type": row.chunker_type,
        "chunk_size": row.chunk_size or 512,
        "chunk_overlap": row.chunk_overlap or 50,
        "retriever_type": row.retriever_type,
        "top_k": row.top_k or 5,
        "reranker_type": row.reranker_type,
        "embedding_model": row.embedding_model or "",
        "generation_model": row.generation_model or "",
        "is_active": bool(row.is_active),
    }


def run_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "query": row.query or "",
        "answer": row.answer or "",
        "model_name": row.model_name or "",
        "latency_ms": row.latency_ms or 0,
        "total_tokens": row.total_tokens or 0,
        "cost_usd": str(row.cost_usd or "0"),
        "status": row.status,
    }


def citation_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "run_id": str(row.run_id),
        "chunk_id": str(row.chunk_id),
        "document_id": str(row.document_id),
        "score": float(row.score or 0.0),
        "rank": row.rank or 0,
        "snippet": row.snippet or "",
    }
