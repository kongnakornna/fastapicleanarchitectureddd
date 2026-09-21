from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for recipe."""
    code = "rcp_DOMAIN_ERROR"