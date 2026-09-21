from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WosOrderCreateRequest(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=200)
    customer_email: str = Field(..., min_length=1, max_length=200)
    customer_phone: str | None = Field(None, max_length=50)
    items: Any = Field(..., description="Order items as JSON")
    total_amount: float = Field(..., gt=0)
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class WosOrderUpdateStatusRequest(BaseModel):
    status: str = Field(..., min_length=1, max_length=20)

    model_config = ConfigDict(extra="forbid")


class WosOrderResponse(BaseModel):
    id: str
    order_number: str
    customer_name: str
    customer_email: str
    customer_phone: str | None = None
    items: Any = None
    total_amount: float
    status: str
    notes: str | None = None
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class PaginatedWosOrdersResponse(BaseModel):
    items: list[WosOrderResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
