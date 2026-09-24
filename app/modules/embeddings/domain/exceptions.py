"""embeddings domain exceptions"""
from __future__ import annotations


class EmbeddingError(Exception):
    """TH: base | EN: base"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class ProviderNotFoundError(EmbeddingError):
    code = "NOT_FOUND"


class ModelNotFoundError(EmbeddingError):
    code = "NOT_FOUND"


class VectorNotFoundError(EmbeddingError):
    code = "NOT_FOUND"


class DimensionMismatchError(EmbeddingError):
    code = "VALIDATION_ERROR"


class ProviderError(EmbeddingError):
    code = "PROVIDER_ERROR"


class RateLimitExceededError(EmbeddingError):
    code = "RATE_LIMITED"


class BatchNotFoundError(EmbeddingError):
    code = "NOT_FOUND"


class TokenLimitExceededError(EmbeddingError):
    code = "LIMIT_EXCEEDED"
