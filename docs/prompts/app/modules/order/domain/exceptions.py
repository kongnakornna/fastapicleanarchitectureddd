from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for order."""
    code = "ord_DOMAIN_ERROR"