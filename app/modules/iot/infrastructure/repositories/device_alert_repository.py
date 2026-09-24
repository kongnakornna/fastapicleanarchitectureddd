"""DeviceAlertRepository"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import DeviceAlert


class DeviceAlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, alert: DeviceAlert) -> DeviceAlert:
        self._session.add(alert)
        await self._session.flush()
        return alert

    async def find_unresolved(self, device_id: str) -> list[DeviceAlert]:
        r = await self._session.execute(
            select(DeviceAlert).where(
                DeviceAlert.device_id == device_id,
                DeviceAlert.resolved.is_(False),
            ).order_by(DeviceAlert.id.desc())
        )
        return list(r.scalars().all())

    async def resolve(self, alert_id: int) -> DeviceAlert | None:
        r = await self._session.execute(select(DeviceAlert).where(DeviceAlert.id == alert_id))
        a = r.scalar_one_or_none()
        if a:
            a.resolved = True
            await self._session.flush()
        return a
