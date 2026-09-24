"""Model repository"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.llm.application.exceptions import ApplicationError
from app.modules.llm.infrastructure.models import ModelModel


class ModelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(
        self, ctx: object, model_id: uuid.UUID,
    ) -> ModelModel | None:
        try:
            result = await self._session.execute(
                select(ModelModel).where(ModelModel.id == model_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"model.find_by_id failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_name(
        self, ctx: object, name: str,
    ) -> ModelModel | None:
        try:
            result = await self._session.execute(
                select(ModelModel).where(
                    ModelModel.name == name,
                    ModelModel.is_active.is_(True),
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"model.find_by_name failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_all_active(
        self, ctx: object,
    ) -> list[ModelModel]:
        try:
            result = await self._session.execute(
                select(ModelModel).where(
                    ModelModel.is_active.is_(True),
                )
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"model.find_all_active failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def find_by_provider(
        self, ctx: object, provider_id: uuid.UUID,
    ) -> list[ModelModel]:
        try:
            result = await self._session.execute(
                select(ModelModel).where(
                    ModelModel.provider_id == provider_id,
                    ModelModel.is_active.is_(True),
                )
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"model.find_by_provider failed: {exc}")
            raise ApplicationError(str(exc)) from exc

    async def save(
        self, ctx: object, model: ModelModel,
    ) -> ModelModel:
        try:
            logger.info(f"Creating model: {model.name}")
            self._session.add(model)
            await self._session.flush()
            return model
        except SQLAlchemyError as exc:
            logger.error(f"model.save failed: {exc}")
            raise ApplicationError(str(exc)) from exc
