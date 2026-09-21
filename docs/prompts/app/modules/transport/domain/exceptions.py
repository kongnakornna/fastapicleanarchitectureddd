from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for transport."""
    code = "trn_DOMAIN_ERROR"