"""pdpa Redis cache — never-raise"""
from __future__ import annotations
import json
from typing import Any

from app.core.logging import logger

from app.modules.pdpa.application.interfaces import InventoryCache



class RedisPdpaCache(InventoryCache):
    """TH: Redis cache (never-raise) | EN: Redis cache (never-raise)"""

    def __init__(self, redis: object, ttl: int = 300) -> None:
        self._redis = redis; self._ttl = ttl

    async def get(self, key: str) -> Any | None:
        try:
            raw = await self._redis.get(key)  # type: ignore[attr-defined]
            return json.loads(raw) if raw else None
        except Exception as e:
            logger.warning("cache.get_failed", key=key, err=str(e)); return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        try:
            await self._redis.set(  # type: ignore[attr-defined]
                key, json.dumps(value, default=str), ex=(ttl or self._ttl))
            return True
        except Exception as e:
            logger.warning("cache.set_failed", key=key, err=str(e)); return False

    async def invalidate(self, key: str) -> bool:
        try:
            await self._redis.delete(key)  # type: ignore[attr-defined]
            return True
        except Exception as e:
            logger.warning("cache.invalidate_failed", key=key, err=str(e)); return False