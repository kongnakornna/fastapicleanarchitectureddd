#!/usr/bin/env python3
"""
create_module_langchain.py — LangChain Wrapper Module Generator v1.0.0

สร้าง module langchain ตาม Clean Architecture + DDD + Event-Driven
Module: langchain · Prefix: lc_ · Schema: public
Layer: 5-Intel · Depends: llm, tool_calling

Actions (9):
  1. create      — สร้าง module structure (4 layers)
  2. sql         — สร้าง SQL migrations V001/V002/V003
  3. alembic     — สร้าง Alembic migration
  4. swagger     — สร้าง OpenAPI docs
  5. postman     — สร้าง Postman collection
  6. update      — อัปเดต app/app.py
  7. update-env  — อัปเดต migrations/env.py
  8. verify      — ตรวจสอบ setup
  9. all         — ทำทุกอย่าง
"""
from __future__ import annotations

import argparse
import io
import json as _json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

# ═══════════════════════════════════════════════════════════════
#  UTF-8 FIX (Windows)
# ═══════════════════════════════════════════════════════════════
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VERSION = "1.0.0"
SCHEMA = "public"

# ═══════════════════════════════════════════════════════════════
#  MODULE CONFIG
# ═══════════════════════════════════════════════════════════════
MODULE = {
    "name": "langchain",
    "title": "LangChain Wrapper",
    "layer": "5-Intel",
    "prefix": "lc",
    "tag": "LangChain",
    "tag_desc": "LangChain Wrapper — LCEL chains · Agents · Memory · Tracing",
    "depends": ["llm", "tool_calling"],
    "tables": (
        "lc_chains",
        "lc_agents",
        "lc_memories",
        "lc_runs",
        "lc_traces",
    ),
}

ACTIONS = {
    "create", "sql", "alembic", "swagger", "postman",
    "update", "update-env", "verify", "all", "help",
}


# ═══════════════════════════════════════════════════════════════
#  LOGGER
# ═══════════════════════════════════════════════════════════════
class C:
    CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; GRAY = "\033[90m"; BOLD = "\033[1m"; RESET = "\033[0m"


