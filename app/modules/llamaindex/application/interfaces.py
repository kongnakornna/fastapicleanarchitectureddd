"""llamaindex application ports"""
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


class LIIndexRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, i: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all_active(self, ctx: Any) -> list[Any]: ...


class LINodeRepository(ABC):
    @abstractmethod
    async def create_many(self, ctx: Any, nodes: list[Any]) -> int: ...
    @abstractmethod
    async def find_by_index(
        self, ctx: Any, index_id: uuid.UUID,
    ) -> list[Any]: ...
    @abstractmethod
    async def delete_by_document(
        self, ctx: Any, document_id: uuid.UUID,
    ) -> int: ...


class LIQueryEngineRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, q: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_index(
        self, ctx: Any, index_id: uuid.UUID,
    ) -> list[Any]: ...


class LIDocumentRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, d: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_hash(self, ctx: Any, h: str) -> Any | None: ...
    @abstractmethod
    async def find_by_index(
        self, ctx: Any, index_id: uuid.UUID,
    ) -> list[Any]: ...
    @abstractmethod
    async def update(self, ctx: Any, d: Any) -> Any: ...


class LIRunRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def update(self, ctx: Any, r: Any) -> Any: ...


class EmbeddingPort(Protocol):
    """TH: port ไปยัง embeddings module | EN: embeddings port"""
    async def embed(
        self, *, model: str, texts: list[str], normalize: bool = True,
    ) -> list[Any]: ...


class VectorStorePort(Protocol):
    """TH: port ไปยัง vector_db module | EN: vector store port"""
    async def upsert(
        self, *, collection_id: uuid.UUID, items: list[dict[str, Any]],
    ) -> int: ...

    async def query(
        self, *, collection_id: uuid.UUID, vector: list[float],
        top_k: int,
    ) -> list[Any]: ...


class LLMPort(Protocol):
    """TH: port ไปยัง llm module | EN: LLM port"""
    async def chat(
        self, *, tenant_id: uuid.UUID, model: str,
        messages: list[dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Any: ...


class NodeParserPort(Protocol):
    """TH: port ของ node parser | EN: node parser port"""
    def split(self, text: str) -> list[str]: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...
