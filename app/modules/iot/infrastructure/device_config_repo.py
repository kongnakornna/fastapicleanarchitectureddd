"""DeviceConfig repository"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceConfigModel


class DeviceConfigRepository:
    """TH: device config repo | EN: device config repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_device_id(self, device_id: str) -> DeviceConfigModel | None:
        result = await self._session.execute(
            select(DeviceConfigModel).where(
                DeviceConfigModel.device_id == device_id,
            )
        )
        return result.scalar_one_or_none()

    async def upsert(self, config: DeviceConfigModel) -> DeviceConfigModel:
        logger.info(f"Upserting device config for device: {config.device_id}")
        # SQLAlchemy merge performs INSERT ... ON CONFLICT when the model has a PK.
        merged = await self._session.merge(config)
        await self._session.flush()
        return merged