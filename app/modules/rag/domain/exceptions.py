"""rag domain exceptions"""
from __future__ import annotations


class RAGError(Exception):
    """TH: base | EN: base"""
    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str = "", *, code: str | None = None) -> None:
        super().__init__(message or self.__class__.__name__)
        if code:
            self.code = code


class DocumentNotFoundError(RAGError):
    code = "NOT_FOUND"


class ChunkNotFoundError(RAGError):
    code = "NOT_FOUND"


class PipelineNotFoundError(RAGError):
    code = "NOT_FOUND"


class RunNotFoundError(RAGError):
    code = "NOT_FOUND"


class IngestionFailedError(RAGError):
    code = "PROVIDER_ERROR"


class ChunkingFailedError(RAGError):
    code = "PROVIDER_ERROR"


class RetrievalFailedError(RAGError):
    code = "PROVIDER_ERROR"


class GenerationFailedError(RAGError):
    code = "PROVIDER_ERROR"


class DuplicateDocumentError(RAGError):
    code = "CONFLICT"


class EmptyQueryError(RAGError):
    code = "VALIDATION_ERROR"
