"""tool_calling domain exceptions"""
from __future__ import annotations


class ToolError(Exception):
    """TH: base | EN: base"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class ToolNotFoundError(ToolError):
    code = "NOT_FOUND"


class InvocationNotFoundError(ToolError):
    code = "NOT_FOUND"


class ToolConflictError(ToolError):
    code = "CONFLICT"


class PermissionDeniedError(ToolError):
    code = "PERMISSION_DENIED"


class RateLimitExceededError(ToolError):
    code = "RATE_LIMITED"


class InvocationTimeoutError(ToolError):
    code = "TIMEOUT"


class InvalidArgumentsError(ToolError):
    code = "VALIDATION_ERROR"


class ToolExecutionError(ToolError):
    code = "PROVIDER_ERROR"


class SecretNotFoundError(ToolError):
    code = "NOT_FOUND"
