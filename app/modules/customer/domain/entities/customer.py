from __future__ import annotations

from sqlalchemy import UUID as SQUID
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Customer(BaseModel):
    __tablename__ = "m_customer"

    customer_code: Mapped[str] = mapped_column(
        String(20), name="customer_code", unique=True, comment="Customer code"
    )
    full_name: Mapped[str] = mapped_column(
        String(200), name="full_name", comment="Full name"
    )
    display_name: Mapped[str | None] = mapped_column(
        String(200), name="display_name", nullable=True, comment="Display name"
    )
    customer_type: Mapped[str] = mapped_column(
        String(20), name="customer_type", default="INDIVIDUAL", comment="Customer type"
    )
    status: Mapped[str] = mapped_column(
        String(20), name="status", default="ACTIVE", comment="Status"
    )
    tax_id: Mapped[str | None] = mapped_column(
        String(20), name="tax_id", nullable=True, comment="Tax ID"
    )
    email: Mapped[str | None] = mapped_column(
        String(100), name="email", nullable=True, comment="Email"
    )
    phone_number: Mapped[str] = mapped_column(
        String(20), name="phone_number", comment="Phone number"
    )
    secondary_phone: Mapped[str | None] = mapped_column(
        String(20), name="secondary_phone", nullable=True, comment="Secondary phone"
    )
    address: Mapped[str | None] = mapped_column(
        Text, name="address", nullable=True, comment="Address"
    )
    province: Mapped[str | None] = mapped_column(
        String(100), name="province", nullable=True, comment="Province"
    )
    city: Mapped[str | None] = mapped_column(
        String(100), name="city", nullable=True, comment="City"
    )
    district: Mapped[str | None] = mapped_column(
        String(100), name="district", nullable=True, comment="District"
    )
    postal_code: Mapped[str | None] = mapped_column(
        String(10), name="postal_code", nullable=True, comment="Postal code"
    )
    country: Mapped[str] = mapped_column(
        String(50), name="country", default="Thailand", comment="Country"
    )
    contact_person: Mapped[str | None] = mapped_column(
        String(100), name="contact_person", nullable=True, comment="Contact person"
    )
    contact_phone: Mapped[str | None] = mapped_column(
        String(20), name="contact_phone", nullable=True, comment="Contact phone"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, name="notes", nullable=True, comment="Notes"
    )
    total_visit_count: Mapped[int] = mapped_column(
        Integer, name="total_visit_count", default=0, comment="Total visit count"
    )
    total_spent: Mapped[float] = mapped_column(
        Float, name="total_spent", default=0.0, comment="Total spent"
    )
    user_id: Mapped[str] = mapped_column(
        SQUID(as_uuid=True), name="user_id", comment="Owner user ID"
    )
    whitelabel_id: Mapped[str] = mapped_column(
        SQUID(as_uuid=True), name="whitelabel_id", comment="Whitelabel ID"
    )
