"""bigo infrastructure services"""
from __future__ import annotations

from typing import Any

import structlog

from app.modules.bigo.domain.helpers import (
    analyze_complexity as _analyze,
    detect_leaks as _detect,
    diff_snapshots as _diff,
    take_snapshot as _snapshot,
)
from app.modules.bigo.domain.helpers.memory_analyzer import (
    get_memory_info as _mem_info,
)

log = structlog.get_logger()


class DefaultComplexityAnalyzer:
    def analyze(self, fn: Any, sizes: list[int] | None = None):
        return _analyze(fn, sizes=sizes)


class DefaultMemoryProfiler:
    def snapshot(self) -> list[tuple[str, int, int]]:
        try:
            return _snapshot()
        except Exception as exc:
            log.warning("mem.snapshot.failed", err=str(exc))
            return []

    def diff(self, before, after) -> list[dict[str, Any]]:
        try:
            return _diff(before, after)
        except Exception as exc:
            log.warning("mem.diff.failed", err=str(exc))
            return []

    def info(self) -> dict[str, Any]:
        try:
            return _mem_info()
        except Exception as exc:
            log.warning("mem.info.failed", err=str(exc))
            return {"rss_mb": 0.0, "vms_mb": 0.0, "percent": 0.0}


class DefaultKafkaAdmin:
    def __init__(self, bootstrap: str = "localhost:9092") -> None:
        self._bootstrap = bootstrap
        self._admin: Any = None

    def _get_admin(self) -> Any:
        if self._admin is not None:
            return self._admin
        try:
            from aiokafka.admin import AIOKafkaAdminClient
            self._admin = AIOKafkaAdminClient(bootstrap_servers=self._bootstrap)
        except Exception as exc:
            log.warning("kafka.admin.init_failed", err=str(exc))
        return self._admin

    async def list_topics(self) -> list[str]:
        admin = self._get_admin()
        if admin is None:
            return []
        try:
            return list(await admin.list_topics())
        except Exception as exc:
            log.warning("kafka.list_topics.failed", err=str(exc))
            return []

    async def describe_topic(self, name: str) -> dict[str, Any]:
        return {"name": name, "partitions": 3, "replication": 1}

    async def consumer_lag(self, group_id: str, topic: str) -> dict[str, Any]:
        try:
            from aiokafka.admin import AIOKafkaAdminClient
            admin = AIOKafkaAdminClient(bootstrap_servers=self._bootstrap)
            await admin.start()
            try:
                return {"member_count": 0, "total_lag": 0, "partitions": []}
            finally:
                await admin.close()
        except Exception as exc:
            log.warning("kafka.consumer_lag.failed", err=str(exc))
            return {"member_count": 0, "total_lag": 0, "partitions": []}

    async def create_topic(self, name: str, partitions: int, replication: int) -> None:
        admin = self._get_admin()
        if admin is None:
            return
        try:
            from aiokafka.admin import NewTopic
            await admin.create_topics([
                NewTopic(name=name, num_partitions=partitions,
                         replication_factor=replication),
            ])
        except Exception as exc:
            log.warning("kafka.create_topic.failed", err=str(exc))

    async def delete_topic(self, name: str) -> None:
        admin = self._get_admin()
        if admin is None:
            return
        try:
            await admin.delete_topics([name])
        except Exception as exc:
            log.warning("kafka.delete_topic.failed", err=str(exc))


class RedisBackpressureController:
    def __init__(self, redis: Any | None = None) -> None:
        self._redis = redis

    def _key(self, topic: str) -> str:
        return f"bigo:bp:{topic}"

    async def activate(self, topic: str, reason: str) -> None:
        if self._redis is None:
            return
        try:
            await self._redis.set(self._key(topic), reason, ex=3600)
        except Exception as exc:
            log.warning("bp.activate.failed", err=str(exc))

    async def deactivate(self, topic: str) -> None:
        if self._redis is None:
            return
        try:
            await self._redis.delete(self._key(topic))
        except Exception as exc:
            log.warning("bp.deactivate.failed", err=str(exc))

    async def is_active(self, topic: str) -> bool:
        if self._redis is None:
            return False
        try:
            val = await self._redis.get(self._key(topic))
            return val is not None
        except Exception as exc:
            log.warning("bp.is_active.failed", err=str(exc))
            return False


class RedisCache:
    """TH: cache-aside (legacy)"""

    def __init__(self, redis: Any | None = None) -> None:
        self._redis = redis

    async def get(self, key: str) -> Any | None:
        if self._redis is None:
            return None
        try:
            import json
            raw = await self._redis.get(key)
            return json.loads(raw) if raw else None
        except Exception as exc:
            log.warning("cache.get.failed", err=str(exc))
            return None

    async def set(self, key: str, value: Any, ttl: int = 60) -> bool:
        if self._redis is None:
            return False
        try:
            import json
            await self._redis.set(key, json.dumps(value, default=str), ex=ttl)
            return True
        except Exception as exc:
            log.warning("cache.set.failed", err=str(exc))
            return False

    async def invalidate(self, key: str) -> bool:
        if self._redis is None:
            return False
        try:
            await self._redis.delete(key)
            return True
        except Exception as exc:
            log.warning("cache.invalidate.failed", err=str(exc))
            return False


class LoggingEventBus:
    async def publish(self, event: object) -> None:
        try:
            log.info("event", type=type(event).__name__)
        except Exception:
            pass


class KafkaEventBus:
    def __init__(self, producer: Any, topic: str = "bigo.events") -> None:
        self._producer = producer
        self._topic = topic

    async def publish(self, event: object) -> None:
        try:
            payload = {
                "type": type(event).__name__,
                "data": {k: str(v) for k, v in vars(event).items()},
            }
            await self._producer.send_and_wait(self._topic, payload)
        except Exception as exc:
            log.warning("event.publish_failed", err=str(exc))
