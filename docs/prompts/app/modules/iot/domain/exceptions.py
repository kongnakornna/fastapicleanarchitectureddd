from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for iot."""
    code = "iot_DOMAIN_ERROR"