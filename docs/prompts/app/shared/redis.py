# app/shared/redis.py - Redis client singleton
from functools import lru_cache

import redis.asyncio as aioredis

from app.core.config import settings


@lru_cache
def get_redis() -> aioredis.Redis:
    """Cached Redis client."""
    return aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=settings.redis_max_connections,
    )


async def close_redis() -> None:
    """Close Redis connection."""
    client = get_redis()
    await client.close()