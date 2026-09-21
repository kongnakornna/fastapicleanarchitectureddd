from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for loyalty."""
    code = "loy_DOMAIN_ERROR"