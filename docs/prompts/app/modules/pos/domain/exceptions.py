from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for pos."""
    code = "pos_DOMAIN_ERROR"