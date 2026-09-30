"""Memory repository"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bigo.application.exceptions import ApplicationError
from app.modules.bigo.infrastructure.models import (
    MemoryLeakModel, MemorySnapshotModel,
)


class SqlMemoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_snapshot(self, ctx: Any, snap: MemorySnapshotModel) -> MemorySnapshotModel:
        try:
            self._session.add(snap)
            await self._session.flush()
            return snap
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def save_leak(self, ctx: Any, leak: MemoryLeakModel) -> MemoryLeakModel:
        try:
            self._session.add(leak)
            await self._session.flush()
            return leak
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_snapshots(
        self, ctx: Any, since: datetime, limit: int = 50,
    ) -> list[MemorySnapshotModel]:
        try:
            result = await self._session.execute(
                select(MemorySnapshotModel)
                .where(MemorySnapshotModel.captured_at >= since)
                .order_by(MemorySnapshotModel.captured_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def find_leaks(
        self, ctx: Any, status: str = "OPEN", limit: int = 50,
    ) -> list[MemoryLeakModel]:
        try:
            stmt = select(MemoryLeakModel).where(MemoryLeakModel.status == status)
            stmt = stmt.order_by(MemoryLeakModel.growth_mb_per_hour.desc()).limit(limit)
            result = await self._session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc

    async def update_leak_status(
        self, ctx: Any, leak_id: uuid.UUID, status: str,
    ) -> bool:
        try:
            leak = await self._session.get(MemoryLeakModel, leak_id)
            if leak is None:
                return False
            leak.status = status
            await self._session.flush()
            return True
        except SQLAlchemyError as exc:
            raise ApplicationError(str(exc)) from exc
