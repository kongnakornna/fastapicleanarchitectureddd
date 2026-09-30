"""bigo use cases — Monitoring orchestration"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import structlog

from app.modules.bigo.application.interfaces import (
    BackpressureController, CachePort, ComplexityAnalyzer, EventBus,
    KafkaAdmin, KafkaConsumerRepository, KafkaQueueRepository,
    KafkaTopicRepository, MemoryProfiler, MemoryRepository,
    MetricRepository, PipelineReportRepository,
    ProfileRepository, RequestContext,
)
from app.modules.bigo.domain.enums import KafkaHealth, MemoryPressure
from app.modules.bigo.domain.events import (
    AlertTriggered, ProfileCaptured,
)
from app.modules.bigo.domain.exceptions import KafkaConnectionError
from app.modules.bigo.infrastructure.models import (
    KafkaConsumerModel, KafkaQueueModel, MemoryLeakModel,
    MemorySnapshotModel, MetricModel, ProfileModel,
)

log = structlog.get_logger()


class BigOUseCase:
    """TH: use cases สำหรับ Big-O monitoring"""

    def __init__(
        self,
        metric_repo: MetricRepository,
        profile_repo: ProfileRepository,
        memory_repo: MemoryRepository,
        topic_repo: KafkaTopicRepository,
        queue_repo: KafkaQueueRepository,
        consumer_repo: KafkaConsumerRepository,
        complexity: ComplexityAnalyzer,
        memory: MemoryProfiler,
        kafka: KafkaAdmin,
        backpressure: BackpressureController,
        cache: CachePort,
        event_bus: EventBus,
        pipeline_report_repo: PipelineReportRepository | None = None,
    ) -> None:
        self._metric_repo = metric_repo
        self._profile_repo = profile_repo
        self._memory_repo = memory_repo
        self._topic_repo = topic_repo
        self._queue_repo = queue_repo
        self._consumer_repo = consumer_repo
        self._complexity = complexity
        self._memory = memory
        self._kafka = kafka
        self._bp = backpressure
        self._cache = cache
        self._bus = event_bus
        self._pipeline_reports = pipeline_report_repo

    async def analyze_function(
        self, ctx: RequestContext, *,
        fn: Any, name: str = "", module: str = "",
        sizes: list[int] | None = None,
    ) -> dict[str, Any]:
        log.info("bigo.analyze.start", name=name)
        try:
            result = self._complexity.analyze(fn, sizes=sizes)
            row = ProfileModel(
                tenant_id=ctx.tenant_id,
                function_name=name or getattr(fn, "__name__", "unknown"),
                module=module or getattr(fn, "__module__", ""),
                complexity=result.notation,
                sample_size=result.sample_size,
                avg_ms=0.0, p95_ms=0.0, memory_peak_mb=0.0,
                notes=result.notes,
            )
            saved = await self._profile_repo.create(ctx, row)
            await self._bus.publish(ProfileCaptured(
                profile_id=saved.id, tenant_id=ctx.tenant_id,
                function_name=saved.function_name,
                complexity=saved.complexity,
                sample_size=saved.sample_size,
            ))
            return {
                "profile_id": str(saved.id),
                "function_name": saved.function_name,
                "complexity": saved.complexity,
                "sample_size": saved.sample_size,
                "r_squared": result.r_squared,
                "coefficients": dict(result.coefficients),
            }
        except Exception:
            log.exception("bigo.analyze.failed")
            raise

    async def list_profiles(
        self, ctx: RequestContext, *,
        function_name: str = "", since_days: int = 7, limit: int = 100,
    ) -> list[dict[str, Any]]:
        if function_name:
            rows = await self._profile_repo.find_by_function(ctx, function_name, limit)
        else:
            since = datetime.now(UTC) - timedelta(days=since_days)
            rows = await self._profile_repo.find_recent(ctx, since, limit)
        return [
            {"id": str(r.id), "function_name": r.function_name,
             "module": r.module, "complexity": r.complexity,
             "sample_size": r.sample_size, "avg_ms": r.avg_ms,
             "p95_ms": r.p95_ms,
             "captured_at": r.captured_at.isoformat() if r.captured_at else ""}
            for r in rows
        ]

    async def take_memory_snapshot(self, ctx: RequestContext) -> dict[str, Any]:
        try:
            info = self._memory.info()
            rss_mb = float(info.get("rss_mb", 0.0))
            vms_mb = float(info.get("vms_mb", 0.0))
            percent = float(info.get("percent", 0.0))
            pressure = self._classify_pressure(rss_mb, percent)
            allocations = self._memory.snapshot()
            row = MemorySnapshotModel(
                tenant_id=ctx.tenant_id, process_id=0,
                rss_mb=rss_mb, vms_mb=vms_mb, percent=percent,
                pressure=pressure.value,
                top_allocations_json=str(allocations[:20]),
            )
            saved = await self._memory_repo.save_snapshot(ctx, row)
            return {
                "snapshot_id": str(saved.id),
                "rss_mb": rss_mb, "vms_mb": vms_mb,
                "percent": percent, "pressure": pressure.value,
                "top_allocations": allocations[:10],
            }
        except Exception:
            log.exception("bigo.snapshot.failed")
            raise

    async def detect_memory_leaks(
        self, ctx: RequestContext, *,
        threshold_mb_per_hour: float = 10.0,
    ) -> list[dict[str, Any]]:
        from app.modules.bigo.domain.helpers.memory_analyzer import detect_leaks
        since = datetime.now(UTC) - timedelta(hours=24)
        snaps = await self._memory_repo.find_snapshots(ctx, since, 50)
        snapshots_data = [
            [(s.top_allocations_json, int(s.rss_mb * 1024 * 1024), 0)]
            for s in snaps
        ]
        leaks = detect_leaks(snapshots_data, threshold_mb_per_hour)
        saved_leaks: list[dict[str, Any]] = []
        for lk in leaks:
            row = MemoryLeakModel(
                tenant_id=ctx.tenant_id,
                location=lk["location"][:500],
                leak_type="UNKNOWN",
                growth_mb_per_hour=lk["growth_mb_per_hour"],
                current_bytes=lk["current_bytes"],
                samples=lk["samples"], status="OPEN",
            )
            saved = await self._memory_repo.save_leak(ctx, row)
            saved_leaks.append({
                "id": str(saved.id),
                "location": saved.location,
                "growth_mb_per_hour": saved.growth_mb_per_hour,
                "status": saved.status,
            })
        return saved_leaks

    async def list_leaks(
        self, ctx: RequestContext, *, status: str = "OPEN", limit: int = 50,
    ) -> list[dict[str, Any]]:
        rows = await self._memory_repo.find_leaks(ctx, status, limit)
        return [
            {"id": str(r.id), "location": r.location,
             "leak_type": r.leak_type,
             "growth_mb_per_hour": r.growth_mb_per_hour,
             "current_bytes": r.current_bytes, "status": r.status}
            for r in rows
        ]

    async def resolve_leak(
        self, ctx: RequestContext, leak_id: uuid.UUID,
    ) -> dict[str, Any]:
        ok_flag = await self._memory_repo.update_leak_status(ctx, leak_id, "RESOLVED")
        return {"id": str(leak_id), "status": "RESOLVED", "updated": ok_flag}

    async def register_topic(
        self, ctx: RequestContext, *,
        name: str, partitions: int = 3, replication: int = 1,
        retention_ms: int = 604800000, max_message_bytes: int = 1048576,
    ) -> dict[str, Any]:
        existing = await self._topic_repo.find_by_name(ctx, name)
        if existing:
            return {"id": str(existing.id), "name": existing.name,
                    "partitions": existing.partitions, "already_exists": True}
        row = KafkaTopicModel(
            tenant_id=ctx.tenant_id, name=name, partitions=partitions,
            replication_factor=replication, retention_ms=retention_ms,
            max_message_bytes=max_message_bytes, is_active=True,
        )
        saved = await self._topic_repo.save(ctx, row)
        try:
            await self._kafka.create_topic(name, partitions, replication)
        except Exception as exc:
            log.warning("bigo.kafka.create_failed", err=str(exc))
        return {"id": str(saved.id), "name": saved.name,
                "partitions": saved.partitions,
                "replication_factor": saved.replication_factor,
                "already_exists": False}

    async def list_topics(self, ctx: RequestContext) -> list[dict[str, Any]]:
        rows = await self._topic_repo.find_all_active(ctx)
        return [
            {"id": str(r.id), "name": r.name, "partitions": r.partitions,
             "replication_factor": r.replication_factor, "is_active": r.is_active}
            for r in rows
        ]

    async def monitor_lag(
        self, ctx: RequestContext, *,
        group_id: str, topic: str, threshold: int = 10000,
    ) -> dict[str, Any]:
        try:
            info = await self._kafka.consumer_lag(group_id, topic)
        except Exception as exc:
            raise KafkaConnectionError(str(exc)) from exc
        total_lag = int(info.get("total_lag", 0))
        health = self._classify_kafka_health(total_lag, threshold)
        for p in info.get("partitions", []):
            q_row = KafkaQueueModel(
                tenant_id=ctx.tenant_id, topic=topic,
                partition=int(p.get("partition", 0)),
                current_offset=int(p.get("current_offset", 0)),
                log_end_offset=int(p.get("log_end_offset", 0)),
                lag=int(p.get("lag", 0)), health=health.value,
            )
            await self._queue_repo.save(ctx, q_row)
        c_row = KafkaConsumerModel(
            tenant_id=ctx.tenant_id, group_id=group_id, topic=topic,
            member_count=int(info.get("member_count", 0)),
            total_lag=total_lag, health=health.value,
            last_commit_at=datetime.now(UTC),
        )
        saved = await self._consumer_repo.save(ctx, c_row)
        return {"consumer_id": str(saved.id), "topic": topic,
                "group_id": group_id, "total_lag": total_lag,
                "health": health.value,
                "partitions": info.get("partitions", [])}

    async def activate_backpressure(
        self, ctx: RequestContext, *,
        topic: str, reason: str = "lag_exceeded",
    ) -> dict[str, Any]:
        try:
            await self._bp.activate(topic, reason)
        except Exception as exc:
            log.warning("bigo.bp.activate_failed", err=str(exc))
        return {"topic": topic, "active": True, "reason": reason}

    async def deactivate_backpressure(
        self, ctx: RequestContext, topic: str,
    ) -> dict[str, Any]:
        try:
            await self._bp.deactivate(topic)
        except Exception as exc:
            log.warning("bigo.bp.deactivate_failed", err=str(exc))
        return {"topic": topic, "active": False}

    async def record_metric(
        self, ctx: RequestContext, *,
        kind: str, name: str, value: float,
        unit: str = "", labels: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        row = MetricModel(
            tenant_id=ctx.tenant_id, kind=kind, name=name,
            value=value, unit=unit, labels_json=str(labels or {}),
        )
        saved = await self._metric_repo.create(ctx, row)
        return {"id": str(saved.id), "kind": saved.kind,
                "name": saved.name, "value": saved.value,
                "unit": saved.unit}

    async def get_metrics(
        self, ctx: RequestContext, *,
        kind: str = "", days: int = 1, limit: int = 500,
    ) -> list[dict[str, Any]]:
        since = datetime.now(UTC) - timedelta(days=days)
        rows = await self._metric_repo.find_by_kind(ctx, kind, since, limit)
        return [
            {"id": str(r.id), "kind": r.kind, "name": r.name,
             "value": r.value, "unit": r.unit,
             "captured_at": r.captured_at.isoformat() if r.captured_at else ""}
            for r in rows
        ]

    async def trigger_alert(
        self, ctx: RequestContext, *,
        severity: str, kind: str, message: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        alert_id = uuid.uuid4()
        await self._bus.publish(AlertTriggered(
            alert_id=alert_id, tenant_id=ctx.tenant_id,
            severity=severity, kind=kind, message=message,
            payload=payload or {},
        ))
        return {"alert_id": str(alert_id), "severity": severity,
                "kind": kind, "message": message}

    def _classify_pressure(self, rss_mb: float, percent: float) -> MemoryPressure:
        if rss_mb >= 4096 or percent >= 95:
            return MemoryPressure.OOM
        if rss_mb >= 2048 or percent >= 85:
            return MemoryPressure.CRITICAL
        if rss_mb >= 1024 or percent >= 70:
            return MemoryPressure.HIGH
        if rss_mb >= 512 or percent >= 50:
            return MemoryPressure.ELEVATED
        return MemoryPressure.NORMAL

    def _classify_kafka_health(self, lag: int, threshold: int) -> KafkaHealth:
        if lag <= 0:
            return KafkaHealth.HEALTHY
        if lag < threshold * 0.5:
            return KafkaHealth.HEALTHY
        if lag < threshold:
            return KafkaHealth.WARNING
        if lag < threshold * 2:
            return KafkaHealth.DEGRADED
        return KafkaHealth.CRITICAL
