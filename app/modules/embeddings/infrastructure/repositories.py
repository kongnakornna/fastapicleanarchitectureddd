"""embeddings repositories — SQLAlchemy 2.0 async"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.embeddings.application.exceptions import AppError
from app.modules.embeddings.infrastructure.models import (
    EmbBatchModel, EmbModelModel, EmbProviderModel, EmbVectorModel,
)


class EmbProviderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, p: EmbProviderModel) -> EmbProviderModel:
        try:
            self._session.add(p)
            await self._session.flush()
            return p
        except SQLAlchemyError as exc:
            logger.error(f"provider.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> EmbProviderModel | None:
        try:
            r = await self._session.execute(
                select(EmbProviderModel).where(EmbProviderModel.id == id)
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"provider.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_all_active(self, ctx: object) -> list[EmbProviderModel]:
        try:
            r = await self._session.execute(
                select(EmbProviderModel)
                .where(EmbProviderModel.is_active.is_(True))
                .order_by(EmbProviderModel.priority.asc())
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"provider.list failed: {exc}")
            raise AppError(str(exc)) from exc


class EmbModelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, m: EmbModelModel) -> EmbModelModel:
        try:
            self._session.add(m)
            await self._session.flush()
            return m
        except SQLAlchemyError as exc:
            logger.error(f"model.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> EmbModelModel | None:
        try:
            r = await self._session.execute(
                select(EmbModelModel).where(EmbModelModel.id == id)
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"model.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_name(self, ctx: object, name: str) -> EmbModelModel | None:
        try:
            r = await self._session.execute(
                select(EmbModelModel).where(
                    EmbModelModel.name == name,
                    EmbModelModel.is_active.is_(True),
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"model.find_by_name failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_all_active(self, ctx: object) -> list[EmbModelModel]:
        try:
            r = await self._session.execute(
                select(EmbModelModel)
                .where(EmbModelModel.is_active.is_(True))
                .order_by(EmbModelModel.name.asc())
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"model.list failed: {exc}")
            raise AppError(str(exc)) from exc


class EmbVectorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, v: dict) -> EmbVectorModel:
        try:
            row = EmbVectorModel(**v) if isinstance(v, dict) else v
            self._session.add(row)
            await self._session.flush()
            return row
        except SQLAlchemyError as exc:
            logger.error(f"vector.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_hash(
        self, ctx: object, model_id: uuid.UUID, h: str,
    ) -> EmbVectorModel | None:
        try:
            r = await self._session.execute(
                select(EmbVectorModel).where(
                    EmbVectorModel.model_id == model_id,
                    EmbVectorModel.source_hash == h,
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"vector.find failed: {exc}")
            raise AppError(str(exc)) from exc


class EmbBatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, b: dict) -> EmbBatchModel:
        try:
            row = EmbBatchModel(**b) if isinstance(b, dict) else b
            self._session.add(row)
            await self._session.flush()
            return row
        except SQLAlchemyError as exc:
            logger.error(f"batch.create failed: {exc}")
            raise AppError(str(exc)) from exc

    async def update(self, ctx: object, b: EmbBatchModel) -> EmbBatchModel:
        try:
            await self._session.flush()
            return b
        except SQLAlchemyError as exc:
            logger.error(f"batch.update failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> EmbBatchModel | None:
        try:
            r = await self._session.execute(
                select(EmbBatchModel).where(EmbBatchModel.id == id)
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"batch.find failed: {exc}")
            raise AppError(str(exc)) from exc
