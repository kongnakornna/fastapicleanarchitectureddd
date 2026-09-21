from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for agriculture."""
    code = "agr_DOMAIN_ERROR"