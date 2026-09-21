from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for crm."""
    code = "crm_DOMAIN_ERROR"