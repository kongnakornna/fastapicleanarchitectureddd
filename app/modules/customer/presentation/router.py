from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.customer.application.use_case import CustomerUseCase
from app.modules.customer.domain.entities.car import Car
from app.modules.customer.domain.entities.customer import Customer
from app.modules.customer.infrastructure.car_repository import CarRepository
from app.modules.customer.infrastructure.customer_repository import CustomerRepository
from app.modules.customer.presentation.schemas import (
    CarCreateRequest,
    CarResponse,
    CarUpdateRequest,
    CustomerCreateRequest,
    CustomerResponse,
    CustomerUpdateRequest,
    PaginatedCarsResponse,
    PaginatedCustomersResponse,
)

router = APIRouter(prefix="/customer", tags=["Customer"])


async def get_customer_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> CustomerUseCase:
    return CustomerUseCase(
        customer_repository=CustomerRepository(session),
        car_repository=CarRepository(session),
    )


def _customer_to_response(c: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=str(c.id),
        customer_code=c.customer_code,
        full_name=c.full_name,
        display_name=c.display_name,
        customer_type=c.customer_type,
        status=c.status,
        tax_id=c.tax_id,
        email=c.email,
        phone_number=c.phone_number,
        secondary_phone=c.secondary_phone,
        address=c.address,
        province=c.province,
        city=c.city,
        district=c.district,
        postal_code=c.postal_code,
        country=c.country,
        contact_person=c.contact_person,
        contact_phone=c.contact_phone,
        notes=c.notes,
        total_visit_count=c.total_visit_count,
        total_spent=c.total_spent,
        created_at=c.created_at.isoformat() if c.created_at else "",
        updated_at=c.updated_at.isoformat() if c.updated_at else "",
    )


def _car_to_response(car: Car) -> CarResponse:
    return CarResponse(
        id=str(car.id),
        customer_id=str(car.customer_id),
        license_plate=car.license_plate,
        province=car.province,
        brand=car.brand,
        model=car.model,
        sub_model=car.sub_model,
        year=car.year,
        color=car.color,
        engine_number=car.engine_number,
        chassis_number=car.chassis_number,
        fuel_type=car.fuel_type,
        transmission_type=car.transmission_type,
        engine_cc=car.engine_cc,
        seating_capacity=car.seating_capacity,
        mileage=car.mileage,
        notes=car.notes,
        created_at=car.created_at.isoformat() if car.created_at else "",
        updated_at=car.updated_at.isoformat() if car.updated_at else "",
    )


# ============================================================
# CUSTOMER ENDPOINTS
# ============================================================


@router.get("/")
async def get_customers(
    page: int = 1,
    per_page: int = 10,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> PaginatedCustomersResponse:
    per_page = min(per_page, 100)
    customers, total = await use_case.get_customers(page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedCustomersResponse(
        items=[_customer_to_response(c) for c in customers],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/")
async def create_customer(
    payload: CustomerCreateRequest,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> CustomerResponse:
    customer = Customer(
        customer_code=payload.customer_code,
        full_name=payload.full_name,
        display_name=payload.display_name,
        customer_type=payload.customer_type,
        status=payload.status,
        tax_id=payload.tax_id,
        email=payload.email,
        phone_number=payload.phone_number,
        secondary_phone=payload.secondary_phone,
        address=payload.address,
        province=payload.province,
        city=payload.city,
        district=payload.district,
        postal_code=payload.postal_code,
        country=payload.country,
        contact_person=payload.contact_person,
        contact_phone=payload.contact_phone,
        notes=payload.notes,
        user_id="00000000-0000-0000-0000-000000000000",
        whitelabel_id="00000000-0000-0000-0000-000000000000",
    )
    result = await use_case.create_customer(customer)
    return _customer_to_response(result)


@router.get("/{customer_id}")
async def get_customer(
    customer_id: str,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> CustomerResponse:
    from uuid import UUID

    customer = await use_case.get_customer(UUID(customer_id))
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return _customer_to_response(customer)


@router.put("/{customer_id}")
async def update_customer(
    customer_id: str,
    payload: CustomerUpdateRequest,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> CustomerResponse:
    from uuid import UUID

    values = payload.model_dump(exclude_none=True)
    customer = await use_case.update_customer(UUID(customer_id), values)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return _customer_to_response(customer)


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> dict[str, bool]:
    from uuid import UUID

    success = await use_case.delete_customer(UUID(customer_id))
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"success": True}


# ============================================================
# CAR ENDPOINTS
# ============================================================


@router.get("/car/")
async def get_cars(
    customer_id: str = "",
    page: int = 1,
    per_page: int = 10,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> PaginatedCarsResponse:
    from uuid import UUID

    per_page = min(per_page, 100)
    cid = UUID(customer_id) if customer_id else None
    cars, total = await use_case.get_cars(customer_id=cid, page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedCarsResponse(
        items=[_car_to_response(c) for c in cars],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/car/")
async def create_car(
    payload: CarCreateRequest,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> CarResponse:
    from uuid import UUID

    car = Car(
        customer_id=UUID(payload.customer_id),
        license_plate=payload.license_plate,
        province=payload.province,
        brand=payload.brand,
        model=payload.model,
        sub_model=payload.sub_model,
        year=payload.year,
        color=payload.color,
        engine_number=payload.engine_number,
        chassis_number=payload.chassis_number,
        fuel_type=payload.fuel_type,
        transmission_type=payload.transmission_type,
        engine_cc=payload.engine_cc,
        seating_capacity=payload.seating_capacity,
        mileage=payload.mileage,
        notes=payload.notes,
        user_id="00000000-0000-0000-0000-000000000000",
        whitelabel_id="00000000-0000-0000-0000-000000000000",
    )
    result = await use_case.create_car(car)
    return _car_to_response(result)


@router.get("/car/{car_id}")
async def get_car(
    car_id: str,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> CarResponse:
    from uuid import UUID

    car = await use_case.get_car(UUID(car_id))
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return _car_to_response(car)


@router.put("/car/{car_id}")
async def update_car(
    car_id: str,
    payload: CarUpdateRequest,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> CarResponse:
    from uuid import UUID

    values = payload.model_dump(exclude_none=True)
    car = await use_case.update_car(UUID(car_id), values)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return _car_to_response(car)


@router.delete("/car/{car_id}")
async def delete_car(
    car_id: str,
    use_case: CustomerUseCase = Depends(get_customer_use_case),
) -> dict[str, bool]:
    from uuid import UUID

    success = await use_case.delete_car(UUID(car_id))
    if not success:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"success": True}
