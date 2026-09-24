"""ActivityLogRepository"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import ActivityLog


class ActivityLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: ActivityLog) -> ActivityLog:
        self._session.add(log)
        await self._session.flush()
        return log
