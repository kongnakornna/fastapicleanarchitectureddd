from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for audit_viewer."""
    code = "av_DOMAIN_ERROR"