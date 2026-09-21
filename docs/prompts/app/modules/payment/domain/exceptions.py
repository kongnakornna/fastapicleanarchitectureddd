from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for payment."""
    code = "pay_DOMAIN_ERROR"