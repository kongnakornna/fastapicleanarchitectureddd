"""embeddings caches — Redis (never-raise)"""
from __future__ import annotations
import json
import logging
import uuid
from typing import Any, Optional

from app.modules.embeddings.application.interfaces import (
    EmbeddingCache, RateLimiter,
)

logger = logging.getLogger(__name__)


class RedisEmbeddingCache(EmbeddingCache):
    def __init__(self, redis: Any, prefix: str = "emb:r:") -> None:
        self._redis = redis
        self._prefix = prefix

    async def get(self, key: str) -> Optional[list[float]]:
        try:
            raw = await self._redis.get(self._prefix + key)
            if raw is None:
                return None
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            data = json.loads(raw)
            if isinstance(data, list):
                return [float(x) for x in data]
            return None
        except Exception as exc:
            logger.debug("cache get failed: %s", exc)
            return None

    async def set(
        self, key: str, value: list[float], ttl: int = 86400,
    ) -> bool:
        try:
            await self._redis.set(
                self._prefix + key,
                json.dumps(value, separators=(",", ":")),
                ex=ttl,
            )
            return True
        except Exception as exc:
            logger.debug("cache set failed: %s", exc)
            return False

    async def invalidate(self, key: str) -> bool:
        try:
            await self._redis.delete(self._prefix + key)
            return True
        except Exception as exc:
            logger.debug("cache invalidate failed: %s", exc)
            return False


class NoopCache(EmbeddingCache):
    async def get(self, key: str) -> Optional[list[float]]:
        return None

    async def set(
        self, key: str, value: list[float], ttl: int = 86400,
    ) -> bool:
        return False

    async def invalidate(self, key: str) -> bool:
        return False


class RedisRateLimiter(RateLimiter):
    def __init__(self, redis: Any, limit_per_minute: int = 600) -> None:
        self._redis = redis
        self._limit = limit_per_minute

    def _key(self, tenant_id: uuid.UUID, user_id: uuid.UUID) -> str:
        return f"emb:rl:{tenant_id}:{user_id}"

    async def check(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
    ) -> bool:
        try:
            raw = await self._redis.get(self._key(tenant_id, user_id))
            current = int(raw or 0)
            return (current + cost) <= self._limit
        except Exception as exc:
            logger.debug("rate check fail-open: %s", exc)
            return True

    async def increment(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
    ) -> None:
        try:
            key = self._key(tenant_id, user_id)
            pipe = self._redis.pipeline()
            pipe.incrby(key, cost)
            pipe.expire(key, 60)
            await pipe.execute()
        except Exception as exc:
            logger.debug("rate increment failed: %s", exc)


class NoopRateLimiter(RateLimiter):
    async def check(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
    ) -> bool:
        return True

    async def increment(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
    ) -> None:
        return None
