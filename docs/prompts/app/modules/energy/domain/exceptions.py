from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for energy."""
    code = "eng_DOMAIN_ERROR"