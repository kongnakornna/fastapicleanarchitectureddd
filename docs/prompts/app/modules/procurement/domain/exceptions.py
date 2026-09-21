from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for procurement."""
    code = "proc_DOMAIN_ERROR"