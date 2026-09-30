"""bigo mappers"""
from __future__ import annotations
from typing import Any


def profile_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "function_name": row.function_name,
            "module": row.module, "complexity": row.complexity,
            "sample_size": row.sample_size, "avg_ms": row.avg_ms,
            "p95_ms": row.p95_ms, "memory_peak_mb": row.memory_peak_mb,
            "notes": row.notes,
            "captured_at": row.captured_at.isoformat() if row.captured_at else ""}


def snapshot_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "process_id": row.process_id,
            "rss_mb": row.rss_mb, "vms_mb": row.vms_mb,
            "percent": row.percent, "pressure": row.pressure,
            "captured_at": row.captured_at.isoformat() if row.captured_at else ""}


def leak_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "location": row.location,
            "leak_type": row.leak_type,
            "growth_mb_per_hour": row.growth_mb_per_hour,
            "current_bytes": row.current_bytes, "samples": row.samples,
            "status": row.status,
            "detected_at": row.detected_at.isoformat() if row.detected_at else ""}


def topic_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "name": row.name, "partitions": row.partitions,
            "replication_factor": row.replication_factor,
            "retention_ms": row.retention_ms,
            "max_message_bytes": row.max_message_bytes,
            "is_active": row.is_active}


def queue_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "topic": row.topic, "partition": row.partition,
            "current_offset": row.current_offset,
            "log_end_offset": row.log_end_offset, "lag": row.lag,
            "health": row.health,
            "captured_at": row.captured_at.isoformat() if row.captured_at else ""}


def consumer_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "group_id": row.group_id, "topic": row.topic,
            "member_count": row.member_count, "total_lag": row.total_lag,
            "health": row.health,
            "last_commit_at": row.last_commit_at.isoformat() if row.last_commit_at else None}


def pipeline_report_to_dict(row: Any) -> dict[str, Any]:
    return {"id": str(row.id), "trace_id": row.trace_id, "n": row.n,
            "complexity": row.complexity, "status": row.status,
            "priority": row.priority, "rss_mb": row.rss_mb,
            "pressure": row.pressure, "duration_ms": row.duration_ms,
            "kafka_partition": row.kafka_partition,
            "kafka_sent": row.kafka_sent}
