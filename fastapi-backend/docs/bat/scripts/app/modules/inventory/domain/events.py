"""Inventory domain events — เหตุการณ์โดเมน inventory"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class InventoryCreated:
    """InventoryCreated — สร้าง inventory สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    code: str
    amount: Decimal
    occurred_at: datetime


@dataclass(frozen=True)
class InventoryUpdated:
    """InventoryUpdated — แก้ไข inventory สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    changes: dict
    occurred_at: datetime


@dataclass(frozen=True)
class InventoryDeleted:
    """InventoryDeleted — ลบ inventory (soft) สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    deleted_at: datetime