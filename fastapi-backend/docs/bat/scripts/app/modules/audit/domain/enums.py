"""
Audit Enums — enum สำหรับ audit
Audit Enums — enumerations for audit module
"""

from __future__ import annotations

from enum import Enum


class AuditAction(str, Enum):
    """Audit action types — ประเภท action ที่ถูก audit"""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    VOID = "VOID"
    PAYMENT = "PAYMENT"
    STOCK_MOVE = "STOCK_MOVE"
    READ = "READ"
    EXPORT = "EXPORT"

    def is_critical(self) -> bool:
        """Actions that touch money/stock are critical — action ที่แตะเงิน/สต็อกถือว่าสำคัญ"""
        return self in {
            AuditAction.PAYMENT,
            AuditAction.STOCK_MOVE,
            AuditAction.VOID,
            AuditAction.APPROVE,
            AuditAction.DELETE,
        }


class AuditSeverity(str, Enum):
    """Audit severity levels — ระดับความรุนแรงของ audit"""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AuditRetentionPolicy(str, Enum):
    """Retention policy — นโยบายการเก็บรักษา"""

    SEVEN_YEARS = "7Y"  # ตามกฎหมายบัญชี — per accounting law
    TEN_YEARS = "10Y"
    PERMANENT = "PERMANENT"
