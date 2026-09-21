from __future__ import annotations

from sqlalchemy import UUID as SQUID
from sqlalchemy import Boolean, Date, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Quotation(BaseModel):
    __tablename__ = "m_quotation"

    quotation_no: Mapped[str] = mapped_column(
        String(50), name="quotation_no", comment="Quotation number"
    )
    job_id: Mapped[str | None] = mapped_column(
        SQUID(as_uuid=True), name="job_id", nullable=True, comment="Job ID"
    )
    customer_id: Mapped[str | None] = mapped_column(
        SQUID(as_uuid=True), name="customer_id", nullable=True, comment="Customer ID"
    )
    quotation_date: Mapped[str | None] = mapped_column(
        Date, name="quotation_date", nullable=True, comment="Quotation date"
    )
    expiry_date: Mapped[str | None] = mapped_column(
        Date, name="expiry_date", nullable=True, comment="Expiry date"
    )
    status: Mapped[str] = mapped_column(
        String(20), name="status", default="draft", comment="Status"
    )
    subtotal: Mapped[float] = mapped_column(
        Float, name="subtotal", default=0, comment="Subtotal"
    )
    tax_rate: Mapped[float] = mapped_column(
        Float, name="tax_rate", default=0, comment="Tax rate"
    )
    tax_amount: Mapped[float] = mapped_column(
        Float, name="tax_amount", default=0, comment="Tax amount"
    )
    discount_type: Mapped[str | None] = mapped_column(
        String(20), name="discount_type", nullable=True, comment="Discount type"
    )
    discount_value: Mapped[float] = mapped_column(
        Float, name="discount_value", default=0, comment="Discount value"
    )
    total: Mapped[float] = mapped_column(
        Float, name="total", default=0, comment="Total"
    )
    amount_in_words_th: Mapped[str | None] = mapped_column(
        Text, name="amount_in_words_th", nullable=True, comment="Amount in words (Thai)"
    )
    amount_in_words_en: Mapped[str | None] = mapped_column(
        Text, name="amount_in_words_en", nullable=True, comment="Amount in words (English)"
    )
    currency: Mapped[str] = mapped_column(
        String(10), name="currency", default="THB", comment="Currency"
    )
    exchange_rate: Mapped[float] = mapped_column(
        Float, name="exchange_rate", default=1, comment="Exchange rate"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, name="notes", nullable=True, comment="Notes"
    )
    terms_and_conditions: Mapped[str | None] = mapped_column(
        Text, name="terms_and_conditions", nullable=True, comment="Terms and conditions"
    )
    approved_by: Mapped[str | None] = mapped_column(
        SQUID(as_uuid=True), name="approved_by", nullable=True, comment="Approved by user ID"
    )
    approved_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), name="approved_at", nullable=True, comment="Approval timestamp"
    )
    rejected_reason: Mapped[str | None] = mapped_column(
        Text, name="rejected_reason", nullable=True, comment="Rejection reason"
    )
    converted_to_po: Mapped[bool] = mapped_column(
        Boolean, name="converted_to_po", default=False, comment="Converted to PO"
    )
