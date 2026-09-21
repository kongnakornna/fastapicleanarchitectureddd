from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for alerting."""
    code = "alr_DOMAIN_ERROR"