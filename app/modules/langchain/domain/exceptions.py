"""langchain domain exceptions"""
from __future__ import annotations


class LCError(Exception):
    """TH: base | EN: base"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class ChainNotFoundError(LCError):
    code = "NOT_FOUND"


class AgentNotFoundError(LCError):
    code = "NOT_FOUND"


class MemoryNotFoundError(LCError):
    code = "NOT_FOUND"


class RunNotFoundError(LCError):
    code = "NOT_FOUND"


class ChainConflictError(LCError):
    code = "CONFLICT"


class AgentConflictError(LCError):
    code = "CONFLICT"


class InvalidChainError(LCError):
    code = "VALIDATION_ERROR"


class ExecutionError(LCError):
    code = "PROVIDER_ERROR"


class MaxIterationsExceededError(LCError):
    code = "LIMIT_EXCEEDED"


class DependencyError(LCError):
    code = "PROVIDER_ERROR"
