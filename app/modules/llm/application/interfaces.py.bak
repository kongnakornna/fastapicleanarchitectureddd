"""llm application ports — อินเทอร์เฟซ"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, AsyncIterator, Protocol

from app.modules.llm.domain.value_objects import ChatOptions


class RequestContext(Protocol):
    """TH: request context | EN: request context"""

    @property
    def tenant_id(self) -> uuid.UUID: ...

    @property
    def user_id(self) -> uuid.UUID | None: ...


class ProviderRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, provider: Any) -> Any: ...

    @abstractmethod
    async def find_by_id(self, ctx: Any, provider_id: uuid.UUID) -> Any | None: ...

    @abstractmethod
    async def find_all_active(self, ctx: Any) -> list[Any]: ...

    @abstractmethod
    async def find_by_type(self, ctx: Any, provider_type: str) -> list[Any]: ...


class ModelRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, model: Any) -> Any: ...

    @abstractmethod
    async def find_by_id(self, ctx: Any, model_id: uuid.UUID) -> Any | None: ...

    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...

    @abstractmethod
    async def find_all_active(self, ctx: Any) -> list[Any]: ...


class ConversationRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, conv: Any) -> Any: ...

    @abstractmethod
    async def find_by_id(self, ctx: Any, conv_id: uuid.UUID) -> Any | None: ...

    @abstractmethod
    async def find_by_user(
        self, ctx: Any, user_id: uuid.UUID, limit: int,
    ) -> list[Any]: ...

    @abstractmethod
    async def update(self, ctx: Any, conv: Any) -> Any: ...


class MessageRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, msg: Any) -> Any: ...

    @abstractmethod
    async def find_by_conversation(
        self, ctx: Any, conv_id: uuid.UUID, limit: int,
    ) -> list[Any]: ...


class UsageLogRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, log: Any) -> Any: ...

    @abstractmethod
    async def sum_by_tenant(
        self, ctx: Any, since: datetime,
    ) -> dict[str, Any]: ...

    @abstractmethod
    async def sum_by_user(
        self, ctx: Any, user_id: uuid.UUID, since: datetime,
    ) -> dict[str, Any]: ...


class LLMClient(Protocol):
    """TH: LLM API client | EN: LLM API client port"""

    async def chat_completion(
        self, messages: list[dict[str, Any]],
        model: str, options: ChatOptions,
    ) -> dict[str, Any]: ...

    def stream_chat_completion(
        self, messages: list[dict[str, Any]],
        model: str, options: ChatOptions,
    ) -> AsyncIterator[dict[str, Any]]: ...


class ProviderRegistry(Protocol):
    def get_client(self, provider: Any) -> LLMClient: ...

    def select_provider(
        self, model_name: str, providers: list[Any],
    ) -> Any: ...


class RateLimiter(ABC):
    @abstractmethod
    async def check(
        self, tenant_id: uuid.UUID,
        user_id: uuid.UUID, cost: int,
    ) -> bool: ...

    @abstractmethod
    async def increment(
        self, tenant_id: uuid.UUID,
        user_id: uuid.UUID, cost: int,
    ) -> None: ...


class LLMCache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any | None: ...

    @abstractmethod
    async def set(
        self, key: str, value: Any, ttl: int = 3600,
    ) -> bool: ...

    @abstractmethod
    async def invalidate(self, key: str) -> bool: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...


class IdempotencyStore(ABC):
    @abstractmethod
    async def check_or_lock(
        self, key: str, scope: str, payload: dict[str, Any],
    ) -> dict[str, Any] | None: ...

    @abstractmethod
    async def complete(
        self, key: str, scope: str,
        status: int, body: dict[str, Any],
    ) -> None: ...
