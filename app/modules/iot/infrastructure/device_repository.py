from __future__ import annotations

from uuid import UUID

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.domain.entities.device import Device


class DeviceRepository:
    """Device repository - translated from Go: internal/modules/iot/repository/device_repo.go"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, device_id: UUID) -> Device | None:
        logger.debug(f"Finding device by id: {device_id}")
        result = await self._session.execute(
            select(Device).where(Device.id == device_id)
        )
        return result.scalar_one_or_none()

    async def find_by_hardware_id(self, hardware_id: int) -> Device | None:
        logger.debug(f"Finding device by hardware_id: {hardware_id}")
        result = await self._session.execute(
            select(Device).where(Device.hardware_id == hardware_id)
        )
        return result.scalar_one_or_none()

    async def find_by_mqtt_topic(self, topic: str) -> Device | None:
        logger.debug(f"Finding device by mqtt_topic: {topic}")
        result = await self._session.execute(
            select(Device).where(Device.mqtt_topic == topic)
        )
        return result.scalar_one_or_none()

    async def find_by_location(self, location_id: int) -> list[Device]:
        logger.debug(f"Finding devices by location_id: {location_id}")
        result = await self._session.execute(
            select(Device).where(
                Device.location_id == location_id,
                Device.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def find_all_active(self) -> list[Device]:
        logger.debug("Finding all active devices")
        result = await self._session.execute(
            select(Device).where(Device.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Device], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Device).where(
                Device.is_active.is_(True)
            )
        )
        total = count_result.scalar() or 0

        query = (
            select(Device)
            .where(Device.is_active.is_(True))
            .order_by(Device.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        devices = list(result.scalars().all())
        return devices, total

    async def create(self, device: Device) -> Device:
        logger.info(f"Creating device: {device.device_name}")
        self._session.add(device)
        await self._session.flush()
        return device

    async def update(self, device: Device) -> Device:
        logger.info(f"Updating device: {device.id}")
        await self._session.flush()
        return device

    async def delete(self, device_id: UUID) -> bool:
        device = await self.find_by_id(device_id)
        if device:
            device.is_active = False
            await self._session.flush()
            return True
        return False
