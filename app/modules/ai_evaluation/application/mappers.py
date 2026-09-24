"""ai_evaluation mappers — ORM → dict"""
from __future__ import annotations
from typing import Any


def dataset_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "name": row.name,
        "description": row.description or "",
        "task_type": row.task_type,
        "case_count": row.case_count or 0,
    }


def case_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "dataset_id": str(row.dataset_id),
        "question": row.question or "",
        "ground_truth": row.ground_truth or "",
    }


def run_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "dataset_id": str(row.dataset_id),
        "target_kind": row.target_kind,
        "target_model": row.target_model or "",
        "status": row.status,
        "case_count": row.case_count or 0,
        "completed_count": row.completed_count or 0,
        "failed_count": row.failed_count or 0,
        "duration_ms": row.duration_ms or 0,
        "total_cost_usd": str(row.total_cost_usd or "0"),
    }


def metric_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "name": row.name,
        "kind": row.kind,
        "higher_is_better": bool(row.higher_is_better),
        "range_min": float(row.range_min or 0.0),
        "range_max": float(row.range_max or 1.0),
        "description": row.description or "",
    }


def result_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "run_id": str(row.run_id),
        "case_id": str(row.case_id),
        "metric_name": row.metric_name,
        "score": float(row.score or 0.0),
        "confidence": float(row.confidence or 1.0),
    }


def report_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": str(row.id), "run_id": str(row.run_id),
        "summary_json": row.summary_json or "{}",
        "passed": bool(row.passed),
    }
