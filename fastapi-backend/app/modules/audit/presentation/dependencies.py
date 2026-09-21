"""
Audit Dependencies — dependency ของ audit
Audit Dependencies — FastAPI dependency providers
"""

from __future__ import annotations

from audit.application.use_cases import AuditUseCases
from audit.infrastructure.caches import RedisAuditCache
from audit.infrastructure.repositories import PostgresAuditRepository
from audit.infrastructure.services import AuditEventBus, AuditPublisher
from fastapi import Depends
from redis.asyncio import Redis
from app.shared.database import get_session
from app.shared.infrastructure.events import get_event_bus
from app.shared.infrastructure.kafka import get_producer
from app.shared.redis import get_redis
from sqlalchemy.ext.asyncio import AsyncSession


async def get_audit_use_cases(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    producer=Depends(get_producer),
    event_bus=Depends(get_event_bus),
) -> AuditUseCases:
    """
    Wire up AuditUseCases with all dependencies — ประกอบ AuditUseCases กับ dependency ทั้งหมด

    Returns a fully-constructed use case ready to run.
    """
    repo = PostgresAuditRepository(session)
    cache = RedisAuditCache(redis)
    publisher = AuditPublisher(producer)
    events = AuditEventBus(event_bus)

    return AuditUseCases(
        repo=repo,
        cache=cache,
        publisher=publisher,
        events=events,
    )
