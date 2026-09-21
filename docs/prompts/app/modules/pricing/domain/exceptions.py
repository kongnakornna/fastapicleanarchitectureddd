from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for pricing."""
    code = "prc_DOMAIN_ERROR"