"""hybrid_search domain exceptions"""
from __future__ import annotations


class HSError(Exception):
    """TH: base | EN: base"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class ConfigNotFoundError(HSError):
    code = "NOT_FOUND"


class ConfigConflictError(HSError):
    code = "CONFLICT"


class QueryNotFoundError(HSError):
    code = "NOT_FOUND"


class EmptyQueryError(HSError):
    code = "VALIDATION_ERROR"


class InvalidFusionError(HSError):
    code = "VALIDATION_ERROR"


class RetrieverError(HSError):
    code = "PROVIDER_ERROR"


class RerankerError(HSError):
    code = "PROVIDER_ERROR"


class NoResultsError(HSError):
    code = "NOT_FOUND"
