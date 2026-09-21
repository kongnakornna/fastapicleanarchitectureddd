"""Idempotency domain events — เหตุการณ์โดเมน"""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class IdempotencyLocked:
    """IdempotencyLocked — เหตุการณ์ล็อก"""
    key: str
    scope: str
    tenant_id: str
    occurred_at: datetime


@dataclass(frozen=True)
class IdempotencyCompleted:
    """IdempotencyCompleted — เหตุการณ์เสร็จสิ้น"""
    key: str
    scope: str
    tenant_id: str
    response_status: int
    occurred_at: datetime


@dataclass(frozen=True)
class IdempotencyConflictEvent:
    """IdempotencyConflictEvent — เหตุการณ์ความขัดแย้ง"""
    key: str
    scope: str
    tenant_id: str
    conflict_type: str
    occurred_at: datetime