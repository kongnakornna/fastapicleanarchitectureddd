from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for cctv."""
    code = "cctv_DOMAIN_ERROR"