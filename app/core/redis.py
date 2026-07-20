from loguru import logger
from redis.asyncio import Redis

from app.core.settings import settings


_redis: Redis | None = None


async def get_redis() -> Redis | None:
    global _redis
    if _redis is not None:
        return _redis

    try:
        _redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            db=settings.REDIS_DB,
            decode_responses=True,
            protocol=2,
            socket_connect_timeout=2,
        )
        await _redis.ping()
        logger.info("Redis connection established successfully.")
        return _redis
    except Exception as e:
        logger.warning(f"Redis connection failed (running without Redis): {e}")
        _redis = None
        return None


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        try:
            await _redis.close()
        except Exception as e:
            logger.warning(f"Redis close error: {e}")
        _redis = None


BLACKLIST_PREFIX = "blacklist:"


async def add_to_blacklist(hashed_jti: str, expires_in_seconds: int) -> None:
    r = await get_redis()
    if r is None:
        return
    key = f"{BLACKLIST_PREFIX}{hashed_jti}"
    await r.setex(key, expires_in_seconds, "1")


async def is_blacklisted(hashed_jti: str) -> bool:
    r = await get_redis()
    if r is None:
        return False
    key = f"{BLACKLIST_PREFIX}{hashed_jti}"
    return await r.exists(key) == 1
