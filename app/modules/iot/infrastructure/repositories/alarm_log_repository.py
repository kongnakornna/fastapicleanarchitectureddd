"""AlarmLogRepository"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import AlarmProcessLog


class AlarmLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: AlarmProcessLog) -> AlarmProcessLog:
        self._session.add(log)
        await self._session.flush()
        return log

    async def count_by_device(self, device_id: int) -> int:
        return int((await self._session.execute(
            select(func.count(AlarmProcessLog.id)).where(AlarmProcessLog.device_id == device_id)
        )).scalar() or 0)

    async def find_by_device(self, device_id: int, limit: int = 100) -> list[AlarmProcessLog]:
        r = await self._session.execute(
            select(AlarmProcessLog).where(AlarmProcessLog.device_id == device_id)
            .order_by(AlarmProcessLog.id.desc()).limit(limit)
        )
        return list(r.scalars().all())
