"""
Audit Domain Events — domain event ของ audit
Audit Domain Events — event names + payload contracts
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from audit.domain.entities import AuditLog


# ---------------------------------------------------------------------------
# Event name constants — ค่าคงที่ชื่อ event
# ---------------------------------------------------------------------------
class AuditEventNames:
    """Domain event names — ชื่อ domain event ของ audit"""

    AUDIT_LOGGED = "AuditLogged"
    AUDIT_QUERY_EXECUTED = "AuditQueryExecuted"
    AUDIT_RETENTION_EXPIRED = "AuditRetentionExpired"


# ---------------------------------------------------------------------------
# Event payloads — payload ของ event
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AuditLogged:
    """
    Emitted after an audit log is successfully appended.
    ปล่อยหลังบันทึก audit สำเร็จ
    """

    log: AuditLog

    @property
    def name(self) -> str:
        return AuditEventNames.AUDIT_LOGGED


@dataclass(frozen=True)
class AuditQueryExecuted:
    """
    Emitted when an audit query is executed.
    ปล่อยเมื่อมีการ query audit
    """

    filters: dict[str, Any]
    page: int
    limit: int
    total: int = 0

    @property
    def name(self) -> str:
        return AuditEventNames.AUDIT_QUERY_EXECUTED


@dataclass(frozen=True)
class AuditRetentionExpired:
    """
    Emitted when retention period elapses for a log.
    ปล่อยเมื่อหมดอายุ retention
    """

    log_id: str
    retention_policy: str

    @property
    def name(self) -> str:
        return AuditEventNames.AUDIT_RETENTION_EXPIRED


__all__ = [
    "AuditEventNames",
    "AuditLogged",
    "AuditQueryExecuted",
    "AuditRetentionExpired",
]
