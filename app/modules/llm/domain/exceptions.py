"""llm domain exceptions — ข้อยกเว้นโดเมน llm"""
from __future__ import annotations


class LLMError(Exception):
    """TH: base error | EN: base error"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class ProviderNotFoundError(LLMError):
    code = "NOT_FOUND"


class ModelNotFoundError(LLMError):
    code = "NOT_FOUND"


class ConversationNotFoundError(LLMError):
    code = "NOT_FOUND"


class ProviderError(LLMError):
    code = "PROVIDER_ERROR"


class ProviderAuthError(LLMError):
    code = "PROVIDER_ERROR"


class RateLimitExceededError(LLMError):
    code = "RATE_LIMITED"


class TokenLimitExceededError(LLMError):
    code = "LIMIT_EXCEEDED"


class InvalidMessageRoleError(LLMError):
    code = "VALIDATION_ERROR"


class StreamingError(LLMError):
    code = "PROVIDER_ERROR"
