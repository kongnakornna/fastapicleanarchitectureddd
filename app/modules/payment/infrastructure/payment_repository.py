from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payment.domain.entities.payment import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self._session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Payment], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Payment).where(
                Payment.is_active.is_(True)
            )
        )
        total = count_result.scalar() or 0
        query = (
            select(Payment)
            .where(Payment.is_active.is_(True))
            .order_by(Payment.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def find_by_invoice_id(self, invoice_id: UUID) -> list[Payment]:
        result = await self._session.execute(
            select(Payment)
            .where(
                Payment.invoice_id == invoice_id,
                Payment.is_active.is_(True),
            )
            .order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())

    async def find_by_customer_id(
        self, customer_id: UUID, page: int = 1, page_size: int = 10
    ) -> tuple[list[Payment], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Payment).where(
                Payment.customer_id == customer_id,
                Payment.is_active.is_(True),
            )
        )
        total = count_result.scalar() or 0
        query = (
            select(Payment)
            .where(
                Payment.customer_id == customer_id,
                Payment.is_active.is_(True),
            )
            .order_by(Payment.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def search_payments(
        self,
        customer_id: UUID | None = None,
        invoice_id: UUID | None = None,
        status: str | None = None,
        payment_method_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Payment], int]:
        conditions = [Payment.is_active.is_(True)]
        if customer_id is not None:
            conditions.append(Payment.customer_id == customer_id)
        if invoice_id is not None:
            conditions.append(Payment.invoice_id == invoice_id)
        if status is not None:
            conditions.append(Payment.status == status)
        if payment_method_id is not None:
            conditions.append(Payment.payment_method_id == payment_method_id)
        if date_from is not None:
            conditions.append(Payment.payment_date >= date_from)
        if date_to is not None:
            conditions.append(Payment.payment_date <= date_to)

        count_result = await self._session.execute(
            select(func.count()).select_from(Payment).where(*conditions)
        )
        total = count_result.scalar() or 0
        query = (
            select(Payment)
            .where(*conditions)
            .order_by(Payment.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Payment).where(
                Payment.is_active.is_(True)
            )
        )
        return result.scalar() or 0

    async def create(self, payment: Payment) -> Payment:
        self._session.add(payment)
        await self._session.flush()
        return payment

    async def update(self, payment: Payment) -> Payment:
        await self._session.flush()
        return payment

    async def delete(self, payment_id: UUID) -> bool:
        payment = await self.find_by_id(payment_id)
        if payment:
            payment.is_active = False
            await self._session.flush()
            return True
        return False
