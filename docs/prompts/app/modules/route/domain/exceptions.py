from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for route."""
    code = "rte_DOMAIN_ERROR"