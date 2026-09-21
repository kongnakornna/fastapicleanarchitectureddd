from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for satisfaction."""
    code = "csat_DOMAIN_ERROR"