"""hybrid_search application ports"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class RequestContext(Protocol):
    @property
    def tenant_id(self) -> uuid.UUID: ...
    @property
    def user_id(self) -> Optional[uuid.UUID]: ...


class HSConfigRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, c: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all_active(self, ctx: Any) -> list[Any]: ...


class HSQueryRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, q: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def list_recent(self, ctx: Any, limit: int = 50) -> list[Any]: ...


class HSResultRepository(ABC):
    @abstractmethod
    async def create_many(self, ctx: Any, results: list[Any]) -> int: ...
    @abstractmethod
    async def find_by_query(self, ctx: Any, query_id: uuid.UUID) -> list[Any]: ...


class HSRankingRepository(ABC):
    @abstractmethod
    async def create_many(self, ctx: Any, rows: list[Any]) -> int: ...
    @abstractmethod
    async def find_by_query(self, ctx: Any, query_id: uuid.UUID) -> list[Any]: ...


class HSRerankLogRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, log: Any) -> Any: ...
    @abstractmethod
    async def find_by_query(self, ctx: Any, query_id: uuid.UUID) -> list[Any]: ...


class EmbeddingPort(Protocol):
    """TH: port ไปยัง embeddings module | EN: embeddings port"""
    async def embed(
        self, *, model: str, texts: list[str], normalize: bool = True,
    ) -> list[Any]: ...


class VectorStorePort(Protocol):
    """TH: port ไปยัง vector_db module | EN: vector store port"""
    async def query(
        self, *, collection_id: uuid.UUID, vector: list[float],
        top_k: int,
    ) -> list[Any]: ...


class SparseRetrieverPort(Protocol):
    """TH: port BM25 retriever | EN: sparse retriever port"""
    async def search(
        self, *, corpus: str, query: str, top_k: int,
    ) -> list[dict[str, Any]]: ...


class RerankerPort(Protocol):
    """TH: port reranker | EN: reranker port"""
    async def rerank(
        self, *, query: str, candidates: list[dict[str, Any]],
        top_k: int,
    ) -> list[dict[str, Any]]: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...
