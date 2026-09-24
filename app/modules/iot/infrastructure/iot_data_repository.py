"""iotData repository"""
from __future__ import annotations
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import iotDataModel


class iotDataRepository:
    """TH: iot data repo | EN: iot data repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: iotDataModel) -> iotDataModel:
        self._session.add(data)
        await self._session.flush()
        return data

    async def find_latest(
        self, device_id: int, limit: int = 10,
    ) -> list[iotDataModel]:
        result = await self._session.execute(
            select(iotDataModel)
            .where(iotDataModel.device_id == device_id)
            .order_by(iotDataModel.created_at.desc())
            .limit(limit))
        return list(result.scalars().all())

    async def find_by_date_range(
        self, device_id: int, start: str, end: str,
    ) -> list[iotDataModel]:
        result = await self._session.execute(
            select(iotDataModel).where(
                iotDataModel.device_id == device_id,
                iotDataModel.created_at >= start,
                iotDataModel.created_at <= end,
            ).order_by(iotDataModel.created_at.desc()))
        return list(result.scalars().all())

    async def find_paginated(
        self, page: int = 1, page_size: int = 20,
    ) -> tuple[list[iotDataModel], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(iotDataModel))
        total = count_result.scalar() or 0
        query = (
            select(iotDataModel)
            .order_by(iotDataModel.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def cleanup_old(self, days: int) -> int:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        result = await self._session.execute(
            select(iotDataModel).where(iotDataModel.created_at < cutoff))
        old = list(result.scalars().all())
        for item in old:
            await self._session.delete(item)
        await self._session.flush()
        return len(old)
