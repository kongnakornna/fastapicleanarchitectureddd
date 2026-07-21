from __future__ import annotations

from sqlalchemy import UUID as SQUID
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Car(BaseModel):
    __tablename__ = "m_car"

    customer_id: Mapped[str] = mapped_column(
        SQUID(as_uuid=True), name="customer_id", comment="Customer ID"
    )
    license_plate: Mapped[str] = mapped_column(
        String(20), name="license_plate", unique=True, comment="License plate"
    )
    province: Mapped[str | None] = mapped_column(
        String(50), name="province", nullable=True, comment="Province"
    )
    brand: Mapped[str] = mapped_column(
        String(50), name="brand", comment="Brand"
    )
    model: Mapped[str] = mapped_column(
        String(100), name="model", comment="Model"
    )
    sub_model: Mapped[str | None] = mapped_column(
        String(100), name="sub_model", nullable=True, comment="Sub model"
    )
    year: Mapped[int | None] = mapped_column(
        Integer, name="year", nullable=True, comment="Year"
    )
    color: Mapped[str | None] = mapped_column(
        String(30), name="color", nullable=True, comment="Color"
    )
    engine_number: Mapped[str | None] = mapped_column(
        String(50), name="engine_number", nullable=True, comment="Engine number"
    )
    chassis_number: Mapped[str | None] = mapped_column(
        String(50), name="chassis_number", nullable=True, comment="Chassis number"
    )
    fuel_type: Mapped[str | None] = mapped_column(
        String(20), name="fuel_type", nullable=True, comment="Fuel type"
    )
    transmission_type: Mapped[str | None] = mapped_column(
        String(20), name="transmission_type", nullable=True, comment="Transmission type"
    )
    engine_cc: Mapped[int | None] = mapped_column(
        Integer, name="engine_cc", nullable=True, comment="Engine CC"
    )
    seating_capacity: Mapped[int | None] = mapped_column(
        Integer, name="seating_capacity", nullable=True, comment="Seating capacity"
    )
    mileage: Mapped[int] = mapped_column(
        Integer, name="mileage", default=0, comment="Mileage"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, name="notes", nullable=True, comment="Notes"
    )
    user_id: Mapped[str] = mapped_column(
        SQUID(as_uuid=True), name="user_id", comment="Owner user ID"
    )
    whitelabel_id: Mapped[str] = mapped_column(
        SQUID(as_uuid=True), name="whitelabel_id", comment="Whitelabel ID"
    )
