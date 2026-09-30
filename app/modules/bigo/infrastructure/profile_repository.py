"""Profile repository"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bigo.application.exceptions import ApplicationError
from app.modules.bigo.infrastructure.models import ProfileModel


class SqlProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: Any, profile: ProfileModel) -> ProfileModel:
        try:
            self._session.add(profile)
            await self._session.flush()
            return profile
        except SQLAlchemyError as exc:
            logger.error(f"profile.create failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> ProfileModel | None:
        try:
            result = await self._session.execute(
                select(ProfileModel).where(ProfileModel.id == id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_by_function(
        self, ctx: Any, function_name: str, limit: int = 100,
    ) -> list[ProfileModel]:
        try:
            result = await self._session.execute(
                select(ProfileModel)
                .where(ProfileModel.function_name == function_name)
                .order_by(ProfileModel.captured_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_recent(
        self, ctx: Any, since: datetime, limit: int = 100,
    ) -> list[ProfileModel]:
        try:
            result = await self._session.execute(
                select(ProfileModel)
                .where(ProfileModel.captured_at >= since)
                .order_by(ProfileModel.captured_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc
