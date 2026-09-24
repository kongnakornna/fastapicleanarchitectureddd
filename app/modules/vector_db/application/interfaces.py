"""vector_db application ports"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, runtime_checkable

from app.modules.vector_db.domain.value_objects import (
    SearchHit, VectorQuery,
)


@runtime_checkable
class RequestContext(Protocol):
    @property
    def tenant_id(self) -> uuid.UUID: ...
    @property
    def user_id(self) -> Optional[uuid.UUID]: ...


class VDBCollectionRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, c: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all(self, ctx: Any) -> list[Any]: ...
    @abstractmethod
    async def delete(self, ctx: Any, id: uuid.UUID) -> bool: ...


class VDBVectorRepository(ABC):
    @abstractmethod
    async def upsert_many(self, ctx: Any, vectors: list[Any]) -> int: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def query_candidates(
        self, ctx: Any, collection_id: uuid.UUID, limit: int,
    ) -> list[Any]: ...
    @abstractmethod
    async def delete(self, ctx: Any, id: uuid.UUID) -> bool: ...
    @abstractmethod
    async def delete_by_collection(
        self, ctx: Any, collection_id: uuid.UUID,
    ) -> int: ...
    @abstractmethod
    async def count(self, ctx: Any, collection_id: uuid.UUID) -> int: ...


class VDBIndexRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, i: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_collection(
        self, ctx: Any, collection_id: uuid.UUID,
    ) -> list[Any]: ...


class VDBNamespaceRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, n: Any) -> Any: ...
    @abstractmethod
    async def find_by_name(
        self, ctx: Any, collection_id: uuid.UUID, name: str,
    ) -> Any | None: ...


class VDBStatsRepository(ABC):
    @abstractmethod
    async def upsert(self, ctx: Any, s: Any) -> Any: ...
    @abstractmethod
    async def find_by_collection(
        self, ctx: Any, collection_id: uuid.UUID,
    ) -> Any | None: ...


class BackendAdapter(Protocol):
    """TH: port ของ vector backend | EN: backend port"""
    async def upsert(self, collection: Any, vectors: list[Any]) -> int: ...
    async def query(self, collection: Any, query: VectorQuery) -> list[SearchHit]: ...
    async def delete(self, collection: Any, vector_ids: list[uuid.UUID]) -> int: ...
    async def build_index(self, collection: Any, index: Any) -> int: ...


class BackendRegistry(Protocol):
    def get_adapter(self, backend: str) -> BackendAdapter: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...
