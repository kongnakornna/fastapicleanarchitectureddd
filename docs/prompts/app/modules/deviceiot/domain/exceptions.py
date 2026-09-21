from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for deviceiot."""
    code = "deviceiot_DOMAIN_ERROR"