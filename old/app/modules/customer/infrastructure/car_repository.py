from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customer.domain.entities.car import Car


class CarRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, car_id: UUID) -> Car | None:
        result = await self._session.execute(
            select(Car).where(Car.id == car_id)
        )
        return result.scalar_one_or_none()

    async def find_by_license_plate(self, license_plate: str) -> Car | None:
        result = await self._session.execute(
            select(Car).where(Car.license_plate == license_plate)
        )
        return result.scalar_one_or_none()

    async def find_all_paginated(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Car], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Car).where(Car.is_active.is_(True))
        )
        total = count_result.scalar() or 0
        query = (
            select(Car)
            .where(Car.is_active.is_(True))
            .order_by(Car.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def find_by_customer_id(
        self, customer_id: UUID, page: int = 1, page_size: int = 10
    ) -> tuple[list[Car], int]:
        count_result = await self._session.execute(
            select(func.count()).select_from(Car).where(
                Car.customer_id == customer_id,
                Car.is_active.is_(True),
            )
        )
        total = count_result.scalar() or 0
        query = (
            select(Car)
            .where(Car.customer_id == customer_id, Car.is_active.is_(True))
            .order_by(Car.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def count_by_customer_id(self, customer_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(Car).where(
                Car.customer_id == customer_id,
                Car.is_active.is_(True),
            )
        )
        return result.scalar() or 0

    async def create(self, car: Car) -> Car:
        self._session.add(car)
        await self._session.flush()
        return car

    async def update(self, car: Car) -> Car:
        await self._session.flush()
        return car

    async def delete(self, car_id: UUID) -> bool:
        car = await self.find_by_id(car_id)
        if car:
            car.is_active = False
            await self._session.flush()
            return True
        return False
