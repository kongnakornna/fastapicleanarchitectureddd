from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for product."""
    code = "prd_DOMAIN_ERROR"