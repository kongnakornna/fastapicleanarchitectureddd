"""
Audit Cache — cache audit
Audit Cache — Redis read-through cache (never raises)
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from audit.domain.entities import AuditLog
from loguru import logger
from redis.asyncio import Redis


class RedisAuditCache:
    """
    Redis audit cache — cache audit บน Redis

    Read-through, never-raise semantics: cache failures are logged but
    never propagate to callers.
    """

    def __init__(self, redis: Redis, ttl_seconds: int = 3600) -> None:
        self.redis = redis
        self.ttl = ttl_seconds

    @staticmethod
    def _key(id: str) -> str:
        """Build cache key — สร้าง cache key"""
        return f"audit:log:{id}"

    async def get(self, id: str) -> AuditLog | None:
        """Get from cache — never raises — ดึงจาก cache ไม่ throw"""
        try:
            raw = await self.redis.get(self._key(id))
            if not raw:
                return None
            data = json.loads(raw)
            return AuditLog(
                id=data["id"],
                action=data["action"],
                resource_type=data["resource_type"],
                resource_id=data["resource_id"],
                actor_id=data["actor_id"],
                before_state=data.get("before_state", {}),
                after_state=data.get("after_state", {}),
                changes=data.get("changes", []),
                ip_address=data.get("ip_address", ""),
                user_agent=data.get("user_agent", ""),
                correlation_id=data.get("correlation_id", ""),
                severity=data.get("severity", "INFO"),
                occurred_at=datetime.fromisoformat(data["occurred_at"])
                if data.get("occurred_at")
                else datetime.now(UTC),
            )
        except Exception as e:
            logger.warning(f"Audit cache get failed (ignored): {e}")
            return None

    async def insert(self, id: str, log: AuditLog) -> None:
        """Insert into cache — never raises — ใส่เข้า cache ไม่ throw"""
        try:
            payload = {
                "id": log.id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "actor_id": log.actor_id,
                "before_state": log.before_state,
                "after_state": log.after_state,
                "changes": log.changes,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "correlation_id": log.correlation_id,
                "severity": log.severity,
                "occurred_at": log.occurred_at.isoformat() if log.occurred_at else None,
            }
            await self.redis.set(self._key(id), json.dumps(payload), ex=self.ttl)
        except Exception as e:
            logger.warning(f"Audit cache insert failed (ignored): {e}")

    async def invalidate(self, id: str) -> None:
        """Invalidate cache — never raises — ลบ cache ไม่ throw"""
        try:
            await self.redis.delete(self._key(id))
        except Exception as e:
            logger.warning(f"Audit cache invalidate failed (ignored): {e}")
