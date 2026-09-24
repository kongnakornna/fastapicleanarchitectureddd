"""tool_calling caches — Redis (never-raise)"""
from __future__ import annotations
import json
from typing import Any

import structlog

log = structlog.get_logger()


class RedisToolCache:
    def __init__(self, redis: object, ttl: int = 300) -> None:
        self._redis = redis
        self._ttl = ttl

    async def get(self, key: str) -> Any | None:
        try:
            raw = await self._redis.get(key)
            return json.loads(raw) if raw else None
        except Exception as e:
            log.warning("toolcache.get_failed", key=key, err=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        try:
            await self._redis.set(
                key, json.dumps(value, default=str),
                ex=(ttl or self._ttl),
            )
            return True
        except Exception as e:
            log.warning("toolcache.set_failed", err=str(e))
            return False
