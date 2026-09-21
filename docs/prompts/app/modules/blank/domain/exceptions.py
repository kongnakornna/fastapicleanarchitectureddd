from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for blank."""
    code = "blk_DOMAIN_ERROR"