"""Pipeline report repository"""
from __future__ import annotations
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bigo.application.exceptions import ApplicationError
from app.modules.bigo.infrastructure.models import PipelineReportModel


class SqlPipelineReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: Any, report: PipelineReportModel) -> PipelineReportModel:
        try:
            self._session.add(report)
            await self._session.flush()
            return report
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_recent(
        self, ctx: Any, since: datetime, limit: int = 100,
    ) -> list[PipelineReportModel]:
        try:
            result = await self._session.execute(
                select(PipelineReportModel)
                .where(PipelineReportModel.created_at >= since)
                .order_by(PipelineReportModel.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_by_trace(
        self, ctx: Any, trace_id: str,
    ) -> PipelineReportModel | None:
        try:
            result = await self._session.execute(
                select(PipelineReportModel)
                .where(PipelineReportModel.trace_id == trace_id)
                .limit(1)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc
