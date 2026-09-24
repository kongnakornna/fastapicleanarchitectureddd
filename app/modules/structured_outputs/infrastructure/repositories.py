"""structured_outputs repositories"""
from __future__ import annotations
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.structured_outputs.application.exceptions import AppError
from app.modules.structured_outputs.infrastructure.models import (
    SOOutputModel, SORepairModel, SORequestModel, SOSchemaModel,
    SOValidationModel,
)

logger = logging.getLogger(__name__)


class SOSchemaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, s: SOSchemaModel) -> SOSchemaModel:
        try:
            self._session.add(s)
            await self._session.flush()
            return s
        except SQLAlchemyError as exc:
            logger.exception("schema.save failed")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> SOSchemaModel | None:
        try:
            r = await self._session.execute(
                select(SOSchemaModel).where(SOSchemaModel.id == id)
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise AppError(str(exc)) from exc

    async def find_by_name(self, ctx: object, name: str) -> SOSchemaModel | None:
        try:
            r = await self._session.execute(
                select(SOSchemaModel).where(SOSchemaModel.name == name)
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise AppError(str(exc)) from exc

    async def find_all(self, ctx: object) -> list[SOSchemaModel]:
        try:
            r = await self._session.execute(
                select(SOSchemaModel).order_by(SOSchemaModel.name)
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            raise AppError(str(exc)) from exc


class SORequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, r_: SORequestModel) -> SORequestModel:
        self._session.add(r_)
        await self._session.flush()
        return r_

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> SORequestModel | None:
        r = await self._session.execute(
            select(SORequestModel).where(SORequestModel.id == id)
        )
        return r.scalar_one_or_none()


class SOOutputRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, o: SOOutputModel) -> SOOutputModel:
        self._session.add(o)
        await self._session.flush()
        return o

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> SOOutputModel | None:
        r = await self._session.execute(
            select(SOOutputModel).where(SOOutputModel.id == id)
        )
        return r.scalar_one_or_none()

    async def update(self, ctx: object, o: SOOutputModel) -> SOOutputModel:
        await self._session.flush()
        return o


class SOValidationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, v: SOValidationModel) -> SOValidationModel:
        self._session.add(v)
        await self._session.flush()
        return v

    async def find_by_output(
        self, ctx: object, output_id: uuid.UUID,
    ) -> list[SOValidationModel]:
        r = await self._session.execute(
            select(SOValidationModel)
            .where(SOValidationModel.output_id == output_id)
            .order_by(SOValidationModel.attempt)
        )
        return list(r.scalars().all())


class SORepairRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, r_: SORepairModel) -> SORepairModel:
        self._session.add(r_)
        await self._session.flush()
        return r_

    async def find_by_output(
        self, ctx: object, output_id: uuid.UUID,
    ) -> list[SORepairModel]:
        r = await self._session.execute(
            select(SORepairModel)
            .where(SORepairModel.output_id == output_id)
            .order_by(SORepairModel.attempt)
        )
        return list(r.scalars().all())
