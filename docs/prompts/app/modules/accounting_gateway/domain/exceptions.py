from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for accounting_gateway."""
    code = "acg_DOMAIN_ERROR"