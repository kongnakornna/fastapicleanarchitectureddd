from app.shared.exceptions import DomainException


class DomainError(DomainException):
    """Domain rule violation for employee."""
    code = "emp_DOMAIN_ERROR"