"""hybrid_search enums"""
from __future__ import annotations
from enum import Enum


class FusionType(str, Enum):
    """TH: ประเภท fusion | EN: Fusion type"""
    RRF = "rrf"
    WEIGHTED_SUM = "weighted_sum"
    COMB_SUM = "comb_sum"
    COMB_MNZ = "comb_mnz"
    BORDA = "borda"
    DBSF = "dbsf"

    def __str__(self) -> str:
        return str(self.value)


class SourceKind(str, Enum):
    """TH: แหล่งที่มา | EN: Source kind"""
    BM25 = "bm25"
    VECTOR = "vector"
    HYBRID = "hybrid"
    RERANK = "rerank"

    def __str__(self) -> str:
        return str(self.value)


class RerankerType(str, Enum):
    """TH: ประเภท reranker | EN: Reranker type"""
    NONE = "none"
    CROSS_ENCODER = "cross_encoder"
    COHERE = "cohere"
    BGE = "bge"
    COLBERT = "colbert"

    def __str__(self) -> str:
        return str(self.value)
