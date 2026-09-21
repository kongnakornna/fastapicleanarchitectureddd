"""Idempotency use cases — กรณีการใช้งาน idempotency"""

import hashlib
import json
import logging
from datetime import UTC, datetime, timedelta

from ..domain.entities import IdempotencyRecord
from ..domain.exceptions import DomainError
from ..domain.value_objects import IdempotencyKey
from .exceptions import (
    IdempotencyConflictException,
    IdempotencyException,
    StandardException,
)

logger = logging.getLogger(__name__)


class IdempotencyUseCases:
    """Idempotency use cases — กรณีการใช้งาน idempotency"""

    def __init__(self, store, ttl: int = 86400):
        self.store = store
        self.ttl = ttl

    async def check_or_lock(
        self, raw_key: str, scope: str, payload: dict, tenant_id: str
    ) -> IdempotencyRecord | None:
        """Check existing or lock — ตรวจสอบหรือล็อก"""
        try:
            key = IdempotencyKey(value=raw_key, scope=scope)
            existing = await self.store.get(key, tenant_id)

            if existing and existing.is_completed():
                if existing.request_hash != self._hash(payload):
                    raise IdempotencyConflictException("Payload mismatch")
                return existing  # replay

            if existing and existing.is_in_progress():
                raise IdempotencyConflictException("Request in progress")

            locked = await self.store.lock(key, tenant_id, self.ttl)
            if not locked:
                raise IdempotencyConflictException("Concurrent request")

            rec = IdempotencyRecord(
                key=raw_key,
                status="IN_PROGRESS",
                request_hash=self._hash(payload),
                tenant_id=tenant_id,
                expires_at=datetime.now(UTC) + timedelta(seconds=self.ttl),
            )
            await self.store.set(key, tenant_id, rec)
            return None  # proceed with execution
        except StandardException:
            raise
        except DomainError as e:
            raise IdempotencyException(str(e))
        except Exception:
            logger.exception("Error in check_or_lock")
            raise IdempotencyException()

    async def complete(
        self,
        raw_key: str,
        scope: str,
        tenant_id: str,
        status: int,
        body: dict,
    ) -> None:
        """Mark completed — บันทึกผลลัพธ์"""
        try:
            key = IdempotencyKey(value=raw_key, scope=scope)
            rec = await self.store.get(key, tenant_id)
            if rec:
                rec.complete(status, body)
                await self.store.set(key, tenant_id, rec)
                await self.store.unlock(key, tenant_id)
        except Exception:
            logger.exception("Error in complete idempotency")
            # don't re-raise — response already returned

    @staticmethod
    def _hash(payload: dict) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()
