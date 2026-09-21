from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for inventory."""
    code = "invt_DOMAIN_ERROR"