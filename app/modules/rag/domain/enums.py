"""rag enums"""
from __future__ import annotations
from enum import Enum


class ChunkerType(str, Enum):
    """TH: ประเภทการแบ่ง chunk | EN: Chunker type"""
    FIXED = "fixed"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    MARKDOWN = "markdown"
    CODE = "code"

    def __str__(self) -> str:
        return str(self.value)


class RetrieverType(str, Enum):
    """TH: ประเภท retriever | EN: Retriever type"""
    VECTOR = "vector"
    BM25 = "bm25"
    HYBRID = "hybrid"
    MMR = "mmr"

    def __str__(self) -> str:
        return str(self.value)


class RerankerType(str, Enum):
    """TH: ประเภท reranker | EN: Reranker type"""
    NONE = "none"
    CROSS_ENCODER = "cross_encoder"
    COHERE = "cohere"
    BGE = "bge"

    def __str__(self) -> str:
        return str(self.value)


class DocumentStatus(str, Enum):
    """TH: สถานะเอกสาร | EN: Document status"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    DELETED = "DELETED"

    def __str__(self) -> str:
        return str(self.value)


class RunStatus(str, Enum):
    """TH: สถานะ run | EN: Run status"""
    QUEUED = "QUEUED"
    RETRIEVING = "RETRIEVING"
    RERANKING = "RERANKING"
    GENERATING = "GENERATING"
    DONE = "DONE"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return str(self.value)
