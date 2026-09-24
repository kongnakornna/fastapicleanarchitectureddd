"""embeddings enums"""
from __future__ import annotations
from enum import Enum


class EmbeddingProviderType(str, Enum):
    """TH: ประเภทผู้ให้บริการ | EN: Provider type"""
    OPENAI = "openai"
    COHERE = "cohere"
    VOYAGE = "voyage"
    HUGGINGFACE = "huggingface"
    BGE = "bge"
    LOCAL = "local"

    def __str__(self) -> str:
        return str(self.value)


class BatchStatus(str, Enum):
    """TH: สถานะ batch | EN: Batch status"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

    def __str__(self) -> str:
        return str(self.value)


class DistanceMetric(str, Enum):
    """TH: metric วัดระยะ | EN: Distance metric"""
    COSINE = "cosine"
    L2 = "l2"
    IP = "ip"

    def __str__(self) -> str:
        return str(self.value)
