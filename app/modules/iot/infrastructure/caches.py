"""IotCache — Redis wrapper (never raise)"""
from __future__ import annotations

import json
from typing import Any

from loguru import logger


class IotCache:
    def __init__(self, redis: Any | None, default_ttl: int = 300) -> None:
        self._redis = redis
        self._ttl = default_ttl

    @property
    def enabled(self) -> bool:
        return self._redis is not None

    async def get(self, key: str) -> Any | None:
        if not self.enabled: return None
        try:
            raw = self._redis.get(key)
            if raw is None: return None
            if isinstance(raw, bytes): raw = raw.decode()
            try: return json.loads(raw)
            except (json.JSONDecodeError, TypeError): return raw
        except Exception as exc:
            logger.warning(f"cache.get {key}: {exc}")
            return None

    async def get_raw(self, key: str) -> str | None:
        if not self.enabled: return None
        try:
            raw = self._redis.get(key)
            if raw is None: return None
            return raw.decode() if isinstance(raw, bytes) else str(raw)
        except Exception as exc:
            logger.warning(f"cache.get_raw {key}: {exc}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if not self.enabled: return False
        try:
            payload = value if isinstance(value, str) else json.dumps(value, default=str)
            self._redis.set(key, payload, ex=(ttl or self._ttl))
            return True
        except Exception as exc:
            logger.warning(f"cache.set {key}: {exc}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.enabled: return False
        try:
            self._redis.delete(key)
            return True
        except Exception as exc:
            logger.warning(f"cache.delete {key}: {exc}")
            return False

    async def lpush_trim(self, key: str, value: Any, max_items: int = 100, ttl: int = 300) -> bool:
        if not self.enabled: return False
        try:
            payload = value if isinstance(value, str) else json.dumps(value, default=str)
            self._redis.lpush(key, payload)
            self._redis.ltrim(key, 0, max_items - 1)
            self._redis.expire(key, ttl)
            return True
        except Exception as exc:
            logger.warning(f"cache.lpush_trim {key}: {exc}")
            return False
