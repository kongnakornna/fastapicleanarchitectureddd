"""IotData + CommandLog repositories"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.iot.infrastructure.models import CommandLogModel, IotDataModel


class IotDataRepository:
    """TH: iot data repo | EN: iot data repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: IotDataModel) -> IotDataModel:
        logger.info(f"Creating iot data for device: {data.device_id}")
        self._session.add(data)
        await self._session.flush()
        return data

    async def get_latest(self, device_id: str) -> IotDataModel | None:
        result = await self._session.execute(
            select(IotDataModel)
            .where(IotDataModel.device_id == device_id)
            .order_by(IotDataModel.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_date_range(
        self,
        device_id: str,
        start: datetime | Any,
        end: datetime | Any,
    ) -> list[IotDataModel]:
        result = await self._session.execute(
            select(IotDataModel)
            .where(
                IotDataModel.device_id == device_id,
                IotDataModel.timestamp.between(start, end),
            )
            .order_by(IotDataModel.timestamp.asc())
        )
        return list(result.scalars().all())

    async def get_by_device_id(
        self, device_id: str, limit: int, offset: int,
    ) -> list[IotDataModel]:
        result = await self._session.execute(
            select(IotDataModel)
            .where(IotDataModel.device_id == device_id)
            .order_by(IotDataModel.timestamp.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_by_device_id(self, device_id: str) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(IotDataModel)
            .where(IotDataModel.device_id == device_id)
        )
        return int(result.scalar() or 0)

    async def delete_older_than(self, cutoff: datetime | Any) -> int:
        result = await self._session.execute(
            delete(IotDataModel).where(IotDataModel.timestamp < cutoff)
        )
        await self._session.flush()
        return int(result.rowcount or 0)


class CommandLogRepository:
    """TH: command log repo | EN: command log repo"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, log: CommandLogModel) -> CommandLogModel:
        logger.info(f"Creating command log: {log}")
        self._session.add(log)
        await self._session.flush()
        return log