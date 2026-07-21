from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreateRequest(BaseModel):
    customer_code: str = Field(..., min_length=1, max_length=20)
    full_name: str = Field(..., min_length=1, max_length=200)
    display_name: str | None = None
    customer_type: str = "INDIVIDUAL"
    status: str = "ACTIVE"
    tax_id: str | None = None
    email: str | None = None
    phone_number: str = Field(..., min_length=1, max_length=20)
    secondary_phone: str | None = None
    address: str | None = None
    province: str | None = None
    city: str | None = None
    district: str | None = None
    postal_code: str | None = None
    country: str = "Thailand"
    contact_person: str | None = None
    contact_phone: str | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class CustomerUpdateRequest(BaseModel):
    customer_code: str | None = None
    full_name: str | None = None
    display_name: str | None = None
    customer_type: str | None = None
    status: str | None = None
    tax_id: str | None = None
    email: str | None = None
    phone_number: str | None = None
    secondary_phone: str | None = None
    address: str | None = None
    province: str | None = None
    city: str | None = None
    district: str | None = None
    postal_code: str | None = None
    country: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class CustomerResponse(BaseModel):
    id: str
    customer_code: str
    full_name: str
    display_name: str | None = None
    customer_type: str
    status: str
    tax_id: str | None = None
    email: str | None = None
    phone_number: str
    secondary_phone: str | None = None
    address: str | None = None
    province: str | None = None
    city: str | None = None
    district: str | None = None
    postal_code: str | None = None
    country: str = "Thailand"
    contact_person: str | None = None
    contact_phone: str | None = None
    notes: str | None = None
    total_visit_count: int = 0
    total_spent: float = 0.0
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class PaginatedCustomersResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")


class CarCreateRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    license_plate: str = Field(..., min_length=1, max_length=20)
    province: str | None = None
    brand: str = Field(..., min_length=1, max_length=50)
    model: str = Field(..., min_length=1, max_length=100)
    sub_model: str | None = None
    year: int | None = None
    color: str | None = None
    engine_number: str | None = None
    chassis_number: str | None = None
    fuel_type: str | None = None
    transmission_type: str | None = None
    engine_cc: int | None = None
    seating_capacity: int | None = None
    mileage: int = 0
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class CarUpdateRequest(BaseModel):
    license_plate: str | None = None
    province: str | None = None
    brand: str | None = None
    model: str | None = None
    sub_model: str | None = None
    year: int | None = None
    color: str | None = None
    engine_number: str | None = None
    chassis_number: str | None = None
    fuel_type: str | None = None
    transmission_type: str | None = None
    engine_cc: int | None = None
    seating_capacity: int | None = None
    mileage: int | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class CarResponse(BaseModel):
    id: str
    customer_id: str
    license_plate: str
    province: str | None = None
    brand: str
    model: str
    sub_model: str | None = None
    year: int | None = None
    color: str | None = None
    engine_number: str | None = None
    chassis_number: str | None = None
    fuel_type: str | None = None
    transmission_type: str | None = None
    engine_cc: int | None = None
    seating_capacity: int | None = None
    mileage: int = 0
    notes: str | None = None
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class PaginatedCarsResponse(BaseModel):
    items: list[CarResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
