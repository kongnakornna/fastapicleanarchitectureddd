from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for support."""
    code = "sup2_DOMAIN_ERROR"