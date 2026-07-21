from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.domain.entities.device_config import DeviceConfig


class DeviceConfigRepository:
    """Device config repository - translated from Go: repository/device_config_repo.go"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_device_id(self, device_id: int) -> DeviceConfig | None:
        logger.debug(f"Finding device config by device_id: {device_id}")
        result = await self._session.execute(
            select(DeviceConfig).where(DeviceConfig.device_id == device_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, config: DeviceConfig) -> DeviceConfig:
        existing = await self.find_by_device_id(config.device_id)
        if existing:
            logger.debug(f"Updating device config for device_id: {config.device_id}")
            for key, value in vars(config).items():
                if key not in ("id", "created_at") and value is not None:
                    setattr(existing, key, value)
            await self._session.flush()
            return existing

        logger.info(f"Creating device config for device_id: {config.device_id}")
        self._session.add(config)
        await self._session.flush()
        return config
