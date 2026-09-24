"""vector_db enums"""
from __future__ import annotations
from enum import Enum


class VDBBackend(str, Enum):
    """TH: backend | EN: Vector DB backend"""
    PGVECTOR = "pgvector"
    QDRANT = "qdrant"
    WEAVIATE = "weaviate"
    PINECONE = "pinecone"
    CHROMA = "chroma"
    MILVUS = "milvus"

    def __str__(self) -> str:
        return str(self.value)


class VectorMetric(str, Enum):
    """TH: metric วัดระยะ | EN: Vector metric"""
    COSINE = "cosine"
    L2 = "l2"
    IP = "ip"

    def __str__(self) -> str:
        return str(self.value)


class ANNIndexType(str, Enum):
    """TH: ประเภท ANN index | EN: ANN index type"""
    HNSW = "hnsw"
    IVFFLAT = "ivfflat"
    FLAT = "flat"
    SCANN = "scann"
    DISKANN = "diskann"

    def __str__(self) -> str:
        return str(self.value)


class IndexBuildStatus(str, Enum):
    """TH: สถานะการสร้าง index | EN: Index build status"""
    PENDING = "PENDING"
    BUILDING = "BUILDING"
    READY = "READY"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return str(self.value)
