from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for recommendation."""
    code = "reco_DOMAIN_ERROR"