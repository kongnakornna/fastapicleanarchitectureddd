from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for forecast."""
    code = "fc_DOMAIN_ERROR"