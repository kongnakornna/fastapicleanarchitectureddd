from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.domain.entities.device_alert import DeviceAlert


class DeviceAlertRepository:
    """Device alert repository - translated from Go: repository/device_alert_repo.go"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, alert: DeviceAlert) -> DeviceAlert:
        logger.info(f"Creating device alert for device_id: {alert.device_id}")
        self._session.add(alert)
        await self._session.flush()
        return alert
