from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for gps."""
    code = "gps_DOMAIN_ERROR"