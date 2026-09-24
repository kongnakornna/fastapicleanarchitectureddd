"""embeddings application ports"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, runtime_checkable

from app.modules.embeddings.domain.value_objects import (
    EmbeddingRequest, EmbeddingResult,
)


@runtime_checkable
class RequestContext(Protocol):
    @property
    def tenant_id(self) -> uuid.UUID: ...
    @property
    def user_id(self) -> Optional[uuid.UUID]: ...


class EmbProviderRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, p: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_all_active(self, ctx: Any) -> list[Any]: ...


class EmbModelRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, m: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all_active(self, ctx: Any) -> list[Any]: ...


class EmbVectorRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, v: Any) -> Any: ...
    @abstractmethod
    async def find_by_hash(
        self, ctx: Any, model_id: uuid.UUID, h: str,
    ) -> Any | None: ...


class EmbBatchRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, b: Any) -> Any: ...
    @abstractmethod
    async def update(self, ctx: Any, b: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...


class EmbeddingClient(Protocol):
    """TH: port ของ API embedding | EN: embedding API port"""
    async def embed(
        self, texts: list[str], model: str,
        *, normalize: bool = True,
        dimensions: Optional[int] = None,
    ) -> list[list[float]]: ...


class EmbeddingRegistry(Protocol):
    def get_client(self, provider: Any) -> EmbeddingClient: ...


class EmbeddingCache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[list[float]]: ...
    @abstractmethod
    async def set(
        self, key: str, value: list[float], ttl: int = 86400,
    ) -> bool: ...
    @abstractmethod
    async def invalidate(self, key: str) -> bool: ...


class RateLimiter(ABC):
    @abstractmethod
    async def check(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
    ) -> bool: ...
    @abstractmethod
    async def increment(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
    ) -> None: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...
