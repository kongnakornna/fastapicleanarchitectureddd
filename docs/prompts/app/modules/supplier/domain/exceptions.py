from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for supplier."""
    code = "sup_DOMAIN_ERROR"