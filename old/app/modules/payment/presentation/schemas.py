from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PaymentRecordRequest(BaseModel):
    invoice_id: UUID | None = None
    job_id: UUID | None = None
    customer_id: UUID | None = None
    payment_method_id: UUID | None = None
    amount: float = Field(..., ge=0)
    amount_received: float | None = None
    currency: str | None = "THB"
    reference_number: str | None = None
    bank_name: str | None = None
    cheque_number: str | None = None
    cheque_bank: str | None = None
    cheque_date: date | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class PaymentSearchRequest(BaseModel):
    customer_id: UUID | None = None
    invoice_id: UUID | None = None
    status: str | None = None
    payment_method_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    page: int = 1
    per_page: int = 10

    model_config = ConfigDict(extra="forbid")


class RefundRequest(BaseModel):
    amount: float = Field(..., gt=0)
    reason: str = ""

    model_config = ConfigDict(extra="forbid")


class PaymentResponse(BaseModel):
    id: str
    payment_no: str
    invoice_id: str | None = None
    job_id: str | None = None
    customer_id: str | None = None
    payment_date: str | None = None
    payment_method_id: str | None = None
    amount: float
    amount_received: float
    change_amount: float
    currency: str
    exchange_rate: float
    status: str
    reference_number: str | None = None
    bank_name: str | None = None
    cheque_number: str | None = None
    cheque_bank: str | None = None
    cheque_date: str | None = None
    notes: str | None = None
    received_by: str | None = None
    approved_by: str | None = None
    approved_at: str | None = None
    refunded_amount: float
    refunded_at: str | None = None
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class ReceiptResponse(BaseModel):
    id: str
    receipt_no: str
    payment_id: str
    invoice_id: str | None = None
    customer_id: str | None = None
    receipt_date: str | None = None
    receipt_type: str
    amount: float
    amount_in_words_th: str | None = None
    amount_in_words_en: str | None = None
    currency: str
    status: str
    notes: str | None = None
    issued_by: str | None = None
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class PaymentHistoryResponse(BaseModel):
    id: str
    payment_id: str
    from_status: str
    to_status: str
    changed_by: str | None = None
    changed_at: str | None = None
    reason: str | None = None

    model_config = ConfigDict(extra="forbid")


class OutstandingBalanceResponse(BaseModel):
    invoice_id: str
    invoice_total: float
    amount_paid: float
    outstanding_amount: float
    last_payment_date: str | None = None
    status: str

    model_config = ConfigDict(extra="forbid")


class PaginatedPaymentsResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
