"""TH: Idempotency store (Redis) | EN: Idempotency store (Redis)"""
from __future__ import annotations

import hashlib
import json
from typing import Any

import redis.asyncio as aioredis
import structlog

from app.core.config import get_settings

log = structlog.get_logger()
_settings = get_settings()

_LOCK_TTL = 60
_DONE_TTL = 86_400


def _client() -> aioredis.Redis:
    return aioredis.from_url(_settings.redis_url, decode_responses=True)


def _fingerprint(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class IdempotencyStore:
    """TH: Redis-backed idempotency | EN: Redis-backed idempotency"""

    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    @staticmethod
    def _lock_key(scope: str, key: str) -> str:
        return f"idem:lock:{scope}:{key}"

    @staticmethod
    def _done_key(scope: str, key: str) -> str:
        return f"idem:done:{scope}:{key}"

    async def check_or_lock(
        self, key: str, scope: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """TH: คืน response เดิมถ้ามี / lock ถ้าใหม่ | EN: replay or lock"""
        done_key = self._done_key(scope, key)
        cached = await self._redis.get(done_key)
        if cached:
            stored = json.loads(cached)
            if stored["fp"] != _fingerprint(payload):
                raise IdempotencyMismatch("payload differs from original request")
            return stored["body"]

        lock_key = self._lock_key(scope, key)
        acquired = await self._redis.set(
            lock_key, _fingerprint(payload), nx=True, ex=_LOCK_TTL
        )
        if not acquired:
            raise IdempotencyConflict("request in progress")
        return None

    async def complete(
        self, key: str, scope: str, status_code: int, body: dict[str, Any]
    ) -> None:
        """TH: บันทึกผลลัพธ์ | EN: store result"""
        payload = {"status": status_code, "body": body, "fp": _fingerprint(body)}
        await self._redis.set(
            self._done_key(scope, key), json.dumps(payload), ex=_DONE_TTL
        )
        await self._redis.delete(self._lock_key(scope, key))


class IdempotencyConflict(Exception):
    """TH: key กำลังถูกประมวลผล | EN: key in progress"""


class IdempotencyMismatch(Exception):
    """TH: key เดิม + payload ต่าง | EN: same key, different payload"""


_redis_singleton: aioredis.Redis | None = None


def get_idempotency_store() -> IdempotencyStore:
    """TH: DI factory | EN: DI factory"""
    global _redis_singleton  # noqa: PLW0603
    if _redis_singleton is None:
        _redis_singleton = _client()
    return IdempotencyStore(_redis_singleton)