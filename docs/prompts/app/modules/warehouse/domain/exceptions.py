from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for warehouse."""
    code = "wh_DOMAIN_ERROR"