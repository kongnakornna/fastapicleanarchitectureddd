"""tenancy infrastructure caches — Redis (never-raise)."""

import json
import logging

from ..domain.entities import Tenant

logger = logging.getLogger(__name__)


class RedisTenantCache:
    """Redis cache for tenant (never-raise)."""

    def __init__(self, redis_client, ttl: int = 300):
        self.redis = redis_client
        self.ttl = ttl

    async def get(self, id: str) -> Tenant | None:
        try:
            data = await self.redis.get(f"ten:lookup:{id}")
            if not data:
                return None
            parsed = json.loads(data)
            return Tenant(
                id=parsed["id"],
                slug=parsed["slug"],
                name=parsed["name"],
                plan=parsed.get("plan", "FREE"),
                status=parsed.get("status", "ACTIVE"),
                schema_name=parsed.get("schema_name", ""),
                owner_email=parsed.get("owner_email", ""),
                max_users=parsed.get("max_users", 5),
                max_storage_gb=parsed.get("max_storage_gb", 1),
            )
        except Exception as e:
            logger.warning("Cache get failed: %s", e)
            return None

    async def insert(self, id: str, tenant: Tenant) -> None:
        try:
            payload = {
                "id": tenant.id,
                "slug": tenant.slug,
                "name": tenant.name,
                "plan": tenant.plan,
                "status": tenant.status,
                "schema_name": tenant.schema_name,
                "owner_email": tenant.owner_email,
                "max_users": tenant.max_users,
                "max_storage_gb": tenant.max_storage_gb,
            }
            await self.redis.setex(f"ten:lookup:{id}", self.ttl, json.dumps(payload))
        except Exception as e:
            logger.warning("Cache insert failed: %s", e)

    async def delete(self, id: str) -> None:
        try:
            await self.redis.delete(f"ten:lookup:{id}")
        except Exception as e:
            logger.warning("Cache delete failed: %s", e)
