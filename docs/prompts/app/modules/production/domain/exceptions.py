from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for production."""
    code = "prod_DOMAIN_ERROR"