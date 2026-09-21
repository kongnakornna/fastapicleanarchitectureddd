"""Money domain events — เหตุการณ์โดเมน money"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class MoneyCreated:
    """MoneyCreated — สร้าง money สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    code: str
    amount: Decimal
    occurred_at: datetime


@dataclass(frozen=True)
class MoneyUpdated:
    """MoneyUpdated — แก้ไข money สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    changes: dict
    occurred_at: datetime


@dataclass(frozen=True)
class MoneyDeleted:
    """MoneyDeleted — ลบ money (soft) สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    deleted_at: datetime