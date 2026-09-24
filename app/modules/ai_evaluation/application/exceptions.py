"""ai_evaluation application exceptions"""
from __future__ import annotations


class AppError(Exception):
    code: str = "APP_ERROR"
    http_status: int = 400

    def __init__(self, message: str = "", *, code: str | None = None,
                 http_status: int | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code
        if http_status:
            self.http_status = http_status


class ValidationAppError(AppError):
    code = "VALIDATION_ERROR"
    http_status = 422


class NotFoundAppError(AppError):
    code = "NOT_FOUND"
    http_status = 404


class ConflictAppError(AppError):
    code = "CONFLICT"
    http_status = 409


class EvaluatorAppError(AppError):
    code = "PROVIDER_ERROR"
    http_status = 502


class LimitExceededAppError(AppError):
    code = "LIMIT_EXCEEDED"
    http_status = 402
