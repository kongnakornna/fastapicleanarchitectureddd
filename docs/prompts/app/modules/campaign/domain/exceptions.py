from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for campaign."""
    code = "cmp_DOMAIN_ERROR"