"""DeviceAlert repository"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceAlertModel


class DeviceAlertRepository:
    """TH: device alert repo | EN: device alert repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, alert: DeviceAlertModel) -> DeviceAlertModel:
        logger.info(f"Creating alert for device: {alert.device_id}")
        self._session.add(alert)
        await self._session.flush()
        return alert

    async def find_unresolved(
        self, device_id: uuid.UUID,
    ) -> list[DeviceAlertModel]:
        result = await self._session.execute(
            select(DeviceAlertModel).where(
                DeviceAlertModel.device_id == device_id,
                DeviceAlertModel.resolved.is_(False)))
        return list(result.scalars().all())

    async def resolve(
        self, alert_id: uuid.UUID,
    ) -> DeviceAlertModel | None:
        result = await self._session.execute(
            select(DeviceAlertModel).where(
                DeviceAlertModel.id == alert_id))
        alert = result.scalar_one_or_none()
        if alert:
            alert.resolved = True
            await self._session.flush()
        return alert
