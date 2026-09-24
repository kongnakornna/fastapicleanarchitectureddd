"""Schedule repository"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.iot.infrastructure.models import ScheduleModel


class ScheduleRepository:
    """TH: schedule repo | EN: schedule repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_schedules(self) -> list[ScheduleModel]:
        logger.info("Loading active schedules")
        result = await self._session.execute(
            select(ScheduleModel)
            .where(ScheduleModel.status == 1)
            .options(
                # Equivalent to GORM Preload("ScheduleDevices.Device")
                selectinload(ScheduleModel.schedule_devices)
                .selectinload("device"),
            )
        )
        return list(result.scalars().all())