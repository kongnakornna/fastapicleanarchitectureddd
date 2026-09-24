"""ToolDefinition repository"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tool_calling.application.exceptions import (
    ApplicationError,
)
from app.modules.tool_calling.infrastructure.models import (
    ToolDefinitionModel,
)


class ToolRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(
        self, ctx: object, tool: ToolDefinitionModel,
    ) -> ToolDefinitionModel:
        try:
            self._session.add(tool)
            await self._session.flush()
            return tool
        except SQLAlchemyError as exc:
            logger.error(f"tool.save failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_id(
        self, ctx: object, tool_id: uuid.UUID,
    ) -> ToolDefinitionModel | None:
        try:
            result = await self._session.execute(
                select(ToolDefinitionModel).where(
                    ToolDefinitionModel.id == tool_id,
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"tool.find_by_id failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_name(
        self, ctx: object, name: str,
    ) -> ToolDefinitionModel | None:
        try:
            result = await self._session.execute(
                select(ToolDefinitionModel).where(
                    ToolDefinitionModel.name == name,
                    ToolDefinitionModel.is_active.is_(True),
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"tool.find_by_name failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_all(
        self, ctx: object, limit: int = 100, offset: int = 0,
    ) -> list[ToolDefinitionModel]:
        try:
            result = await self._session.execute(
                select(ToolDefinitionModel)
                .where(ToolDefinitionModel.is_active.is_(True))
                .order_by(ToolDefinitionModel.name.asc())
                .limit(limit).offset(offset)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"tool.find_all failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def delete(
        self, ctx: object, tool_id: uuid.UUID,
    ) -> bool:
        try:
            stmt = (
                update(ToolDefinitionModel)
                .where(ToolDefinitionModel.id == tool_id)
                .values(is_active=False)
            )
            res = await self._session.execute(stmt)
            await self._session.flush()
            return (res.rowcount or 0) > 0
        except SQLAlchemyError as exc:
            logger.error(f"tool.delete failed: {exc}")
            raise ApplicationError(str(exc)) from exc
