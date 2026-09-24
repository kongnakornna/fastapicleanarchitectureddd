"""structured_outputs application ports"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Protocol, runtime_checkable

from app.modules.structured_outputs.domain.value_objects import (
    SOResult, SchemaSpec,
)


@runtime_checkable
class RequestContext(Protocol):
    @property
    def tenant_id(self) -> uuid.UUID: ...
    @property
    def user_id(self) -> Optional[uuid.UUID]: ...


class SOSchemaRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, s: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all(self, ctx: Any) -> list[Any]: ...


class SORequestRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...


class SOOutputRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, o: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def update(self, ctx: Any, o: Any) -> Any: ...


class SOValidationRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, v: Any) -> Any: ...
    @abstractmethod
    async def find_by_output(self, ctx: Any, output_id: uuid.UUID) -> list[Any]: ...


class SORepairRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def find_by_output(self, ctx: Any, output_id: uuid.UUID) -> list[Any]: ...


class LLMPort(Protocol):
    """TH: port ไปยัง llm module | EN: LLM port"""
    async def chat(
        self, *, tenant_id: uuid.UUID, model: str,
        messages: list[dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Any: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...
