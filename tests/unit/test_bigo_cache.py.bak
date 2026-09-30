"""Unit tests for RedisCache"""
from __future__ import annotations
import pytest

from app.modules.bigo.infrastructure.redis_cache import RedisCache

pytestmark = pytest.mark.unit


class FakeRedis:
    def __init__(self):
        self._data: dict[str, str] = {}

    async def get(self, k): return self._data.get(k)

    async def set(self, k, v, ex=None, nx=False):
        if nx and k in self._data:
            return None
        self._data[k] = v
        return True

    async def delete(self, *keys):
        n = 0
        for k in keys:
            if k in self._data:
                del self._data[k]
                n += 1
        return n

    async def ping(self): return True

    async def scan_iter(self, match=None, count=200):
        pat = (match or "*").rstrip("*")
        for k in list(self._data):
            if k.startswith(pat):
                yield k


@pytest.mark.asyncio
async def test_set_get():
    c = RedisCache(FakeRedis())
    await c.set("k1", {"a": 1})
    assert await c.get("k1") == {"a": 1}


@pytest.mark.asyncio
async def test_get_or_set_caches():
    c = RedisCache(FakeRedis())
    calls = {"n": 0}

    async def loader():
        calls["n"] += 1
        return [1, 2, 3]

    v1 = await c.get_or_set("k", loader)
    v2 = await c.get_or_set("k", loader)
    assert v1 == v2 == [1, 2, 3]
    assert calls["n"] == 1


@pytest.mark.asyncio
async def test_no_redis():
    c = RedisCache(None)
    assert await c.get("x") is None
    assert await c.set("x", 1) is False


@pytest.mark.asyncio
async def test_stats():
    c = RedisCache(FakeRedis())
    await c.set("x", 1)
    await c.get("x")
    await c.get("missing")
    s = c.stats()
    assert s["hits"] == 1
    assert s["misses"] == 1
