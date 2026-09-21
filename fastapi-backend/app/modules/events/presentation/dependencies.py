# events/presentation/dependencies.py
# DI provider — ตัวจัดหาการพึ่งพา

from fastapi import Depends

from app.shared.database import get_session

from ..application.use_cases import eventsUseCases
from ..infrastructure.repositories import PostgreseventsRepository


async def get_events_use_cases(
    session=Depends(get_session),
) -> eventsUseCases:
    """DI provider for events use cases.

    ตัวจัดหา use cases สำหรับ events
    """
    tenant_id = "00000000-0000-0000-0000-000000000001"  # TODO: from tenant context
    repo = PostgreseventsRepository(session, tenant_id)
    return eventsUseCases(bus=None, store=repo, handlers=[], serializer=None)
