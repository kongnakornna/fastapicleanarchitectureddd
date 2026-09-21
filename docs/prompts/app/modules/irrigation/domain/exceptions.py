from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for irrigation."""
    code = "irr_DOMAIN_ERROR"