"""DeviceAlert repository"""
from __future__ import annotations

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceAlertModel


class DeviceAlertRepository:
    """TH: device alert repo | EN: device alert repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, alert: DeviceAlertModel) -> DeviceAlertModel:
        logger.info(f"Creating device alert for device: {alert.device_id}")
        self._session.add(alert)
        await self._session.flush()
        return alert