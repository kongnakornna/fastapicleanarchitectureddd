"""
Audit Schemas — schema audit
Audit Schemas — Pydantic request/response schemas
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditQuery(BaseModel):
    """Query filters for audit logs — filter สำหรับค้นหาบันทึก audit"""

    action: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    actor_id: str | None = None
    correlation_id: str | None = None
    severity: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=50, ge=1, le=500)


class AuditLogSchema(BaseModel):
    """Audit log response schema — schema ตอบกลับบันทึก audit"""

    id: str
    action: str
    resource_type: str
    resource_id: str
    actor_id: str
    before_state: dict[str, Any] = Field(default_factory=dict)
    after_state: dict[str, Any] = Field(default_factory=dict)
    changes: list[dict[str, Any]] = Field(default_factory=list)
    ip_address: str | None = None
    user_agent: str | None = None
    correlation_id: str | None = None
    severity: str = "INFO"
    occurred_at: datetime


class AuditLogPage(BaseModel):
    """Paginated audit log response — หน้าบันทึก audit"""

    items: list[AuditLogSchema]
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        """Total pages — จำนวนหน้าทั้งหมด"""
        return (self.total + self.limit - 1) // self.limit if self.limit else 0
