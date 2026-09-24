"""Schedule repository"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import ScheduleModel


class ScheduleRepository:
    """TH: schedule repo | EN: schedule repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_active_schedules(self) -> list[ScheduleModel]:
        result = await self._session.execute(
            select(ScheduleModel).where(ScheduleModel.is_active.is_(True)))
        return list(result.scalars().all())

    async def find_by_device_id(
        self, device_id: int,
    ) -> list[ScheduleModel]:
        result = await self._session.execute(
            select(ScheduleModel).where(
                ScheduleModel.device_id == device_id,
                ScheduleModel.is_active.is_(True)))
        return list(result.scalars().all())
