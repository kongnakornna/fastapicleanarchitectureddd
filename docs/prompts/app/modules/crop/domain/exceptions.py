from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for crop."""
    code = "crp_DOMAIN_ERROR"