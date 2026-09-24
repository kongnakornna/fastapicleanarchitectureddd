"""structured_outputs domain exceptions"""
from __future__ import annotations


class SOError(Exception):
    """TH: base | EN: base"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class SchemaNotFoundError(SOError):
    code = "NOT_FOUND"


class SchemaConflictError(SOError):
    code = "CONFLICT"


class OutputNotFoundError(SOError):
    code = "NOT_FOUND"


class RequestNotFoundError(SOError):
    code = "NOT_FOUND"


class InvalidSchemaError(SOError):
    code = "VALIDATION_ERROR"


class ParseError(SOError):
    code = "PROVIDER_ERROR"


class RepairFailedError(SOError):
    code = "PROVIDER_ERROR"


class MaxRepairsExceededError(SOError):
    code = "LIMIT_EXCEEDED"


class ProviderError(SOError):
    code = "PROVIDER_ERROR"
