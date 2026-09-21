from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import Date, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class PurchaseOrderHeader(BaseModel):
    __tablename__ = "m_purchase_order_header"

    po_no: Mapped[str] = mapped_column(
        String(50), name="po_no", comment="Purchase order number"
    )
    quotation_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="quotation_id", nullable=True, comment="Related quotation ID"
    )
    job_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="job_id", nullable=True, comment="Related job ID"
    )
    supplier_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="supplier_id", nullable=True, comment="Supplier ID"
    )
    po_date: Mapped[date | None] = mapped_column(
        Date, name="po_date", nullable=True, comment="Purchase order date"
    )
    expected_delivery_date: Mapped[date | None] = mapped_column(
        Date, name="expected_delivery_date", nullable=True, comment="Expected delivery date"
    )
    actual_delivery_date: Mapped[date | None] = mapped_column(
        Date, name="actual_delivery_date", nullable=True, comment="Actual delivery date"
    )
    status: Mapped[str] = mapped_column(
        String(20), name="status", default="draft", comment="PO status"
    )
    subtotal: Mapped[float] = mapped_column(
        Float, name="subtotal", default=0, comment="Subtotal amount"
    )
    tax_rate: Mapped[float] = mapped_column(
        Float, name="tax_rate", default=0, comment="Tax rate percentage"
    )
    tax_amount: Mapped[float] = mapped_column(
        Float, name="tax_amount", default=0, comment="Tax amount"
    )
    discount_type: Mapped[str | None] = mapped_column(
        String(20), name="discount_type", nullable=True, comment="Discount type (percentage/fixed)"
    )
    discount_value: Mapped[float] = mapped_column(
        Float, name="discount_value", default=0, comment="Discount value"
    )
    total: Mapped[float] = mapped_column(
        Float, name="total", default=0, comment="Total amount"
    )
    currency: Mapped[str] = mapped_column(
        String(10), name="currency", default="THB", comment="Currency code"
    )
    exchange_rate: Mapped[float] = mapped_column(
        Float, name="exchange_rate", default=1, comment="Exchange rate"
    )
    shipping_cost: Mapped[float] = mapped_column(
        Float, name="shipping_cost", default=0, comment="Shipping cost"
    )
    payment_terms: Mapped[str | None] = mapped_column(
        Text, name="payment_terms", nullable=True, comment="Payment terms"
    )
    delivery_address: Mapped[str | None] = mapped_column(
        Text, name="delivery_address", nullable=True, comment="Delivery address"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, name="notes", nullable=True, comment="Notes"
    )
    terms_and_conditions: Mapped[str | None] = mapped_column(
        Text, name="terms_and_conditions", nullable=True, comment="Terms and conditions"
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime, name="sent_at", nullable=True, comment="Timestamp when PO was sent"
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime, name="confirmed_at", nullable=True, comment="Timestamp when PO was confirmed"
    )
    received_by: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="received_by", nullable=True,
        comment="User who received the goods"
    )
