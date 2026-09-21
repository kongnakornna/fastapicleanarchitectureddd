from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for line_channel."""
    code = "line_DOMAIN_ERROR"