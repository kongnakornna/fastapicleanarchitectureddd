# app/shared/exceptions.py - base exceptions (3-branch pattern)


class StandardException(Exception):
    """Base for all application exceptions."""

    code: str = "STD_ERROR"


class DomainException(StandardException):
    """Raised when a domain rule is violated."""

    code = "DOMAIN_ERROR"


class ApplicationException(StandardException):
    """Raised by use cases."""

    code = "APP_ERROR"


class InfrastructureException(StandardException):
    """Raised by repositories / external services."""

    code = "INFRA_ERROR"
