"""DeviceStatus repository"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceStatusModel


class DeviceStatusRepository:
    """TH: device status repo | EN: device status repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_device_id(
        self, device_id: uuid.UUID,
    ) -> DeviceStatusModel | None:
        result = await self._session.execute(
            select(DeviceStatusModel).where(
                DeviceStatusModel.device_id == device_id))
        return result.scalar_one_or_none()

    async def upsert(self, status: DeviceStatusModel) -> DeviceStatusModel:
        existing = await self.find_by_device_id(status.device_id)
        if existing:
            for key, value in vars(status).items():
                if key not in ("id", "created_at", "_sa_instance_state") and value is not None:
                    setattr(existing, key, value)
            await self._session.flush()
            return existing
        self._session.add(status)
        await self._session.flush()
        return status

    async def update_last_seen(self, device_id: uuid.UUID) -> None:
        status = await self.find_by_device_id(device_id)
        if status:
            status.last_seen = datetime.now(UTC)
            status.is_online = True
            await self._session.flush()
