"""IotDataRepository"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import IotData


class IotDataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: IotData) -> IotData:
        self._session.add(data)
        await self._session.flush()
        return data

    async def find_latest(self, device_id: str, limit: int = 10) -> list[IotData]:
        r = await self._session.execute(
            select(IotData).where(IotData.device_id == device_id)
            .order_by(IotData.timestamp.desc()).limit(limit)
        )
        return list(r.scalars().all())

    async def find_by_date_range(
        self, device_id: str, start: datetime, end: datetime,
    ) -> list[IotData]:
        r = await self._session.execute(
            select(IotData).where(
                IotData.device_id == device_id,
                IotData.timestamp >= start,
                IotData.timestamp <= end,
            ).order_by(IotData.timestamp.asc())
        )
        return list(r.scalars().all())

    async def find_paginated(
        self, device_id: str, page: int = 1, page_size: int = 50,
    ) -> tuple[list[IotData], int]:
        total = int((await self._session.execute(
            select(func.count(IotData.id)).where(IotData.device_id == device_id)
        )).scalar() or 0)
        r = await self._session.execute(
            select(IotData).where(IotData.device_id == device_id)
            .order_by(IotData.timestamp.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )
        return list(r.scalars().all()), total

    async def cleanup_old(self, days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        r = await self._session.execute(select(IotData).where(IotData.timestamp < cutoff))
        old = list(r.scalars().all())
        for x in old:
            await self._session.delete(x)
        await self._session.flush()
        return len(old)
