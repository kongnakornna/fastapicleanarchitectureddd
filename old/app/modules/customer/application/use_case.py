from __future__ import annotations

from uuid import UUID

from app.modules.customer.domain.entities.car import Car
from app.modules.customer.domain.entities.customer import Customer
from app.modules.customer.infrastructure.car_repository import CarRepository
from app.modules.customer.infrastructure.customer_repository import CustomerRepository


class CustomerUseCase:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        car_repository: CarRepository,
    ) -> None:
        self._customer_repo = customer_repository
        self._car_repo = car_repository

    async def get_customers(
        self, user_id: UUID | None = None, page: int = 1, page_size: int = 10
    ) -> tuple[list[Customer], int]:
        if user_id:
            return await self._customer_repo.find_by_user_id(user_id, page, page_size)
        return await self._customer_repo.find_all_paginated(page, page_size)

    async def get_customer(self, customer_id: UUID) -> Customer | None:
        return await self._customer_repo.find_by_id(customer_id)

    async def create_customer(self, customer: Customer) -> Customer:
        return await self._customer_repo.create(customer)

    async def update_customer(
        self, customer_id: UUID, values: dict
    ) -> Customer | None:
        customer = await self._customer_repo.find_by_id(customer_id)
        if not customer:
            return None
        for key, value in values.items():
            if value is not None and hasattr(customer, key):
                setattr(customer, key, value)
        return await self._customer_repo.update(customer)

    async def delete_customer(self, customer_id: UUID) -> bool:
        return await self._customer_repo.delete(customer_id)

    async def count(self) -> int:
        return await self._customer_repo.count()

    async def count_by_user_id(self, user_id: UUID) -> int:
        return await self._customer_repo.count_by_user_id(user_id)

    async def get_cars(
        self, customer_id: UUID | None = None, page: int = 1, page_size: int = 10
    ) -> tuple[list[Car], int]:
        if customer_id:
            return await self._car_repo.find_by_customer_id(customer_id, page, page_size)
        return await self._car_repo.find_all_paginated(page, page_size)

    async def get_car(self, car_id: UUID) -> Car | None:
        return await self._car_repo.find_by_id(car_id)

    async def create_car(self, car: Car) -> Car:
        return await self._car_repo.create(car)

    async def update_car(self, car_id: UUID, values: dict) -> Car | None:
        car = await self._car_repo.find_by_id(car_id)
        if not car:
            return None
        for key, value in values.items():
            if value is not None and hasattr(car, key):
                setattr(car, key, value)
        return await self._car_repo.update(car)

    async def delete_car(self, car_id: UUID) -> bool:
        return await self._car_repo.delete(car_id)

    async def count_cars_by_customer(self, customer_id: UUID) -> int:
        return await self._car_repo.count_by_customer_id(customer_id)
