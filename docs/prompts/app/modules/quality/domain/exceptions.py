from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for quality."""
    code = "qc_DOMAIN_ERROR"