def info(msg: str) -> None: print(f"{C.CYAN}{msg}{C.RESET}")
def ok(msg: str) -> None: print(f"  {C.GREEN}[OK]{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"  {C.YELLOW}[!!]{C.RESET} {msg}")
def err(msg: str) -> None: print(f"  {C.RED}[XX]{C.RESET} {msg}")
def skip(msg: str) -> None: print(f"  {C.GRAY}[--]{C.RESET} {msg}")


# ═══════════════════════════════════════════════════════════════
#  FILE WRITER
# ═══════════════════════════════════════════════════════════════
class FileWriter:
    def __init__(self, project_root: Path, force: bool = False):
        self.root = project_root
        self.force = force
        self.written: list[Path] = []
        self.skipped: list[Path] = []

    def write(self, rel_path: str, content: str) -> None:
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not self.force:
            skip(f"skip (exists): {rel_path}")
            self.skipped.append(path)
            return

        if path.exists() and self.force:
            bak = path.with_suffix(path.suffix + ".bak")
            bak.write_bytes(path.read_bytes())

        if rel_path.endswith(".py"):
            try:
                compile(content, rel_path, "exec")
            except SyntaxError as exc:
                err(f"SYNTAX ERROR in {rel_path}: {exc}")
                raise RuntimeError(f"Refuse to write invalid Python: {rel_path}") from exc

        path.write_text(content, encoding="utf-8", newline="\n")
        ok(rel_path)
        self.written.append(path)


# ═══════════════════════════════════════════════════════════════
#  GENERATOR
# ═══════════════════════════════════════════════════════════════
class LangChainGenerator:
    def __init__(self, project_root: Path, force: bool = False):
        self.cfg = MODULE
        self.module = MODULE["name"]
        self.prefix = MODULE["prefix"]
        self.layer = MODULE["layer"]
        self.tag = MODULE["tag"]
        self.tables = MODULE["tables"]
        self.root = project_root
        self.writer = FileWriter(project_root, force=force)

        self.mod_root = f"app/modules/{self.module}"
        self.sql_dir = "db/migrations"
        self.env_py = "migrations/env.py"
        self.app_py = "app/app.py"

    # ═══════════════════════════════════════════════════════════
    #  1. CREATE MODULE
    # ═══════════════════════════════════════════════════════════
    def create_module(self) -> None:
        info(f"[CREATE] {self.module} — {self.cfg['title']}")
        self._create_domain()
        self._create_application()
        self._create_infrastructure()
        self._create_presentation()
        self._create_root_init()

    # ─── DOMAIN LAYER ─────────────────────────────────────────
    def _create_domain(self) -> None:
        base = f"{self.mod_root}/domain"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} domain layer"""
            from .enums import *      # noqa: F401,F403
            from .events import *     # noqa: F401,F403
            from .exceptions import * # noqa: F401,F403
        '''))

        self.writer.write(f"{base}/enums.py", self._domain_enums())
        self.writer.write(f"{base}/exceptions.py", self._domain_exceptions())
        self.writer.write(f"{base}/events.py", self._domain_events())

        self.writer.write(f"{base}/value_objects/__init__.py", dedent('''\
            """langchain value objects"""
            from .chain_spec import ChainSpec
            from .agent_spec import AgentSpec
            from .memory_snapshot import MemorySnapshot
            from .run_context import RunContext

            __all__ = ["ChainSpec", "AgentSpec", "MemorySnapshot", "RunContext"]
        '''))

        self.writer.write(f"{base}/value_objects/chain_spec.py", dedent('''\
            """ChainSpec VO"""
            from __future__ import annotations
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.langchain.domain.enums import ChainType


            class ChainSpec(BaseModel):
                """TH: ข้อกำหนด chain | EN: Chain specification"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                name: str = Field(min_length=1, max_length=100)
                chain_type: ChainType = ChainType.LCEL
                config: dict[str, Any] = Field(default_factory=dict)
                description: str = ""
                version: str = "1.0.0"
        '''))

        self.writer.write(f"{base}/value_objects/agent_spec.py", dedent('''\
            """AgentSpec VO"""
            from __future__ import annotations
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.langchain.domain.enums import AgentType


            class AgentSpec(BaseModel):
                """TH: ข้อกำหนด agent | EN: Agent specification"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                name: str = Field(min_length=1, max_length=100)
                agent_type: AgentType = AgentType.REACT
                tools: list[str] = Field(default_factory=list)
                model: str = Field(default="gpt-4o-mini", max_length=100)
                max_iterations: int = Field(default=10, ge=1, le=50)
                system_prompt: str = ""
                config: dict = Field(default_factory=dict)
        '''))

        self.writer.write(f"{base}/value_objects/memory_snapshot.py", dedent('''\
            """MemorySnapshot VO"""
            from __future__ import annotations
            from typing import Any
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.langchain.domain.enums import MemoryType


            class MemorySnapshot(BaseModel):
                """TH: snapshot ของ memory | EN: Memory snapshot"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                memory_type: MemoryType = MemoryType.BUFFER
                payload: list[dict[str, Any]] = Field(default_factory=list)
                size_bytes: int = Field(default=0, ge=0)
        '''))

        self.writer.write(f"{base}/value_objects/run_context.py", dedent('''\
            """RunContext VO"""
            from __future__ import annotations
            import uuid
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field


            class RunContext(BaseModel):
                """TH: context ของ run | EN: Run context"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                run_id: uuid.UUID
                kind: str = "chain"
                target_id: uuid.UUID
                inputs: dict[str, Any] = Field(default_factory=dict)
                conversation_id: Optional[uuid.UUID] = None
        '''))

        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """langchain entities — aliases to ORM"""
            from .lc_chain import LCChain
            from .lc_agent import LCAgent
            from .lc_memory import LCMemory
            from .lc_run import LCRun
            from .lc_trace import LCTrace

            __all__ = ["LCChain", "LCAgent", "LCMemory", "LCRun", "LCTrace"]
        '''))

        for name, cls, model in (
            ("lc_chain", "LCChain", "LCChainModel"),
            ("lc_agent", "LCAgent", "LCAgentModel"),
            ("lc_memory", "LCMemory", "LCMemoryModel"),
            ("lc_run", "LCRun", "LCRunModel"),
            ("lc_trace", "LCTrace", "LCTraceModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias to ORM"""
                from __future__ import annotations
                from app.modules.{self.module}.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """langchain helpers"""
            from .memory import (
                BufferMemory, WindowMemory, SummaryBufferMemory,
                approx_token_count,
            )
            from .tracer import Tracer

            __all__ = [
                "BufferMemory", "WindowMemory", "SummaryBufferMemory",
                "approx_token_count", "Tracer",
            ]
        '''))

        self.writer.write(f"{base}/helpers/memory.py", dedent('''\
            """memory helpers — Buffer, Window, SummaryBuffer"""
            from __future__ import annotations
            import json
            from typing import Any


            def approx_token_count(text: str) -> int:
                if not text:
                    return 0
                return max(1, len(text) // 4)


            class BufferMemory:
                """TH: เก็บ message ทั้งหมด | EN: full buffer memory"""

                def __init__(self, max_tokens: int = 4096) -> None:
                    self._max = max_tokens
                    self._messages: list[dict[str, Any]] = []

                def add(self, role: str, content: str) -> None:
                    self._messages.append({"role": role, "content": content})
                    self._trim()

                def messages(self) -> list[dict[str, Any]]:
                    return list(self._messages)

                def _trim(self) -> None:
                    total = sum(approx_token_count(m.get("content", ""))
                                for m in self._messages)
                    while total > self._max and len(self._messages) > 1:
                        removed = self._messages.pop(0)
                        total -= approx_token_count(removed.get("content", ""))

                def snapshot(self) -> dict[str, Any]:
                    payload = self.messages()
                    return {
                        "memory_type": "buffer",
                        "payload": payload,
                        "size_bytes": len(json.dumps(payload, default=str).encode("utf-8")),
                    }


            class WindowMemory(BufferMemory):
                """TH: sliding window N messages | EN: window memory"""

                def __init__(self, window_size: int = 10, max_tokens: int = 4096) -> None:
                    super().__init__(max_tokens=max_tokens)
                    self._window = window_size

                def _trim(self) -> None:
                    super()._trim()
                    if len(self._messages) > self._window:
                        self._messages = self._messages[-self._window:]

                def snapshot(self) -> dict[str, Any]:
                    s = super().snapshot()
                    s["memory_type"] = "window"
                    return s


            class SummaryBufferMemory(BufferMemory):
                """TH: buffer + summary placeholder | EN: summary-buffer memory"""

                def __init__(self, max_tokens: int = 4096, summary_threshold: int = 2048) -> None:
                    super().__init__(max_tokens=max_tokens)
                    self._threshold = summary_threshold
                    self._summary = ""

                def set_summary(self, text: str) -> None:
                    self._summary = text or ""

                def snapshot(self) -> dict[str, Any]:
                    s = super().snapshot()
                    s["memory_type"] = "summary_buffer"
                    s["payload"] = [{"role": "system", "content": self._summary}] + s["payload"]
                    return s
        '''))

        self.writer.write(f"{base}/helpers/tracer.py", dedent('''\
            """tracer — step-by-step run recorder"""
            from __future__ import annotations
            import time
            from typing import Any


            class Tracer:
                """TH: บันทึก trace step | EN: trace recorder"""

                def __init__(self) -> None:
                    self._steps: list[dict[str, Any]] = []
                    self._t0 = time.monotonic()
                    self._step_no = 0

                def record(self, kind: str, payload: dict[str, Any]) -> None:
                    self._step_no += 1
                    self._steps.append({
                        "step": self._step_no,
                        "kind": kind,
                        "payload": payload,
                        "latency_ms": int((time.monotonic() - self._t0) * 1000),
                    })

                def steps(self) -> list[dict[str, Any]]:
                    return list(self._steps)

                def total_ms(self) -> int:
                    return int((time.monotonic() - self._t0) * 1000)
        '''))

    def _domain_enums(self) -> str:
        return dedent('''\
            """langchain enums"""
            from __future__ import annotations
            from enum import Enum


            class ChainType(str, Enum):
                """TH: ประเภท chain | EN: Chain type"""
                LCEL = "lcel"
                SEQUENTIAL = "sequential"
                ROUTER = "router"
                MAP_REDUCE = "map_reduce"
                REFINE = "refine"
                STUFF = "stuff"

                def __str__(self) -> str:
                    return str(self.value)


            class AgentType(str, Enum):
                """TH: ประเภท agent | EN: Agent type"""
                REACT = "react"
                OPENAI_TOOLS = "openai_tools"
                PLAN_EXECUTE = "plan_execute"
                SELF_ASK = "self_ask"
                REFLEXION = "reflexion"

                def __str__(self) -> str:
                    return str(self.value)


            class MemoryType(str, Enum):
                """TH: ประเภท memory | EN: Memory type"""
                BUFFER = "buffer"
                WINDOW = "window"
                SUMMARY = "summary"
                SUMMARY_BUFFER = "summary_buffer"
                VECTOR = "vector"
                KG = "kg"

                def __str__(self) -> str:
                    return str(self.value)


            class RunStatus(str, Enum):
                """TH: สถานะ run | EN: Run status"""
                QUEUED = "QUEUED"
                RUNNING = "RUNNING"
                DONE = "DONE"
                FAILED = "FAILED"
                CANCELLED = "CANCELLED"

                def __str__(self) -> str:
                    return str(self.value)


            class TraceKind(str, Enum):
                """TH: ประเภท trace step | EN: Trace step kind"""
                LLM_CALL = "llm_call"
                TOOL_CALL = "tool_call"
                MEMORY_READ = "memory_read"
                MEMORY_WRITE = "memory_write"
                ROUTER_BRANCH = "router_branch"
                RETRIEVAL = "retrieval"
                OTHER = "other"

                def __str__(self) -> str:
                    return str(self.value)
        ''')

    def _domain_exceptions(self) -> str:
        return dedent('''\
            """langchain domain exceptions"""
            from __future__ import annotations


            class LCError(Exception):
                """TH: base | EN: base"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class ChainNotFoundError(LCError):
                code = "NOT_FOUND"


            class AgentNotFoundError(LCError):
                code = "NOT_FOUND"


            class MemoryNotFoundError(LCError):
                code = "NOT_FOUND"


            class RunNotFoundError(LCError):
                code = "NOT_FOUND"


            class ChainConflictError(LCError):
                code = "CONFLICT"


            class AgentConflictError(LCError):
                code = "CONFLICT"


            class InvalidChainError(LCError):
                code = "VALIDATION_ERROR"


            class ExecutionError(LCError):
                code = "PROVIDER_ERROR"


            class MaxIterationsExceededError(LCError):
                code = "LIMIT_EXCEEDED"


            class DependencyError(LCError):
                code = "PROVIDER_ERROR"
        ''')

    def _domain_events(self) -> str:
        return dedent('''\
            """langchain domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import datetime, timezone


            def _now():
                return datetime.now(timezone.utc)


            @dataclass(frozen=True)
            class ChainRegistered:
                chain_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                chain_type: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class AgentRegistered:
                agent_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                agent_type: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class ChainInvoked:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                chain_id: uuid.UUID
                latency_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class AgentStepExecuted:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                step: int
                kind: str
                latency_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class MemoryUpdated:
                memory_id: uuid.UUID
                tenant_id: uuid.UUID
                memory_type: str
                size_bytes: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class RunCompleted:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                kind: str
                status: str
                latency_ms: int
                tokens_used: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class RunFailed:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                error: str
                occurred_at: datetime = field(default_factory=_now)
        ''')

    # ─── APPLICATION LAYER ────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} application layer"""
        '''))

        self.writer.write(f"{base}/exceptions.py", self._app_exceptions())
        self.writer.write(f"{base}/interfaces.py", self._interfaces_content())
        self.writer.write(f"{base}/mappers.py", self._mappers_content())
        self.writer.write(f"{base}/utils.py", self._utils_content())
        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _app_exceptions(self) -> str:
        return dedent('''\
            """langchain application exceptions"""
            from __future__ import annotations


            class AppError(Exception):
                code: str = "APP_ERROR"
                http_status: int = 400

                def __init__(self, message: str = "", *, code: str | None = None,
                             http_status: int | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code
                    if http_status:
                        self.http_status = http_status


            class ValidationAppError(AppError):
                code = "VALIDATION_ERROR"
                http_status = 422


            class NotFoundAppError(AppError):
                code = "NOT_FOUND"
                http_status = 404


            class ConflictAppError(AppError):
                code = "CONFLICT"
                http_status = 409


            class ExecutionAppError(AppError):
                code = "PROVIDER_ERROR"
                http_status = 502


            class LimitExceededAppError(AppError):
                code = "LIMIT_EXCEEDED"
                http_status = 402
        ''')

    def _interfaces_content(self) -> str:
        return dedent('''\
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
        ''')

    def _mappers_content(self) -> str:
        return dedent('''\
            """langchain mappers — ORM → dict"""
            from __future__ import annotations
            from typing import Any


            def chain_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "chain_type": row.chain_type,
                    "version": row.version,
                    "is_active": bool(row.is_active),
                }


            def agent_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "agent_type": row.agent_type,
                    "model": row.model,
                    "max_iterations": int(row.max_iterations or 10),
                    "is_active": bool(row.is_active),
                }


            def memory_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "conversation_id": str(row.conversation_id),
                    "memory_type": row.memory_type,
                    "size_bytes": int(row.size_bytes or 0),
                }


            def run_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "kind": row.kind,
                    "target_id": str(row.target_id),
                    "status": row.status,
                    "latency_ms": int(row.latency_ms or 0),
                    "tokens_used": int(row.tokens_used or 0),
                    "cost_usd": str(row.cost_usd or "0"),
                }


            def trace_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "run_id": str(row.run_id),
                    "step": int(row.step or 0),
                    "kind": row.kind,
                    "latency_ms": int(row.latency_ms or 0),
                }
        ''')

    def _utils_content(self) -> str:
        return dedent('''\
            """langchain application utils"""
            from __future__ import annotations
            import json
            import time
            from typing import Any


            def json_dumps_safe(obj: Any) -> str:
                return json.dumps(obj, separators=(",", ":"), default=str)


            def json_loads_safe(raw: Any, default: Any = None) -> Any:
                if raw is None:
                    return default
                if isinstance(raw, (dict, list)):
                    return raw
                if isinstance(raw, str):
                    try:
                        return json.loads(raw)
                    except Exception:
                        return default
                return default


            def ms_now() -> int:
                return int(time.time() * 1000)
        ''')

    def _use_case_content(self) -> str:
        return dedent('''\
            """langchain use cases"""
            from __future__ import annotations
            import logging
            import uuid
            from decimal import Decimal
            from typing import Any, Optional

            from app.modules.langchain.application.exceptions import (
                ConflictAppError, ExecutionAppError, LimitExceededAppError,
                NotFoundAppError, ValidationAppError,
            )
            from app.modules.langchain.application.utils import (
                json_dumps_safe, json_loads_safe, ms_now,
            )
            from app.modules.langchain.domain.enums import RunStatus, TraceKind
            from app.modules.langchain.domain.events import (
                AgentRegistered, AgentStepExecuted, ChainInvoked,
                ChainRegistered, MemoryUpdated, RunCompleted, RunFailed,
            )
            from app.modules.langchain.domain.helpers.tracer import Tracer
            from app.modules.langchain.domain.value_objects import (
                AgentSpec, ChainSpec,
            )

            logger = logging.getLogger(__name__)

            _DEFAULT_MAX_ITERATIONS = 10


            class LangChainUseCase:
                """TH: use case หลัก | EN: core use case"""

                def __init__(self, **deps: Any) -> None:
                    for key, value in deps.items():
                        setattr(self, f"_{key}", value)

                # ─── Chains ──────────────────────────────────
                async def register_chain(
                    self, ctx: Any, spec: ChainSpec,
                ) -> Any:
                    from app.modules.langchain.infrastructure.models import (
                        LCChainModel,
                    )
                    existing = await self._chains.find_by_name(ctx, spec.name)
                    if existing is not None:
                        raise ConflictAppError(f"chain exists: {spec.name}")

                    row = LCChainModel(
                        tenant_id=ctx.tenant_id, name=spec.name,
                        chain_type=str(spec.chain_type),
                        config_json=json_dumps_safe(spec.config or {}),
                        version=spec.version, is_active=True,
                    )
                    saved = await self._chains.save(ctx, row)
                    if self._bus:
                        try:
                            await self._bus.publish(ChainRegistered(
                                chain_id=saved.id, tenant_id=ctx.tenant_id,
                                name=saved.name, chain_type=str(spec.chain_type),
                            ))
                        except Exception:
                            pass
                    return saved

                async def list_chains(self, ctx: Any) -> list[Any]:
                    return await self._chains.find_all_active(ctx)

                async def get_chain(self, ctx: Any, chain_id: uuid.UUID) -> Any:
                    c = await self._chains.find_by_id(ctx, chain_id)
                    if c is None:
                        raise NotFoundAppError("chain not found")
                    return c

                async def invoke_chain(
                    self, ctx: Any, *, chain_id: uuid.UUID,
                    inputs: dict[str, Any],
                ) -> dict[str, Any]:
                    """TH: invoke chain | EN: invoke chain"""
                    from app.modules.langchain.infrastructure.models import (
                        LCRunModel, LCTraceModel,
                    )
                    chain = await self.get_chain(ctx, chain_id)

                    run = LCRunModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id,
                        kind="chain", target_id=chain.id,
                        input_json=json_dumps_safe(inputs),
                        status=str(RunStatus.RUNNING),
                    )
                    saved_run = await self._runs.create(ctx, run)

                    started = ms_now()
                    tracer = Tracer()
                    output: dict[str, Any] = {}
                    tokens = 0
                    status = RunStatus.DONE
                    error = ""

                    try:
                        if self._chain_runner is None:
                            # fallback: direct LLM call
                            if self._llm is None:
                                raise ExecutionAppError("LLM port not configured")
                            prompt = inputs.get("input") or inputs.get("query") or ""
                            tracer.record("llm_call", {"model": "gpt-4o-mini",
                                                        "chars": len(str(prompt))})
                            result = await self._llm.chat(
                                tenant_id=ctx.tenant_id,
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": str(prompt)}],
                            )
                            content = getattr(result, "content", "") or ""
                            usage = getattr(result, "usage", None)
                            tokens = int(getattr(usage, "total_tokens", 0) or 0) \\
                                if usage is not None else 0
                            output = {"output": content}
                        else:
                            output = await self._chain_runner.run(
                                chain_type=str(chain.chain_type),
                                config=json_loads_safe(chain.config_json, {}),
                                inputs=inputs, ctx=ctx,
                            )
                    except Exception as exc:
                        logger.exception("chain invoke failed: %s", exc)
                        status = RunStatus.FAILED
                        error = str(exc)[:500]

                    latency = ms_now() - started

                    saved_run.output_json = json_dumps_safe(output)
                    saved_run.status = str(status)
                    saved_run.latency_ms = latency
                    saved_run.tokens_used = tokens
                    saved_run.cost_usd = Decimal("0")
                    saved_run.error_message = error
                    await self._runs.update(ctx, saved_run)

                    # persist traces
                    if tracer.steps():
                        try:
                            trace_rows = [
                                LCTraceModel(
                                    tenant_id=ctx.tenant_id, run_id=saved_run.id,
                                    step=int(s["step"]), kind=s["kind"],
                                    payload_json=json_dumps_safe(s.get("payload", {})),
                                    latency_ms=int(s.get("latency_ms", 0)),
                                )
                                for s in tracer.steps()
                            ]
                            await self._traces.create_many(ctx, trace_rows)
                        except Exception as exc:
                            logger.debug("persist traces failed: %s", exc)

                    if self._bus:
                        try:
                            await self._bus.publish(ChainInvoked(
                                run_id=saved_run.id, tenant_id=ctx.tenant_id,
                                chain_id=chain.id, latency_ms=latency,
                            ))
                            await self._bus.publish(RunCompleted(
                                run_id=saved_run.id, tenant_id=ctx.tenant_id,
                                kind="chain", status=str(status),
                                latency_ms=latency, tokens_used=tokens,
                            ))
                        except Exception:
                            pass

                    if status == RunStatus.FAILED:
                        raise ExecutionAppError(error or "chain failed")

                    return {
                        "run_id": str(saved_run.id),
                        "output": output,
                        "status": str(status),
                        "latency_ms": latency,
                        "tokens_used": tokens,
                        "trace_steps": len(tracer.steps()),
                    }

                # ─── Agents ──────────────────────────────────
                async def register_agent(
                    self, ctx: Any, spec: AgentSpec,
                ) -> Any:
                    from app.modules.langchain.infrastructure.models import (
                        LCAgentModel,
                    )
                    existing = await self._agents.find_by_name(ctx, spec.name)
                    if existing is not None:
                        raise ConflictAppError(f"agent exists: {spec.name}")

                    row = LCAgentModel(
                        tenant_id=ctx.tenant_id, name=spec.name,
                        agent_type=str(spec.agent_type),
                        tools_json=json_dumps_safe(spec.tools),
                        model=spec.model,
                        max_iterations=spec.max_iterations,
                        config_json=json_dumps_safe({
                            "system_prompt": spec.system_prompt,
                            **(spec.config or {}),
                        }),
                        is_active=True,
                    )
                    saved = await self._agents.save(ctx, row)
                    if self._bus:
                        try:
                            await self._bus.publish(AgentRegistered(
                                agent_id=saved.id, tenant_id=ctx.tenant_id,
                                name=saved.name, agent_type=str(spec.agent_type),
                            ))
                        except Exception:
                            pass
                    return saved

                async def list_agents(self, ctx: Any) -> list[Any]:
                    return await self._agents.find_all_active(ctx)

                async def get_agent(self, ctx: Any, agent_id: uuid.UUID) -> Any:
                    a = await self._agents.find_by_id(ctx, agent_id)
                    if a is None:
                        raise NotFoundAppError("agent not found")
                    return a

                async def invoke_agent(
                    self, ctx: Any, *, agent_id: uuid.UUID,
                    question: str,
                ) -> dict[str, Any]:
                    """TH: invoke agent | EN: invoke agent"""
                    from app.modules.langchain.infrastructure.models import (
                        LCRunModel, LCTraceModel,
                    )
                    agent = await self.get_agent(ctx, agent_id)
                    config = json_loads_safe(agent.config_json, {})
                    system_prompt = config.get("system_prompt") or ""

                    run = LCRunModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id,
                        kind="agent", target_id=agent.id,
                        input_json=json_dumps_safe({"question": question}),
                        status=str(RunStatus.RUNNING),
                    )
                    saved_run = await self._runs.create(ctx, run)

                    started = ms_now()
                    tracer = Tracer()
                    output: dict[str, Any] = {}
                    tokens = 0
                    status = RunStatus.DONE
                    error = ""

                    try:
                        if self._agent_runner is not None:
                            tools = json_loads_safe(agent.tools_json, [])
                            output = await self._agent_runner.run(
                                agent_type=str(agent.agent_type),
                                tools=tools, model=agent.model,
                                max_iterations=int(agent.max_iterations or _DEFAULT_MAX_ITERATIONS),
                                question=question,
                                system_prompt=system_prompt, ctx=ctx,
                            )
                            tokens = int(output.get("tokens_used", 0) or 0)
                            tracer.record("other", {
                                "iterations": int(output.get("iterations", 0)),
                                "tool_calls": int(output.get("tool_calls", 0)),
                            })
                        elif self._tool_invoker is not None and self._llm is not None:
                            # simple ReAct-like loop using tool invoker
                            tools = json_loads_safe(agent.tools_json, [])
                            max_iter = int(agent.max_iterations or _DEFAULT_MAX_ITERATIONS)
                            messages = [{"role": "user", "content": question}]
                            for i in range(1, max_iter + 1):
                                result = await self._llm.chat(
                                    tenant_id=ctx.tenant_id,
                                    model=agent.model,
                                    messages=messages,
                                    system_prompt=system_prompt,
                                )
                                content = getattr(result, "content", "") or ""
                                tool_calls = getattr(result, "tool_calls", None) or []
                                tracer.record("llm_call", {"iteration": i})

                                if not tool_calls:
                                    output = {"answer": content, "iterations": i,
                                              "tool_calls": 0}
                                    break

                                for call in tool_calls:
                                    tool_name = call.get("name", "")
                                    args = json_loads_safe(
                                        call.get("arguments", "{}"), {},
                                    )
                                    tracer.record("tool_call", {
                                        "name": tool_name, "iteration": i,
                                    })
                                    try:
                                        await self._tool_invoker.invoke(
                                            tenant_id=ctx.tenant_id,
                                            tool_name=tool_name, args=args,
                                        )
                                    except Exception as exc:
                                        logger.debug("tool invoke failed: %s", exc)
                                messages.append({"role": "assistant", "content": content})
                                messages.append({"role": "user", "content":
                                                 "Continue based on tool results."})
                            else:
                                raise LimitExceededAppError(
                                    f"agent exceeded {max_iter} iterations"
                                )
                        else:
                            raise ExecutionAppError(
                                "no agent runner or LLM port configured"
                            )
                    except Exception as exc:
                        logger.exception("agent invoke failed: %s", exc)
                        status = RunStatus.FAILED
                        error = str(exc)[:500]

                    latency = ms_now() - started

                    saved_run.output_json = json_dumps_safe(output)
                    saved_run.status = str(status)
                    saved_run.latency_ms = latency
                    saved_run.tokens_used = tokens
                    saved_run.cost_usd = Decimal("0")
                    saved_run.error_message = error
                    await self._runs.update(ctx, saved_run)

                    if tracer.steps():
                        try:
                            trace_rows = [
                                LCTraceModel(
                                    tenant_id=ctx.tenant_id, run_id=saved_run.id,
                                    step=int(s["step"]), kind=s["kind"],
                                    payload_json=json_dumps_safe(s.get("payload", {})),
                                    latency_ms=int(s.get("latency_ms", 0)),
                                )
                                for s in tracer.steps()
                            ]
                            await self._traces.create_many(ctx, trace_rows)
                        except Exception as exc:
                            logger.debug("persist traces failed: %s", exc)

                    if self._bus:
                        try:
                            await self._bus.publish(RunCompleted(
                                run_id=saved_run.id, tenant_id=ctx.tenant_id,
                                kind="agent", status=str(status),
                                latency_ms=latency, tokens_used=tokens,
                            ))
                        except Exception:
                            pass

                    if status == RunStatus.FAILED:
                        raise ExecutionAppError(error or "agent failed")

                    return {
                        "run_id": str(saved_run.id),
                        "output": output,
                        "status": str(status),
                        "latency_ms": latency,
                        "tokens_used": tokens,
                        "trace_steps": len(tracer.steps()),
                    }

                # ─── Memory ──────────────────────────────────
                async def get_memory(
                    self, ctx: Any, conversation_id: uuid.UUID,
                ) -> Any:
                    m = await self._memories.find_by_conversation(ctx, conversation_id)
                    if m is None:
                        raise NotFoundAppError("memory not found")
                    return m

                async def update_memory(
                    self, ctx: Any, *, conversation_id: uuid.UUID,
                    memory_type: str, messages: list[dict[str, Any]],
                ) -> Any:
                    from app.modules.langchain.infrastructure.models import (
                        LCMemoryModel,
                    )
                    payload_json = json_dumps_safe(messages)
                    size_bytes = len(payload_json.encode("utf-8"))

                    existing = await self._memories.find_by_conversation(
                        ctx, conversation_id,
                    )
                    if existing is None:
                        row = LCMemoryModel(
                            tenant_id=ctx.tenant_id,
                            conversation_id=conversation_id,
                            memory_type=memory_type,
                            snapshot_json=payload_json,
                            size_bytes=size_bytes,
                        )
                        saved = await self._memories.save(ctx, row)
                    else:
                        existing.memory_type = memory_type
                        existing.snapshot_json = payload_json
                        existing.size_bytes = size_bytes
                        saved = await self._memories.save(ctx, existing)

                    if self._bus:
                        try:
                            await self._bus.publish(MemoryUpdated(
                                memory_id=saved.id, tenant_id=ctx.tenant_id,
                                memory_type=memory_type, size_bytes=size_bytes,
                            ))
                        except Exception:
                            pass
                    return saved

                # ─── Runs & traces ───────────────────────────
                async def get_run(self, ctx: Any, run_id: uuid.UUID) -> Any:
                    r = await self._runs.find_by_id(ctx, run_id)
                    if r is None:
                        raise NotFoundAppError("run not found")
                    return r

                async def get_run_trace(
                    self, ctx: Any, run_id: uuid.UUID,
                ) -> list[Any]:
                    await self.get_run(ctx, run_id)
                    return await self._traces.find_by_run(ctx, run_id)
        ''')

    # ─── INFRASTRUCTURE LAYER ─────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} infrastructure layer"""
        '''))

        self.writer.write(f"{base}/models.py", self._models_content())
        self.writer.write(f"{base}/repositories.py", self._repositories_content())
        self.writer.write(f"{base}/services.py", self._services_content())

    def _models_content(self) -> str:
        return dedent(f'''\
            """langchain SQLAlchemy models — schema=public, prefix=lc_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal
            from typing import Optional

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Index, Integer, Numeric,
                String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: base | EN: base"""


            class LCChainModel(Base):
                __tablename__ = "lc_chains"
                __table_args__ = (
                    CheckConstraint(
                        "chain_type IN ('lcel','sequential','router','map_reduce','refine','stuff')",
                        name="ck_lc_chain_type",
                    ),
                    UniqueConstraint("tenant_id", "name", name="uq_lc_chain_name"),
                    Index("ix_lc_chain_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                chain_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="lcel")
                config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                version: Mapped[str] = mapped_column(String(20), nullable=False, server_default="1.0.0")
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class LCAgentModel(Base):
                __tablename__ = "lc_agents"
                __table_args__ = (
                    CheckConstraint(
                        "agent_type IN ('react','openai_tools','plan_execute','self_ask','reflexion')",
                        name="ck_lc_agent_type",
                    ),
                    UniqueConstraint("tenant_id", "name", name="uq_lc_agent_name"),
                    Index("ix_lc_agent_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                agent_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="react")
                tools_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
                model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="gpt-4o-mini")
                max_iterations: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
                config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class LCMemoryModel(Base):
                __tablename__ = "lc_memories"
                __table_args__ = (
                    CheckConstraint(
                        "memory_type IN ('buffer','window','summary','summary_buffer','vector','kg')",
                        name="ck_lc_memory_type",
                    ),
                    Index("ix_lc_memory_conv", "conversation_id"),
                    Index("ix_lc_memory_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                memory_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="buffer")
                snapshot_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
                size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class LCRunModel(Base):
                __tablename__ = "lc_runs"
                __table_args__ = (
                    CheckConstraint(
                        "kind IN ('chain','agent')",
                        name="ck_lc_run_kind",
                    ),
                    CheckConstraint(
                        "status IN ('QUEUED','RUNNING','DONE','FAILED','CANCELLED')",
                        name="ck_lc_run_status",
                    ),
                    Index("ix_lc_run_tenant_time", "tenant_id", "created_at"),
                    Index("ix_lc_run_user_time", "user_id", "created_at"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                kind: Mapped[str] = mapped_column(String(20), nullable=False, server_default="chain")
                target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                input_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                output_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="QUEUED")
                latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                cost_usd: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                error_message: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class LCTraceModel(Base):
                __tablename__ = "lc_traces"
                __table_args__ = (
                    Index("ix_lc_trace_run_step", "run_id", "step"),
                    Index("ix_lc_trace_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                step: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                kind: Mapped[str] = mapped_column(String(30), nullable=False, server_default="other")
                payload_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            __all__ = [
                "Base", "LCChainModel", "LCAgentModel", "LCMemoryModel",
                "LCRunModel", "LCTraceModel",
            ]
        ''')

    def _repositories_content(self) -> str:
        return dedent('''\
            """langchain repositories"""
            from __future__ import annotations
            import logging
            import uuid

            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.langchain.application.exceptions import AppError
            from app.modules.langchain.infrastructure.models import (
                LCAgentModel, LCChainModel, LCMemoryModel, LCRunModel,
                LCTraceModel,
            )

            logger = logging.getLogger(__name__)


            class LCChainRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, c: LCChainModel) -> LCChainModel:
                    try:
                        self._session.add(c)
                        await self._session.flush()
                        return c
                    except SQLAlchemyError as exc:
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> LCChainModel | None:
                    r = await self._session.execute(
                        select(LCChainModel).where(LCChainModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def find_by_name(self, ctx: object, name: str) -> LCChainModel | None:
                    r = await self._session.execute(
                        select(LCChainModel).where(LCChainModel.name == name)
                    )
                    return r.scalar_one_or_none()

                async def find_all_active(self, ctx: object) -> list[LCChainModel]:
                    r = await self._session.execute(
                        select(LCChainModel)
                        .where(LCChainModel.is_active.is_(True))
                        .order_by(LCChainModel.name)
                    )
                    return list(r.scalars().all())


            class LCAgentRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, a: LCAgentModel) -> LCAgentModel:
                    self._session.add(a)
                    await self._session.flush()
                    return a

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> LCAgentModel | None:
                    r = await self._session.execute(
                        select(LCAgentModel).where(LCAgentModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def find_by_name(self, ctx: object, name: str) -> LCAgentModel | None:
                    r = await self._session.execute(
                        select(LCAgentModel).where(LCAgentModel.name == name)
                    )
                    return r.scalar_one_or_none()

                async def find_all_active(self, ctx: object) -> list[LCAgentModel]:
                    r = await self._session.execute(
                        select(LCAgentModel)
                        .where(LCAgentModel.is_active.is_(True))
                        .order_by(LCAgentModel.name)
                    )
                    return list(r.scalars().all())


            class LCMemoryRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, m: LCMemoryModel) -> LCMemoryModel:
                    self._session.add(m)
                    await self._session.flush()
                    return m

                async def find_by_conversation(
                    self, ctx: object, conversation_id: uuid.UUID,
                ) -> LCMemoryModel | None:
                    r = await self._session.execute(
                        select(LCMemoryModel).where(
                            LCMemoryModel.conversation_id == conversation_id
                        )
                    )
                    return r.scalar_one_or_none()


            class LCRunRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, r_: LCRunModel) -> LCRunModel:
                    self._session.add(r_)
                    await self._session.flush()
                    return r_

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> LCRunModel | None:
                    r = await self._session.execute(
                        select(LCRunModel).where(LCRunModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def update(self, ctx: object, r_: LCRunModel) -> LCRunModel:
                    await self._session.flush()
                    return r_

                async def list_by_user(
                    self, ctx: object, user_id: uuid.UUID, limit: int,
                ) -> list[LCRunModel]:
                    r = await self._session.execute(
                        select(LCRunModel)
                        .where(LCRunModel.user_id == user_id)
                        .order_by(LCRunModel.created_at.desc())
                        .limit(max(1, min(limit, 500)))
                    )
                    return list(r.scalars().all())


            class LCTraceRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create_many(self, ctx: object, traces: list) -> int:
                    for t in traces:
                        self._session.add(t)
                    await self._session.flush()
                    return len(traces)

                async def find_by_run(
                    self, ctx: object, run_id: uuid.UUID,
                ) -> list[LCTraceModel]:
                    r = await self._session.execute(
                        select(LCTraceModel)
                        .where(LCTraceModel.run_id == run_id)
                        .order_by(LCTraceModel.step)
                    )
                    return list(r.scalars().all())
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """langchain services — adapters + simple runners + bus"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any, Optional

            from app.modules.langchain.application.interfaces import (
                EventBus,
            )

            logger = logging.getLogger(__name__)


            class LLMPortAdapter:
                """TH: adapter ไปยัง llm module | EN: LLM port adapter"""

                def __init__(self, llm_use_case: Any) -> None:
                    self._uc = llm_use_case

                async def chat(
                    self, *, tenant_id: uuid.UUID, model: str,
                    messages: list[dict[str, Any]],
                    system_prompt: Optional[str] = None,
                ) -> Any:
                    try:
                        from app.shared.context import RequestContext as SharedCtx
                        ctx = SharedCtx(tenant_id=tenant_id)
                        return await self._uc.chat(
                            ctx, model_name=model, messages=messages,
                            system_prompt=system_prompt,
                        )
                    except Exception as exc:
                        logger.warning("llm adapter failed: %s", exc)
                        raise

                def stream(
                    self, *, tenant_id: uuid.UUID, model: str,
                    messages: list[dict[str, Any]],
                    system_prompt: Optional[str] = None,
                ) -> Any:
                    from app.shared.context import RequestContext as SharedCtx
                    ctx = SharedCtx(tenant_id=tenant_id)
                    return self._uc.chat_stream(
                        ctx, model_name=model, messages=messages,
                        system_prompt=system_prompt,
                    )


            class ToolInvokerAdapter:
                """TH: adapter ไปยัง tool_calling module
                | EN: tool invoker adapter"""

                def __init__(self, tool_use_case: Any) -> None:
                    self._uc = tool_use_case

                async def invoke(
                    self, *, tenant_id: uuid.UUID,
                    tool_name: str, args: dict[str, Any],
                    role: str = "user",
                ) -> Any:
                    from app.shared.context import RequestContext as SharedCtx
                    from app.modules.tool_calling.domain.value_objects import (
                        InvocationRequest,
                    )
                    ctx = SharedCtx(tenant_id=tenant_id)
                    return await self._uc.invoke(
                        ctx, InvocationRequest(tool_name=tool_name, args=args),
                        role=role,
                    )


            class LCELChainRunner:
                """TH: LCEL runner (simple prompt → llm → output)
                | EN: LCEL runner"""

                def __init__(self, llm: Any) -> None:
                    self._llm = llm

                async def run(
                    self, *, chain_type: str, config: dict[str, Any],
                    inputs: dict[str, Any], ctx: Any,
                ) -> dict[str, Any]:
                    model = config.get("model", "gpt-4o-mini")
                    prompt = inputs.get("input") or inputs.get("query") or ""
                    system_prompt = config.get("system_prompt")
                    messages = [{"role": "user", "content": str(prompt)}]
                    result = await self._llm.chat(
                        tenant_id=ctx.tenant_id, model=model,
                        messages=messages, system_prompt=system_prompt,
                    )
                    content = getattr(result, "content", "") or ""
                    usage = getattr(result, "usage", None)
                    tokens = int(getattr(usage, "total_tokens", 0) or 0) \\
                        if usage is not None else 0
                    return {"output": content, "tokens_used": tokens}


            class SimpleReActAgent:
                """TH: simple ReAct (placeholder) | EN: simple ReAct agent"""

                def __init__(self, llm: Any, tool_invoker: Any) -> None:
                    self._llm = llm
                    self._tool = tool_invoker

                async def run(
                    self, *, agent_type: str, tools: list[str], model: str,
                    max_iterations: int, question: str,
                    system_prompt: str, ctx: Any,
                ) -> dict[str, Any]:
                    messages = [{"role": "user", "content": question}]
                    tokens = 0
                    iterations = 0
                    tool_calls = 0

                    for i in range(1, max_iterations + 1):
                        iterations = i
                        result = await self._llm.chat(
                            tenant_id=ctx.tenant_id, model=model,
                            messages=messages, system_prompt=system_prompt,
                        )
                        content = getattr(result, "content", "") or ""
                        usage = getattr(result, "usage", None)
                        if usage is not None:
                            tokens += int(getattr(usage, "total_tokens", 0) or 0)
                        raw_calls = getattr(result, "tool_calls", None) or []
                        if not raw_calls:
                            return {
                                "answer": content, "iterations": i,
                                "tool_calls": tool_calls, "tokens_used": tokens,
                            }
                        for call in raw_calls:
                            tool_calls += 1
                            try:
                                await self._tool.invoke(
                                    tenant_id=ctx.tenant_id,
                                    tool_name=call.get("name", ""),
                                    args=call.get("arguments", {}) or {},
                                )
                            except Exception as exc:
                                logger.debug("tool failed: %s", exc)
                        messages.append({"role": "assistant", "content": content})
                        messages.append({"role": "user", "content":
                                         "Continue to final answer."})
                    return {
                        "answer": "max iterations reached",
                        "iterations": iterations, "tool_calls": tool_calls,
                        "tokens_used": tokens,
                    }


            class LoggingEventBus(EventBus):
                async def publish(self, event: object) -> None:
                    try:
                        logger.info("event %s", type(event).__name__)
                    except Exception:
                        pass
        ''')

    # ─── PRESENTATION LAYER ───────────────────────────────────
    def _create_presentation(self) -> None:
        base = f"{self.mod_root}/presentation"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} presentation layer"""
        '''))

        self.writer.write(f"{base}/schemas.py", self._schemas_content())
        self.writer.write(f"{base}/dependencies.py", self._dependencies_content())
        self.writer.write(f"{base}/router.py", self._router_content())
        self.writer.write(f"{base}/swagger.py", self._swagger_content())

    def _schemas_content(self) -> str:
        return dedent('''\
            """langchain Pydantic schemas"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.langchain.domain.enums import (
                AgentType, ChainType, MemoryType,
            )


            class ChainCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(min_length=1, max_length=100)
                chain_type: ChainType = ChainType.LCEL
                config: dict[str, Any] = Field(default_factory=dict)
                description: str = ""
                version: str = "1.0.0"


            class ChainOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                chain_type: str
                version: str
                is_active: bool


            class AgentCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(min_length=1, max_length=100)
                agent_type: AgentType = AgentType.REACT
                tools: list[str] = Field(default_factory=list)
                model: str = "gpt-4o-mini"
                max_iterations: int = Field(default=10, ge=1, le=50)
                system_prompt: str = ""
                config: dict[str, Any] = Field(default_factory=dict)


            class AgentOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                agent_type: str
                model: str
                max_iterations: int
                is_active: bool


            class InvokeRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                inputs: dict[str, Any] = Field(default_factory=dict)
                question: Optional[str] = None


            class InvokeResponse(BaseModel):
                run_id: uuid.UUID
                output: dict[str, Any] = Field(default_factory=dict)
                status: str
                latency_ms: int
                tokens_used: int = 0
                trace_steps: int = 0


            class RunOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                kind: str
                target_id: uuid.UUID
                status: str
                latency_ms: int
                tokens_used: int
                error_message: str
                created_at: datetime


            class TraceOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                run_id: uuid.UUID
                step: int
                kind: str
                latency_ms: int


            class MemoryUpdateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                conversation_id: uuid.UUID
                memory_type: MemoryType = MemoryType.BUFFER
                messages: list[dict[str, Any]] = Field(default_factory=list)


            class MemoryOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                conversation_id: uuid.UUID
                memory_type: str
                size_bytes: int
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """langchain DI container"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass
            from typing import Annotated, Optional

            from fastapi import Depends, Header, HTTPException, Request, status
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.langchain.application.use_case import (
                LangChainUseCase,
            )
            from app.modules.langchain.infrastructure.repositories import (
                LCAgentRepository, LCChainRepository, LCMemoryRepository,
                LCRunRepository, LCTraceRepository,
            )
            from app.modules.langchain.infrastructure.services import (
                LoggingEventBus,
            )


            @dataclass
            class Ctx:
                tenant_id: uuid.UUID
                user_id: Optional[uuid.UUID]


            async def get_db(request: Request) -> AsyncSession:
                session = getattr(request.app.state, "db_session", None)
                if session is None:
                    sm = getattr(request.app.state, "session_factory", None)
                    if sm is None:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={"code": "DB_ERROR", "message": "db session unavailable"},
                        )
                    session = sm()
                return session


            async def get_ctx(
                x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-Id"),
                x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
            ) -> Ctx:
                if not x_tenant_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail={"code": "AUTH_ERROR", "message": "X-Tenant-Id required"},
                    )
                try:
                    tenant_id = uuid.UUID(x_tenant_id)
                except ValueError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"code": "VALIDATION_ERROR", "message": "invalid tenant id"},
                    ) from exc
                user_id: Optional[uuid.UUID] = None
                if x_user_id:
                    try:
                        user_id = uuid.UUID(x_user_id)
                    except ValueError:
                        user_id = None
                return Ctx(tenant_id=tenant_id, user_id=user_id)


            async def get_use_case(
                request: Request,
                db: AsyncSession = Depends(get_db),
            ) -> LangChainUseCase:
                llm_port = getattr(request.app.state, "lc_llm_port", None)
                tool_invoker = getattr(request.app.state, "lc_tool_invoker", None)
                chain_runner = getattr(request.app.state, "lc_chain_runner", None)
                agent_runner = getattr(request.app.state, "lc_agent_runner", None)
                memory_store = getattr(request.app.state, "lc_memory_store", None)
                bus = getattr(request.app.state, "lc_event_bus", None) \\
                    or LoggingEventBus()

                return LangChainUseCase(
                    chains=LCChainRepository(db),
                    agents=LCAgentRepository(db),
                    memories=LCMemoryRepository(db),
                    runs=LCRunRepository(db),
                    traces=LCTraceRepository(db),
                    llm=llm_port,
                    tool_invoker=tool_invoker,
                    chain_runner=chain_runner,
                    agent_runner=agent_runner,
                    memory_store=memory_store,
                    bus=bus,
                )
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """langchain HTTP router"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException

            from app.modules.langchain.application.exceptions import AppError
            from app.modules.langchain.application.use_case import LangChainUseCase
            from app.modules.langchain.domain.exceptions import LCError
            from app.modules.langchain.domain.value_objects import (
                AgentSpec, ChainSpec,
            )
            from app.modules.langchain.presentation.dependencies import (
                Ctx, get_ctx, get_use_case,
            )
            from app.modules.langchain.presentation.schemas import (
                AgentCreateRequest, AgentOut, ChainCreateRequest, ChainOut,
                InvokeRequest, InvokeResponse, MemoryOut, MemoryUpdateRequest,
                RunOut, TraceOut,
            )

            logger = logging.getLogger(__name__)

            router = APIRouter(prefix="/lc", tags=["LangChain"])


            def _raise(exc: Exception) -> None:
                if isinstance(exc, LCError):
                    http = 400
                    code = getattr(exc, "code", "DOMAIN_ERROR")
                    if code == "NOT_FOUND":
                        http = 404
                    elif code == "VALIDATION_ERROR":
                        http = 422
                    elif code == "CONFLICT":
                        http = 409
                    elif code == "LIMIT_EXCEEDED":
                        http = 402
                    elif code == "PROVIDER_ERROR":
                        http = 502
                    raise HTTPException(
                        status_code=http,
                        detail={"code": code, "message": str(exc)},
                    )
                if isinstance(exc, AppError):
                    raise HTTPException(
                        status_code=getattr(exc, "http_status", 400),
                        detail={
                            "code": getattr(exc, "code", "APP_ERROR"),
                            "message": str(exc),
                        },
                    )
                logger.exception("unhandled error")
                raise HTTPException(
                    status_code=500,
                    detail={"code": "INTERNAL_ERROR", "message": "internal error"},
                )


            @router.get("/chains", response_model=list[ChainOut])
            async def list_chains(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LangChainUseCase, Depends(get_use_case)],
            ) -> list[ChainOut]:
                try:
                    items = await uc.list_chains(ctx)
                    return [ChainOut.model_validate(c.model_dump()) for c in items]
                except (LCError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/chains", response_model=ChainOut, status_code=201)
            async def create_chain(
                req: ChainCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LangChainUseCase, Depends(get_use_case)],
            ) -> ChainOut:
                try:
                    spec = ChainSpec(
                        name=req.name, chain_type=req.chain_type,
                        config=req.config, description=req.description,
                        version=req.version,
                    )
                    row = await uc.register_chain(ctx, spec)
                    return ChainOut.model_validate(row.model_dump())
                except (LCError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/chains/{chain_id}/invoke", response_model=InvokeResponse)
            async def invoke_chain(
                chain_id: uuid.UUID,
                req: InvokeRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LangChainUseCase, Depends(get_use_case)],
            ) -> InvokeResponse:
                try:
                    out = await uc.invoke_chain(ctx, chain_id=chain_id,
                                                inputs=req.inputs)
                    return InvokeResponse(**out)
                except (LCError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/agents", response_model=list[AgentOut])
            async def list_agents(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LangChainUseCase, Depends(get_use_case)],
            ) -> list[AgentOut]:
                try:
                    items = await uc.list_agents(ctx)
                    return [AgentOut.model_validate(a.model_dump()) for a in items]
                except (LCError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/agents", response_model=AgentOut, status_code=201)
            async def create_agent(
                req: AgentCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LangChainUseCase, Depends(get_use_case)],
            ) -> AgentOut:
                try:
                    spec = AgentSpec(
                        name=req.name, agent_type=req.agent_type,
                        tools=req.tools, model=req.model,
                        max_iterations=req.max_iterations,
                        system_prompt=req.system_prompt,
                        config=req.config,
                    )
                    row = await uc.register_agent(ctx, spec)
                    return AgentOut.model_validate(row.model_dump())
                except (LCError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/agents/{agent_id}/invoke", response_model=InvokeResponse)
            async def invoke_agent(
                agent_id: uuid.UUID,
                req: InvokeRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LangChainUseCase, Depends(get_use_case)],
            ) -> InvokeResponse:
                try:
                    question = req.question or str(req.inputs.get("input", ""))
                    out = await uc.invoke_agent(
                        ctx, agent_id=agent_id, question=question,
                    )
                    return InvokeResponse(**out)
                except (LCError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/runs/{run_id}", response_model=RunOut)
            async def get_run(
                run_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LangChainUseCase, Depends(get_use_case)],
            ) -> RunOut:
                try:
                    r = await uc.get_run(ctx, run_id)
                    return RunOut.model_validate(r.model_dump())
                except (LCError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/runs/{run_id}/trace", response_model=list[TraceOut])
            async def get_trace(
                run_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LangChainUseCase, Depends(get_use_case)],
            ) -> list[TraceOut]:
                try:
                    items = await uc.get_run_trace(ctx, run_id)
                    return [TraceOut.model_validate(t.model_dump()) for t in items]
                except (LCError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/memory", response_model=MemoryOut)
            async def update_memory(
                req: MemoryUpdateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LangChainUseCase, Depends(get_use_case)],
            ) -> MemoryOut:
                try:
                    m = await uc.update_memory(
                        ctx, conversation_id=req.conversation_id,
                        memory_type=str(req.memory_type),
                        messages=req.messages,
                    )
                    return MemoryOut.model_validate(m.model_dump())
                except (LCError, AppError) as exc:
                    _raise(exc)
                    raise
        ''')

    def _swagger_content(self) -> str:
        return dedent(f'''\
            """langchain OpenAPI docs"""
            from __future__ import annotations
            from typing import Any


            def register_langchain_openapi(app: object) -> None:
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "{self.tag}" for t in tags):
                        tags.append({{
                            "name": "{self.tag}",
                            "description": (
                                "โมดูล langchain — LCEL + Agents + Memory\\n\\n"
                                "• LCEL / Sequential / Router / MapReduce / Refine\\n"
                                "• ReAct / OpenAI-Tools / Plan-Execute / Reflexion\\n"
                                "• Buffer / Window / Summary memory\\n"
                                "• Step-by-step trace"
                            ),
                            "externalDocs": {{
                                "description": "{self.module} Module README",
                                "url": "/docs/README_{self.module}.md",
                            }},
                        }})
                    info_ = schema.setdefault("info", {{}})
                    info_.setdefault("x-module", "{self.module}")
                    info_.setdefault("x-layer", "{self.layer}")
                    info_.setdefault("x-prefix", "{self.prefix}")
                    info_.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent(f'''\
            """{self.module} module"""
            from .presentation.router import router as {self.prefix}_router

            __all__ = ["{self.prefix}_router"]
        '''))

    # ═══════════════════════════════════════════════════════════
    #  2. SQL
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info(f"[SQL] {self.module} — {self.tables}")
        self.writer.write(
            f"{self.sql_dir}/V001__create_{self.module}.sql", self._v001_sql(),
        )
        self.writer.write(
            f"{self.sql_dir}/V002__seed_{self.module}.sql", self._v002_sql(),
        )
        self.writer.write(
            f"{self.sql_dir}/V003__rollback_{self.module}.sql", self._v003_sql(),
        )

    def _v001_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V001__create_langchain.sql | Module: langchain | Prefix: lc
-- Schema: public | Tables: lc_chains, lc_agents, lc_memories,
--                          lc_runs, lc_traces
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."lc_chains";
CREATE TABLE "public"."lc_chains" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "name"         varchar(100) NOT NULL,
  "chain_type"   varchar(20) NOT NULL DEFAULT 'lcel',
  "config_json"  text NOT NULL DEFAULT '{}',
  "version"      varchar(20) NOT NULL DEFAULT '1.0.0',
  "is_active"    bool NOT NULL DEFAULT true,
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "lc_chains_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_lc_chain_name" UNIQUE ("tenant_id", "name"),
  CONSTRAINT "ck_lc_chain_type" CHECK (
    chain_type IN ('lcel','sequential','router','map_reduce','refine','stuff')
  )
);
CREATE INDEX "ix_lc_chain_tenant" ON "public"."lc_chains" ("tenant_id");

DROP TABLE IF EXISTS "public"."lc_agents";
CREATE TABLE "public"."lc_agents" (
  "id"              uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"       uuid NOT NULL,
  "name"            varchar(100) NOT NULL,
  "agent_type"      varchar(30) NOT NULL DEFAULT 'react',
  "tools_json"      text NOT NULL DEFAULT '[]',
  "model"           varchar(100) NOT NULL DEFAULT 'gpt-4o-mini',
  "max_iterations"  int4 NOT NULL DEFAULT 10,
  "config_json"     text NOT NULL DEFAULT '{}',
  "is_active"       bool NOT NULL DEFAULT true,
  "created_at"      timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"      timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "lc_agents_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_lc_agent_name" UNIQUE ("tenant_id", "name"),
  CONSTRAINT "ck_lc_agent_type" CHECK (
    agent_type IN ('react','openai_tools','plan_execute','self_ask','reflexion')
  )
);
CREATE INDEX "ix_lc_agent_tenant" ON "public"."lc_agents" ("tenant_id");

DROP TABLE IF EXISTS "public"."lc_memories";
CREATE TABLE "public"."lc_memories" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "conversation_id"  uuid NOT NULL,
  "memory_type"      varchar(30) NOT NULL DEFAULT 'buffer',
  "snapshot_json"    text NOT NULL DEFAULT '[]',
  "size_bytes"       int4 NOT NULL DEFAULT 0,
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "lc_memories_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_lc_memory_type" CHECK (
    memory_type IN ('buffer','window','summary','summary_buffer','vector','kg')
  )
);
CREATE INDEX "ix_lc_memory_conv"   ON "public"."lc_memories" ("conversation_id");
CREATE INDEX "ix_lc_memory_tenant" ON "public"."lc_memories" ("tenant_id");

DROP TABLE IF EXISTS "public"."lc_runs";
CREATE TABLE "public"."lc_runs" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "user_id"        uuid NOT NULL,
  "kind"           varchar(20) NOT NULL DEFAULT 'chain',
  "target_id"      uuid NOT NULL,
  "input_json"     text NOT NULL DEFAULT '{}',
  "output_json"    text NOT NULL DEFAULT '{}',
  "status"         varchar(20) NOT NULL DEFAULT 'QUEUED',
  "latency_ms"     int4 NOT NULL DEFAULT 0,
  "tokens_used"    int4 NOT NULL DEFAULT 0,
  "cost_usd"       numeric(12,8) NOT NULL DEFAULT 0,
  "error_message"  text NOT NULL DEFAULT '',
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "lc_runs_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_lc_run_kind" CHECK (kind IN ('chain','agent')),
  CONSTRAINT "ck_lc_run_status" CHECK (
    status IN ('QUEUED','RUNNING','DONE','FAILED','CANCELLED')
  )
);
CREATE INDEX "ix_lc_run_tenant_time" ON "public"."lc_runs" ("tenant_id", "created_at" DESC);
CREATE INDEX "ix_lc_run_user_time"   ON "public"."lc_runs" ("user_id", "created_at" DESC);

DROP TABLE IF EXISTS "public"."lc_traces";
CREATE TABLE "public"."lc_traces" (
  "id"            uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"     uuid NOT NULL,
  "run_id"        uuid NOT NULL,
  "step"          int4 NOT NULL DEFAULT 0,
  "kind"          varchar(30) NOT NULL DEFAULT 'other',
  "payload_json"  text NOT NULL DEFAULT '{}',
  "latency_ms"    int4 NOT NULL DEFAULT 0,
  "created_at"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"    timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "lc_traces_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_lc_trace_run_step" ON "public"."lc_traces" ("run_id", "step");
CREATE INDEX "ix_lc_trace_tenant"   ON "public"."lc_traces" ("tenant_id");

CREATE OR REPLACE FUNCTION public.set_updated_at_lc()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_lc_chain_updated ON "public"."lc_chains";
CREATE TRIGGER trg_lc_chain_updated BEFORE UPDATE ON "public"."lc_chains"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_lc();

DROP TRIGGER IF EXISTS trg_lc_agent_updated ON "public"."lc_agents";
CREATE TRIGGER trg_lc_agent_updated BEFORE UPDATE ON "public"."lc_agents"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_lc();

DROP TRIGGER IF EXISTS trg_lc_mem_updated ON "public"."lc_memories";
CREATE TRIGGER trg_lc_mem_updated BEFORE UPDATE ON "public"."lc_memories"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_lc();

DROP TRIGGER IF EXISTS trg_lc_run_updated ON "public"."lc_runs";
CREATE TRIGGER trg_lc_run_updated BEFORE UPDATE ON "public"."lc_runs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_lc();

DROP TRIGGER IF EXISTS trg_lc_trace_updated ON "public"."lc_traces";
CREATE TRIGGER trg_lc_trace_updated BEFORE UPDATE ON "public"."lc_traces"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_lc();

ALTER TABLE "public"."lc_chains"    ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."lc_agents"    ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."lc_memories"  ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."lc_runs"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."lc_traces"    ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_lc_chain ON "public"."lc_chains";
CREATE POLICY p_lc_chain ON "public"."lc_chains"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_lc_agent ON "public"."lc_agents";
CREATE POLICY p_lc_agent ON "public"."lc_agents"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_lc_mem ON "public"."lc_memories";
CREATE POLICY p_lc_mem ON "public"."lc_memories"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_lc_run ON "public"."lc_runs";
CREATE POLICY p_lc_run ON "public"."lc_runs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_lc_trace ON "public"."lc_traces";
CREATE POLICY p_lc_trace ON "public"."lc_traces"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_langchain.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."lc_chains"
    (tenant_id, name, chain_type, config_json, version)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'default_lcel',
     'lcel', '{"model":"gpt-4o-mini"}', '1.0.0'),
    ('00000000-0000-0000-0000-000000000001', 'sequential_qa',
     'sequential', '{"model":"gpt-4o-mini","steps":["retrieve","generate"]}', '1.0.0')
ON CONFLICT DO NOTHING;

INSERT INTO "public"."lc_agents"
    (tenant_id, name, agent_type, tools_json, model, max_iterations, config_json)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'default_react',
     'react', '[]', 'gpt-4o-mini', 10,
     '{"system_prompt":"You are a helpful agent."}')
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_langchain.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_lc_trace_updated ON "public"."lc_traces";
DROP TRIGGER IF EXISTS trg_lc_run_updated   ON "public"."lc_runs";
DROP TRIGGER IF EXISTS trg_lc_mem_updated   ON "public"."lc_memories";
DROP TRIGGER IF EXISTS trg_lc_agent_updated ON "public"."lc_agents";
DROP TRIGGER IF EXISTS trg_lc_chain_updated ON "public"."lc_chains";

DROP POLICY IF EXISTS p_lc_trace ON "public"."lc_traces";
DROP POLICY IF EXISTS p_lc_run   ON "public"."lc_runs";
DROP POLICY IF EXISTS p_lc_mem   ON "public"."lc_memories";
DROP POLICY IF EXISTS p_lc_agent ON "public"."lc_agents";
DROP POLICY IF EXISTS p_lc_chain ON "public"."lc_chains";

DROP TABLE IF EXISTS "public"."lc_traces"   CASCADE;
DROP TABLE IF EXISTS "public"."lc_runs"     CASCADE;
DROP TABLE IF EXISTS "public"."lc_memories" CASCADE;
DROP TABLE IF EXISTS "public"."lc_agents"   CASCADE;
DROP TABLE IF EXISTS "public"."lc_chains"   CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_lc();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "lc_001"
        content = f'''"""add langchain tables

Revision ID: {rev}
Revises: None
Create Date: {datetime.now(timezone.utc).date().isoformat()}
"""
from __future__ import annotations
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "{rev}"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "public"


def upgrade() -> None:
    """TH: สร้างตาราง langchain | EN: create tables"""
    op.create_table(
        "lc_chains",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("chain_type", sa.String(20), nullable=False, server_default="lcel"),
        sa.Column("config_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("version", sa.String(20), nullable=False, server_default="1.0.0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_lc_chain_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "lc_agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("agent_type", sa.String(30), nullable=False, server_default="react"),
        sa.Column("tools_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("model", sa.String(100), nullable=False, server_default="gpt-4o-mini"),
        sa.Column("max_iterations", sa.Integer, nullable=False, server_default="10"),
        sa.Column("config_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_lc_agent_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "lc_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("memory_type", sa.String(30), nullable=False, server_default="buffer"),
        sa.Column("snapshot_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("size_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "lc_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.String(20), nullable=False, server_default="chain"),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("input_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("output_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="QUEUED"),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("tokens_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Numeric(12, 8), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "lc_traces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step", sa.Integer, nullable=False, server_default="0"),
        sa.Column("kind", sa.String(30), nullable=False, server_default="other"),
        sa.Column("payload_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )

    op.create_index("ix_lc_chain_tenant", "lc_chains", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_lc_agent_tenant", "lc_agents", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_lc_memory_conv", "lc_memories", ["conversation_id"], schema=SCHEMA)
    op.create_index("ix_lc_memory_tenant", "lc_memories", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_lc_run_tenant_time", "lc_runs", ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_lc_run_user_time", "lc_runs", ["user_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_lc_trace_run_step", "lc_traces", ["run_id", "step"], schema=SCHEMA)
    op.create_index("ix_lc_trace_tenant", "lc_traces", ["tenant_id"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_lc()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in ("lc_chains", "lc_agents", "lc_memories", "lc_runs", "lc_traces"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE TRIGGER trg_{{tbl}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_lc();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """TH: ลบตาราง | EN: drop tables"""
    for tbl in ("lc_traces", "lc_runs", "lc_memories", "lc_agents", "lc_chains"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_lc();")
'''
        self.writer.write(
            f"migrations/versions/{rev}_add_{self.module}_tables.py", content,
        )

    # ═══════════════════════════════════════════════════════════
    #  4. SWAGGER
    # ═══════════════════════════════════════════════════════════
    def create_swagger(self) -> None:
        info(f"[SWAGGER] {self.module}")
        self.writer.write(
            f"{self.mod_root}/presentation/swagger.py", self._swagger_content(),
        )

    # ═══════════════════════════════════════════════════════════
    #  5. POSTMAN
    # ═══════════════════════════════════════════════════════════
    def create_postman(self) -> None:
        info(f"[POSTMAN] {self.module}")
        self.writer.write(
            f"docs/postman/{self.module}.json", self._postman_json(),
        )

    def _postman_json(self) -> str:
        return _json.dumps({
            "info": {
                "name": f"{self.module} API",
                "_postman_id": str(uuid.uuid4()),
                "description": self.cfg["title"],
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "variable": [
                {"key": "base_url", "value": "http://localhost:8000"},
                {"key": "tenant_id", "value": "00000000-0000-0000-0000-000000000001"},
                {"key": "user_id", "value": "00000000-0000-0000-0000-000000000002"},
                {"key": "chain_id", "value": "REPLACE_WITH_CHAIN_UUID"},
                {"key": "agent_id", "value": "REPLACE_WITH_AGENT_UUID"},
            ],
            "item": [
                {
                    "name": "List Chains",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "X-Tenant-Id", "value": "{{tenant_id}}"}],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/chains",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "chains"],
                        },
                    },
                },
                {
                    "name": "Create Chain (LCEL)",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/chains",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "chains"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"my_chain","chain_type":"lcel","config":{"model":"gpt-4o-mini"}}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Invoke Chain",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/chains/{{{{chain_id}}}}/invoke",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "chains",
                                     "{{chain_id}}", "invoke"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"inputs":{"input":"Say hello in French"}}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Create Agent",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/agents",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "agents"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"my_agent","agent_type":"react","tools":["get_weather"],"model":"gpt-4o-mini","max_iterations":5}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Invoke Agent",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/agents/{{{{agent_id}}}}/invoke",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "agents",
                                     "{{agent_id}}", "invoke"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"question":"What is the weather in Bangkok?"}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Get Run Trace",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "X-Tenant-Id", "value": "{{tenant_id}}"}],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/runs/REPLACE/trace",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "runs", "REPLACE", "trace"],
                        },
                    },
                },
                {
                    "name": "Update Memory",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/memory",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "memory"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"conversation_id":"00000000-0000-0000-0000-000000000099","memory_type":"buffer","messages":[{"role":"user","content":"hi"},{"role":"assistant","content":"hello"}]}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
            ],
        }, indent=2, ensure_ascii=False)

    # ═══════════════════════════════════════════════════════════
    #  6. UPDATE APP
    # ═══════════════════════════════════════════════════════════
    def update_app(self) -> None:
        info(f"[UPDATE APP] {self.module}")
        app_file = self.root / self.app_py
        if not app_file.exists():
            warn(f"{self.app_py} not found")
            return

        content = app_file.read_text(encoding="utf-8")
        original = content

        router_import = (
            f"from app.modules.{self.module}.presentation.router "
            f"import router as {self.prefix}_router"
        )
        swagger_import = (
            f"from app.modules.{self.module}.presentation.swagger "
            f"import register_{self.module}_openapi"
        )

        if router_import not in content:
            lines = content.split("\n")
            insert_at = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    insert_at = i + 1
            lines.insert(insert_at, router_import + "\n" + swagger_import)
            content = "\n".join(lines)

        if f"include_router({self.prefix}_router" not in content:
            include_call = (
                f"\napp.include_router({self.prefix}_router, prefix='/api/v1')\n"
                f"register_{self.module}_openapi(app)\n"
            )
            if "app = FastAPI(" in content:
                m = re.search(r"app\s*=\s*FastAPI\([^)]*\)\n", content)
                if m:
                    content = content[:m.end()] + include_call + content[m.end():]
                else:
                    content += include_call
            else:
                content += include_call

        if content != original:
            app_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.app_py} updated")
        else:
            skip(f"{self.app_py} unchanged")

    # ═══════════════════════════════════════════════════════════
    #  7. UPDATE ENV
    # ═══════════════════════════════════════════════════════════
    def update_env(self) -> None:
        info(f"[UPDATE ENV] {self.module}")
        env_file = self.root / self.env_py
        if not env_file.exists():
            warn(f"{self.env_py} not found")
            return

        content = env_file.read_text(encoding="utf-8")
        marker = f"# --- module {self.module} ---"
        if marker in content:
            skip(f"{self.module} already in env.py")
            return

        block = f'''{marker}
try:
    from app.modules.{self.module}.infrastructure.models import (  # noqa: F401
        LCAgentModel,
        LCChainModel,
        LCMemoryModel,
        LCRunModel,
        LCTraceModel,
    )
except ImportError:
    pass

'''
        anchor = "config = context.config"
        idx = content.find(anchor)
        if idx == -1:
            warn("anchor not found in env.py")
            return

        content = content[:idx] + block + content[idx:]
        env_file.write_text(content, encoding="utf-8", newline="\n")
        ok(f"{self.env_py} updated")

    # ═══════════════════════════════════════════════════════════
    #  8. VERIFY
    # ═══════════════════════════════════════════════════════════
    def verify(self) -> None:
        info(f"[VERIFY] {self.module}")
        issues: list[str] = []

        for rel in (
            f"{self.mod_root}/presentation/router.py",
            f"{self.mod_root}/presentation/swagger.py",
            f"{self.mod_root}/infrastructure/models.py",
            f"{self.mod_root}/application/use_case.py",
            f"{self.mod_root}/domain/helpers/memory.py",
            f"{self.mod_root}/domain/helpers/tracer.py",
        ):
            p = self.root / rel
            if p.exists():
                ok(f"{rel} ✓")
            else:
                issues.append(f"missing: {rel}")

        app_file = self.root / self.app_py
        if app_file.exists():
            content = app_file.read_text(encoding="utf-8")
            for check in (
                f"{self.prefix}_router",
                f"register_{self.module}_openapi",
            ):
                if check in content:
                    ok(f"app.py: {check} ✓")
                else:
                    issues.append(f"app.py missing: {check}")

        postman = self.root / f"docs/postman/{self.module}.json"
        if postman.exists():
            try:
                _json.loads(postman.read_text(encoding="utf-8"))
                ok("postman.json valid")
            except Exception as e:
                issues.append(f"postman.json invalid: {e}")
        else:
            issues.append("postman.json missing")

        print()
        if issues:
            warn(f"{len(issues)} issues:")
            for i, m in enumerate(issues, 1):
                err(f"  {i}. {m}")
        else:
            ok("ALL CHECKS PASSED ✓")

    # ═══════════════════════════════════════════════════════════
    #  RUN ALL
    # ═══════════════════════════════════════════════════════════
    def run_all(self) -> None:
        self.create_module()
        self.create_sql()
        self.create_migration()
        self.create_swagger()
        self.create_postman()
        self.update_app()
        self.update_env()

    def summary(self) -> None:
        print()
        info("═" * 60)
        ok(f"DONE — {self.module} ({self.cfg['title']})")
        info(f"  Prefix  : {self.prefix}_")
        info(f"  Tables  : {len(self.tables)}")
        info(f"  Written : {len(self.writer.written)}")
        info(f"  Skipped : {len(self.writer.skipped)}")
        info("═" * 60)


# ═══════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════
HELP = f"""
create_module_langchain.py — LangChain Wrapper Module Generator v{VERSION}

USAGE
    python create_module_langchain.py <action> [options]

MODULE
    name    : langchain
    layer   : 5-Intel
    prefix  : lc
    schema  : public
    tables  : lc_chains, lc_agents, lc_memories, lc_runs, lc_traces

ACTIONS (10)
    create       สร้าง module structure (4 layers)
    sql          สร้าง SQL migrations V001/V002/V003
    alembic      สร้าง Alembic migration
    swagger      สร้าง OpenAPI docs
    postman      สร้าง Postman collection
    update       อัปเดต app/app.py
    update-env   อัปเดต migrations/env.py
    verify       ตรวจสอบ setup
    all          ทำทุกอย่าง
    help         แสดง help

EXAMPLES
    python create_module_langchain.py all
    python create_module_langchain.py create --force
    python create_module_langchain.py verify
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--help", action="store_true")

    args, _ = parser.parse_known_args()

    if args.help or args.action == "help":
        print(HELP)
        return 0

    if args.action not in ACTIONS:
        err(f"unknown action: {args.action}")
        print(HELP)
        return 1

    root = Path(args.project_root).resolve()
    if not root.exists():
        err(f"root not found: {root}")
        return 1

    gen = LangChainGenerator(root, force=args.force)

    print()
    info("═" * 60)
    info(f"  MODULE : {gen.module} — {gen.cfg['title']}")
    info(f"  LAYER  : {gen.layer}")
    info(f"  PREFIX : {gen.prefix}_")
    info(f"  ACTION : {args.action}")
    info("═" * 60)

    action_map = {
        "create": gen.create_module,
        "sql": gen.create_sql,
        "alembic": gen.create_migration,
        "swagger": gen.create_swagger,
        "postman": gen.create_postman,
        "update": gen.update_app,
        "update-env": gen.update_env,
        "verify": gen.verify,
        "all": gen.run_all,
    }

    try:
        action_map[args.action]()
    except Exception as e:
        err(f"Aborted: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if args.action != "verify":
        gen.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())