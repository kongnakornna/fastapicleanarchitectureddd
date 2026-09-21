from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for oee."""
    code = "oee_DOMAIN_ERROR"