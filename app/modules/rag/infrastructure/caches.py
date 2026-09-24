"""rag caches — Redis (never-raise)"""
from __future__ import annotations
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RedisRAGCache:
    def __init__(
        self, redis: Any, prefix: str = "rag:r:", ttl: int = 3600,
    ) -> None:
        self._redis = redis
        self._prefix = prefix
        self._ttl = ttl

    async def get(self, key: str) -> Optional[dict[str, Any]]:
        try:
            raw = await self._redis.get(self._prefix + key)
            if raw is None:
                return None
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            return json.loads(raw)
        except Exception as exc:
            logger.debug("cache get failed: %s", exc)
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None,
    ) -> bool:
        try:
            await self._redis.set(
                self._prefix + key,
                json.dumps(
                    value, default=str, ensure_ascii=False,
                ),
                ex=ttl or self._ttl,
            )
            return True
        except Exception as exc:
            logger.debug("cache set failed: %s", exc)
            return False


class NoopRAGCache:
    async def get(self, key: str) -> Optional[dict[str, Any]]:
        return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None,
    ) -> bool:
        return False
