"""rag application ports"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, runtime_checkable

from app.modules.rag.domain.value_objects import CitationVO


@runtime_checkable
class RequestContext(Protocol):
    @property
    def tenant_id(self) -> uuid.UUID: ...
    @property
    def user_id(self) -> Optional[uuid.UUID]: ...


class DocumentRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, d: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_hash(self, ctx: Any, h: str) -> Any | None: ...
    @abstractmethod
    async def list(
        self, ctx: Any, limit: int, offset: int,
    ) -> list[Any]: ...
    @abstractmethod
    async def update(self, ctx: Any, d: Any) -> Any: ...


class ChunkRepository(ABC):
    @abstractmethod
    async def create_many(
        self, ctx: Any, chunks: list[Any],
    ) -> int: ...
    @abstractmethod
    async def find_by_document(
        self, ctx: Any, document_id: uuid.UUID,
    ) -> list[Any]: ...
    @abstractmethod
    async def delete_by_document(
        self, ctx: Any, document_id: uuid.UUID,
    ) -> int: ...


class PipelineRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, p: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all_active(self, ctx: Any) -> list[Any]: ...


class RunRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def update(self, ctx: Any, r: Any) -> Any: ...


class CitationRepository(ABC):
    @abstractmethod
    async def create_many(
        self, ctx: Any, citations: list[Any],
    ) -> int: ...
    @abstractmethod
    async def find_by_run(
        self, ctx: Any, run_id: uuid.UUID,
    ) -> list[Any]: ...


class RetrievalLogRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, log: Any) -> Any: ...
    @abstractmethod
    async def find_by_run(
        self, ctx: Any, run_id: uuid.UUID,
    ) -> list[Any]: ...


class EmbeddingPort(Protocol):
    async def embed(
        self, *, model: str, texts: list[str],
        normalize: bool = True,
    ) -> list[Any]: ...


class VectorStorePort(Protocol):
    async def upsert(
        self, *, collection_id: uuid.UUID,
        items: list[dict[str, Any]],
    ) -> int: ...

    async def query(
        self, *, collection_id: uuid.UUID,
        vector: list[float], top_k: int,
    ) -> list[Any]: ...


class HybridSearchPort(Protocol):
    async def search(
        self, *, query: str, top_k: int,
    ) -> list[Any]: ...


class RerankerPort(Protocol):
    async def rerank(
        self, *, query: str,
        candidates: list[dict[str, Any]], top_k: int,
    ) -> list[dict[str, Any]]: ...


class GeneratorPort(Protocol):
    async def chat(
        self, *, model: str, messages: list[dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Any: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...
