from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for delivery."""
    code = "dlv_DOMAIN_ERROR"