from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.domain.entities.device_status import DeviceStatus


class DeviceStatusRepository:
    """Device status repository - translated from Go: repository/device_status_repo.go"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_device_id(self, device_id: int) -> DeviceStatus | None:
        logger.debug(f"Finding device status by device_id: {device_id}")
        result = await self._session.execute(
            select(DeviceStatus).where(DeviceStatus.device_id == device_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, status: DeviceStatus) -> DeviceStatus:
        existing = await self.find_by_device_id(status.device_id)
        if existing:
            logger.debug(f"Updating device status for device_id: {status.device_id}")
            for key, value in vars(status).items():
                if key not in ("id", "created_at") and value is not None:
                    setattr(existing, key, value)
            await self._session.flush()
            return existing

        logger.info(f"Creating device status for device_id: {status.device_id}")
        self._session.add(status)
        await self._session.flush()
        return status

    async def update_last_seen(self, device_id: int) -> None:
        from datetime import UTC, datetime

        status = await self.find_by_device_id(device_id)
        if status:
            status.last_seen = datetime.now(UTC)
            status.is_online = True
            await self._session.flush()
