"""Provider repository — SQLAlchemy 2.0 async (2-branch)"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.llm.application.exceptions import ApplicationError
from app.modules.llm.infrastructure.models import ProviderModel


class ProviderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(
        self, ctx: object, provider_id: uuid.UUID,
    ) -> ProviderModel | None:
        try:
            result = await self._session.execute(
                select(ProviderModel).where(
                    ProviderModel.id == provider_id,
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"provider.find_by_id failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_all_active(
        self, ctx: object,
    ) -> list[ProviderModel]:
        try:
            result = await self._session.execute(
                select(ProviderModel)
                .where(ProviderModel.is_active.is_(True))
                .order_by(ProviderModel.priority.asc())
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"provider.find_all_active failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_type(
        self, ctx: object, provider_type: str,
    ) -> list[ProviderModel]:
        try:
            result = await self._session.execute(
                select(ProviderModel).where(
                    ProviderModel.provider_type == provider_type,
                    ProviderModel.is_active.is_(True),
                )
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"provider.find_by_type failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def save(
        self, ctx: object, provider: ProviderModel,
    ) -> ProviderModel:
        try:
            logger.info(f"Creating provider: {provider.name}")
            self._session.add(provider)
            await self._session.flush()
            return provider
        except SQLAlchemyError as exc:
            logger.error(f"provider.save failed: {exc}")
            raise ApplicationError(str(exc)) from exc
