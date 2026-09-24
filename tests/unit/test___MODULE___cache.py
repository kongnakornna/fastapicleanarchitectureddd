"""tests/unit/test_money_cache.py — Tombstone protocol."""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.modules.money.domain.entities import Money
from app.modules.money.infrastructure.caches import (
    RedisMoneyCache,
    _entry_key,
    _tombstone_key,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def redis() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def cache(redis) -> RedisMoneyCache:
    return RedisMoneyCache(redis_client=redis)


class TestTombstoneProtocol:
    async def test_invalidate_writes_tombstone_before_delete(
        self, cache, redis
    ) -> None:
        calls: list[str] = []
        async def rec_set(*a, **kw): calls.append("set")
        async def rec_del(*a, **kw): calls.append("del")
        redis.set.side_effect = rec_set
        redis.delete.side_effect = rec_del

        await cache.invalidate("money:x")
        assert calls == ["set", "del"], "tombstone must be written first"

    async def test_set_suppressed_when_tombstone_present(
        self, cache, redis
    ) -> None:
        redis.get.return_value = "1"  # tombstone present
        entity = Money.create(
            tenant_id=None, code="X", name="N", amount=Decimal("1.00"),
        )
        await cache.set("money:x", entity)
        redis.set.assert_not_awaited()

    async def test_set_writes_when_no_tombstone(self, cache, redis) -> None:
        redis.get.return_value = None
        entity = Money.create(
            tenant_id=None, code="X", name="N", amount=Decimal("1.00"),
        )
        await cache.set("money:x", entity)
        redis.set.assert_awaited_once()

    async def test_get_failure_returns_none(self, cache, redis) -> None:
        redis.get.side_effect = RuntimeError("redis down")
        assert await cache.get("money:x") is None

    async def test_invalidate_failure_returns_false(self, cache, redis) -> None:
        redis.set.side_effect = RuntimeError("redis down")
        assert await cache.invalidate("money:x") is False