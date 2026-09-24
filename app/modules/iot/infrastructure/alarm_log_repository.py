"""AlarmLog repository"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import AlarmLogModel


class AlarmLogRepository:
    """TH: alarm log repo | EN: alarm log repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: AlarmLogModel) -> AlarmLogModel:
        logger.info(f"Creating alarm log for device: {log.device_id}")
        self._session.add(log)
        await self._session.flush()
        return log

    async def count_by_device(self, device_id: int) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(AlarmLogModel)
            .where(AlarmLogModel.device_id == device_id))
        return result.scalar() or 0

    async def find_by_device(
        self, device_id: int, limit: int = 100,
    ) -> list[AlarmLogModel]:
        result = await self._session.execute(
            select(AlarmLogModel)
            .where(AlarmLogModel.device_id == device_id)
            .order_by(AlarmLogModel.created_at.desc())
            .limit(limit))
        return list(result.scalars().all())
