"""llamaindex repositories"""
from __future__ import annotations
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.llamaindex.application.exceptions import AppError
from app.modules.llamaindex.infrastructure.models import (
    LIDocumentModel, LIIndexModel, LINodeModel, LIQueryEngineModel,
    LIRunModel,
)

logger = logging.getLogger(__name__)


class LIIndexRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, i: LIIndexModel) -> LIIndexModel:
        try:
            self._session.add(i)
            await self._session.flush()
            return i
        except SQLAlchemyError as exc:
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> LIIndexModel | None:
        r = await self._session.execute(
            select(LIIndexModel).where(LIIndexModel.id == id)
        )
        return r.scalar_one_or_none()

    async def find_by_name(self, ctx: object, name: str) -> LIIndexModel | None:
        r = await self._session.execute(
            select(LIIndexModel).where(LIIndexModel.name == name)
        )
        return r.scalar_one_or_none()

    async def find_all_active(self, ctx: object) -> list[LIIndexModel]:
        r = await self._session.execute(
            select(LIIndexModel)
            .where(LIIndexModel.is_active.is_(True))
            .order_by(LIIndexModel.name)
        )
        return list(r.scalars().all())


class LINodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, ctx: object, nodes: list) -> int:
        for n in nodes:
            self._session.add(n)
        await self._session.flush()
        return len(nodes)

    async def find_by_index(
        self, ctx: object, index_id: uuid.UUID,
    ) -> list[LINodeModel]:
        r = await self._session.execute(
            select(LINodeModel)
            .where(LINodeModel.index_id == index_id)
            .order_by(LINodeModel.ordinal)
        )
        return list(r.scalars().all())

    async def delete_by_document(
        self, ctx: object, document_id: uuid.UUID,
    ) -> int:
        from sqlalchemy import delete
        r = await self._session.execute(
            delete(LINodeModel).where(LINodeModel.document_id == document_id)
        )
        await self._session.flush()
        return int(r.rowcount or 0)


class LIQueryEngineRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, q: LIQueryEngineModel) -> LIQueryEngineModel:
        self._session.add(q)
        await self._session.flush()
        return q

    async def find_by_id(
        self, ctx: object, id: uuid.UUID,
    ) -> LIQueryEngineModel | None:
        r = await self._session.execute(
            select(LIQueryEngineModel).where(LIQueryEngineModel.id == id)
        )
        return r.scalar_one_or_none()

    async def find_by_index(
        self, ctx: object, index_id: uuid.UUID,
    ) -> list[LIQueryEngineModel]:
        r = await self._session.execute(
            select(LIQueryEngineModel)
            .where(LIQueryEngineModel.index_id == index_id)
            .order_by(LIQueryEngineModel.name)
        )
        return list(r.scalars().all())


class LIDocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, d: LIDocumentModel) -> LIDocumentModel:
        self._session.add(d)
        await self._session.flush()
        return d

    async def find_by_id(
        self, ctx: object, id: uuid.UUID,
    ) -> LIDocumentModel | None:
        r = await self._session.execute(
            select(LIDocumentModel).where(LIDocumentModel.id == id)
        )
        return r.scalar_one_or_none()

    async def find_by_hash(
        self, ctx: object, h: str,
    ) -> LIDocumentModel | None:
        r = await self._session.execute(
            select(LIDocumentModel).where(LIDocumentModel.hash == h)
        )
        return r.scalar_one_or_none()

    async def find_by_index(
        self, ctx: object, index_id: uuid.UUID,
    ) -> list[LIDocumentModel]:
        r = await self._session.execute(
            select(LIDocumentModel)
            .where(LIDocumentModel.index_id == index_id)
            .order_by(LIDocumentModel.created_at.desc())
        )
        return list(r.scalars().all())

    async def update(self, ctx: object, d: LIDocumentModel) -> LIDocumentModel:
        await self._session.flush()
        return d


class LIRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, r_: LIRunModel) -> LIRunModel:
        self._session.add(r_)
        await self._session.flush()
        return r_

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> LIRunModel | None:
        r = await self._session.execute(
            select(LIRunModel).where(LIRunModel.id == id)
        )
        return r.scalar_one_or_none()

    async def update(self, ctx: object, r_: LIRunModel) -> LIRunModel:
        await self._session.flush()
        return r_
