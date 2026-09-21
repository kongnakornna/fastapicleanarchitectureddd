from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for waste."""
    code = "wst_DOMAIN_ERROR"