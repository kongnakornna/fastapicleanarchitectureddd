from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class QuotationCreateRequest(BaseModel):
    quotation_no: str = Field(..., min_length=1, max_length=50)
    job_id: str | None = None
    customer_id: str | None = None
    quotation_date: str | None = None
    expiry_date: str | None = None
    subtotal: float = 0
    tax_rate: float = 0
    tax_amount: float = 0
    discount_type: str | None = None
    discount_value: float = 0
    total: float = 0
    currency: str = "THB"
    notes: str | None = None
    terms_and_conditions: str | None = None

    model_config = ConfigDict(extra="forbid")


class QuotationUpdateRequest(BaseModel):
    quotation_no: str | None = None
    job_id: str | None = None
    customer_id: str | None = None
    quotation_date: str | None = None
    expiry_date: str | None = None
    status: str | None = None
    subtotal: float | None = None
    tax_rate: float | None = None
    tax_amount: float | None = None
    discount_type: str | None = None
    discount_value: float | None = None
    total: float | None = None
    amount_in_words_th: str | None = None
    amount_in_words_en: str | None = None
    currency: str | None = None
    exchange_rate: float | None = None
    notes: str | None = None
    terms_and_conditions: str | None = None
    approved_by: str | None = None
    approved_at: str | None = None
    rejected_reason: str | None = None
    converted_to_po: bool | None = None

    model_config = ConfigDict(extra="forbid")


class QuotationResponse(BaseModel):
    id: str
    quotation_no: str
    job_id: str | None = None
    customer_id: str | None = None
    quotation_date: str | None = None
    expiry_date: str | None = None
    status: str
    subtotal: float
    tax_rate: float
    tax_amount: float
    discount_type: str | None = None
    discount_value: float
    total: float
    amount_in_words_th: str | None = None
    amount_in_words_en: str | None = None
    currency: str
    exchange_rate: float
    notes: str | None = None
    terms_and_conditions: str | None = None
    approved_by: str | None = None
    approved_at: str | None = None
    rejected_reason: str | None = None
    converted_to_po: bool
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class PaginatedQuotationsResponse(BaseModel):
    items: list[QuotationResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
