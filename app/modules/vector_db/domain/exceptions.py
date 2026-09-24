"""vector_db domain exceptions"""
from __future__ import annotations


class VectorDBError(Exception):
    """TH: base | EN: base"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class CollectionNotFoundError(VectorDBError):
    code = "NOT_FOUND"


class VectorNotFoundError(VectorDBError):
    code = "NOT_FOUND"


class IndexNotFoundError(VectorDBError):
    code = "NOT_FOUND"


class DimensionMismatchError(VectorDBError):
    code = "VALIDATION_ERROR"


class CollectionConflictError(VectorDBError):
    code = "CONFLICT"


class BackendError(VectorDBError):
    code = "PROVIDER_ERROR"


class IndexBuildError(VectorDBError):
    code = "PROVIDER_ERROR"


class NamespaceQuotaExceededError(VectorDBError):
    code = "LIMIT_EXCEEDED"
