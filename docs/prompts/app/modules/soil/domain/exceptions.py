from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for soil."""
    code = "soil_DOMAIN_ERROR"