from __future__ import annotations

from datetime import datetime, timedelta

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.domain.entities.iot_data import IoTData


class IoTDataRepository:
    """IoT data repository - translated from Go: repository/iot_data_repo.go"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: IoTData) -> IoTData:
        logger.debug(f"Creating IoT data for device_id: {data.device_id}")
        self._session.add(data)
        await self._session.flush()
        return data

    async def find_latest(
        self, device_id: int, limit: int = 10
    ) -> list[IoTData]:
        logger.debug(f"Finding latest IoT data for device_id: {device_id}")
        result = await self._session.execute(
            select(IoTData)
            .where(IoTData.device_id == device_id)
            .order_by(IoTData.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def find_by_date_range(
        self, device_id: int, start: str, end: str
    ) -> list[IoTData]:
        logger.debug(
            f"Finding IoT data by date range: device_id={device_id}, "
            f"start={start}, end={end}"
        )
        result = await self._session.execute(
            select(IoTData)
            .where(
                IoTData.device_id == device_id,
                IoTData.created_at >= start,
                IoTData.created_at <= end,
            )
            .order_by(IoTData.created_at.desc())
        )
        return list(result.scalars().all())

    async def find_paginated(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[IoTData], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(IoTData)
        )
        total = count_result.scalar() or 0

        query = (
            select(IoTData)
            .order_by(IoTData.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def cleanup_old(self, days: int) -> int:
        logger.info(f"Cleaning up IoT data older than {days} days")
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self._session.execute(
            select(IoTData).where(IoTData.created_at < cutoff)
        )
        old_data = list(result.scalars().all())
        for item in old_data:
            await self._session.delete(item)
        await self._session.flush()
        return len(old_data)
