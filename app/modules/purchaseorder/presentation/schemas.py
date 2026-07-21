from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PurchaseOrderDetailRequest(BaseModel):
    part_id: UUID | None = None
    quantity_ordered: int = Field(default=0, ge=0)
    unit_price: float = Field(default=0, ge=0)
    discount: float = Field(default=0, ge=0)
    note: str | None = None

    model_config = ConfigDict(extra="forbid")


class PurchaseOrderCreateRequest(BaseModel):
    po_no: str = Field(..., min_length=1, max_length=50)
    quotation_id: UUID | None = None
    job_id: UUID | None = None
    supplier_id: UUID | None = None
    po_date: date | None = None
    expected_delivery_date: date | None = None
    subtotal: float = Field(default=0, ge=0)
    tax_rate: float = Field(default=0, ge=0)
    tax_amount: float = Field(default=0, ge=0)
    discount_type: str | None = None
    discount_value: float = Field(default=0, ge=0)
    total: float = Field(default=0, ge=0)
    currency: str = Field(default="THB", max_length=10)
    shipping_cost: float = Field(default=0, ge=0)
    payment_terms: str | None = None
    delivery_address: str | None = None
    notes: str | None = None
    terms_and_conditions: str | None = None
    items: list[PurchaseOrderDetailRequest] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class PurchaseOrderUpdateRequest(BaseModel):
    po_no: str | None = None
    quotation_id: UUID | None = None
    job_id: UUID | None = None
    supplier_id: UUID | None = None
    po_date: date | None = None
    expected_delivery_date: date | None = None
    subtotal: float | None = None
    tax_rate: float | None = None
    tax_amount: float | None = None
    discount_type: str | None = None
    discount_value: float | None = None
    total: float | None = None
    currency: str | None = None
    shipping_cost: float | None = None
    payment_terms: str | None = None
    delivery_address: str | None = None
    notes: str | None = None
    terms_and_conditions: str | None = None
    items: list[PurchaseOrderDetailRequest] | None = None

    model_config = ConfigDict(extra="forbid")


class PurchaseOrderStatusRequest(BaseModel):
    reason: str | None = None

    model_config = ConfigDict(extra="forbid")


class ReceiveItemRequest(BaseModel):
    detail_id: UUID
    received_quantity: int = Field(..., ge=0)

    model_config = ConfigDict(extra="forbid")


class PurchaseOrderReceiveRequest(BaseModel):
    items: list[ReceiveItemRequest]

    model_config = ConfigDict(extra="forbid")


class PurchaseOrderDetailResponse(BaseModel):
    id: UUID
    po_header_id: UUID
    part_id: UUID | None = None
    quantity_ordered: int
    quantity_received: int
    unit_price: float
    total_price: float
    discount: float
    net_price: float
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderStatusHistoryResponse(BaseModel):
    id: UUID
    po_header_id: UUID
    from_status: str
    to_status: str
    changed_by: UUID | None = None
    changed_at: datetime | None = None
    reason: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderResponse(BaseModel):
    id: UUID
    po_no: str
    quotation_id: UUID | None = None
    job_id: UUID | None = None
    supplier_id: UUID | None = None
    po_date: date | None = None
    expected_delivery_date: date | None = None
    actual_delivery_date: date | None = None
    status: str
    subtotal: float
    tax_rate: float
    tax_amount: float
    discount_type: str | None = None
    discount_value: float
    total: float
    currency: str
    exchange_rate: float
    shipping_cost: float
    payment_terms: str | None = None
    delivery_address: str | None = None
    notes: str | None = None
    terms_and_conditions: str | None = None
    sent_at: datetime | None = None
    confirmed_at: datetime | None = None
    received_by: UUID | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseOrderDetailResponse] = Field(default_factory=list)
    status_history: list[PurchaseOrderStatusHistoryResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(from_attributes=True)


class PaginatedPurchaseOrdersResponse(BaseModel):
    items: list[PurchaseOrderResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
