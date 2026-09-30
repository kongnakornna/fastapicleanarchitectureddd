"""RedisCache — async cache-aside with namespaces, TTL, stats, stampede lock"""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from typing import Any, Awaitable, Callable

import structlog

from app.modules.bigo.infrastructure.metrics_registry import MetricsRegistry

log = structlog.get_logger()


class CacheStats:
    def __init__(self) -> None:
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0

    def snapshot(self) -> dict[str, Any]:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "errors": self.errors,
            "hit_ratio": round(self.hits / total, 4) if total else 0.0,
        }


class RedisCache:
    """TH: cache-aside + TTL + namespace + stampede lock"""

    def __init__(
        self,
        redis: Any | None = None,
        *,
        namespace: str = "bigo",
        default_ttl: int = 300,
        metrics: MetricsRegistry | None = None,
    ) -> None:
        self._redis = redis
        self._ns = namespace
        self._ttl = default_ttl
        self._metrics = metrics or MetricsRegistry()
        self._stats = CacheStats()

    def key(self, *parts: str) -> str:
        return f"{self._ns}:" + ":".join(parts)

    @staticmethod
    def hash_key(payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

    async def get(self, key: str) -> Any | None:
        if self._redis is None:
            self._stats.misses += 1
            return None
        try:
            raw = await self._redis.get(key)
            if raw is None:
                self._stats.misses += 1
                self._metrics.incr("bigo.cache.miss", ns=self._ns)
                return None
            self._stats.hits += 1
            self._metrics.incr("bigo.cache.hit", ns=self._ns)
            try:
                return json.loads(raw)
            except (TypeError, ValueError):
                return raw
        except Exception as exc:
            self._stats.errors += 1
            self._metrics.incr("bigo.cache.error", op="get")
            log.warning("cache.get.failed", key=key, err=str(exc))
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if self._redis is None:
            return False
        try:
            await self._redis.set(
                key,
                json.dumps(value, default=str),
                ex=ttl if ttl is not None else self._ttl,
            )
            self._stats.sets += 1
            self._metrics.incr("bigo.cache.set", ns=self._ns)
            return True
        except Exception as exc:
            self._stats.errors += 1
            log.warning("cache.set.failed", key=key, err=str(exc))
            return False

    async def delete(self, key: str) -> bool:
        if self._redis is None:
            return False
        try:
            await self._redis.delete(key)
            self._stats.deletes += 1
            return True
        except Exception as exc:
            self._stats.errors += 1
            log.warning("cache.delete.failed", key=key, err=str(exc))
            return False

    async def delete_prefix(self, prefix: str) -> int:
        if self._redis is None:
            return 0
        pattern = prefix if prefix.endswith("*") else f"{prefix}*"
        count = 0
        try:
            async for k in self._redis.scan_iter(match=pattern, count=200):
                await self._redis.delete(k)
                count += 1
            self._stats.deletes += count
            return count
        except Exception as exc:
            log.warning("cache.delete_prefix.failed", prefix=prefix, err=str(exc))
            return 0

    async def get_or_set(
        self,
        key: str,
        loader: Callable[[], Awaitable[Any]],
        ttl: int | None = None,
        *,
        lock_timeout: float = 5.0,
    ) -> Any:
        cached = await self.get(key)
        if cached is not None:
            return cached

        lock_key = f"{key}:lock"
        acquired = False
        if self._redis is not None:
            try:
                acquired = bool(
                    await self._redis.set(lock_key, "1", nx=True, ex=int(lock_timeout))
                )
            except Exception:
                acquired = False

        if acquired:
            try:
                value = await loader()
                await self.set(key, value, ttl=ttl)
                return value
            finally:
                try:
                    await self._redis.delete(lock_key)
                except Exception:
                    pass

        await asyncio.sleep(0.05)
        cached = await self.get(key)
        if cached is not None:
            return cached
        return await loader()

    def stats(self) -> dict[str, Any]:
        return {
            "namespace": self._ns,
            "default_ttl": self._ttl,
            "connected": self._redis is not None,
            **self._stats.snapshot(),
        }

    async def health(self) -> dict[str, Any]:
        if self._redis is None:
            return {"connected": False, "ping_ms": None}
        try:
            t0 = time.perf_counter()
            await self._redis.ping()
            return {
                "connected": True,
                "ping_ms": round((time.perf_counter() - t0) * 1000, 3),
            }
        except Exception as exc:
            return {"connected": False, "error": str(exc)}
