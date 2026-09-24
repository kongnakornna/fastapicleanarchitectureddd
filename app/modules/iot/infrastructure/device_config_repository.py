"""DeviceConfig repository"""
from __future__ import annotations
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceConfigModel


class DeviceConfigRepository:
    """TH: device config repo | EN: device config repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_device_id(
        self, device_id: uuid.UUID,
    ) -> DeviceConfigModel | None:
        result = await self._session.execute(
            select(DeviceConfigModel).where(
                DeviceConfigModel.device_id == device_id))
        return result.scalar_one_or_none()

    async def upsert(self, config: DeviceConfigModel) -> DeviceConfigModel:
        existing = await self.find_by_device_id(config.device_id)
        if existing:
            for key, value in vars(config).items():
                if key not in ("id", "created_at", "_sa_instance_state") and value is not None:
                    setattr(existing, key, value)
            await self._session.flush()
            return existing
        self._session.add(config)
        await self._session.flush()
        return config
