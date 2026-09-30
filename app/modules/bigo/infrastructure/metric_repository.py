"""Metric repository"""
from __future__ import annotations
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bigo.application.exceptions import ApplicationError
from app.modules.bigo.infrastructure.models import MetricModel


class SqlMetricRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: Any, metric: MetricModel) -> MetricModel:
        try:
            self._session.add(metric)
            await self._session.flush()
            return metric
        except SQLAlchemyError as exc:
            logger.error(f"metric.create failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_kind(
        self, ctx: Any, kind: str, since: datetime, limit: int = 500,
    ) -> list[MetricModel]:
        try:
            stmt = select(MetricModel).where(MetricModel.captured_at >= since)
            if kind:
                stmt = stmt.where(MetricModel.kind == kind)
            stmt = stmt.order_by(MetricModel.captured_at.desc()).limit(limit)
            result = await self._session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"metric.find_by_kind failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def aggregate(
        self, ctx: Any, name: str, since: datetime,
    ) -> dict[str, Any]:
        try:
            stmt = select(
                func.coalesce(func.avg(MetricModel.value), 0),
                func.coalesce(func.min(MetricModel.value), 0),
                func.coalesce(func.max(MetricModel.value), 0),
                func.count(MetricModel.id),
            ).where(MetricModel.name == name, MetricModel.captured_at >= since)
            result = await self._session.execute(stmt)
            row = result.one()
            return {"avg": float(row[0]), "min": float(row[1]),
                    "max": float(row[2]), "count": int(row[3])}
        except SQLAlchemyError as exc:
            logger.error(f"metric.aggregate failed: {exc}")
            raise ApplicationError(str(exc)) from exc
