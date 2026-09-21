from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import Date, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Payment(BaseModel):
    __tablename__ = "m_payment"

    payment_no: Mapped[str] = mapped_column(
        String(50), name="payment_no", comment="Payment number"
    )
    invoice_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="invoice_id", nullable=True, comment="Invoice ID"
    )
    job_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="job_id", nullable=True, comment="Job ID"
    )
    customer_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="customer_id", nullable=True, comment="Customer ID"
    )
    payment_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), name="payment_date", nullable=True, comment="Payment date"
    )
    payment_method_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="payment_method_id", nullable=True, comment="Payment method ID"
    )
    amount: Mapped[float] = mapped_column(
        Float, name="amount", default=0, comment="Payment amount"
    )
    amount_received: Mapped[float] = mapped_column(
        Float, name="amount_received", default=0, comment="Amount received"
    )
    change_amount: Mapped[float] = mapped_column(
        Float, name="change_amount", default=0, comment="Change amount"
    )
    currency: Mapped[str] = mapped_column(
        String(10), name="currency", default="THB", comment="Currency"
    )
    exchange_rate: Mapped[float] = mapped_column(
        Float, name="exchange_rate", default=1, comment="Exchange rate"
    )
    status: Mapped[str] = mapped_column(
        String(20), name="status", default="pending", comment="Payment status"
    )
    reference_number: Mapped[str | None] = mapped_column(
        String(100), name="reference_number", nullable=True, comment="Reference number"
    )
    bank_name: Mapped[str | None] = mapped_column(
        String(100), name="bank_name", nullable=True, comment="Bank name"
    )
    cheque_number: Mapped[str | None] = mapped_column(
        String(50), name="cheque_number", nullable=True, comment="Cheque number"
    )
    cheque_bank: Mapped[str | None] = mapped_column(
        String(100), name="cheque_bank", nullable=True, comment="Cheque bank"
    )
    cheque_date: Mapped[date | None] = mapped_column(
        Date, name="cheque_date", nullable=True, comment="Cheque date"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, name="notes", nullable=True, comment="Notes"
    )
    received_by: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="received_by", nullable=True, comment="Received by user ID"
    )
    approved_by: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="approved_by", nullable=True, comment="Approved by user ID"
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), name="approved_at", nullable=True, comment="Approved at"
    )
    refunded_amount: Mapped[float] = mapped_column(
        Float, name="refunded_amount", default=0, comment="Refunded amount"
    )
    refunded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), name="refunded_at", nullable=True, comment="Refunded at"
    )
