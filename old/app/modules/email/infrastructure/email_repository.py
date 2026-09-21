from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.email.domain.entities.email_config import EmailConfig
from app.modules.email.domain.entities.email_log import EmailLog


class EmailRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, log_id: UUID) -> EmailLog | None:
        result = await self._session.execute(
            select(EmailLog).where(EmailLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[EmailLog], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(EmailLog).where(EmailLog.is_active.is_(True))
        )
        total = count_result.scalar() or 0
        query = (
            select(EmailLog)
            .where(EmailLog.is_active.is_(True))
            .order_by(EmailLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def create(self, log: EmailLog) -> EmailLog:
        self._session.add(log)
        await self._session.flush()
        return log

    async def update(self, log: EmailLog) -> EmailLog:
        await self._session.flush()
        return log

    async def delete(self, log_id: UUID) -> bool:
        log = await self.find_by_id(log_id)
        if log:
            log.is_active = False
            await self._session.flush()
            return True
        return False

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(EmailLog).where(EmailLog.is_active.is_(True))
        )
        return result.scalar() or 0

    async def get_config(self) -> EmailConfig | None:
        result = await self._session.execute(
            select(EmailConfig).where(EmailConfig.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def update_config(self, config: EmailConfig) -> EmailConfig:
        await self._session.flush()
        return config
