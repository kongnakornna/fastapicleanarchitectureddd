from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for kpi."""
    code = "kpi_DOMAIN_ERROR"