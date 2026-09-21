"""
Audit Application Exceptions — ข้อยกเว้นระดับ application ของ audit
Audit Application Exceptions — application-level exceptions
"""

from __future__ import annotations

from app.shared.exceptions import StandardException


class AuditException(StandardException):
    """Base audit exception — ข้อยกเว้นพื้นฐาน audit"""

    code = "AUDIT_ERROR"
    message = "Audit operation failed"


class AuditImmutableViolation(AuditException):
    """Raised when attempting to modify/delete audit log — เกิดเมื่อพยายามแก้ไข/ลบบันทึก audit"""

    code = "AUDIT_IMMUTABLE_VIOLATION"
    message = "Audit log is immutable — append-only"

    def __init__(self, detail: str = "") -> None:
        super().__init__()
        if detail:
            self.message = f"{self.message}: {detail}"


class AuditRetentionViolation(AuditException):
    """Raised when attempting to delete audit log before retention period."""

    code = "AUDIT_RETENTION_VIOLATION"
    message = "Cannot delete audit log before retention period (7 years)"


class AuditNotFoundException(AuditException):
    """Raised when audit log not found — เกิดเมื่อไม่พบบันทึก audit"""

    code = "AUDIT_NOT_FOUND"
    message = "Audit log not found"


__all__ = [
    "AuditException",
    "AuditImmutableViolation",
    "AuditNotFoundException",
    "AuditRetentionViolation",
]
