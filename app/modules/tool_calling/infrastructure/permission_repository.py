"""ToolPermission repository"""
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
    ToolPermissionModel,
)


class PermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(
        self, ctx: object, perm: ToolPermissionModel,
    ) -> ToolPermissionModel:
        try:
            self._session.add(perm)
            await self._session.flush()
            return perm
        except SQLAlchemyError as exc:
            logger.error(f"perm.save failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def check(
        self, ctx: object, tool_id: uuid.UUID, role: str,
    ) -> ToolPermissionModel | None:
        try:
            result = await self._session.execute(
                select(ToolPermissionModel).where(
                    ToolPermissionModel.tool_id == tool_id,
                    ToolPermissionModel.role == role,
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"perm.check failed: {exc}")
            raise ApplicationError(str(exc)) from exc
