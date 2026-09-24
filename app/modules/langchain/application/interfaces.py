"""langchain application ports"""
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


class LCChainRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, c: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all_active(self, ctx: Any) -> list[Any]: ...


class LCAgentRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, a: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
    @abstractmethod
    async def find_all_active(self, ctx: Any) -> list[Any]: ...


class LCMemoryRepository(ABC):
    @abstractmethod
    async def save(self, ctx: Any, m: Any) -> Any: ...
    @abstractmethod
    async def find_by_conversation(
        self, ctx: Any, conversation_id: uuid.UUID,
    ) -> Any | None: ...


class LCRunRepository(ABC):
    @abstractmethod
    async def create(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
    @abstractmethod
    async def update(self, ctx: Any, r: Any) -> Any: ...
    @abstractmethod
    async def list_by_user(self, ctx: Any, user_id: uuid.UUID,
                           limit: int) -> list[Any]: ...


class LCTraceRepository(ABC):
    @abstractmethod
    async def create_many(self, ctx: Any, traces: list[Any]) -> int: ...
    @abstractmethod
    async def find_by_run(self, ctx: Any, run_id: uuid.UUID) -> list[Any]: ...


class LLMPort(Protocol):
    """TH: port ไปยัง llm module | EN: LLM port"""
    async def chat(
        self, *, tenant_id: uuid.UUID, model: str,
        messages: list[dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Any: ...

    def stream(
        self, *, tenant_id: uuid.UUID, model: str,
        messages: list[dict[str, Any]],
        system_prompt: Optional[str] = None,
    ) -> Any: ...


class ToolInvokerPort(Protocol):
    """TH: port ไปยัง tool_calling module | EN: Tool invoker port"""
    async def invoke(
        self, *, tenant_id: uuid.UUID,
        tool_name: str, args: dict[str, Any],
        role: str = "user",
    ) -> Any: ...


class ChainRunnerPort(Protocol):
    """TH: port ของ chain runner | EN: Chain runner port"""
    async def run(
        self, *, chain_type: str, config: dict[str, Any],
        inputs: dict[str, Any], ctx: Any,
    ) -> dict[str, Any]: ...


class AgentRunnerPort(Protocol):
    """TH: port ของ agent runner | EN: Agent runner port"""
    async def run(
        self, *, agent_type: str, tools: list[str], model: str,
        max_iterations: int, question: str,
        system_prompt: str, ctx: Any,
    ) -> dict[str, Any]: ...


class MemoryStorePort(Protocol):
    """TH: port ของ memory store | EN: Memory store port"""
    async def load(
        self, *, conversation_id: uuid.UUID, memory_type: str,
    ) -> list[dict[str, Any]]: ...
    async def save(
        self, *, conversation_id: uuid.UUID, memory_type: str,
        messages: list[dict[str, Any]],
    ) -> None: ...


class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: object) -> None: ...
