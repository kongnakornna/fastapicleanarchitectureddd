"""llm infrastructure cache — Redis (never-raise)"""
from __future__ import annotations
import json
from typing import Any

import structlog

log = structlog.get_logger()


class RedisLLMCache:
    """TH: cache ด้วย Redis | EN: Redis cache (never-raise)"""

    def __init__(self, redis: object, ttl: int = 3600) -> None:
        self._redis = redis
        self._ttl = ttl

    async def get(self, key: str) -> Any | None:
        try:
            raw = await self._redis.get(key)
            return json.loads(raw) if raw else None
        except Exception as e:
            log.warning("cache.get_failed", key=key, err=str(e))
            return None

    async def set(
        self, key: str, value: Any, ttl: int | None = None,
    ) -> bool:
        try:
            await self._redis.set(
                key, json.dumps(value, default=str),
                ex=(ttl or self._ttl),
            )
            return True
        except Exception as e:
            log.warning("cache.set_failed", key=key, err=str(e))
            return False

    async def invalidate(self, key: str) -> bool:
        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            log.warning(
                "cache.invalidate_failed", key=key, err=str(e),
            )
            return False
