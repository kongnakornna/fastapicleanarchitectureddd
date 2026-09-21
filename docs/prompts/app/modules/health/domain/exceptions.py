from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for health."""
    code = "hlth_DOMAIN_ERROR"