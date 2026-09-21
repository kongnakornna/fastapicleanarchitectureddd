from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for backup."""
    code = "bkp_DOMAIN_ERROR"