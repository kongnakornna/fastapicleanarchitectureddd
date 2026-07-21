from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.domain.entities.activity_log import ActivityLog


class ActivityLogRepository:
    """Activity log repository - translated from Go: repository/activity_log_repo.go"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: ActivityLog) -> ActivityLog:
        logger.debug(
            f"Creating activity log: type={log.log_type}, device_id={log.device_id}"
        )
        self._session.add(log)
        await self._session.flush()
        return log
