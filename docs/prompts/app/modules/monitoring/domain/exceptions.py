from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for monitoring."""
    code = "mon_DOMAIN_ERROR"