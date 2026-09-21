"""tenant_context infrastructure caches — Redis cache (never-raise).

Cache ห้าม raise — fallback เงียบ ๆ
Cache must never raise — silent fallback
"""

import json
import logging

from ..domain.value_objects import TenantContext

logger = logging.getLogger(__name__)


class RedisTenantCache:
    """Cache tenant lookup — แคชข้อมูล tenant."""

    def __init__(self, redis_client, ttl: int = 300):
        self.redis = redis_client
        self.ttl = ttl

    async def get(self, identifier: str) -> TenantContext | None:
        """ดึง tenant จาก cache — Get tenant from cache (never-raise)."""
        try:
            data = await self.redis.get(f"tenant:lookup:{identifier}")
            if not data:
                return None
            parsed = json.loads(data)
            return TenantContext(
                tenant_id=parsed["tenant_id"],
                user_id=parsed.get("user_id"),
                correlation_id=parsed.get("correlation_id", ""),
                request_id=parsed.get("request_id", ""),
                locale=parsed.get("locale", "th-TH"),
                timezone=parsed.get("timezone", "Asia/Bangkok"),
            )
        except Exception as e:
            logger.warning("Cache get failed. Falling back: %s", e)
            return None

    async def insert(self, identifier: str, ctx: TenantContext) -> None:
        """บันทึก tenant ลง cache — Insert tenant into cache."""
        try:
            await self.redis.setex(
                f"tenant:lookup:{identifier}",
                self.ttl,
                json.dumps(ctx.to_dict()),
            )
        except Exception as e:
            logger.warning("Cache insert failed: %s", e)

    async def delete(self, identifier: str) -> None:
        """ลบ tenant จาก cache — Delete tenant from cache."""
        try:
            await self.redis.delete(f"tenant:lookup:{identifier}")
        except Exception as e:
            logger.warning("Cache delete failed: %s", e)
