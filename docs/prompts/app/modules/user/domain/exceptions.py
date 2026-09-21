from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for user."""
    code = "usr_DOMAIN_ERROR"