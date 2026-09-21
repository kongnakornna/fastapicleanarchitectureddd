from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for traceability."""
    code = "trc_DOMAIN_ERROR"