"""ToolPermission repository"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from tool_calling.application.exceptions import ApplicationError
from tool_calling.infrastructure.models import ToolPermissionModel


class PermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx, perm):
        try:
            self._session.add(perm)
            await self._session.flush()
            return perm
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def check(self, ctx, tool_id, role):
        try:
            r = await self._session.execute(
                select(ToolPermissionModel).where(
                    ToolPermissionModel.tool_id == tool_id,
                    ToolPermissionModel.role == role))
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc
