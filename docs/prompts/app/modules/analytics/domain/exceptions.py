from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for analytics."""
    code = "anl_DOMAIN_ERROR"