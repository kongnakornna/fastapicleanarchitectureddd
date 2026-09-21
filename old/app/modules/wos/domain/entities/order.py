from __future__ import annotations

from sqlalchemy import JSON, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class WosOrder(BaseModel):
    __tablename__ = "m_wos_order"

    order_number: Mapped[str] = mapped_column(
        String(50), name="order_number", unique=True, comment="Unique order number"
    )
    customer_name: Mapped[str] = mapped_column(
        String(200), name="customer_name", comment="Customer full name"
    )
    customer_email: Mapped[str] = mapped_column(
        String(200), name="customer_email", comment="Customer email address"
    )
    customer_phone: Mapped[str | None] = mapped_column(
        String(50), name="customer_phone", nullable=True, comment="Customer phone number"
    )
    items: Mapped[dict | None] = mapped_column(
        JSON, name="items", nullable=True, comment="Order items as JSON"
    )
    total_amount: Mapped[float] = mapped_column(
        Float, name="total_amount", comment="Total order amount"
    )
    status: Mapped[str] = mapped_column(
        String(20), name="status", default="pending", server_default="pending",
        comment="Order status"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, name="notes", nullable=True, comment="Additional notes"
    )
