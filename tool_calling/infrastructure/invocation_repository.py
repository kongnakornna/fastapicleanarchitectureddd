"""ToolInvocation repository"""
from __future__ import annotations

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from tool_calling.application.exceptions import ApplicationError
from tool_calling.infrastructure.models import ToolInvocationModel


class InvocationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx, inv):
        try:
            self._session.add(inv)
            await self._session.flush()
            return inv
        except SQLAlchemyError as exc:
            logger.error(f"inv.save failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_id(self, ctx, inv_id):
        try:
            r = await self._session.execute(
                select(ToolInvocationModel).where(ToolInvocationModel.id == inv_id))
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def list(self, ctx, limit=50, offset=0):
        try:
            r = await self._session.execute(
                select(ToolInvocationModel)
                .order_by(ToolInvocationModel.created_at.desc())
                .limit(limit).offset(offset))
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc
