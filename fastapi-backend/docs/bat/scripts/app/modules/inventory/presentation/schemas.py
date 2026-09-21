"""Inventory schemas — Pydantic v2"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..domain.enums import InventoryStatus


class InventoryCreateRequest(BaseModel):
    """InventoryCreateRequest — payload สร้างใหม่"""
    model_config = ConfigDict(strict=True, extra="forbid")

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    currency: str = Field(default="THB", pattern="^(THB|USD|EUR)$")
    metadata: dict = Field(default_factory=dict)


class InventoryUpdateRequest(BaseModel):
    """InventoryUpdateRequest — payload แก้ไข (partial)"""
    model_config = ConfigDict(strict=True, extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    version: int | None = Field(default=None, ge=1)


class InventoryResponse(BaseModel):
    """InventoryResponse — response เดี่ยว"""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    code: str
    name: str
    amount: Decimal
    currency: str = "THB"
    status: InventoryStatus
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class InventoryListResponse(BaseModel):
    """InventoryListResponse — response list"""

    items: list[InventoryResponse]
    total: int
    limit: int
    offset: int