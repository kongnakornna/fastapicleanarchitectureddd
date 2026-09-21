from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for reporting."""
    code = "rpt_DOMAIN_ERROR"