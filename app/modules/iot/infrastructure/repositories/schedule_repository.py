"""ScheduleRepository"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import Schedule


class ScheduleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_active(self) -> list[Schedule]:
        r = await self._session.execute(select(Schedule).where(Schedule.status == 1))
        return list(r.scalars().all())

    async def find_by_device(self, device_id: int) -> list[Schedule]:
        r = await self._session.execute(
            select(Schedule).where(Schedule.device_id == device_id, Schedule.status == 1)
        )
        return list(r.scalars().all())
