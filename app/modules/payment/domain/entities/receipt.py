from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Receipt(BaseModel):
    __tablename__ = "m_receipt"

    receipt_no: Mapped[str] = mapped_column(
        String(50), name="receipt_no", comment="Receipt number"
    )
    payment_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True), name="payment_id", comment="Payment ID"
    )
    invoice_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="invoice_id", nullable=True, comment="Invoice ID"
    )
    customer_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="customer_id", nullable=True, comment="Customer ID"
    )
    receipt_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), name="receipt_date", nullable=True, comment="Receipt date"
    )
    receipt_type: Mapped[str] = mapped_column(
        String(20), name="receipt_type", comment="Receipt type"
    )
    amount: Mapped[float] = mapped_column(
        Float, name="amount", default=0, comment="Receipt amount"
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
    status: Mapped[str] = mapped_column(
        String(20), name="status", default="active", comment="Receipt status"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, name="notes", nullable=True, comment="Notes"
    )
    issued_by: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="issued_by", nullable=True, comment="Issued by user ID"
    )
