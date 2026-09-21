"""123Abc caches — Redis with tombstone-first invalidation.

Protocol (from Migrations.txt):
  1. invalidate: SET tombstone (TTL) BEFORE DEL entry
  2. set:        check tombstone BEFORE writing
  3. tombstones outlive the longest plausible read-then-write window

Policy (when to read-through, when to invalidate, which TTL) lives in the
use case. This class only executes — and never raises. Postgres is the
source of truth; Redis is an accelerator we must be able to lose.
"""
from __future__ import annotations

import json
from decimal import Decimal

import structlog

from ..domain.entities import 123Abc
from ..domain.enums import 123AbcStatus
from ..domain.value_objects import Money

log = structlog.get_logger()

# ── Namespacing & versioning ────────────────────────────────────
# Every key hangs off this namespace. Bump REDIS_CACHE_VERSION whenever
# the serialized payload changes — the previous generation becomes
# unreachable and expires by TTL on its own.
REDIS_KEY_PREFIX = "erp"
REDIS_CACHE_VERSION = "1"
REDIS_NAMESPACE = f"{REDIS_KEY_PREFIX}:v{REDIS_CACHE_VERSION}"

REDIS_DEFAULT_TTL_SECONDS = 3600
REDIS_TOMBSTONE_TTL_SECONDS = 30


def _entry_key(logical: str) -> str:
    """TH: ประกอบ key จริงใต้ namespace | EN: build real key under namespace"""
    return f"{REDIS_NAMESPACE}:{logical}"


def _tombstone_key(logical: str) -> str:
    return f"{REDIS_NAMESPACE}:{logical}:tombstone"


class Redis123AbcCache:
    """Redis123AbcCache — never-raise cache (tombstone-first)."""

    def __init__(self, redis_client) -> None:
        self.redis = redis_client

    async def get(self, key: str) -> 123Abc | None:
        try:
            raw = await self.redis.get(_entry_key(key))
            if not raw:
                return None
            data = json.loads(raw)
            return 123Abc(
                code=data["code"],
                name=data["name"],
                amount=Money(Decimal(data["amount"]), data.get("currency", "THB")),
                status=123AbcStatus(data.get("status", "ACTIVE")),
            )
        except Exception as e:
            log.warning("cache.get_failed", key=key, err=str(e))
            return None

    async def set(
        self,
        key: str,
        entity: 123Abc,
        ttl: int = REDIS_DEFAULT_TTL_SECONDS,
    ) -> None:
        """TH: เขียน cache (tombstone check ก่อน) | EN: write (tombstone check first)."""
        try:
            # 1. tombstone check BEFORE write — a slow reader that missed
            #    the cache must not resurrect revoked data.
            tomb = await self.redis.get(_tombstone_key(key))
            if tomb:
                log.info("cache.set.suppressed_by_tombstone", key=key)
                return

            payload = {
                "code": entity.code,
                "name": entity.name,
                "amount": str(entity.amount.amount),
                "currency": entity.amount.currency,
                "status": entity.status.value,
            }
            await self.redis.set(_entry_key(key), json.dumps(payload), ex=ttl)
        except Exception as e:
            log.warning("cache.set_failed", key=key, err=str(e))

    async def invalidate(self, key: str) -> bool:
        """TH: tombstone ก่อน แล้วค่อย DEL | EN: tombstone first, then DEL."""
        try:
            # 1. write tombstone BEFORE removing the entry
            await self.redis.set(
                _tombstone_key(key), "1", ex=REDIS_TOMBSTONE_TTL_SECONDS
            )
            # 2. then delete the entry
            await self.redis.delete(_entry_key(key))
            return True
        except Exception as e:
            log.warning("cache.invalidate_failed", key=key, err=str(e))
            return False