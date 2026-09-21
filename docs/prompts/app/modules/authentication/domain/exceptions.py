from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for authentication."""
    code = "auth_DOMAIN_ERROR"