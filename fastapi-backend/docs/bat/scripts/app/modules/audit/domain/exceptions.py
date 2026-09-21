"""
Audit Domain Exceptions — ข้อยกเว้นระดับ domain ของ audit
Audit Domain Exceptions — domain-level exceptions
"""

from __future__ import annotations

from app.shared.exceptions import DomainException


class AuditDomainError(DomainError):
    """Base domain error for audit — domain error พื้นฐานของ audit"""

    code = "AUD_DOMAIN_ERROR"
    message = "Audit domain rule violated"


class AuditImmutableDomainError(AuditDomainError):
    """Raised when mutating an immutable audit log — เกิดเมื่อพยายามแก้ไข audit log ที่ immutable"""

    code = "AUD_IMMUTABLE"
    message = "Audit log is immutable — append-only"


class AuditMissingActorError(AuditDomainError):
    """Raised when actor_id is missing — เกิดเมื่อไม่มี actor_id"""

    code = "AUD_MISSING_ACTOR"
    message = "actor_id is required for every audit log"


class AuditMissingResourceError(AuditDomainError):
    """Raised when resource_type/resource_id missing — เกิดเมื่อไม่มี resource info"""

    code = "AUD_MISSING_RESOURCE"
    message = "resource_type and resource_id are required"


__all__ = [
    "AuditDomainError",
    "AuditImmutableDomainError",
    "AuditMissingActorError",
    "AuditMissingResourceError",
]
