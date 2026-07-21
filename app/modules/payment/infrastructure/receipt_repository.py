from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payment.domain.entities.receipt import Receipt


class ReceiptRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, receipt_id: UUID) -> Receipt | None:
        result = await self._session.execute(
            select(Receipt).where(Receipt.id == receipt_id)
        )
        return result.scalar_one_or_none()

    async def find_by_payment_id(self, payment_id: UUID) -> Receipt | None:
        result = await self._session.execute(
            select(Receipt).where(
                Receipt.payment_id == payment_id,
                Receipt.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, receipt: Receipt) -> Receipt:
        self._session.add(receipt)
        await self._session.flush()
        return receipt

    async def update(self, receipt: Receipt) -> Receipt:
        await self._session.flush()
        return receipt
