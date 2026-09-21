"""Idempotency infrastructure repositories — Postgres fallback"""

import logging

from ..domain.entities import IdempotencyRecord
from ..domain.value_objects import IdempotencyKey
from .models import IdempotencyRecordModel

logger = logging.getLogger(__name__)


class PostgresIdempotencyRepository:
    """PostgresIdempotencyRepository — fallback เมื่อ Redis ล่ม"""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get(
        self, key: IdempotencyKey, tenant_id: str
    ) -> IdempotencyRecord | None:
        try:
            async with self.session_factory() as session:
                from sqlalchemy import select

                stmt = select(IdempotencyRecordModel).where(
                    IdempotencyRecordModel.key == key.value,
                    IdempotencyRecordModel.scope == key.scope,
                    IdempotencyRecordModel.tenant_id == tenant_id,
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                if row is None:
                    return None
                return IdempotencyRecord(
                    key=row.key,
                    status=row.status,
                    request_hash=row.request_hash,
                    response_body=row.response_body or {},
                    response_status=row.response_status or 0,
                    expires_at=row.expires_at,
                )
        except Exception:
            logger.exception("Postgres get failed")
            return None

    async def set(
        self, key: IdempotencyKey, tenant_id: str, rec: IdempotencyRecord
    ) -> None:
        try:
            async with self.session_factory() as session:
                row = IdempotencyRecordModel(
                    key=key.value,
                    scope=key.scope,
                    tenant_id=tenant_id,
                    status=rec.status,
                    request_hash=rec.request_hash,
                    response_body=rec.response_body,
                    response_status=rec.response_status,
                    expires_at=rec.expires_at,
                )
                session.add(row)
                await session.commit()
        except Exception:
            logger.exception("Postgres set failed")

    async def lock(self, key: IdempotencyKey, tenant_id: str, ttl: int) -> bool:
        # Postgres fallback: always allow (Redis เป็น primary)
        return True

    async def unlock(self, key: IdempotencyKey, tenant_id: str) -> None:
        return None
