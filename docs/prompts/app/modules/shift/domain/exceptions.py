from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for shift."""
    code = "shf_DOMAIN_ERROR"