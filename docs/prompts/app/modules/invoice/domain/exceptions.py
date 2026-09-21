from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for invoice."""
    code = "inv_DOMAIN_ERROR"