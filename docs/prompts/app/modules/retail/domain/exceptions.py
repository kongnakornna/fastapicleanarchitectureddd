from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for retail."""
    code = "rtl_DOMAIN_ERROR"