"""tool_calling application ports"""
from __future__ import annotations
import uuid
from abc import ABC, abstractmethod
from typing import Any, Protocol

from app.modules.tool_calling.domain.value_objects import InvocationResult


class RequestContext(Protocol):
    @property
    def tenant_id(self) -> uuid.UUID: ...
    @property
    def user_id(self) -> uuid.UUID | None: ...


class ToolRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, t: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all(self, ctx: Any, limit: int, offset: int) -> list[Any]: ...
    @abstractmethod
    async def delete(self, ctx: Any, id: uuid.UUID) -> bool: ...


class RegistrationRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def find_by_tool(self, ctx: Any, tool_id: uuid.UUID) -> Any | None: ...


class InvocationRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, i: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def list(
        self, ctx: Any, limit: int, offset: int,
    ) -> list[Any]: ...


class PermissionRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, p: Any) -> Any: ...
    @abstractmethod
    async def check(
        self, ctx: Any, tool_id: uuid.UUID, role: str,
    ) -> Any | None: ...


class ToolClient(Protocol):
    kind: str

    async def invoke(
        self, *, spec: Any, args: dict[str, Any],
        secrets: dict[str, str], timeout: int,
    ) -> Any: ...


class ToolClientRegistry(Protocol):
    def get(self, kind: str) -> ToolClient: ...


class RateLimiter(ABC):
    @abstractmethod
    async def check_and_incr(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID,
        tool_id: uuid.UUID, limit_per_min: int,
    ) -> bool: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...
