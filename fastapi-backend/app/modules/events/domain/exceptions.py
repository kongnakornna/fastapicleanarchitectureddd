# events/domain/exceptions.py
# Domain exceptions — ข้อยกเว้นชั้นโดเมน

from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for events."""

    code = "evt_DOMAIN_ERROR"
