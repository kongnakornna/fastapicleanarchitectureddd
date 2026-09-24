"""DeviceStatusRepository"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceStatus


class DeviceStatusRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_device_id(self, device_id: str) -> DeviceStatus | None:
        r = await self._session.execute(
            select(DeviceStatus).where(DeviceStatus.device_id == device_id)
        )
        return r.scalar_one_or_none()

    async def upsert(self, st: DeviceStatus) -> DeviceStatus:
        existing = await self.find_by_device_id(st.device_id)
        if existing:
            existing.is_online = st.is_online
            existing.last_seen = st.last_seen
            existing.last_data = st.last_data
            existing.battery_level = st.battery_level
            existing.signal_strength = st.signal_strength
            existing.firmware_version = st.firmware_version
            existing.location = st.location
            await self._session.flush()
            return existing
        self._session.add(st)
        await self._session.flush()
        return st

    async def update_last_seen(self, device_id: str) -> None:
        st = await self.find_by_device_id(device_id)
        if st:
            st.last_seen = datetime.now(timezone.utc)
            st.is_online = True
            await self._session.flush()
