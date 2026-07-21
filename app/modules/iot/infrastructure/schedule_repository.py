from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.domain.entities.schedule import Schedule


class ScheduleRepository:
    """Schedule repository - translated from Go: repository/schedule_repo.go"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_active_schedules(self) -> list[Schedule]:
        logger.debug("Finding active schedules")
        result = await self._session.execute(
            select(Schedule).where(Schedule.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def find_by_device_id(self, device_id: int) -> list[Schedule]:
        logger.debug(f"Finding schedules for device_id: {device_id}")
        result = await self._session.execute(
            select(Schedule).where(
                Schedule.device_id == device_id,
                Schedule.is_active.is_(True),
            )
        )
        return list(result.scalars().all())
