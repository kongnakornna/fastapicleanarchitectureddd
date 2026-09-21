from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.quotation.domain.entities.quotation import Quotation


class QuotationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, quotation_id: UUID) -> Quotation | None:
        result = await self._session.execute(
            select(Quotation).where(Quotation.id == quotation_id)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Quotation], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Quotation).where(
                Quotation.is_active.is_(True)
            )
        )
        total = count_result.scalar() or 0
        query = (
            select(Quotation)
            .where(Quotation.is_active.is_(True))
            .order_by(Quotation.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Quotation).where(
                Quotation.is_active.is_(True)
            )
        )
        return result.scalar() or 0

    async def create(self, quotation: Quotation) -> Quotation:
        self._session.add(quotation)
        await self._session.flush()
        return quotation

    async def update(self, quotation: Quotation) -> Quotation:
        await self._session.flush()
        return quotation

    async def delete(self, quotation_id: UUID) -> bool:
        quotation = await self.find_by_id(quotation_id)
        if quotation:
            quotation.is_active = False
            await self._session.flush()
            return True
        return False
