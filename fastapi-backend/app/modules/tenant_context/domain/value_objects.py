"""tenant_context value objects — วัตถุค่า บริบทผู้เช่า.

ใช้ contextvars แทน global state → async-safe
Use contextvars instead of global state → async-safe
"""
from __future__ import annotations


from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .exceptions import DomainError


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ============================================================
# TenantContext VO
# ============================================================
@dataclass(frozen=True)
class TenantContext:
    """Tenant context VO — วัตถุบริบทผู้เช่า."""

    tenant_id: str
    user_id: str | None = None
    correlation_id: str = ""
    request_id: str = ""
    locale: str = "th-TH"
    timezone: str = "Asia/Bangkok"
    established_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.tenant_id:
            raise DomainError("Tenant ID is required")
        if not self.correlation_id:
            raise DomainError("Correlation ID is required")

    @property
    def schema_name(self) -> str:
        """PostgreSQL schema name — ชื่อ schema."""
        return f"tenant_{self.tenant_id}"

    def redis_namespace(self, key: str) -> str:
        """Namespace Redis key — prefix Redis."""
        return f"t:{self.tenant_id}:{key}"

    def kafka_topic(self, topic: str) -> str:
        """Namespace Kafka topic — prefix Kafka."""
        return f"t.{self.tenant_id}.{topic}"

    def to_dict(self) -> dict:
        """Serialize to dict — แปลงเป็น dict."""
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "request_id": self.request_id,
            "locale": self.locale,
            "timezone": self.timezone,
            "established_at": self.established_at.isoformat(),
        }


# ============================================================
# RequestContext VO
# ============================================================
@dataclass(frozen=True)
class RequestContext:
    """Request context VO — วัตถุบริบทคำขอ."""

    method: str
    path: str
    ip_address: str
    user_agent: str = ""
    started_at: datetime = field(default_factory=_utcnow)


# ============================================================
# ContextVar-based propagation (async-safe)
# ============================================================
_context_var: ContextVar[TenantContext | None] = ContextVar(
    "tenant_context", default=None
)


def set_context(ctx: TenantContext) -> None:
    """Set current context — ตั้งค่า context ปัจจุบัน."""
    _context_var.set(ctx)


def get_context() -> TenantContext:
    """Get current context — ดึง context ปัจจุบัน."""
    ctx = _context_var.get()
    if ctx is None:
        raise DomainError("Tenant context not set")
    return ctx


def clear_context() -> None:
    """Clear context — ล้าง context."""
    _context_var.set(None)


def has_context() -> bool:
    """Check if context is set — ตรวจสอบว่ามี context หรือไม่."""
    return _context_var.get() is not None
