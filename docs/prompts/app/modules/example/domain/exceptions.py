from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for example."""
    code = "ex_DOMAIN_ERROR"