"""Device repository — SQLAlchemy 2.0 async"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceModel


class DeviceRepository:
    """TH: device repo | EN: device repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, device_id: uuid.UUID) -> DeviceModel | None:
        result = await self._session.execute(
            select(DeviceModel).where(DeviceModel.id == device_id))
        return result.scalar_one_or_none()

    async def find_by_hardware_id(self, hardware_id: int) -> DeviceModel | None:
        result = await self._session.execute(
            select(DeviceModel).where(DeviceModel.hardware_id == hardware_id))
        return result.scalar_one_or_none()

    async def find_by_mqtt_topic(self, topic: str) -> DeviceModel | None:
        result = await self._session.execute(
            select(DeviceModel).where(DeviceModel.mqtt_topic == topic))
        return result.scalar_one_or_none()

    async def find_by_location(self, location_id: int) -> list[DeviceModel]:
        result = await self._session.execute(
            select(DeviceModel).where(
                DeviceModel.location_id == location_id,
                DeviceModel.is_active.is_(True),
            ))
        return list(result.scalars().all())

    async def find_all_active(self) -> list[DeviceModel]:
        result = await self._session.execute(
            select(DeviceModel).where(DeviceModel.is_active.is_(True)))
        return list(result.scalars().all())

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 20,
    ) -> tuple[list[DeviceModel], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(DeviceModel).where(
                DeviceModel.is_active.is_(True)))
        total = count_result.scalar() or 0
        query = (
            select(DeviceModel)
            .where(DeviceModel.is_active.is_(True))
            .order_by(DeviceModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, device: DeviceModel) -> DeviceModel:
        logger.info(f"Creating device: {device.device_name}")
        self._session.add(device)
        await self._session.flush()
        return device

    async def update(self, device: DeviceModel) -> DeviceModel:
        await self._session.flush()
        return device

    async def delete(self, device_id: uuid.UUID) -> bool:
        device = await self.find_by_id(device_id)
        if device:
            device.is_active = False
            await self._session.flush()
            return True
        return False
