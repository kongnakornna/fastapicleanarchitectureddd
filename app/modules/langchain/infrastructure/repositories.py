"""langchain repositories"""
from __future__ import annotations
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.langchain.application.exceptions import AppError
from app.modules.langchain.infrastructure.models import (
    LCAgentModel, LCChainModel, LCMemoryModel, LCRunModel,
    LCTraceModel,
)

logger = logging.getLogger(__name__)


class LCChainRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, c: LCChainModel) -> LCChainModel:
        try:
            self._session.add(c)
            await self._session.flush()
            return c
        except SQLAlchemyError as exc:
            raise AppError(str(exc)) from exc

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> LCChainModel | None:
        r = await self._session.execute(
            select(LCChainModel).where(LCChainModel.id == id)
        )
        return r.scalar_one_or_none()

    async def find_by_name(self, ctx: object, name: str) -> LCChainModel | None:
        r = await self._session.execute(
            select(LCChainModel).where(LCChainModel.name == name)
        )
        return r.scalar_one_or_none()

    async def find_all_active(self, ctx: object) -> list[LCChainModel]:
        r = await self._session.execute(
            select(LCChainModel)
            .where(LCChainModel.is_active.is_(True))
            .order_by(LCChainModel.name)
        )
        return list(r.scalars().all())


class LCAgentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, a: LCAgentModel) -> LCAgentModel:
        self._session.add(a)
        await self._session.flush()
        return a

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> LCAgentModel | None:
        r = await self._session.execute(
            select(LCAgentModel).where(LCAgentModel.id == id)
        )
        return r.scalar_one_or_none()

    async def find_by_name(self, ctx: object, name: str) -> LCAgentModel | None:
        r = await self._session.execute(
            select(LCAgentModel).where(LCAgentModel.name == name)
        )
        return r.scalar_one_or_none()

    async def find_all_active(self, ctx: object) -> list[LCAgentModel]:
        r = await self._session.execute(
            select(LCAgentModel)
            .where(LCAgentModel.is_active.is_(True))
            .order_by(LCAgentModel.name)
        )
        return list(r.scalars().all())


class LCMemoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, ctx: object, m: LCMemoryModel) -> LCMemoryModel:
        self._session.add(m)
        await self._session.flush()
        return m

    async def find_by_conversation(
        self, ctx: object, conversation_id: uuid.UUID,
    ) -> LCMemoryModel | None:
        r = await self._session.execute(
            select(LCMemoryModel).where(
                LCMemoryModel.conversation_id == conversation_id
            )
        )
        return r.scalar_one_or_none()


class LCRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, ctx: object, r_: LCRunModel) -> LCRunModel:
        self._session.add(r_)
        await self._session.flush()
        return r_

    async def find_by_id(self, ctx: object, id: uuid.UUID) -> LCRunModel | None:
        r = await self._session.execute(
            select(LCRunModel).where(LCRunModel.id == id)
        )
        return r.scalar_one_or_none()

    async def update(self, ctx: object, r_: LCRunModel) -> LCRunModel:
        await self._session.flush()
        return r_

    async def list_by_user(
        self, ctx: object, user_id: uuid.UUID, limit: int,
    ) -> list[LCRunModel]:
        r = await self._session.execute(
            select(LCRunModel)
            .where(LCRunModel.user_id == user_id)
            .order_by(LCRunModel.created_at.desc())
            .limit(max(1, min(limit, 500)))
        )
        return list(r.scalars().all())


class LCTraceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_many(self, ctx: object, traces: list) -> int:
        for t in traces:
            self._session.add(t)
        await self._session.flush()
        return len(traces)

    async def find_by_run(
        self, ctx: object, run_id: uuid.UUID,
    ) -> list[LCTraceModel]:
        r = await self._session.execute(
            select(LCTraceModel)
            .where(LCTraceModel.run_id == run_id)
            .order_by(LCTraceModel.step)
        )
        return list(r.scalars().all())
