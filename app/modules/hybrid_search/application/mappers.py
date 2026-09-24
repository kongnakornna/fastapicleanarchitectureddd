"""hybrid_search mappers — ORM → dict"""
from __future__ import annotations
from typing import Any


def config_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "fusion_type": row.fusion_type,
        "rrf_k": int(row.rrf_k or 60),
        "bm25_weight": float(row.bm25_weight or 0.5),
        "vector_weight": float(row.vector_weight or 0.5),
        "top_k": int(row.top_k or 10),
        "reranker_type": row.reranker_type,
        "is_active": bool(row.is_active),
    }


def query_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "config_id": str(row.config_id),
        "query_text": row.query_text or "",
        "latency_ms": int(row.latency_ms or 0),
        "result_count": int(row.result_count or 0),
    }


def result_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "query_id": str(row.query_id),
        "rank": int(row.rank or 0),
        "score": float(row.score or 0.0),
        "source_kind": row.source_kind,
        "source_id": row.source_id,
        "snippet": row.snippet or "",
    }


def ranking_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "query_id": str(row.query_id),
        "stage": row.stage,
        "source_kind": row.source_kind,
        "source_id": row.source_id,
        "raw_score": float(row.raw_score or 0.0),
        "normalized_score": float(row.normalized_score or 0.0),
        "rank": int(row.rank or 0),
    }


def rerank_log_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "query_id": str(row.query_id),
        "reranker_type": row.reranker_type,
        "input_count": int(row.input_count or 0),
        "output_count": int(row.output_count or 0),
        "latency_ms": int(row.latency_ms or 0),
    }
