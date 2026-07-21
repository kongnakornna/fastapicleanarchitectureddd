from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payment.domain.entities.payment_history import PaymentHistory


class PaymentHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_payment_id(self, payment_id: UUID) -> list[PaymentHistory]:
        result = await self._session.execute(
            select(PaymentHistory)
            .where(PaymentHistory.payment_id == payment_id)
            .order_by(PaymentHistory.changed_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, payment_history: PaymentHistory) -> PaymentHistory:
        self._session.add(payment_history)
        await self._session.flush()
        return payment_history
