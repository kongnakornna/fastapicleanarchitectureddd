from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for maintenance."""
    code = "mnt_DOMAIN_ERROR"