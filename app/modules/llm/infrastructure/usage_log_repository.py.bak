"""UsageLog repository"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.llm.application.exceptions import ApplicationError
from app.modules.llm.infrastructure.models import UsageLogModel


class UsageLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, ctx: object, log: UsageLogModel,
    ) -> UsageLogModel:
        try:
            self._session.add(log)
            await self._session.flush()
            return log
        except SQLAlchemyError as exc:
            logger.error(f"usage.create failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def sum_by_tenant(
        self, ctx: object, since: datetime,
    ) -> dict[str, Any]:
        try:
            result = await self._session.execute(
                select(
                    func.coalesce(
                        func.sum(UsageLogModel.tokens_input), 0,
                    ),
                    func.coalesce(
                        func.sum(UsageLogModel.tokens_output), 0,
                    ),
                    func.coalesce(
                        func.sum(UsageLogModel.cost_usd), 0,
                    ),
                    func.count(UsageLogModel.id),
                ).where(UsageLogModel.created_at >= since)
            )
            row = result.one()
            return {
                "tokens_input": int(row[0]),
                "tokens_output": int(row[1]),
                "cost_usd": str(row[2]),
                "requests": int(row[3]),
            }
        except SQLAlchemyError as exc:
            logger.error(f"usage.sum_tenant failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def sum_by_user(
        self, ctx: object,
        user_id: uuid.UUID, since: datetime,
    ) -> dict[str, Any]:
        try:
            result = await self._session.execute(
                select(
                    func.coalesce(
                        func.sum(UsageLogModel.tokens_input), 0,
                    ),
                    func.coalesce(
                        func.sum(UsageLogModel.tokens_output), 0,
                    ),
                    func.coalesce(
                        func.sum(UsageLogModel.cost_usd), 0,
                    ),
                    func.count(UsageLogModel.id),
                ).where(
                    UsageLogModel.user_id == user_id,
                    UsageLogModel.created_at >= since,
                )
            )
            row = result.one()
            return {
                "tokens_input": int(row[0]),
                "tokens_output": int(row[1]),
                "cost_usd": str(row[2]),
                "requests": int(row[3]),
            }
        except SQLAlchemyError as exc:
            logger.error(f"usage.sum_user failed: {exc}")
            raise ApplicationError(str(exc)) from exc
