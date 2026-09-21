from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for promotion."""
    code = "promo_DOMAIN_ERROR"