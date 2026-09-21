"""Idempotency infrastructure caches — Redis store (primary)"""

import json
import logging

from ..domain.entities import IdempotencyRecord
from ..domain.value_objects import IdempotencyKey

logger = logging.getLogger(__name__)


class RedisIdempotencyStore:
    """RedisIdempotencyStore — primary store ด้วย atomic SET NX"""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def get(
        self, key: IdempotencyKey, tenant_id: str
    ) -> IdempotencyRecord | None:
        try:
            raw = await self.redis.get(key.redis_key(tenant_id))
            if not raw:
                return None
            data = json.loads(raw)
            return IdempotencyRecord(
                key=data.get("key", key.value),
                status=data.get("status", "IN_PROGRESS"),
                request_hash=data.get("request_hash", ""),
                response_body=data.get("response_body", {}),
                response_status=data.get("response_status", 0),
                expires_at=data.get("expires_at"),
            )
        except Exception:
            logger.exception("Redis get failed")
            return None

    async def set(
        self, key: IdempotencyKey, tenant_id: str, rec: IdempotencyRecord
    ) -> None:
        try:
            payload = {
                "key": rec.key,
                "status": rec.status,
                "request_hash": rec.request_hash,
                "response_body": rec.response_body,
                "response_status": rec.response_status,
                "expires_at": (rec.expires_at.isoformat() if rec.expires_at else None),
            }
            await self.redis.set(
                key.redis_key(tenant_id),
                json.dumps(payload),
                ex=86400,
            )
        except Exception:
            logger.exception("Redis set failed")

    async def lock(self, key: IdempotencyKey, tenant_id: str, ttl: int) -> bool:
        try:
            result = await self.redis.set(
                f"{key.redis_key(tenant_id)}:lock",
                "1",
                nx=True,
                ex=ttl,
            )
            return bool(result)
        except Exception:
            logger.exception("Lock failed")
            return False  # conservative: fail closed

    async def unlock(self, key: IdempotencyKey, tenant_id: str) -> None:
        try:
            await self.redis.delete(f"{key.redis_key(tenant_id)}:lock")
        except Exception:
            logger.exception("Unlock failed")
