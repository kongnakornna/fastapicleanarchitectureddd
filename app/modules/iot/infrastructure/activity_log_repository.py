"""ActivityLog repository"""
from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import ActivityLogModel


class ActivityLogRepository:
    """TH: activity log repo | EN: activity log repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: ActivityLogModel) -> ActivityLogModel:
        logger.debug(f"Creating activity log: {log.log_type}")
        self._session.add(log)
        await self._session.flush()
        return log
