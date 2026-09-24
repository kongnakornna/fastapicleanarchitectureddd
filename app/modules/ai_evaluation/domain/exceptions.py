"""ai_evaluation domain exceptions"""
from __future__ import annotations


class EvalError(Exception):
    """TH: base | EN: base"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class DatasetNotFoundError(EvalError):
    code = "NOT_FOUND"


class CaseNotFoundError(EvalError):
    code = "NOT_FOUND"


class RunNotFoundError(EvalError):
    code = "NOT_FOUND"


class ReportNotFoundError(EvalError):
    code = "NOT_FOUND"


class MetricNotFoundError(EvalError):
    code = "NOT_FOUND"


class DatasetConflictError(EvalError):
    code = "CONFLICT"


class EvaluatorError(EvalError):
    code = "PROVIDER_ERROR"


class InsufficientDataError(EvalError):
    code = "VALIDATION_ERROR"
