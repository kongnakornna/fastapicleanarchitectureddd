"""llm application exceptions"""
from __future__ import annotations


class ApplicationError(Exception):
    """TH: base | EN: base"""
    code: str = "APP_ERROR"
    http_status: int = 400


class ProviderNotFoundAppError(ApplicationError):
    code = "NOT_FOUND"
    http_status = 404


class ModelNotFoundAppError(ApplicationError):
    code = "NOT_FOUND"
    http_status = 404


class ConversationNotFoundAppError(ApplicationError):
    code = "NOT_FOUND"
    http_status = 404


class ProviderCallAppError(ApplicationError):
    code = "PROVIDER_ERROR"
    http_status = 502
