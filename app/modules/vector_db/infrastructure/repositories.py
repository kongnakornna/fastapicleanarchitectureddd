"""vector_db repositories — SQLAlchemy 2.0 async"""
from __future__ import annotations
import uuid

from loguru import logger
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.vector_db.application.exceptions import AppError
from app.modules.vector_db.infrastructure.models import (
    VDBCollectionModel, VDBIndexModel, VDBNamespaceModel,
    VDBStatsModel, VDBVectorModel,
)


class VDBCollectionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, c: VDBCollectionModel) -> VDBCollectionModel:
        try:
            self._session.add(c)
            await self._session.flush()
            return c
        except SQLAlchemyError as exc:
            logger.error(f"coll.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> VDBCollectionModel | None:
        try:
            r = await self._session.execute(
                select(VDBCollectionModel).where(
                    VDBCollectionModel.id == id,
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"coll.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_name(self, ctx: object, name: str) -> VDBCollectionModel | None:
        try:
            r = await self._session.execute(
                select(VDBCollectionModel).where(
                    VDBCollectionModel.name == name,
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"coll.find_name failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_all(self, ctx: object) -> list:
        try:
            r = await self._session.execute(
                select(VDBCollectionModel)
                .where(VDBCollectionModel.is_active.is_(True))
                .order_by(VDBCollectionModel.name.asc())
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"coll.list failed: {exc}")
            raise AppError(str(exc)) from exc

    async def delete(self, ctx: object, id: uuid.UUID) -> bool:
        try:
            stmt = (
                update(VDBCollectionModel)
                .where(VDBCollectionModel.id == id)
                .values(is_active=False)
            )
            res = await self._session.execute(stmt)
            await self._session.flush()
            return (res.rowcount or 0) > 0
        except SQLAlchemyError as exc:
            logger.error(f"coll.delete failed: {exc}")
            raise AppError(str(exc)) from exc


class VDBVectorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, ctx: object, vectors: list) -> int:
        try:
            for v in vectors:
                self._session.add(v)
            await self._session.flush()
            return len(vectors)
        except SQLAlchemyError as exc:
            logger.error(f"vec.upsert failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> VDBVectorModel | None:
        try:
            r = await self._session.execute(
                select(VDBVectorModel).where(VDBVectorModel.id == id)
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"vec.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def query_candidates(
        self, ctx: object, collection_id: uuid.UUID, limit: int,
    ) -> list:
        try:
            r = await self._session.execute(
                select(VDBVectorModel)
                .where(VDBVectorModel.collection_id == collection_id)
                .limit(max(1, min(limit, 10000)))
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"vec.query failed: {exc}")
            raise AppError(str(exc)) from exc

    async def delete(self, ctx: object, id: uuid.UUID) -> bool:
        try:
            res = await self._session.execute(
                delete(VDBVectorModel).where(VDBVectorModel.id == id)
            )
            await self._session.flush()
            return (res.rowcount or 0) > 0
        except SQLAlchemyError as exc:
            logger.error(f"vec.delete failed: {exc}")
            raise AppError(str(exc)) from exc

    async def delete_by_collection(self, ctx: object, collection_id: uuid.UUID) -> int:
        try:
            res = await self._session.execute(
                delete(VDBVectorModel).where(
                    VDBVectorModel.collection_id == collection_id,
                )
            )
            await self._session.flush()
            return int(res.rowcount or 0)
        except SQLAlchemyError as exc:
            logger.error(f"vec.delete_coll failed: {exc}")
            raise AppError(str(exc)) from exc

    async def count(self, ctx: object, collection_id: uuid.UUID) -> int:
        try:
            r = await self._session.execute(
                select(func.count()).select_from(VDBVectorModel).where(
                    VDBVectorModel.collection_id == collection_id,
                )
            )
            return int(r.scalar() or 0)
        except SQLAlchemyError as exc:
            logger.error(f"vec.count failed: {exc}")
            raise AppError(str(exc)) from exc


class VDBIndexRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, i: VDBIndexModel) -> VDBIndexModel:
        try:
            self._session.add(i)
            await self._session.flush()
            return i
        except SQLAlchemyError as exc:
            logger.error(f"idx.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> VDBIndexModel | None:
        try:
            r = await self._session.execute(
                select(VDBIndexModel).where(VDBIndexModel.id == id)
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"idx.find failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_collection(self, ctx: object, collection_id: uuid.UUID) -> list:
        try:
            r = await self._session.execute(
                select(VDBIndexModel).where(
                    VDBIndexModel.collection_id == collection_id,
                )
            )
            return list(r.scalars().all())
        except SQLAlchemyError as exc:
            logger.error(f"idx.list failed: {exc}")
            raise AppError(str(exc)) from exc


class VDBNamespaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, n: VDBNamespaceModel) -> VDBNamespaceModel:
        try:
            self._session.add(n)
            await self._session.flush()
            return n
        except SQLAlchemyError as exc:
            logger.error(f"ns.save failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_name(
        self, ctx: object, collection_id: uuid.UUID, name: str,
    ) -> VDBNamespaceModel | None:
        try:
            r = await self._session.execute(
                select(VDBNamespaceModel).where(
                    VDBNamespaceModel.collection_id == collection_id,
                    VDBNamespaceModel.namespace == name,
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"ns.find failed: {exc}")
            raise AppError(str(exc)) from exc


class VDBStatsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(self, ctx: object, s: VDBStatsModel) -> VDBStatsModel:
        try:
            self._session.add(s)
            await self._session.flush()
            return s
        except SQLAlchemyError as exc:
            logger.error(f"stats.upsert failed: {exc}")
            raise AppError(str(exc)) from exc

    async def find_by_collection(
        self, ctx: object, collection_id: uuid.UUID,
    ) -> VDBStatsModel | None:
        try:
            r = await self._session.execute(
                select(VDBStatsModel).where(
                    VDBStatsModel.collection_id == collection_id,
                )
            )
            return r.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"stats.find failed: {exc}")
            raise AppError(str(exc)) from exc
