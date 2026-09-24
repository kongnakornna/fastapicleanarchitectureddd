"""DeviceConfigRepository"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceConfig


class DeviceConfigRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_device_id(self, device_id: str) -> DeviceConfig | None:
        r = await self._session.execute(
            select(DeviceConfig).where(DeviceConfig.device_id == device_id)
        )
        return r.scalar_one_or_none()

    async def upsert(self, cfg: DeviceConfig) -> DeviceConfig:
        existing = await self.find_by_device_id(cfg.device_id)
        if existing:
            existing.config = cfg.config
            existing.status = cfg.status
            await self._session.flush()
            return existing
        self._session.add(cfg)
        await self._session.flush()
        return cfg
