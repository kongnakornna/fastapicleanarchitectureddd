"""tenancy domain events — เหตุการณ์โดเมน."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class TenantCreated:
    """TenantCreated — สร้าง tenant สำเร็จ."""

    tenant_id: str
    slug: str
    plan: str
    occurred_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class TenantSuspended:
    """TenantSuspended — ระงับ tenant."""

    tenant_id: str
    reason: str
    occurred_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class TenantActivated:
    """TenantActivated — เปิดใช้งาน tenant."""

    tenant_id: str
    occurred_at: datetime = field(default_factory=_utcnow)
