"""ToolInvocation repository"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tool_calling.application.exceptions import (
    ApplicationError,
)
from app.modules.tool_calling.infrastructure.models import (
    ToolInvocationModel,
)


class InvocationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(
        self, ctx: object, inv: ToolInvocationModel,
    ) -> ToolInvocationModel:
        try:
            self._session.add(inv)
            await self._session.flush()
            return inv
        except SQLAlchemyError as exc:
            logger.error(f"inv.save failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_id(
        self, ctx: object, inv_id: uuid.UUID,
    ) -> ToolInvocationModel | None:
        try:
            result = await self._session.execute(
                select(ToolInvocationModel).where(
                    ToolInvocationModel.id == inv_id,
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"inv.find_by_id failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def list(
        self, ctx: object, limit: int = 50, offset: int = 0,
    ) -> list[ToolInvocationModel]:
        try:
            result = await self._session.execute(
                select(ToolInvocationModel)
                .order_by(ToolInvocationModel.created_at.desc())
                .limit(limit).offset(offset)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"inv.list failed: {exc}")
            raise ApplicationError(str(exc)) from exc
