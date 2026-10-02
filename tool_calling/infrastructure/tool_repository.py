"""ToolDefinition repository"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from tool_calling.application.exceptions import ApplicationError
from tool_calling.infrastructure.models import ToolDefinitionModel


class ToolRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx, tool):
        try:
            self._session.add(tool)
            await self._session.flush()
            return tool
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_by_id(self, ctx, tool_id):
        try:
            r = await self._session.execute(
                select(ToolDefinitionModel).where(ToolDefinitionModel.id == tool_id))
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_by_name(self, ctx, name):
        try:
            r = await self._session.execute(
                select(ToolDefinitionModel).where(
                    ToolDefinitionModel.name == name,
                    ToolDefinitionModel.is_active.is_(True)))
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_all(self, ctx, limit=100, offset=0):
        try:
            r = await self._session.execute(
                select(ToolDefinitionModel)
                .where(ToolDefinitionModel.is_active.is_(True))
                .order_by(ToolDefinitionModel.name.asc())
                .limit(limit).offset(offset))
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def delete(self, ctx, tool_id):
        try:
            stmt = (update(ToolDefinitionModel)
                    .where(ToolDefinitionModel.id == tool_id)
                    .values(is_active=False))
            res = await self._session.execute(stmt)
            await self._session.flush()
            return (res.rowcount or 0) > 0
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc
