from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customer.domain.entities.customer import Customer


class CustomerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, customer_id: UUID) -> Customer | None:
        result = await self._session.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    async def find_by_code(self, customer_code: str) -> Customer | None:
        result = await self._session.execute(
            select(Customer).where(Customer.customer_code == customer_code)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Customer], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Customer).where(
                Customer.is_active.is_(True)
            )
        )
        total = count_result.scalar() or 0
        query = (
            select(Customer)
            .where(Customer.is_active.is_(True))
            .order_by(Customer.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def find_by_user_id(
        self, user_id: UUID, page: int = 1, page_size: int = 10
    ) -> tuple[list[Customer], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Customer).where(
                Customer.user_id == user_id,
                Customer.is_active.is_(True),
            )
        )
        total = count_result.scalar() or 0
        query = (
            select(Customer)
            .where(Customer.user_id == user_id, Customer.is_active.is_(True))
            .order_by(Customer.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Customer).where(
                Customer.is_active.is_(True)
            )
        )
        return result.scalar() or 0

    async def count_by_user_id(self, user_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Customer).where(
                Customer.user_id == user_id,
                Customer.is_active.is_(True),
            )
        )
        return result.scalar() or 0

    async def create(self, customer: Customer) -> Customer:
        self._session.add(customer)
        await self._session.flush()
        return customer

    async def update(self, customer: Customer) -> Customer:
        await self._session.flush()
        return customer

    async def delete(self, customer_id: UUID) -> bool:
        customer = await self.find_by_id(customer_id)
        if customer:
            customer.is_active = False
            await self._session.flush()
            return True
        return False
