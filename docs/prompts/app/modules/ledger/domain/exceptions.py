from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for ledger."""
    code = "led_DOMAIN_ERROR"