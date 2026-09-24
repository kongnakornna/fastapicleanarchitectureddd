"""llamaindex enums"""
from __future__ import annotations
from enum import Enum


class IndexType(str, Enum):
    """TH: ประเภท index | EN: Index type"""
    VECTOR_STORE = "vector_store"
    SUMMARY = "summary"
    TREE = "tree"
    KEYWORD = "keyword"
    KG = "kg"
    DOCUMENT_SUMMARY = "document_summary"

    def __str__(self) -> str:
        return str(self.value)


class NodeType(str, Enum):
    """TH: ประเภท node | EN: Node type"""
    TEXT = "text"
    IMAGE = "image"
    INDEX = "index"
    MULTIMODAL = "multimodal"

    def __str__(self) -> str:
        return str(self.value)


class ResponseMode(str, Enum):
    """TH: โหมดการสังเคราะห์คำตอบ | EN: Response mode"""
    COMPACT = "compact"
    REFINE = "refine"
    TREE_SUMMARIZE = "tree_summarize"
    SIMPLE_SUMMARIZE = "simple_summarize"
    NO_TEXT = "no_text"
    GENERATION = "generation"
    ACCUMULATE = "accumulate"

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
