"""DeviceStatus repository"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceStatusModel


class DeviceStatusRepository:
    """TH: device status repo | EN: device status repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_device_id(self, device_id: str) -> DeviceStatusModel | None:
        result = await self._session.execute(
            select(DeviceStatusModel).where(
                DeviceStatusModel.device_id == device_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(self, status: DeviceStatusModel) -> DeviceStatusModel:
        logger.info(f"Upserting device status for device: {status.device_id}")
        merged = await self._session.merge(status)
        await self._session.flush()
        return merged

    async def update_last_seen(self, device_id: str) -> None:
        await self._session.execute(
            update(DeviceStatusModel)
            .where(DeviceStatusModel.device_id == device_id)
            .values(last_seen=func.now())
        )
        await self._session.flush()