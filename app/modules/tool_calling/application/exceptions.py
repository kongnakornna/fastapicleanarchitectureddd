"""tool_calling application exceptions"""
from __future__ import annotations


class ApplicationError(Exception):
    code: str = "APP_ERROR"
    http_status: int = 400


class NotFoundAppError(ApplicationError):
    code = "NOT_FOUND"
    http_status = 404


class ConflictAppError(ApplicationError):
    code = "CONFLICT"
    http_status = 409


class ValidationAppError(ApplicationError):
    code = "VALIDATION_ERROR"
    http_status = 422


class PermissionAppError(ApplicationError):
    code = "PERMISSION_DENIED"
    http_status = 403


class RateLimitAppError(ApplicationError):
    code = "RATE_LIMITED"
    http_status = 429


class TimeoutAppError(ApplicationError):
    code = "TIMEOUT"
    http_status = 504


class ExecutionAppError(ApplicationError):
    code = "PROVIDER_ERROR"
    http_status = 502
