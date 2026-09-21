from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for tax."""
    code = "tax_DOMAIN_ERROR"