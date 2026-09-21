"""123Abc domain events — เหตุการณ์โดเมน 123abc"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class 123AbcCreated:
    """123AbcCreated — สร้าง 123abc สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    code: str
    amount: Decimal
    occurred_at: datetime


@dataclass(frozen=True)
class 123AbcUpdated:
    """123AbcUpdated — แก้ไข 123abc สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    changes: dict
    occurred_at: datetime


@dataclass(frozen=True)
class 123AbcDeleted:
    """123AbcDeleted — ลบ 123abc (soft) สำเร็จ"""
    entity_id: UUID
    tenant_id: UUID
    deleted_at: datetime