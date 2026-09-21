"""tenant_context domain events — เหตุการณ์โดเมน."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class TenantContextEstablished:
    """TenantContextEstablished — สร้าง context สำเร็จ."""

    tenant_id: str
    user_id: str | None
    correlation_id: str
    request_id: str
    occurred_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class TenantContextCleared:
    """TenantContextCleared — ล้าง context."""

    tenant_id: str
    correlation_id: str
    occurred_at: datetime = field(default_factory=_utcnow)


@dataclass(frozen=True)
class TenantSwitched:
    """TenantSwitched — เปลี่ยน tenant."""

    from_tenant_id: str
    to_tenant_id: str
    user_id: str | None
    occurred_at: datetime = field(default_factory=_utcnow)
