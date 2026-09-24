"""llamaindex domain exceptions"""
from __future__ import annotations


class LIError(Exception):
    """TH: base | EN: base"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class IndexNotFoundError(LIError):
    code = "NOT_FOUND"


class QueryEngineNotFoundError(LIError):
    code = "NOT_FOUND"


class DocumentNotFoundError(LIError):
    code = "NOT_FOUND"


class RunNotFoundError(LIError):
    code = "NOT_FOUND"


class IndexConflictError(LIError):
    code = "CONFLICT"


class QueryEngineConflictError(LIError):
    code = "CONFLICT"


class InvalidIndexTypeError(LIError):
    code = "VALIDATION_ERROR"


class IngestionError(LIError):
    code = "PROVIDER_ERROR"


class QueryError(LIError):
    code = "PROVIDER_ERROR"


class SynthesisError(LIError):
    code = "PROVIDER_ERROR"
