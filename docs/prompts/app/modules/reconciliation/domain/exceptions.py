from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for reconciliation."""
    code = "rec_DOMAIN_ERROR"