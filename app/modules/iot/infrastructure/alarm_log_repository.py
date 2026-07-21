from __future__ import annotations

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.domain.entities.alarm_log import AlarmLog


class AlarmLogRepository:
    """Alarm log repository - translated from Go: repository/alarm_log_repo.go"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: AlarmLog) -> AlarmLog:
        logger.info(f"Creating alarm log for device_id: {log.device_id}")
        self._session.add(log)
        await self._session.flush()
        return log

    async def count_by_device(self, device_id: int) -> int:
        logger.debug(f"Counting alarm logs for device_id: {device_id}")
        result = await self._session.execute(
            select(func.count())
            .select_from(AlarmLog)
            .where(AlarmLog.device_id == device_id)
        )
        return result.scalar() or 0

    async def find_by_device(
        self, device_id: int, limit: int = 100
    ) -> list[AlarmLog]:
        logger.debug(f"Finding alarm logs for device_id: {device_id}")
        result = await self._session.execute(
            select(AlarmLog)
            .where(AlarmLog.device_id == device_id)
            .order_by(AlarmLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
