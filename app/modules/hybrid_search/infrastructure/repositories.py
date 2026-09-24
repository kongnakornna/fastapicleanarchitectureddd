"""hybrid_search repositories"""
from __future__ import annotations
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hybrid_search.application.exceptions import AppError
from app.modules.hybrid_search.infrastructure.models import (
    HSConfigModel, HSQueryModel, HSRankingModel, HSRerankLogModel,
    HSResultModel,
)

logger = logging.getLogger(__name__)


class HSConfigRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, c: HSConfigModel) -> HSConfigModel:
        try:
            self._session.add(c)
            await self._session.flush()
            return c
        except SQLAlchemyError as exc:
            logger.exception("config.save failed")
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> HSConfigModel | None:
        r = await self._session.execute(
            select(HSConfigModel).where(HSConfigModel.id == id)
        )
        return r.scalar_one_or_none()

    async def find_by_name(self, ctx: object, name: str) -> HSConfigModel | None:
        r = await self._session.execute(
            select(HSConfigModel).where(HSConfigModel.name == name)
        )
        return r.scalar_one_or_none()

    async def find_all_active(self, ctx: object) -> list[HSConfigModel]:
        r = await self._session.execute(
            select(HSConfigModel)
            .where(HSConfigModel.is_active.is_(True))
            .order_by(HSConfigModel.name)
        )
        return list(r.scalars().all())


class HSQueryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, q: HSQueryModel) -> HSQueryModel:
        self._session.add(q)
        await self._session.flush()
        return q

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> HSQueryModel | None:
        r = await self._session.execute(
            select(HSQueryModel).where(HSQueryModel.id == id)
        )
        return r.scalar_one_or_none()

    async def list_recent(self, ctx: object, limit: int = 50) -> list[HSQueryModel]:
        r = await self._session.execute(
            select(HSQueryModel)
            .order_by(HSQueryModel.created_at.desc())
            .limit(max(1, min(limit, 500)))
        )
        return list(r.scalars().all())


class HSResultRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, ctx: object, results: list) -> int:
        for r in results:
            self._session.add(r)
        await self._session.flush()
        return len(results)

    async def find_by_query(
        self, ctx: object, query_id: uuid.UUID,
    ) -> list[HSResultModel]:
        r = await self._session.execute(
            select(HSResultModel)
            .where(HSResultModel.query_id == query_id)
            .order_by(HSResultModel.rank)
        )
        return list(r.scalars().all())


class HSRankingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, ctx: object, rows: list) -> int:
        for r in rows:
            self._session.add(r)
        await self._session.flush()
        return len(rows)

    async def find_by_query(
        self, ctx: object, query_id: uuid.UUID,
    ) -> list[HSRankingModel]:
        r = await self._session.execute(
            select(HSRankingModel)
            .where(HSRankingModel.query_id == query_id)
            .order_by(HSRankingModel.stage, HSRankingModel.rank)
        )
        return list(r.scalars().all())


class HSRerankLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, log: HSRerankLogModel) -> HSRerankLogModel:
        self._session.add(log)
        await self._session.flush()
        return log

    async def find_by_query(
        self, ctx: object, query_id: uuid.UUID,
    ) -> list[HSRerankLogModel]:
        r = await self._session.execute(
            select(HSRerankLogModel).where(HSRerankLogModel.query_id == query_id)
        )
        return list(r.scalars().all())
