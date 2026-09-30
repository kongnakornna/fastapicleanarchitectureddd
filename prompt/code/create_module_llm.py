#!/usr/bin/env python3
"""
create_module_llm.py — LLM Module Generator v1.3

สร้าง llm module ตาม Clean Architecture + DDD + Event-Driven
Schema: public · Prefix: llm_ · Tables: llm_*

Actions (10):
  1.  create      — สร้าง module structure (llm) 4 layers
  2.  activate    — register router + swagger + models
  3.  sql         — สร้าง SQL migrations V001/V002/V003
  4.  update      — อัปเดต app/app.py
  5.  update-env  — อัปเดต migrations/env.py
  6.  alembic     — สร้าง Alembic migration (5 tables + triggers + RLS)
  7.  swagger     — สร้าง OpenAPI docs
  8.  postman     — สร้าง Postman collection
  9.  verify      — ตรวจสอบ Swagger + Postman + SQL   ★ NEW
 10.  all         — ทำทุกอย่าง

v1.3 CHANGES:
  - FIX: _update_app_py() → เพิ่ม register_llm_openapi(app) call
  - NEW: verify action ตรวจสอบ setup
  - NEW: auto-patch swagger import + call
"""
from __future__ import annotations

import argparse
import json as _json_mod
import re
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════
VERSION = "1.3.0"

LAYER_NAMES = {
    "0": "0-Core", "1": "1-Foundation", "2": "2-Money",
    "3": "3-Goods", "4": "4-Ops", "5": "5-Intel",
    "6": "6-Monitor", "7": "7-Template",
}

ACTIONS = {
    "create", "activate", "sql", "alembic",
    "swagger", "postman", "update", "update-env",
    "all", "verify", "help",
}

SCHEMA = "public"
PREFIX = "llm"
TABLE_NAMES = (
    "llm_providers",
    "llm_models",
    "llm_conversations",
    "llm_messages",
    "llm_usage_logs",
)


# ═══════════════════════════════════════════════════════════════
#  LOGGER
# ═══════════════════════════════════════════════════════════════
class C:
    CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; GRAY = "\033[90m"; RESET = "\033[0m"


def info(msg: str) -> None: print(f"{C.CYAN}{msg}{C.RESET}")
def ok(msg: str) -> None: print(f"  {C.GREEN}[OK]{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"  {C.YELLOW}[!!]{C.RESET} {msg}")
def err(msg: str) -> None: print(f"  {C.RED}[XX]{C.RESET} {msg}")
def skip(msg: str) -> None: print(f"  {C.GRAY}[--]{C.RESET} {msg}")


# ═══════════════════════════════════════════════════════════════
#  FILE WRITER
# ═══════════════════════════════════════════════════════════════
class FileWriter:
    def __init__(self, project_root: Path, force: bool = False, backup: bool = True):
        self.root = project_root
        self.force = force
        self.backup = backup
        self.written: list[Path] = []
        self.skipped: list[Path] = []
        self.backups: list[Path] = []

    def write(self, rel_path: str, content: str) -> None:
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not self.force:
            skip(f"skip (exists): {rel_path}")
            self.skipped.append(path)
            return

        if path.exists() and self.backup:
            bak = path.with_suffix(path.suffix + ".bak")
            bak.write_bytes(path.read_bytes())
            self.backups.append(bak)
            ok(f"backup: {rel_path}.bak")

        if rel_path.endswith(".py"):
            try:
                compile(content, rel_path, "exec")
            except SyntaxError as exc:
                err(f"SYNTAX ERROR in {rel_path}: {exc}")
                err(f"  line {exc.lineno}: {exc.text}")
                raise RuntimeError(f"Refuse to write invalid Python: {rel_path}") from exc

        path.write_text(content, encoding="utf-8", newline="\n")
        ok(rel_path)
        self.written.append(path)


# ═══════════════════════════════════════════════════════════════
#  GENERATOR
# ═══════════════════════════════════════════════════════════════
class LLMModuleGenerator:
    def __init__(
        self,
        project_root: Path,
        module: str = "llm",
        layer: str = "5",
        prefix: str = "llm",
        template: str = "A",
        force: bool = False,
    ):
        self.root = project_root
        self.module = module.lower()
        self.layer = layer
        self.prefix = prefix.lower()
        self.template = template
        self.layer_name = LAYER_NAMES.get(layer, "5-Intel")
        self.writer = FileWriter(project_root, force=force)

        self.mod_root = f"app/modules/{self.module}"
        self.sql_dir = "db/migrations"
        self.alembic_dir = "migrations/versions"
        self.env_py = "migrations/env.py"
        self.app_py = "app/app.py"

    # ═══════════════════════════════════════════════════════════
    #  1. CREATE MODULE
    # ═══════════════════════════════════════════════════════════
    def create_module(self) -> None:
        info(f"[CREATE] module: {self.module} (Layer {self.layer_name})")
        self._create_domain()
        self._create_application()
        self._create_infrastructure()
        self._create_presentation()
        self._create_root_init()

    # ─── DOMAIN LAYER ───────────────────────────────────────────
    def _create_domain(self) -> None:
        base = f"{self.mod_root}/domain"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """llm domain layer — ชั้นโดเมน llm"""
            from .entities import (
                Conversation, Message, Model, Provider, UsageLog,
            )
            from .enums import (
                ConversationStatus, FinishReason, MessageRole, ProviderType,
            )
            from .events import (
                CompletionGenerated, ConversationCreated,
                MessageSent, ProviderRegistered, TokenLimitExceeded,
            )
            from .exceptions import (
                ConversationNotFoundError, InvalidMessageRoleError,
                LLMError, ModelNotFoundError, ProviderAuthError,
                ProviderError, ProviderNotFoundError,
                RateLimitExceededError, StreamingError,
                TokenLimitExceededError,
            )

            __all__ = [
                "Conversation", "Message", "Model", "Provider", "UsageLog",
                "ConversationStatus", "FinishReason",
                "MessageRole", "ProviderType",
                "CompletionGenerated", "ConversationCreated",
                "MessageSent", "ProviderRegistered", "TokenLimitExceeded",
                "ConversationNotFoundError", "InvalidMessageRoleError",
                "LLMError", "ModelNotFoundError", "ProviderAuthError",
                "ProviderError", "ProviderNotFoundError",
                "RateLimitExceededError", "StreamingError",
                "TokenLimitExceededError",
            ]
        '''))

        self.writer.write(f"{base}/enums.py", dedent('''\
            """llm enums — Enum ของ llm"""
            from __future__ import annotations
            from enum import StrEnum


            class ProviderType(StrEnum):
                """TH: ประเภทผู้ให้บริการ | EN: Provider type"""
                OPENAI = "openai"
                ANTHROPIC = "anthropic"
                LOCAL = "local"
                AZURE = "azure"


            class MessageRole(StrEnum):
                """TH: บทบาทข้อความ | EN: Message role"""
                SYSTEM = "system"
                USER = "user"
                ASSISTANT = "assistant"
                TOOL = "tool"


            class ConversationStatus(StrEnum):
                """TH: สถานะ conversation | EN: Conversation status"""
                ACTIVE = "ACTIVE"
                ARCHIVED = "ARCHIVED"
                DELETED = "DELETED"


            class FinishReason(StrEnum):
                """TH: เหตุผลที่จบ | EN: Finish reason"""
                STOP = "stop"
                LENGTH = "length"
                TOOL_CALLS = "tool_calls"
                CONTENT_FILTER = "content_filter"
                ERROR = "error"
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """llm domain exceptions — ข้อยกเว้นโดเมน llm"""
            from __future__ import annotations


            class LLMError(Exception):
                """TH: base error | EN: base error"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class ProviderNotFoundError(LLMError):
                code = "NOT_FOUND"


            class ModelNotFoundError(LLMError):
                code = "NOT_FOUND"


            class ConversationNotFoundError(LLMError):
                code = "NOT_FOUND"


            class ProviderError(LLMError):
                code = "PROVIDER_ERROR"


            class ProviderAuthError(LLMError):
                code = "PROVIDER_ERROR"


            class RateLimitExceededError(LLMError):
                code = "RATE_LIMITED"


            class TokenLimitExceededError(LLMError):
                code = "LIMIT_EXCEEDED"


            class InvalidMessageRoleError(LLMError):
                code = "VALIDATION_ERROR"


            class StreamingError(LLMError):
                code = "PROVIDER_ERROR"
        '''))

        self.writer.write(f"{base}/events.py", dedent('''\
            """llm domain events — เหตุการณ์โดเมน llm"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import UTC, datetime


            def _now() -> datetime:
                return datetime.now(UTC)


            @dataclass(frozen=True, slots=True)
            class ConversationCreated:
                conversation_id: uuid.UUID
                tenant_id: uuid.UUID
                user_id: uuid.UUID
                model_id: uuid.UUID
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class MessageSent:
                message_id: uuid.UUID
                conversation_id: uuid.UUID
                tenant_id: uuid.UUID
                role: str
                tokens_input: int
                tokens_output: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class CompletionGenerated:
                message_id: uuid.UUID
                tenant_id: uuid.UUID
                model_name: str
                finish_reason: str
                latency_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class ProviderRegistered:
                provider_id: uuid.UUID
                tenant_id: uuid.UUID
                provider_type: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class TokenLimitExceeded:
                tenant_id: uuid.UUID
                user_id: uuid.UUID
                current_usage: int
                limit: int
                occurred_at: datetime = field(default_factory=_now)
        '''))

        self.writer.write(f"{base}/value_objects/__init__.py", dedent('''\
            """llm value objects"""
            from .chat_options import ChatOptions
            from .provider_config import ProviderConfig
            from .token_usage import TokenUsage

            __all__ = ["ChatOptions", "ProviderConfig", "TokenUsage"]
        '''))

        self.writer.write(f"{base}/value_objects/token_usage.py", dedent('''\
            """TokenUsage value object — ใช้ Decimal เท่านั้น"""
            from __future__ import annotations
            from dataclasses import dataclass
            from decimal import Decimal


            @dataclass(frozen=True, slots=True)
            class TokenUsage:
                """TH: การใช้ token | EN: token usage VO"""
                input_tokens: int
                output_tokens: int
                cost_usd: Decimal = Decimal("0")

                @property
                def total_tokens(self) -> int:
                    return self.input_tokens + self.output_tokens

                def __post_init__(self) -> None:
                    if self.input_tokens < 0 or self.output_tokens < 0:
                        raise ValueError("tokens must be non-negative")
                    if self.cost_usd < 0:
                        raise ValueError("cost must be non-negative")
        '''))

        self.writer.write(f"{base}/value_objects/chat_options.py", dedent('''\
            """ChatOptions value object"""
            from __future__ import annotations
            from dataclasses import dataclass
            from typing import Any


            @dataclass(frozen=True, slots=True)
            class ChatOptions:
                """TH: ตัวเลือกการแชท | EN: chat options VO"""
                temperature: float = 0.7
                top_p: float = 1.0
                max_tokens: int = 1024
                stop: tuple[str, ...] = ()
                tools: tuple[dict[str, Any], ...] = ()
                tool_choice: str = "auto"
                stream: bool = False

                def __post_init__(self) -> None:
                    if not 0.0 <= self.temperature <= 2.0:
                        raise ValueError("temperature must be 0.0-2.0")
                    if not 0.0 <= self.top_p <= 1.0:
                        raise ValueError("top_p must be 0.0-1.0")
                    if self.max_tokens < 1:
                        raise ValueError("max_tokens must be >= 1")
        '''))

        self.writer.write(f"{base}/value_objects/provider_config.py", dedent('''\
            """ProviderConfig value object"""
            from __future__ import annotations
            from dataclasses import dataclass


            @dataclass(frozen=True, slots=True)
            class ProviderConfig:
                """TH: config ผู้ให้บริการ | EN: provider config VO"""
                name: str
                provider_type: str
                api_key: str
                base_url: str = ""
                timeout_seconds: int = 60
        '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """llm domain helpers"""
            from .token_counter import count_message_tokens, count_tokens

            __all__ = ["count_message_tokens", "count_tokens"]
        '''))

        self.writer.write(f"{base}/helpers/token_counter.py", dedent('''\
            """Token counter — นับ token แบบ best-effort"""
            from __future__ import annotations

            import structlog

            log = structlog.get_logger()

            _ENCODINGS: dict[str, object] = {}


            def _get_encoding(model: str) -> object | None:
                try:
                    import tiktoken
                except ImportError:
                    return None
                if model in _ENCODINGS:
                    return _ENCODINGS[model]
                try:
                    enc = tiktoken.encoding_for_model(model)
                    _ENCODINGS[model] = enc
                    return enc
                except Exception:
                    try:
                        enc = tiktoken.get_encoding("cl100k_base")
                        _ENCODINGS[model] = enc
                        return enc
                    except Exception:
                        return None


            def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
                """TH: นับ token | EN: count tokens (never-raise)"""
                if not text:
                    return 0
                enc = _get_encoding(model)
                if enc is not None:
                    try:
                        return len(enc.encode(text))
                    except Exception as exc:
                        log.warning("token_counter.encode_failed", err=str(exc))
                return max(1, len(text) // 4)


            def count_message_tokens(
                messages: list[dict], model: str = "gpt-4o-mini",
            ) -> int:
                """TH: นับ token ของ messages | EN: count message tokens"""
                total = 0
                for msg in messages:
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        total += count_tokens(content, model)
                    total += 4
                return total + 2
        '''))

        # entities
        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """llm entities"""
            from .conversation import Conversation
            from .message import Message
            from .model import Model
            from .provider import Provider
            from .usage_log import UsageLog

            __all__ = [
                "Conversation", "Message", "Model", "Provider", "UsageLog",
            ]
        '''))

        for name, cls, model in (
            ("provider", "Provider", "ProviderModel"),
            ("model", "Model", "ModelModel"),
            ("conversation", "Conversation", "ConversationModel"),
            ("message", "Message", "MessageModel"),
            ("usage_log", "UsageLog", "UsageLogModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias"""
                from __future__ import annotations
                from app.modules.llm.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

    # ─── APPLICATION LAYER ──────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """llm application layer — ชั้นแอปพลิเคชัน llm"""
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """llm application exceptions"""
            from __future__ import annotations


            class ApplicationError(Exception):
                """TH: base | EN: base"""
                code: str = "APP_ERROR"
                http_status: int = 400


            class ProviderNotFoundAppError(ApplicationError):
                code = "NOT_FOUND"
                http_status = 404


            class ModelNotFoundAppError(ApplicationError):
                code = "NOT_FOUND"
                http_status = 404


            class ConversationNotFoundAppError(ApplicationError):
                code = "NOT_FOUND"
                http_status = 404


            class ProviderCallAppError(ApplicationError):
                code = "PROVIDER_ERROR"
                http_status = 502
        '''))

        self.writer.write(f"{base}/interfaces.py", dedent('''\
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
        '''))

        self.writer.write(f"{base}/mappers.py", dedent('''\
            """llm mappers — ORM ↔ domain"""
            from __future__ import annotations
            from typing import Any


            def provider_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "name": row.name,
                    "provider_type": row.provider_type,
                    "base_url": row.base_url, "is_active": row.is_active,
                }


            def model_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "provider_id": str(row.provider_id),
                    "name": row.name, "display_name": row.display_name,
                    "context_window": row.context_window,
                    "max_output_tokens": row.max_output_tokens,
                    "supports_streaming": row.supports_streaming,
                    "supports_tools": row.supports_tools,
                }


            def conversation_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "user_id": str(row.user_id),
                    "title": row.title, "model_id": str(row.model_id),
                    "status": row.status, "message_count": row.message_count,
                    "total_tokens": row.total_tokens,
                }


            def message_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "role": row.role,
                    "content": row.content, "tokens_input": row.tokens_input,
                    "tokens_output": row.tokens_output,
                    "finish_reason": row.finish_reason,
                }
        '''))

        self.writer.write(f"{base}/utils.py", dedent('''\
            """llm application utils"""
            from __future__ import annotations
            import hashlib
            from typing import Any

            from app.modules.llm.domain.value_objects import ChatOptions


            def build_cache_key(
                messages: list[dict[str, Any]],
                model: str,
                options: ChatOptions,
            ) -> str:
                """TH: สร้าง cache key จาก hash | EN: build deterministic cache key"""
                parts = [model]
                for m in messages:
                    parts.append(f"{m.get('role','')}:{m.get('content','')}")
                parts.append(f"t={options.temperature}")
                parts.append(f"m={options.max_tokens}")
                parts.append(f"p={options.top_p}")
                raw = "|".join(parts)
                return "llm:cache:" + hashlib.sha256(raw.encode()).hexdigest()[:32]


            def sanitize_payload(data: dict[str, Any]) -> dict[str, Any]:
                """TH: ทำความสะอาด payload | EN: sanitize payload"""
                MASK = {
                    "api_key", "api_key_encrypted", "password",
                    "token", "secret",
                }
                return {k: ("***" if k in MASK else v) for k, v in data.items()}
        '''))

        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _use_case_content(self) -> str:
        return dedent('''\
            """llm use cases"""
            from __future__ import annotations

            import time
            import uuid
            from datetime import UTC, datetime, timedelta
            from decimal import Decimal
            from typing import Any, AsyncIterator

            import structlog

            from app.modules.llm.application.interfaces import (
                ConversationRepository, EventBus, IdempotencyStore,
                LLMCache, MessageRepository, ModelRepository,
                ProviderRegistry, ProviderRepository, RateLimiter,
                RequestContext, UsageLogRepository,
            )
            from app.modules.llm.application.utils import build_cache_key
            from app.modules.llm.domain.enums import MessageRole
            from app.modules.llm.domain.events import (
                CompletionGenerated, ConversationCreated, MessageSent,
            )
            from app.modules.llm.domain.exceptions import (
                ConversationNotFoundError, LLMError,
                ModelNotFoundError, ProviderError, RateLimitExceededError,
            )
            from app.modules.llm.domain.helpers import count_message_tokens
            from app.modules.llm.domain.value_objects import ChatOptions
            from app.modules.llm.infrastructure.models import (
                ConversationModel, MessageModel, UsageLogModel,
            )

            log = structlog.get_logger()

            _COSTS: dict[str, tuple[Decimal, Decimal]] = {
                "gpt-4o-mini": (Decimal("0.00015"), Decimal("0.0006")),
                "gpt-4o": (Decimal("0.005"), Decimal("0.015")),
                "gpt-4-turbo": (Decimal("0.01"), Decimal("0.03")),
                "claude-3-5-sonnet-20241022": (
                    Decimal("0.003"), Decimal("0.015"),
                ),
                "claude-3-opus-20240229": (
                    Decimal("0.015"), Decimal("0.075"),
                ),
            }


            class LLMUseCase:
                """TH: use cases รวมทุก operation | EN: all LLM operations"""

                def __init__(
                    self,
                    provider_repo: ProviderRepository,
                    model_repo: ModelRepository,
                    conversation_repo: ConversationRepository,
                    message_repo: MessageRepository,
                    usage_repo: UsageLogRepository,
                    registry: ProviderRegistry,
                    rate_limiter: RateLimiter,
                    cache: LLMCache,
                    event_bus: EventBus,
                    idempotency: IdempotencyStore,
                ) -> None:
                    self._provider_repo = provider_repo
                    self._model_repo = model_repo
                    self._conversation_repo = conversation_repo
                    self._message_repo = message_repo
                    self._usage_repo = usage_repo
                    self._registry = registry
                    self._rate_limiter = rate_limiter
                    self._cache = cache
                    self._bus = event_bus
                    self._idem = idempotency

                async def chat(
                    self,
                    ctx: RequestContext,
                    conversation_id: uuid.UUID | None,
                    model_name: str,
                    user_message: str,
                    options: ChatOptions,
                    system_prompt: str = "",
                    idempotency_key: str = "",
                ) -> dict[str, Any]:
                    """TH: chat completion | EN: chat completion (3-branch)"""
                    log.info("llm.chat.start", model=model_name)
                    try:
                        estimated = count_message_tokens(
                            [{"role": "user", "content": user_message}],
                            model_name,
                        )
                        uid = ctx.user_id or uuid.uuid4()
                        allowed = await self._rate_limiter.check(
                            ctx.tenant_id, uid,
                            cost=estimated + options.max_tokens,
                        )
                        if not allowed:
                            raise RateLimitExceededError("rate limit exceeded")

                        messages = self._build_messages(
                            system_prompt, user_message, [],
                        )
                        cache_key = build_cache_key(messages, model_name, options)
                        cached = await self._cache.get(cache_key)
                        if cached:
                            log.info("llm.chat.cache_hit", model=model_name)
                            return cached

                        model = await self._model_repo.find_by_name(ctx, model_name)
                        if model is None:
                            raise ModelNotFoundError(
                                f"model {model_name} not found",
                            )

                        providers = await self._provider_repo.find_all_active(ctx)
                        if not providers:
                            raise ProviderError("no active providers")

                        provider = self._registry.select_provider(
                            model_name, providers,
                        )
                        client = self._registry.get_client(provider)

                        started = time.monotonic()
                        response = await client.chat_completion(
                            messages, model_name, options,
                        )
                        latency_ms = int((time.monotonic() - started) * 1000)

                        conv_id = await self._persist_chat(
                            ctx, conversation_id, model.id, model_name,
                            system_prompt, user_message, response, latency_ms,
                        )

                        result: dict[str, Any] = {
                            "conversation_id": str(conv_id),
                            "model": model_name,
                            "content": response.get("content", ""),
                            "finish_reason": response.get("finish_reason", "stop"),
                            "usage": response.get("usage", {}),
                            "latency_ms": latency_ms,
                        }

                        await self._cache.set(cache_key, result, ttl=3600)

                        usage = response.get("usage", {}) or {}
                        actual_tokens = int(usage.get("total_tokens", estimated))
                        await self._rate_limiter.increment(
                            ctx.tenant_id, uid, cost=actual_tokens,
                        )

                        log.info(
                            "llm.chat.success",
                            model=model_name, latency_ms=latency_ms,
                        )
                        return result

                    except LLMError:
                        raise
                    except Exception:
                        log.exception("llm.chat.unexpected")
                        raise

                async def chat_stream(
                    self,
                    ctx: RequestContext,
                    conversation_id: uuid.UUID | None,
                    model_name: str,
                    user_message: str,
                    options: ChatOptions,
                    system_prompt: str = "",
                ) -> AsyncIterator[dict[str, Any]]:
                    """TH: chat streaming | EN: chat streaming (SSE)"""
                    log.info("llm.stream.start", model=model_name)
                    try:
                        messages = self._build_messages(
                            system_prompt, user_message, [],
                        )
                        model = await self._model_repo.find_by_name(
                            ctx, model_name,
                        )
                        if model is None:
                            raise ModelNotFoundError(
                                f"model {model_name} not found",
                            )

                        providers = await self._provider_repo.find_all_active(ctx)
                        if not providers:
                            raise ProviderError("no active providers")

                        provider = self._registry.select_provider(
                            model_name, providers,
                        )
                        client = self._registry.get_client(provider)

                        buffer: list[str] = []
                        started = time.monotonic()
                        async for chunk in client.stream_chat_completion(
                            messages, model_name, options,
                        ):
                            content = chunk.get("delta", "")
                            if content:
                                buffer.append(content)
                            yield chunk
                        latency_ms = int((time.monotonic() - started) * 1000)

                        full_content = "".join(buffer)
                        await self._persist_chat(
                            ctx, conversation_id, model.id, model_name,
                            system_prompt, user_message,
                            {
                                "content": full_content,
                                "finish_reason": "stop",
                                "usage": {
                                    "prompt_tokens": count_message_tokens(
                                        messages, model_name,
                                    ),
                                    "completion_tokens": count_message_tokens(
                                        [{"role": "assistant",
                                          "content": full_content}],
                                        model_name,
                                    ),
                                },
                            },
                            latency_ms,
                        )

                    except LLMError:
                        raise
                    except Exception:
                        log.exception("llm.stream.unexpected")
                        raise

                async def create_conversation(
                    self, ctx: RequestContext, model_name: str, title: str = "",
                ) -> dict[str, Any]:
                    model = await self._model_repo.find_by_name(ctx, model_name)
                    if model is None:
                        raise ModelNotFoundError(
                            f"model {model_name} not found",
                        )

                    conv = ConversationModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or uuid.uuid4(),
                        title=title or f"Chat with {model_name}",
                        model_id=model.id,
                        status="ACTIVE",
                    )
                    saved = await self._conversation_repo.save(ctx, conv)
                    await self._bus.publish(ConversationCreated(
                        conversation_id=saved.id,
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or uuid.uuid4(),
                        model_id=model.id,
                    ))
                    return {
                        "id": str(saved.id), "title": saved.title,
                        "model_id": str(saved.model_id),
                        "status": saved.status,
                        "message_count": saved.message_count,
                        "total_tokens": saved.total_tokens,
                    }

                async def list_conversations(
                    self, ctx: RequestContext, limit: int = 50,
                ) -> list[dict[str, Any]]:
                    uid = ctx.user_id or uuid.uuid4()
                    rows = await self._conversation_repo.find_by_user(
                        ctx, uid, limit,
                    )
                    return [
                        {
                            "id": str(r.id), "title": r.title,
                            "model_id": str(r.model_id),
                            "status": r.status,
                            "message_count": r.message_count,
                            "total_tokens": r.total_tokens,
                        }
                        for r in rows
                    ]

                async def get_conversation(
                    self, ctx: RequestContext, conversation_id: uuid.UUID,
                ) -> dict[str, Any]:
                    conv = await self._conversation_repo.find_by_id(
                        ctx, conversation_id,
                    )
                    if conv is None:
                        raise ConversationNotFoundError(
                            "conversation not found",
                        )
                    messages = await self._message_repo.find_by_conversation(
                        ctx, conversation_id, limit=200,
                    )
                    return {
                        "id": str(conv.id), "title": conv.title,
                        "status": conv.status,
                        "model_id": str(conv.model_id),
                        "messages": [
                            {
                                "id": str(m.id), "role": m.role,
                                "content": m.content,
                                "created_at": (
                                    m.created_at.isoformat()
                                    if m.created_at else ""
                                ),
                            }
                            for m in messages
                        ],
                    }

                async def list_providers(
                    self, ctx: RequestContext,
                ) -> list[dict[str, Any]]:
                    rows = await self._provider_repo.find_all_active(ctx)
                    return [
                        {
                            "id": str(r.id), "name": r.name,
                            "provider_type": r.provider_type,
                            "base_url": r.base_url,
                            "is_active": r.is_active,
                            "priority": r.priority,
                        }
                        for r in rows
                    ]

                async def list_models(
                    self, ctx: RequestContext,
                ) -> list[dict[str, Any]]:
                    rows = await self._model_repo.find_all_active(ctx)
                    return [
                        {
                            "id": str(r.id), "name": r.name,
                            "display_name": r.display_name,
                            "context_window": r.context_window,
                            "max_output_tokens": r.max_output_tokens,
                            "supports_streaming": r.supports_streaming,
                            "supports_tools": r.supports_tools,
                        }
                        for r in rows
                    ]

                async def get_usage(
                    self, ctx: RequestContext, since_days: int = 30,
                ) -> dict[str, Any]:
                    since = datetime.now(UTC) - timedelta(days=since_days)
                    tenant_sum = await self._usage_repo.sum_by_tenant(
                        ctx, since,
                    )
                    uid = ctx.user_id or uuid.uuid4()
                    user_sum = await self._usage_repo.sum_by_user(
                        ctx, uid, since,
                    )
                    return {
                        "tenant": tenant_sum,
                        "user": user_sum,
                        "since": since.isoformat(),
                    }

                def _build_messages(
                    self,
                    system_prompt: str,
                    user_message: str,
                    history: list[dict[str, Any]],
                ) -> list[dict[str, Any]]:
                    msgs: list[dict[str, Any]] = []
                    if system_prompt:
                        msgs.append(
                            {"role": "system", "content": system_prompt},
                        )
                    msgs.extend(history)
                    msgs.append({"role": "user", "content": user_message})
                    return msgs

                async def _persist_chat(
                    self,
                    ctx: RequestContext,
                    conversation_id: uuid.UUID | None,
                    model_id: uuid.UUID,
                    model_name: str,
                    system_prompt: str,
                    user_message: str,
                    response: dict[str, Any],
                    latency_ms: int,
                ) -> uuid.UUID:
                    uid = ctx.user_id or uuid.uuid4()

                    if conversation_id is None:
                        conv = ConversationModel(
                            tenant_id=ctx.tenant_id,
                            user_id=uid,
                            title=user_message[:50],
                            model_id=model_id,
                            system_prompt=system_prompt,
                        )
                        conv = await self._conversation_repo.save(ctx, conv)
                        conversation_id = conv.id
                    else:
                        conv = await self._conversation_repo.find_by_id(
                            ctx, conversation_id,
                        )
                        if conv is None:
                            raise ConversationNotFoundError(
                                "conversation not found",
                            )

                    usage = response.get("usage", {}) or {}
                    tokens_in = int(usage.get("prompt_tokens", 0) or 0)
                    tokens_out = int(usage.get("completion_tokens", 0) or 0)

                    user_msg = MessageModel(
                        tenant_id=ctx.tenant_id,
                        conversation_id=conversation_id,
                        role=MessageRole.USER.value,
                        content=user_message,
                        tokens_input=tokens_in,
                    )
                    await self._message_repo.create(ctx, user_msg)

                    asst_msg = MessageModel(
                        tenant_id=ctx.tenant_id,
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT.value,
                        content=response.get("content", ""),
                        tokens_output=tokens_out,
                        finish_reason=response.get("finish_reason", "stop"),
                        latency_ms=latency_ms,
                    )
                    saved = await self._message_repo.create(ctx, asst_msg)

                    conv.message_count = (conv.message_count or 0) + 2
                    conv.total_tokens = (
                        (conv.total_tokens or 0) + tokens_in + tokens_out
                    )
                    await self._conversation_repo.update(ctx, conv)

                    cost = self._compute_cost(model_name, tokens_in, tokens_out)
                    usage_log = UsageLogModel(
                        tenant_id=ctx.tenant_id,
                        user_id=uid,
                        model_id=model_id,
                        conversation_id=conversation_id,
                        tokens_input=tokens_in,
                        tokens_output=tokens_out,
                        cost_usd=cost,
                        source="chat",
                    )
                    await self._usage_repo.create(ctx, usage_log)

                    await self._bus.publish(MessageSent(
                        message_id=saved.id,
                        conversation_id=conversation_id,
                        tenant_id=ctx.tenant_id,
                        role=MessageRole.ASSISTANT.value,
                        tokens_input=tokens_in,
                        tokens_output=tokens_out,
                    ))
                    await self._bus.publish(CompletionGenerated(
                        message_id=saved.id,
                        tenant_id=ctx.tenant_id,
                        model_name=model_name,
                        finish_reason=response.get("finish_reason", "stop"),
                        latency_ms=latency_ms,
                    ))

                    return conversation_id

                def _compute_cost(
                    self, model_name: str, tokens_in: int, tokens_out: int,
                ) -> Decimal:
                    """TH: คำนวณค่าใช้จ่าย | EN: compute cost (Decimal only)"""
                    in_cost, out_cost = _COSTS.get(
                        model_name, (Decimal("0"), Decimal("0")),
                    )
                    total = (
                        in_cost * Decimal(tokens_in) / Decimal(1000)
                        + out_cost * Decimal(tokens_out) / Decimal(1000)
                    )
                    return total.quantize(Decimal("0.00000001"))
        ''')

    # ─── INFRASTRUCTURE LAYER ───────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """llm infrastructure layer"""
        '''))

        self.writer.write(f"{base}/models.py", self._models_content())
        self.writer.write(f"{base}/provider_repository.py", self._provider_repo_content())
        self.writer.write(f"{base}/model_repository.py", self._model_repo_content())
        self.writer.write(f"{base}/conversation_repository.py", self._conversation_repo_content())
        self.writer.write(f"{base}/message_repository.py", self._message_repo_content())
        self.writer.write(f"{base}/usage_log_repository.py", self._usage_log_repo_content())
        self.writer.write(f"{base}/caches.py", self._caches_content())
        self.writer.write(f"{base}/services.py", self._services_content())

    def _models_content(self) -> str:
        return dedent('''\
            """llm SQLAlchemy 2.0 models — schema=public, prefix=llm_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Index, Integer,
                Numeric, String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: declarative base | EN: declarative base"""


            class ProviderModel(Base):
                __tablename__ = "llm_providers"
                __table_args__ = (
                    CheckConstraint(
                        "provider_type IN ('openai','anthropic','local','azure')",
                        name="ck_llm_provider_type",
                    ),
                    UniqueConstraint(
                        "tenant_id", "name", name="uq_llm_provider_name",
                    ),
                    Index("ix_llm_provider_tenant", "tenant_id"),
                    Index("ix_llm_provider_type", "provider_type", "is_active"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                provider_type: Mapped[str] = mapped_column(String(50), nullable=False)
                api_key_encrypted: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                base_url: Mapped[str] = mapped_column(
                    String(500), nullable=False, server_default="",
                )
                timeout_seconds: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="60",
                )
                priority: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="100",
                )
                is_active: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("true"),
                )
                config_json: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="{}",
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class ModelModel(Base):
                __tablename__ = "llm_models"
                __table_args__ = (
                    UniqueConstraint(
                        "tenant_id", "name", name="uq_llm_model_name",
                    ),
                    Index("ix_llm_model_tenant", "tenant_id"),
                    Index("ix_llm_model_provider", "provider_id", "is_active"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                provider_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                display_name: Mapped[str] = mapped_column(
                    String(200), nullable=False, server_default="",
                )
                context_window: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="4096",
                )
                max_output_tokens: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="4096",
                )
                cost_per_1k_input: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                cost_per_1k_output: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                supports_streaming: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("true"),
                )
                supports_tools: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("false"),
                )
                is_active: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("true"),
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class ConversationModel(Base):
                __tablename__ = "llm_conversations"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('ACTIVE','ARCHIVED','DELETED')",
                        name="ck_llm_conv_status",
                    ),
                    Index("ix_llm_conv_tenant", "tenant_id"),
                    Index("ix_llm_conv_user", "user_id", "created_at"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                user_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                title: Mapped[str] = mapped_column(
                    String(500), nullable=False, server_default="",
                )
                model_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                system_prompt: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                metadata_json: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="{}",
                )
                status: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="ACTIVE",
                )
                message_count: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                total_tokens: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class MessageModel(Base):
                __tablename__ = "llm_messages"
                __table_args__ = (
                    CheckConstraint(
                        "role IN ('system','user','assistant','tool')",
                        name="ck_llm_msg_role",
                    ),
                    Index("ix_llm_msg_conv", "conversation_id", "created_at"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                conversation_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                role: Mapped[str] = mapped_column(String(20), nullable=False)
                content: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                tool_calls_json: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="[]",
                )
                tool_call_id: Mapped[str] = mapped_column(
                    String(100), nullable=False, server_default="",
                )
                tokens_input: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                tokens_output: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                finish_reason: Mapped[str] = mapped_column(
                    String(30), nullable=False, server_default="",
                )
                latency_ms: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class UsageLogModel(Base):
                __tablename__ = "llm_usage_logs"
                __table_args__ = (
                    Index("ix_llm_usage_tenant", "tenant_id", "created_at"),
                    Index("ix_llm_usage_user", "user_id", "created_at"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                user_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                model_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                conversation_id: Mapped[uuid.UUID | None] = mapped_column(
                    UUID(as_uuid=True), nullable=True,
                )
                tokens_input: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                tokens_output: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                cost_usd: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                source: Mapped[str] = mapped_column(
                    String(50), nullable=False, server_default="chat",
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )
        ''')

    def _provider_repo_content(self) -> str:
        return dedent('''\
            """Provider repository — SQLAlchemy 2.0 async (2-branch)"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.llm.application.exceptions import ApplicationError
            from app.modules.llm.infrastructure.models import ProviderModel


            class ProviderRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(
                    self, ctx: object, provider_id: uuid.UUID,
                ) -> ProviderModel | None:
                    try:
                        result = await self._session.execute(
                            select(ProviderModel).where(
                                ProviderModel.id == provider_id,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"provider.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_all_active(
                    self, ctx: object,
                ) -> list[ProviderModel]:
                    try:
                        result = await self._session.execute(
                            select(ProviderModel)
                            .where(ProviderModel.is_active.is_(True))
                            .order_by(ProviderModel.priority.asc())
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"provider.find_all_active failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_type(
                    self, ctx: object, provider_type: str,
                ) -> list[ProviderModel]:
                    try:
                        result = await self._session.execute(
                            select(ProviderModel).where(
                                ProviderModel.provider_type == provider_type,
                                ProviderModel.is_active.is_(True),
                            )
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"provider.find_by_type failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(
                    self, ctx: object, provider: ProviderModel,
                ) -> ProviderModel:
                    try:
                        logger.info(f"Creating provider: {provider.name}")
                        self._session.add(provider)
                        await self._session.flush()
                        return provider
                    except SQLAlchemyError as exc:
                        logger.error(f"provider.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _model_repo_content(self) -> str:
        return dedent('''\
            """Model repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.llm.application.exceptions import ApplicationError
            from app.modules.llm.infrastructure.models import ModelModel


            class ModelRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(
                    self, ctx: object, model_id: uuid.UUID,
                ) -> ModelModel | None:
                    try:
                        result = await self._session.execute(
                            select(ModelModel).where(ModelModel.id == model_id)
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_name(
                    self, ctx: object, name: str,
                ) -> ModelModel | None:
                    try:
                        result = await self._session.execute(
                            select(ModelModel).where(
                                ModelModel.name == name,
                                ModelModel.is_active.is_(True),
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_by_name failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_all_active(
                    self, ctx: object,
                ) -> list[ModelModel]:
                    try:
                        result = await self._session.execute(
                            select(ModelModel).where(
                                ModelModel.is_active.is_(True),
                            )
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_all_active failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_provider(
                    self, ctx: object, provider_id: uuid.UUID,
                ) -> list[ModelModel]:
                    try:
                        result = await self._session.execute(
                            select(ModelModel).where(
                                ModelModel.provider_id == provider_id,
                                ModelModel.is_active.is_(True),
                            )
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_by_provider failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(
                    self, ctx: object, model: ModelModel,
                ) -> ModelModel:
                    try:
                        logger.info(f"Creating model: {model.name}")
                        self._session.add(model)
                        await self._session.flush()
                        return model
                    except SQLAlchemyError as exc:
                        logger.error(f"model.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _conversation_repo_content(self) -> str:
        return dedent('''\
            """Conversation repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.llm.application.exceptions import ApplicationError
            from app.modules.llm.infrastructure.models import ConversationModel


            class ConversationRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(
                    self, ctx: object, conv_id: uuid.UUID,
                ) -> ConversationModel | None:
                    try:
                        result = await self._session.execute(
                            select(ConversationModel).where(
                                ConversationModel.id == conv_id,
                                ConversationModel.status != "DELETED",
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"conv.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_user(
                    self, ctx: object, user_id: uuid.UUID, limit: int = 50,
                ) -> list[ConversationModel]:
                    try:
                        result = await self._session.execute(
                            select(ConversationModel)
                            .where(
                                ConversationModel.user_id == user_id,
                                ConversationModel.status != "DELETED",
                            )
                            .order_by(ConversationModel.created_at.desc())
                            .limit(limit)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"conv.find_by_user failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(
                    self, ctx: object, conv: ConversationModel,
                ) -> ConversationModel:
                    try:
                        self._session.add(conv)
                        await self._session.flush()
                        return conv
                    except SQLAlchemyError as exc:
                        logger.error(f"conv.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def update(
                    self, ctx: object, conv: ConversationModel,
                ) -> ConversationModel:
                    try:
                        await self._session.flush()
                        return conv
                    except SQLAlchemyError as exc:
                        logger.error(f"conv.update failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def soft_delete(
                    self, ctx: object, conv_id: uuid.UUID,
                ) -> bool:
                    try:
                        conv = await self.find_by_id(ctx, conv_id)
                        if conv:
                            conv.status = "DELETED"
                            await self._session.flush()
                            return True
                        return False
                    except SQLAlchemyError as exc:
                        logger.error(f"conv.soft_delete failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _message_repo_content(self) -> str:
        return dedent('''\
            """Message repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.llm.application.exceptions import ApplicationError
            from app.modules.llm.infrastructure.models import MessageModel


            class MessageRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(
                    self, ctx: object, msg: MessageModel,
                ) -> MessageModel:
                    try:
                        self._session.add(msg)
                        await self._session.flush()
                        return msg
                    except SQLAlchemyError as exc:
                        logger.error(f"msg.create failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_conversation(
                    self, ctx: object, conv_id: uuid.UUID, limit: int = 200,
                ) -> list[MessageModel]:
                    try:
                        result = await self._session.execute(
                            select(MessageModel)
                            .where(MessageModel.conversation_id == conv_id)
                            .order_by(MessageModel.created_at.asc())
                            .limit(limit)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"msg.find_by_conv failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def count_by_conversation(
                    self, ctx: object, conv_id: uuid.UUID,
                ) -> int:
                    try:
                        result = await self._session.execute(
                            select(func.count())
                            .select_from(MessageModel)
                            .where(MessageModel.conversation_id == conv_id)
                        )
                        return int(result.scalar() or 0)
                    except SQLAlchemyError as exc:
                        logger.error(f"msg.count failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _usage_log_repo_content(self) -> str:
        return dedent('''\
            """UsageLog repository"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from typing import Any

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.llm.application.exceptions import ApplicationError
            from app.modules.llm.infrastructure.models import UsageLogModel


            class UsageLogRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(
                    self, ctx: object, log: UsageLogModel,
                ) -> UsageLogModel:
                    try:
                        self._session.add(log)
                        await self._session.flush()
                        return log
                    except SQLAlchemyError as exc:
                        logger.error(f"usage.create failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def sum_by_tenant(
                    self, ctx: object, since: datetime,
                ) -> dict[str, Any]:
                    try:
                        result = await self._session.execute(
                            select(
                                func.coalesce(
                                    func.sum(UsageLogModel.tokens_input), 0,
                                ),
                                func.coalesce(
                                    func.sum(UsageLogModel.tokens_output), 0,
                                ),
                                func.coalesce(
                                    func.sum(UsageLogModel.cost_usd), 0,
                                ),
                                func.count(UsageLogModel.id),
                            ).where(UsageLogModel.created_at >= since)
                        )
                        row = result.one()
                        return {
                            "tokens_input": int(row[0]),
                            "tokens_output": int(row[1]),
                            "cost_usd": str(row[2]),
                            "requests": int(row[3]),
                        }
                    except SQLAlchemyError as exc:
                        logger.error(f"usage.sum_tenant failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def sum_by_user(
                    self, ctx: object,
                    user_id: uuid.UUID, since: datetime,
                ) -> dict[str, Any]:
                    try:
                        result = await self._session.execute(
                            select(
                                func.coalesce(
                                    func.sum(UsageLogModel.tokens_input), 0,
                                ),
                                func.coalesce(
                                    func.sum(UsageLogModel.tokens_output), 0,
                                ),
                                func.coalesce(
                                    func.sum(UsageLogModel.cost_usd), 0,
                                ),
                                func.count(UsageLogModel.id),
                            ).where(
                                UsageLogModel.user_id == user_id,
                                UsageLogModel.created_at >= since,
                            )
                        )
                        row = result.one()
                        return {
                            "tokens_input": int(row[0]),
                            "tokens_output": int(row[1]),
                            "cost_usd": str(row[2]),
                            "requests": int(row[3]),
                        }
                    except SQLAlchemyError as exc:
                        logger.error(f"usage.sum_user failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _caches_content(self) -> str:
        return dedent('''\
            """llm infrastructure cache — Redis (never-raise)"""
            from __future__ import annotations
            import json
            from typing import Any

            import structlog

            log = structlog.get_logger()


            class RedisLLMCache:
                """TH: cache ด้วย Redis | EN: Redis cache (never-raise)"""

                def __init__(self, redis: object, ttl: int = 3600) -> None:
                    self._redis = redis
                    self._ttl = ttl

                async def get(self, key: str) -> Any | None:
                    try:
                        raw = await self._redis.get(key)
                        return json.loads(raw) if raw else None
                    except Exception as e:
                        log.warning("cache.get_failed", key=key, err=str(e))
                        return None

                async def set(
                    self, key: str, value: Any, ttl: int | None = None,
                ) -> bool:
                    try:
                        await self._redis.set(
                            key, json.dumps(value, default=str),
                            ex=(ttl or self._ttl),
                        )
                        return True
                    except Exception as e:
                        log.warning("cache.set_failed", key=key, err=str(e))
                        return False

                async def invalidate(self, key: str) -> bool:
                    try:
                        await self._redis.delete(key)
                        return True
                    except Exception as e:
                        log.warning(
                            "cache.invalidate_failed", key=key, err=str(e),
                        )
                        return False
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """llm infrastructure services — Provider clients · EventBus · RateLimiter"""
            from __future__ import annotations

            import asyncio
            import uuid
            from typing import Any, AsyncIterator

            import structlog

            from app.modules.llm.application.interfaces import (
                LLMClient, ProviderRegistry,
            )
            from app.modules.llm.domain.exceptions import ProviderError
            from app.modules.llm.domain.value_objects import ChatOptions
            from app.modules.llm.infrastructure.models import ProviderModel

            log = structlog.get_logger()

            _RETRY_DELAYS = (1.0, 2.0, 4.0)


            async def _retry_async(coro_factory, retries: int = 3):
                last_exc: Exception | None = None
                for attempt in range(retries):
                    try:
                        return await coro_factory()
                    except ProviderError:
                        raise
                    except Exception as exc:
                        last_exc = exc
                        if attempt < retries - 1:
                            await asyncio.sleep(_RETRY_DELAYS[attempt])
                raise last_exc if last_exc else ProviderError("retry failed")


            class OpenAIClient:
                def __init__(self, api_key: str, base_url: str = "") -> None:
                    self._api_key = api_key
                    self._base_url = base_url

                async def chat_completion(
                    self, messages: list[dict[str, Any]],
                    model: str, options: ChatOptions,
                ) -> dict[str, Any]:
                    async def _call() -> dict[str, Any]:
                        from openai import AsyncOpenAI
                        client = AsyncOpenAI(
                            api_key=self._api_key,
                            base_url=self._base_url or None,
                        )
                        response = await client.chat.completions.create(
                            model=model, messages=messages,
                            temperature=options.temperature,
                            top_p=options.top_p,
                            max_tokens=options.max_tokens,
                            stream=False,
                        )
                        choice = response.choices[0]
                        u = response.usage
                        return {
                            "content": choice.message.content or "",
                            "finish_reason": choice.finish_reason or "stop",
                            "usage": {
                                "prompt_tokens": u.prompt_tokens if u else 0,
                                "completion_tokens": (
                                    u.completion_tokens if u else 0
                                ),
                                "total_tokens": u.total_tokens if u else 0,
                            },
                        }
                    try:
                        return await _retry_async(_call)
                    except Exception as e:
                        log.error("openai.chat_failed", err=str(e))
                        raise ProviderError(str(e)) from e

                async def stream_chat_completion(
                    self, messages: list[dict[str, Any]],
                    model: str, options: ChatOptions,
                ) -> AsyncIterator[dict[str, Any]]:
                    try:
                        from openai import AsyncOpenAI
                        client = AsyncOpenAI(
                            api_key=self._api_key,
                            base_url=self._base_url or None,
                        )
                        stream = await client.chat.completions.create(
                            model=model, messages=messages,
                            temperature=options.temperature,
                            top_p=options.top_p,
                            max_tokens=options.max_tokens,
                            stream=True,
                        )
                        async for chunk in stream:
                            if chunk.choices:
                                delta = chunk.choices[0].delta.content or ""
                                if delta:
                                    yield {"delta": delta}
                    except Exception as e:
                        log.error("openai.stream_failed", err=str(e))
                        raise ProviderError(str(e)) from e


            class AnthropicClient:
                def __init__(self, api_key: str, base_url: str = "") -> None:
                    self._api_key = api_key
                    self._base_url = base_url

                @staticmethod
                def _split_system(
                    messages: list[dict[str, Any]],
                ) -> tuple[str, list[dict[str, Any]]]:
                    system = ""
                    api_messages: list[dict[str, Any]] = []
                    for m in messages:
                        if m.get("role") == "system":
                            system = m.get("content", "")
                        else:
                            api_messages.append(m)
                    return system, api_messages

                async def chat_completion(
                    self, messages: list[dict[str, Any]],
                    model: str, options: ChatOptions,
                ) -> dict[str, Any]:
                    async def _call() -> dict[str, Any]:
                        from anthropic import AsyncAnthropic
                        client = AsyncAnthropic(
                            api_key=self._api_key,
                            base_url=self._base_url or None,
                        )
                        system, api_messages = self._split_system(messages)
                        response = await client.messages.create(
                            model=model, messages=api_messages,
                            system=system or None,
                            max_tokens=options.max_tokens,
                            temperature=options.temperature,
                        )
                        content = ""
                        for block in response.content:
                            if hasattr(block, "text"):
                                content += block.text
                        return {
                            "content": content,
                            "finish_reason": response.stop_reason or "stop",
                            "usage": {
                                "prompt_tokens": response.usage.input_tokens,
                                "completion_tokens": response.usage.output_tokens,
                                "total_tokens": (
                                    response.usage.input_tokens
                                    + response.usage.output_tokens
                                ),
                            },
                        }
                    try:
                        return await _retry_async(_call)
                    except Exception as e:
                        log.error("anthropic.chat_failed", err=str(e))
                        raise ProviderError(str(e)) from e

                async def stream_chat_completion(
                    self, messages: list[dict[str, Any]],
                    model: str, options: ChatOptions,
                ) -> AsyncIterator[dict[str, Any]]:
                    try:
                        from anthropic import AsyncAnthropic
                        client = AsyncAnthropic(
                            api_key=self._api_key,
                            base_url=self._base_url or None,
                        )
                        system, api_messages = self._split_system(messages)
                        async with client.messages.stream(
                            model=model, messages=api_messages,
                            system=system or None,
                            max_tokens=options.max_tokens,
                        ) as stream:
                            async for text in stream.text_stream:
                                if text:
                                    yield {"delta": text}
                    except Exception as e:
                        log.error("anthropic.stream_failed", err=str(e))
                        raise ProviderError(str(e)) from e


            class DefaultProviderRegistry:
                def __init__(self, secrets_provider: Any = None) -> None:
                    self._secrets = secrets_provider

                def get_client(self, provider: ProviderModel) -> LLMClient:
                    api_key = self._resolve_key(provider)
                    if provider.provider_type == "openai":
                        return OpenAIClient(api_key, provider.base_url)
                    if provider.provider_type == "anthropic":
                        return AnthropicClient(api_key, provider.base_url)
                    return OpenAIClient(api_key, provider.base_url)

                def select_provider(
                    self, model_name: str, providers: list[ProviderModel],
                ) -> ProviderModel:
                    if not providers:
                        raise ProviderError("no providers available")
                    return sorted(providers, key=lambda p: p.priority)[0]

                def _resolve_key(self, provider: ProviderModel) -> str:
                    if self._secrets:
                        try:
                            return self._secrets.decrypt(
                                provider.api_key_encrypted,
                            )
                        except Exception:
                            pass
                    return provider.api_key_encrypted or ""


            class RedisRateLimiter:
                def __init__(
                    self, redis: object,
                    tenant_limit: int = 10_000_000,
                    user_limit: int = 1_000_000,
                ) -> None:
                    self._redis = redis
                    self._tenant_limit = tenant_limit
                    self._user_limit = user_limit

                async def check(
                    self, tenant_id: uuid.UUID,
                    user_id: uuid.UUID, cost: int,
                ) -> bool:
                    try:
                        t_key = f"llm:rate:tenant:{tenant_id}"
                        u_key = f"llm:rate:user:{user_id}"
                        t_val = await self._redis.get(t_key) or 0
                        u_val = await self._redis.get(u_key) or 0
                        return (
                            int(t_val) + cost <= self._tenant_limit
                            and int(u_val) + cost <= self._user_limit
                        )
                    except Exception as e:
                        log.warning("ratelimit.check_failed", err=str(e))
                        return True

                async def increment(
                    self, tenant_id: uuid.UUID,
                    user_id: uuid.UUID, cost: int,
                ) -> None:
                    try:
                        t_key = f"llm:rate:tenant:{tenant_id}"
                        u_key = f"llm:rate:user:{user_id}"
                        pipe = self._redis.pipeline()
                        pipe.incrby(t_key, cost)
                        pipe.expire(t_key, 86400)
                        pipe.incrby(u_key, cost)
                        pipe.expire(u_key, 86400)
                        await pipe.execute()
                    except Exception as e:
                        log.warning("ratelimit.increment_failed", err=str(e))


            class KafkaEventBus:
                def __init__(
                    self, producer: object, topic: str = "llm.events",
                ) -> None:
                    self._producer = producer
                    self._topic = topic

                async def publish(self, event: object) -> None:
                    try:
                        payload = {
                            "type": type(event).__name__,
                            "data": {k: str(v) for k, v in vars(event).items()},
                        }
                        await self._producer.send_and_wait(self._topic, payload)
                        log.info("event.published", type=type(event).__name__)
                    except Exception as e:
                        log.warning("event.publish_failed", err=str(e))


            class NoopEventBus:
                async def publish(self, event: object) -> None:
                    log.debug("event.noop", type=type(event).__name__)
        ''')

    # ─── PRESENTATION LAYER ─────────────────────────────────────
    def _create_presentation(self) -> None:
        base = f"{self.mod_root}/presentation"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """llm presentation layer"""
        '''))

        self.writer.write(f"{base}/schemas.py", self._schemas_content())
        self.writer.write(f"{base}/docs.py", self._docs_content())
        self.writer.write(f"{base}/sse.py", self._sse_content())
        self.writer.write(f"{base}/dependencies.py", self._dependencies_content())
        self.writer.write(f"{base}/router.py", self._router_content())
        self.writer.write(f"{base}/swagger.py", self._swagger_content())

    def _schemas_content(self) -> str:
        return dedent('''\
            """llm Pydantic v2 schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class ChatRequest(BaseModel):
                conversation_id: str | None = None
                model: str = Field(..., min_length=1, max_length=100)
                message: str = Field(..., min_length=1, max_length=100000)
                system_prompt: str = ""
                temperature: float = Field(default=0.7, ge=0.0, le=2.0)
                top_p: float = Field(default=1.0, ge=0.0, le=1.0)
                max_tokens: int = Field(default=1024, ge=1, le=128000)
                stream: bool = False
                model_config = ConfigDict(extra="forbid")


            class ChatResponse(BaseModel):
                conversation_id: str
                model: str
                content: str
                finish_reason: str = "stop"
                usage: dict[str, Any] = Field(default_factory=dict)
                latency_ms: int = 0
                model_config = ConfigDict(extra="forbid")


            class CompletionRequest(BaseModel):
                model: str = Field(..., min_length=1, max_length=100)
                prompt: str = Field(..., min_length=1, max_length=100000)
                temperature: float = Field(default=0.7, ge=0.0, le=2.0)
                max_tokens: int = Field(default=1024, ge=1, le=128000)
                model_config = ConfigDict(extra="forbid")


            class ConversationCreateRequest(BaseModel):
                model: str = Field(..., min_length=1, max_length=100)
                title: str = ""
                model_config = ConfigDict(extra="forbid")


            class ConversationResponse(BaseModel):
                id: str
                title: str = ""
                model_id: str = ""
                status: str = "ACTIVE"
                message_count: int = 0
                total_tokens: int = 0
                model_config = ConfigDict(extra="forbid")


            class ConversationDetailResponse(BaseModel):
                id: str
                title: str
                status: str
                model_id: str
                messages: list[dict[str, Any]] = Field(default_factory=list)
                model_config = ConfigDict(extra="forbid")


            class ProviderResponse(BaseModel):
                id: str
                name: str
                provider_type: str
                base_url: str = ""
                is_active: bool = True
                priority: int = 100
                model_config = ConfigDict(extra="forbid")


            class ModelResponse(BaseModel):
                id: str
                name: str
                display_name: str = ""
                context_window: int = 4096
                max_output_tokens: int = 4096
                supports_streaming: bool = True
                supports_tools: bool = False
                model_config = ConfigDict(extra="forbid")


            class UsageResponse(BaseModel):
                tenant: dict[str, Any]
                user: dict[str, Any]
                since: str
                model_config = ConfigDict(extra="forbid")
        ''')

    def _docs_content(self) -> str:
        return dedent('''\
            """llm OpenAPI metadata — response examples"""
            from __future__ import annotations

            RESPONSE_CHAT_200 = {
                "description": "Chat completion",
                "content": {"application/json": {"example": {
                    "conversation_id": "uuid",
                    "model": "gpt-4o-mini",
                    "content": "Hello!",
                    "finish_reason": "stop",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                    },
                    "latency_ms": 850,
                }}},
            }
            RESPONSE_ERROR_400 = {
                "description": "Domain error",
                "content": {"application/json": {"example": {
                    "detail": "model not found", "code": "DOMAIN_ERROR",
                }}},
            }
            RESPONSE_ERROR_402 = {
                "description": "Token limit exceeded",
                "content": {"application/json": {"example": {
                    "detail": "token limit exceeded",
                    "code": "LIMIT_EXCEEDED",
                }}},
            }
            RESPONSE_ERROR_404 = {
                "description": "Not found",
                "content": {"application/json": {"example": {
                    "detail": "conversation not found",
                    "code": "NOT_FOUND",
                }}},
            }
            RESPONSE_ERROR_429 = {
                "description": "Rate limit exceeded",
                "content": {"application/json": {"example": {
                    "detail": "rate limit exceeded",
                    "code": "RATE_LIMITED",
                }}},
            }
            RESPONSE_ERROR_502 = {
                "description": "Provider error",
                "content": {"application/json": {"example": {
                    "detail": "openai API error",
                    "code": "PROVIDER_ERROR",
                }}},
            }
        ''')

    def _sse_content(self) -> str:
        return dedent('''\
            """llm SSE helper — Server-Sent Events streaming"""
            from __future__ import annotations
            import json
            from typing import AsyncIterator

            from fastapi.responses import StreamingResponse


            def sse_response(stream: AsyncIterator[dict]) -> StreamingResponse:
                """TH: SSE response | EN: SSE streaming response"""

                async def event_gen() -> AsyncIterator[str]:
                    try:
                        async for chunk in stream:
                            yield (
                                f"data: {json.dumps(chunk, default=str)}\\n\\n"
                            )
                        yield "data: [DONE]\\n\\n"
                    except Exception as e:
                        error = json.dumps({"error": str(e)})
                        yield f"data: {error}\\n\\n"
                        yield "data: [DONE]\\n\\n"

                return StreamingResponse(
                    event_gen(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "X-Accel-Buffering": "no",
                    },
                )
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """llm DI container"""
            from __future__ import annotations
            from typing import Annotated, Any

            from fastapi import Depends
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.core.db import get_session
            from app.modules.llm.application.use_case import LLMUseCase
            from app.modules.llm.infrastructure.caches import RedisLLMCache
            from app.modules.llm.infrastructure.conversation_repository import (
                ConversationRepository,
            )
            from app.modules.llm.infrastructure.message_repository import (
                MessageRepository,
            )
            from app.modules.llm.infrastructure.model_repository import (
                ModelRepository,
            )
            from app.modules.llm.infrastructure.provider_repository import (
                ProviderRepository,
            )
            from app.modules.llm.infrastructure.services import (
                DefaultProviderRegistry, NoopEventBus, RedisRateLimiter,
            )
            from app.modules.llm.infrastructure.usage_log_repository import (
                UsageLogRepository,
            )

            _registry: DefaultProviderRegistry | None = None


            def _get_registry() -> DefaultProviderRegistry:
                global _registry
                if _registry is None:
                    _registry = DefaultProviderRegistry()
                return _registry


            async def _get_redis() -> Any:
                try:
                    from app.core.redis import get_redis
                    return await get_redis()
                except Exception:
                    return None


            async def _get_event_bus() -> Any:
                try:
                    from app.core.events import get_event_bus
                    return await get_event_bus()
                except Exception:
                    return NoopEventBus()


            async def _get_idempotency() -> Any:
                try:
                    from app.core.idempotency import get_idempotency_store
                    return await get_idempotency_store()
                except Exception:
                    return _NoopIdempotency()


            async def get_llm_use_case(
                session: Annotated[AsyncSession, Depends(get_session)],
            ) -> LLMUseCase:
                redis = await _get_redis()
                bus = await _get_event_bus()
                idem = await _get_idempotency()
                rate_limiter = (
                    RedisRateLimiter(redis) if redis else _NoopRateLimiter()
                )
                cache = RedisLLMCache(redis) if redis else _NoopCache()
                return LLMUseCase(
                    provider_repo=ProviderRepository(session),
                    model_repo=ModelRepository(session),
                    conversation_repo=ConversationRepository(session),
                    message_repo=MessageRepository(session),
                    usage_repo=UsageLogRepository(session),
                    registry=_get_registry(),
                    rate_limiter=rate_limiter,
                    cache=cache,
                    event_bus=bus,
                    idempotency=idem,
                )


            class _NoopCache:
                async def get(self, key: str) -> Any | None:
                    return None

                async def set(
                    self, key: str, value: Any, ttl: int = 3600,
                ) -> bool:
                    return False

                async def invalidate(self, key: str) -> bool:
                    return False


            class _NoopRateLimiter:
                async def check(
                    self, tenant_id: Any, user_id: Any, cost: int,
                ) -> bool:
                    return True

                async def increment(
                    self, tenant_id: Any, user_id: Any, cost: int,
                ) -> None:
                    return None


            class _NoopIdempotency:
                async def check_or_lock(
                    self, key: str, scope: str, payload: dict,
                ) -> dict | None:
                    return None

                async def complete(
                    self, key: str, scope: str,
                    status: int, body: dict,
                ) -> None:
                    return None
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """llm HTTP routers"""
            from __future__ import annotations
            import uuid
            from typing import Annotated, Any

            from fastapi import APIRouter, Depends, Header, HTTPException, status

            from app.modules.llm.application.use_case import LLMUseCase
            from app.modules.llm.domain.exceptions import (
                ConversationNotFoundError, LLMError,
                ModelNotFoundError, RateLimitExceededError,
            )
            from app.modules.llm.domain.value_objects import ChatOptions
            from app.modules.llm.presentation.dependencies import get_llm_use_case
            from app.modules.llm.presentation.docs import (
                RESPONSE_CHAT_200, RESPONSE_ERROR_400, RESPONSE_ERROR_402,
                RESPONSE_ERROR_404, RESPONSE_ERROR_429, RESPONSE_ERROR_502,
            )
            from app.modules.llm.presentation.schemas import (
                ChatRequest, ChatResponse, CompletionRequest,
                ConversationCreateRequest, ConversationDetailResponse,
                ConversationResponse, ModelResponse, ProviderResponse,
                UsageResponse,
            )
            from app.modules.llm.presentation.sse import sse_response

            router = APIRouter(prefix="/llm", tags=["LLM"])


            def _error_status(exc: Exception) -> int:
                if isinstance(exc, ModelNotFoundError):
                    return status.HTTP_404_NOT_FOUND
                if isinstance(exc, ConversationNotFoundError):
                    return status.HTTP_404_NOT_FOUND
                if isinstance(exc, RateLimitExceededError):
                    return status.HTTP_429_TOO_MANY_REQUESTS
                return status.HTTP_400_BAD_REQUEST


            class _CtxStub:
                def __init__(
                    self, tenant_id: uuid.UUID, user_id: uuid.UUID,
                ) -> None:
                    self.tenant_id = tenant_id
                    self.user_id = user_id


            async def _get_ctx() -> Any:
                try:
                    from app.core.context import get_context
                    return await get_context()
                except Exception:
                    return _CtxStub(
                        tenant_id=uuid.UUID(int=1),
                        user_id=uuid.UUID(int=2),
                    )


            @router.post(
                "/chat",
                response_model=ChatResponse,
                summary="Chat completion (sync)",
                operation_id="llm_chat",
                responses={
                    200: RESPONSE_CHAT_200,
                    400: RESPONSE_ERROR_400,
                    402: RESPONSE_ERROR_402,
                    404: RESPONSE_ERROR_404,
                    429: RESPONSE_ERROR_429,
                    502: RESPONSE_ERROR_502,
                },
            )
            async def chat(
                payload: ChatRequest,
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
                idem_key: Annotated[
                    str, Header(alias="Idempotency-Key", min_length=8),
                ] = "",
            ) -> ChatResponse:
                """TH: chat completion | EN: chat completion"""
                ctx = await _get_ctx()
                try:
                    options = ChatOptions(
                        temperature=payload.temperature,
                        top_p=payload.top_p,
                        max_tokens=payload.max_tokens,
                    )
                    conv_id = (
                        uuid.UUID(payload.conversation_id)
                        if payload.conversation_id else None
                    )
                    result = await uc.chat(
                        ctx=ctx, conversation_id=conv_id,
                        model_name=payload.model,
                        user_message=payload.message,
                        options=options,
                        system_prompt=payload.system_prompt,
                        idempotency_key=idem_key,
                    )
                    return ChatResponse(**result)
                except LLMError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            @router.post(
                "/chat/stream",
                summary="Chat completion (SSE stream)",
                operation_id="llm_chat_stream",
            )
            async def chat_stream(
                payload: ChatRequest,
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
            ) -> Any:
                """TH: chat streaming | EN: chat streaming (SSE)"""
                ctx = await _get_ctx()
                options = ChatOptions(
                    temperature=payload.temperature,
                    top_p=payload.top_p,
                    max_tokens=payload.max_tokens,
                    stream=True,
                )
                conv_id = (
                    uuid.UUID(payload.conversation_id)
                    if payload.conversation_id else None
                )
                stream = uc.chat_stream(
                    ctx=ctx, conversation_id=conv_id,
                    model_name=payload.model,
                    user_message=payload.message,
                    options=options,
                    system_prompt=payload.system_prompt,
                )
                return sse_response(stream)


            @router.post(
                "/completions",
                response_model=ChatResponse,
                summary="Raw completion",
                operation_id="llm_completion",
            )
            async def completions(
                payload: CompletionRequest,
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
            ) -> ChatResponse:
                """TH: raw completion | EN: raw completion"""
                ctx = await _get_ctx()
                options = ChatOptions(
                    temperature=payload.temperature,
                    max_tokens=payload.max_tokens,
                )
                try:
                    result = await uc.chat(
                        ctx=ctx, conversation_id=None,
                        model_name=payload.model,
                        user_message=payload.prompt,
                        options=options,
                    )
                    return ChatResponse(**result)
                except LLMError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            @router.get(
                "/conversations",
                response_model=list[ConversationResponse],
                summary="List conversations",
                operation_id="llm_list_conversations",
            )
            async def list_conversations(
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
                limit: int = 50,
            ) -> list[ConversationResponse]:
                ctx = await _get_ctx()
                rows = await uc.list_conversations(ctx, limit)
                return [ConversationResponse(**r) for r in rows]


            @router.post(
                "/conversations",
                response_model=ConversationResponse,
                status_code=status.HTTP_201_CREATED,
                summary="Create conversation",
                operation_id="llm_create_conversation",
            )
            async def create_conversation(
                payload: ConversationCreateRequest,
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
            ) -> ConversationResponse:
                ctx = await _get_ctx()
                try:
                    result = await uc.create_conversation(
                        ctx, payload.model, payload.title,
                    )
                    return ConversationResponse(**result)
                except LLMError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            @router.get(
                "/conversations/{conversation_id}",
                response_model=ConversationDetailResponse,
                summary="Get conversation",
                operation_id="llm_get_conversation",
            )
            async def get_conversation(
                conversation_id: uuid.UUID,
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
            ) -> ConversationDetailResponse:
                ctx = await _get_ctx()
                try:
                    result = await uc.get_conversation(ctx, conversation_id)
                    return ConversationDetailResponse(**result)
                except LLMError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            @router.get(
                "/providers",
                response_model=list[ProviderResponse],
                summary="List providers",
                operation_id="llm_list_providers",
            )
            async def list_providers(
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
            ) -> list[ProviderResponse]:
                ctx = await _get_ctx()
                rows = await uc.list_providers(ctx)
                return [ProviderResponse(**r) for r in rows]


            @router.get(
                "/models",
                response_model=list[ModelResponse],
                summary="List models",
                operation_id="llm_list_models",
            )
            async def list_models(
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
            ) -> list[ModelResponse]:
                ctx = await _get_ctx()
                rows = await uc.list_models(ctx)
                return [ModelResponse(**r) for r in rows]


            @router.get(
                "/usage",
                response_model=UsageResponse,
                summary="Usage stats (tenant + user)",
                operation_id="llm_usage",
            )
            async def get_usage(
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
                days: int = 30,
            ) -> UsageResponse:
                ctx = await _get_ctx()
                result = await uc.get_usage(ctx, days)
                return UsageResponse(**result)


            @router.get(
                "/usage/me",
                response_model=UsageResponse,
                summary="Usage stats (user)",
                operation_id="llm_usage_me",
            )
            async def get_usage_me(
                uc: Annotated[LLMUseCase, Depends(get_llm_use_case)],
                days: int = 30,
            ) -> UsageResponse:
                ctx = await _get_ctx()
                result = await uc.get_usage(ctx, days)
                return UsageResponse(**result)
        ''')

    def _swagger_content(self) -> str:
        return dedent('''\
            """OpenAPI docs — llm module

            TH: register OpenAPI metadata (tag, externalDocs, x-*)
            EN: register OpenAPI metadata
            """
            from __future__ import annotations
            from typing import Any


            def register_llm_openapi(app: object) -> None:
                """TH: register OpenAPI metadata | EN: register OpenAPI metadata"""
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "LLM" for t in tags):
                        tags.append({
                            "name": "LLM",
                            "description": (
                                "โมดูล llm — Unified LLM Gateway\\n\\n"
                                "• Multi-provider (OpenAI / Anthropic / Local)\\n"
                                "• Chat completion (sync + SSE streaming)\\n"
                                "• Conversation management\\n"
                                "• Token tracking + Cost (Decimal)\\n"
                                "• Rate limiting + Caching + Failover"
                            ),
                            "externalDocs": {
                                "description": "llm Module README",
                                "url": "/docs/README_llm.md",
                            },
                        })
                    info = schema.setdefault("info", {})
                    info.setdefault("x-module", "llm")
                    info.setdefault("x-layer", "5-Intel")
                    info.setdefault("x-prefix", "llm")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent('''\
            """llm module — โมดูล llm"""
            from .presentation.router import router as llm_router

            __all__ = ["llm_router"]
        '''))

    # ═══════════════════════════════════════════════════════════
    #  2. ACTIVATE
    # ═══════════════════════════════════════════════════════════
    def activate_module(self) -> None:
        info("[2/10] ACTIVATE — register router + swagger + models")
        self._update_app_py()
        self._update_env_py()

    # ═══════════════════════════════════════════════════════════
    #  4. UPDATE APP  ★★★ v1.3 — FIXED SWAGGER ★★★
    # ═══════════════════════════════════════════════════════════
    def update_app(self) -> None:
        info("[4/10] UPDATE APP — app/app.py")
        self._update_app_py()

    def _update_app_py(self) -> None:
        app_file = self.root / self.app_py
        if not app_file.exists():
            warn(f"{self.app_py} not found — skipping")
            return

        content = app_file.read_text(encoding="utf-8")
        original = content

        # ─── 1) Import router ────────────────────────
        router_import = (
            "from app.modules.llm.presentation.router "
            "import router as llm_router"
        )
        if router_import not in content:
            lines = content.split("\n")
            insert_at = None
            for i, line in enumerate(lines):
                if (
                    "from app.modules.health.presentation" in line
                    or "from app.modules.iot.presentation" in line
                    or "from app.modules.pdpa.presentation" in line
                ):
                    insert_at = i + 1
            if insert_at is None:
                last = 0
                for i, line in enumerate(lines):
                    if line.startswith("from ") or line.startswith("import "):
                        last = i
                insert_at = last + 1
            lines.insert(insert_at, router_import)
            content = "\n".join(lines)
            ok(f"added import: {router_import}")

        # ─── 2) Import swagger register ──────────────
        swagger_import = (
            "from app.modules.llm.presentation.swagger "
            "import register_llm_openapi"
        )
        if swagger_import not in content:
            if router_import in content:
                content = content.replace(
                    router_import,
                    router_import + "\n" + swagger_import,
                    1,
                )
            else:
                lines = content.split("\n")
                last = 0
                for i, line in enumerate(lines):
                    if line.startswith("from ") or line.startswith("import "):
                        last = i
                lines.insert(last + 1, swagger_import)
                content = "\n".join(lines)
            ok(f"added import: {swagger_import}")

        # ─── 3) Add llm_router to routers list ───────
        m = re.search(r"(routers\s*=\s*\[)(.*?)(\n\])", content, re.S)
        if m:
            inner = m.group(2)
            if "llm_router" not in inner:
                anchor = None
                for cand in (
                    "iot_router,", "pdpa_router,", "health_router,",
                ):
                    if cand in inner:
                        anchor = cand
                        break
                if anchor:
                    inner_new = inner.replace(
                        anchor,
                        f"{anchor}\n    llm_router,    "
                        f"# llm module (Layer 5-Intel)",
                        1,
                    )
                else:
                    inner_new = (
                        inner.rstrip()
                        + "\n    llm_router,    # llm module\n"
                    )
                content = (
                    content[:m.start(2)] + inner_new + content[m.end(2):]
                )
                ok("added llm_router to routers list")

        # ─── 4) Add OpenAPI tag ──────────────────────
        if '"name": "LLM"' not in content:
            tag_line = (
                '            {"name": "LLM", "description": '
                '"LLM Module — Unified LLM Gateway '
                '(OpenAI / Anthropic / Local)."},\n'
            )
            m = re.search(
                r'(\{"name":\s*"(?:Health|iot|IOT|PDPA|pdpa)"[^\}]*\},\s*\n)',
                content,
            )
            if m:
                content = content[:m.end(1)] + tag_line + content[m.end(1):]
                ok("added OpenAPI tag: LLM")
            else:
                warn("Anchor tag not found — skip OpenAPI tag")

        # ═══ 5) ★★★ REGISTER SWAGGER HOOK ★★★ ═══════
        if "register_llm_openapi(app)" not in content:
            # หา include_router(llm_router...) ก่อน
            include_match = re.search(
                r"(app\.include_router\(llm_router[^\n]*\n)",
                content,
            )
            swagger_call = (
                "\n# TH: Register LLM OpenAPI metadata "
                "(x-module, x-layer, externalDocs)\n"
                "# EN: Register LLM OpenAPI metadata\n"
                "register_llm_openapi(app)\n"
            )
            if include_match:
                insert_at = include_match.end(1)
                content = (
                    content[:insert_at] + swagger_call + content[insert_at:]
                )
                ok("called register_llm_openapi(app) (after include_router)")
            else:
                # fallback: หลัง app = FastAPI(...)
                m2 = re.search(
                    r"(app\s*=\s*FastAPI\([^)]*\)\s*\n)", content,
                )
                if m2:
                    insert_at = m2.end(1)
                    content = (
                        content[:insert_at]
                        + "\n# Register LLM OpenAPI metadata\n"
                        + "register_llm_openapi(app)\n"
                        + content[insert_at:]
                    )
                    ok("called register_llm_openapi(app) (after FastAPI init)")
                else:
                    content = (
                        content.rstrip()
                        + "\n\n# Register LLM OpenAPI metadata\n"
                        + "register_llm_openapi(app)\n"
                    )
                    ok("called register_llm_openapi(app) (end of file)")

        # ─── 6) Save ─────────────────────────────────
        if content != original:
            bak = app_file.with_suffix(".py.bak")
            bak.write_bytes(app_file.read_bytes())
            ok(f"backup: {self.app_py}.bak")
            app_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.app_py} updated")
        else:
            skip(f"{self.app_py} unchanged")

    # ═══════════════════════════════════════════════════════════
    #  5. UPDATE ENV
    # ═══════════════════════════════════════════════════════════
    def update_env(self) -> None:
        info("[5/10] UPDATE ENV — migrations/env.py")
        self._update_env_py()

    def _update_env_py(self) -> None:
        env_file = self.root / self.env_py
        if not env_file.exists():
            warn(f"{self.env_py} not found — skipping")
            return

        content = env_file.read_text(encoding="utf-8")
        original = content

        marker = (
            "# --- module llm "
            "(Provider / Model / Conversation / Message / UsageLog) ---"
        )
        if marker in content:
            skip("llm models block already present in env.py")
            return

        llm_block = f'''{marker}
# TH: llm module — 5 models (Layer 5-Intel, schema=public, prefix=llm_)
# EN: llm module — 5 models (Layer 5-Intel, schema=public, prefix=llm_)
try:
    from app.modules.llm.infrastructure.models import (  # noqa: F401
        ConversationModel,
        MessageModel,
        ModelModel,
        ProviderModel,
        UsageLogModel,
    )
except ImportError:
    pass


'''

        pattern = re.compile(
            r"(# --- module (?:iot|pdpa).*?except ImportError:\s*\n\s*pass\s*\n)",
            re.S,
        )
        m = pattern.search(content)
        if m:
            insert_at = m.end(1)
            content = (
                content[:insert_at] + "\n" + llm_block + content[insert_at:]
            )
        else:
            anchor = "config = context.config"
            idx = content.find(anchor)
            if idx == -1:
                warn("Cannot find anchor in env.py — skipping")
                return
            content = content[:idx] + llm_block + content[idx:]

        if content != original:
            bak = env_file.with_suffix(".py.bak")
            bak.write_bytes(env_file.read_bytes())
            ok(f"backup: {self.env_py}.bak")
            env_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.env_py} updated — registered llm models")
        else:
            skip(f"{self.env_py} unchanged")

    # ═══════════════════════════════════════════════════════════
    #  3. SQL
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info(f"[3/10] SQL — {self.module} (v1.2: public + llm_)")
        self.writer.write(
            f"{self.sql_dir}/V001__create_{self.module}.sql",
            self._v001_sql(),
        )
        self.writer.write(
            f"{self.sql_dir}/V002__seed_{self.module}.sql",
            self._v002_sql(),
        )
        self.writer.write(
            f"{self.sql_dir}/V003__rollback_{self.module}.sql",
            self._v003_sql(),
        )

    def _v001_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V001__create_llm.sql | Module: llm | Prefix: llm
-- Schema: public | Tables: llm_providers, llm_models, llm_conversations,
--                          llm_messages, llm_usage_logs
-- ═══════════════════════════════════════════════════════════════
BEGIN;

-- ─── llm_providers ──────────────────────────────
DROP TABLE IF EXISTS "public"."llm_providers";
CREATE TABLE "public"."llm_providers" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"          uuid NOT NULL,
  "name"               varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "provider_type"      varchar(50)  COLLATE "pg_catalog"."default" NOT NULL,
  "api_key_encrypted"  text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "base_url"           varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "timeout_seconds"    int4 NOT NULL DEFAULT 60,
  "priority"           int4 NOT NULL DEFAULT 100,
  "is_active"          bool NOT NULL DEFAULT true,
  "config_json"        text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"         timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "llm_providers_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_llm_provider_type" CHECK (
    provider_type IN ('openai','anthropic','local','azure')
  ),
  CONSTRAINT "uq_llm_provider_name" UNIQUE ("tenant_id", "name")
);

CREATE INDEX "ix_llm_provider_tenant"
    ON "public"."llm_providers" USING btree ("tenant_id");
CREATE INDEX "ix_llm_provider_type"
    ON "public"."llm_providers" USING btree ("provider_type", "is_active");

-- ─── llm_models ─────────────────────────────────
DROP TABLE IF EXISTS "public"."llm_models";
CREATE TABLE "public"."llm_models" (
  "id"                   uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"            uuid NOT NULL,
  "provider_id"          uuid NOT NULL,
  "name"                 varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "display_name"         varchar(200) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "context_window"       int4 NOT NULL DEFAULT 4096,
  "max_output_tokens"    int4 NOT NULL DEFAULT 4096,
  "cost_per_1k_input"    numeric(12,8) NOT NULL DEFAULT 0,
  "cost_per_1k_output"   numeric(12,8) NOT NULL DEFAULT 0,
  "supports_streaming"   bool NOT NULL DEFAULT true,
  "supports_tools"       bool NOT NULL DEFAULT false,
  "is_active"            bool NOT NULL DEFAULT true,
  "created_at"           timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"           timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "llm_models_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_llm_model_name" UNIQUE ("tenant_id", "name")
);

CREATE INDEX "ix_llm_model_tenant"
    ON "public"."llm_models" USING btree ("tenant_id");
CREATE INDEX "ix_llm_model_provider"
    ON "public"."llm_models" USING btree ("provider_id", "is_active");

-- ─── llm_conversations ──────────────────────────
DROP TABLE IF EXISTS "public"."llm_conversations";
CREATE TABLE "public"."llm_conversations" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "user_id"        uuid NOT NULL,
  "title"          varchar(500) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "model_id"       uuid NOT NULL,
  "system_prompt"  text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "metadata_json"  text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '{}'::text,
  "status"         varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'ACTIVE'::character varying,
  "message_count"  int4 NOT NULL DEFAULT 0,
  "total_tokens"   int4 NOT NULL DEFAULT 0,
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "llm_conversations_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_llm_conv_status" CHECK (
    status IN ('ACTIVE','ARCHIVED','DELETED')
  )
);

CREATE INDEX "ix_llm_conv_tenant"
    ON "public"."llm_conversations" USING btree ("tenant_id");
CREATE INDEX "ix_llm_conv_user"
    ON "public"."llm_conversations" USING btree ("user_id", "created_at" DESC);

-- ─── llm_messages ───────────────────────────────
DROP TABLE IF EXISTS "public"."llm_messages";
CREATE TABLE "public"."llm_messages" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "conversation_id"  uuid NOT NULL,
  "role"             varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "content"          text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "tool_calls_json"  text COLLATE "pg_catalog"."default" NOT NULL DEFAULT '[]'::text,
  "tool_call_id"     varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "tokens_input"     int4 NOT NULL DEFAULT 0,
  "tokens_output"    int4 NOT NULL DEFAULT 0,
  "finish_reason"    varchar(30) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "latency_ms"       int4 NOT NULL DEFAULT 0,
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "llm_messages_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_llm_msg_role" CHECK (
    role IN ('system','user','assistant','tool')
  )
);

CREATE INDEX "ix_llm_msg_conv"
    ON "public"."llm_messages" USING btree ("conversation_id", "created_at");

-- ─── llm_usage_logs ─────────────────────────────
DROP TABLE IF EXISTS "public"."llm_usage_logs";
CREATE TABLE "public"."llm_usage_logs" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "user_id"          uuid NOT NULL,
  "model_id"         uuid NOT NULL,
  "conversation_id"  uuid NULL,
  "tokens_input"     int4 NOT NULL DEFAULT 0,
  "tokens_output"    int4 NOT NULL DEFAULT 0,
  "cost_usd"         numeric(12,8) NOT NULL DEFAULT 0,
  "source"           varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'chat'::character varying,
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "llm_usage_logs_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "ix_llm_usage_tenant"
    ON "public"."llm_usage_logs" USING btree ("tenant_id", "created_at" DESC);
CREATE INDEX "ix_llm_usage_user"
    ON "public"."llm_usage_logs" USING btree ("user_id", "created_at" DESC);

-- ─── Trigger fn ─────────────────────────────────
CREATE OR REPLACE FUNCTION public.set_updated_at_llm()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_llm_provider_updated ON "public"."llm_providers";
CREATE TRIGGER trg_llm_provider_updated BEFORE UPDATE
    ON "public"."llm_providers"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_llm();

DROP TRIGGER IF EXISTS trg_llm_model_updated ON "public"."llm_models";
CREATE TRIGGER trg_llm_model_updated BEFORE UPDATE
    ON "public"."llm_models"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_llm();

DROP TRIGGER IF EXISTS trg_llm_conv_updated ON "public"."llm_conversations";
CREATE TRIGGER trg_llm_conv_updated BEFORE UPDATE
    ON "public"."llm_conversations"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_llm();

DROP TRIGGER IF EXISTS trg_llm_msg_updated ON "public"."llm_messages";
CREATE TRIGGER trg_llm_msg_updated BEFORE UPDATE
    ON "public"."llm_messages"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_llm();

DROP TRIGGER IF EXISTS trg_llm_usage_updated ON "public"."llm_usage_logs";
CREATE TRIGGER trg_llm_usage_updated BEFORE UPDATE
    ON "public"."llm_usage_logs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_llm();

-- ─── RLS ────────────────────────────────────────
ALTER TABLE "public"."llm_providers"     ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."llm_models"        ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."llm_conversations" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."llm_messages"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."llm_usage_logs"    ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_llm_provider ON "public"."llm_providers";
CREATE POLICY p_llm_provider ON "public"."llm_providers"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_llm_model ON "public"."llm_models";
CREATE POLICY p_llm_model ON "public"."llm_models"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_llm_conv ON "public"."llm_conversations";
CREATE POLICY p_llm_conv ON "public"."llm_conversations"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_llm_msg ON "public"."llm_messages";
CREATE POLICY p_llm_msg ON "public"."llm_messages"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_llm_usage ON "public"."llm_usage_logs";
CREATE POLICY p_llm_usage ON "public"."llm_usage_logs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_llm.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."llm_providers"
    (tenant_id, name, provider_type, base_url, priority)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'openai-default', 'openai',
     'https://api.openai.com/v1', 10),
    ('00000000-0000-0000-0000-000000000001', 'anthropic-default', 'anthropic',
     'https://api.anthropic.com/v1', 20)
ON CONFLICT DO NOTHING;

INSERT INTO "public"."llm_models"
    (tenant_id, provider_id, name, display_name, context_window,
     max_output_tokens, cost_per_1k_input, cost_per_1k_output,
     supports_streaming, supports_tools)
SELECT
    '00000000-0000-0000-0000-000000000001',
    p.id, 'gpt-4o-mini', 'GPT-4o Mini', 128000, 16384,
    0.00015, 0.0006, TRUE, TRUE
FROM "public"."llm_providers" p
WHERE p.name = 'openai-default'
ON CONFLICT DO NOTHING;

INSERT INTO "public"."llm_models"
    (tenant_id, provider_id, name, display_name, context_window,
     max_output_tokens, cost_per_1k_input, cost_per_1k_output,
     supports_streaming, supports_tools)
SELECT
    '00000000-0000-0000-0000-000000000001',
    p.id, 'claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet',
    200000, 8192, 0.003, 0.015, TRUE, TRUE
FROM "public"."llm_providers" p
WHERE p.name = 'anthropic-default'
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_llm.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_llm_usage_updated    ON "public"."llm_usage_logs";
DROP TRIGGER IF EXISTS trg_llm_msg_updated      ON "public"."llm_messages";
DROP TRIGGER IF EXISTS trg_llm_conv_updated     ON "public"."llm_conversations";
DROP TRIGGER IF EXISTS trg_llm_model_updated    ON "public"."llm_models";
DROP TRIGGER IF EXISTS trg_llm_provider_updated ON "public"."llm_providers";

DROP POLICY IF EXISTS p_llm_usage    ON "public"."llm_usage_logs";
DROP POLICY IF EXISTS p_llm_msg      ON "public"."llm_messages";
DROP POLICY IF EXISTS p_llm_conv     ON "public"."llm_conversations";
DROP POLICY IF EXISTS p_llm_model    ON "public"."llm_models";
DROP POLICY IF EXISTS p_llm_provider ON "public"."llm_providers";

DROP TABLE IF EXISTS "public"."llm_usage_logs"    CASCADE;
DROP TABLE IF EXISTS "public"."llm_messages"      CASCADE;
DROP TABLE IF EXISTS "public"."llm_conversations" CASCADE;
DROP TABLE IF EXISTS "public"."llm_models"        CASCADE;
DROP TABLE IF EXISTS "public"."llm_providers"     CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_llm();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  6. ALEMBIC MIGRATION
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[6/10] ALEMBIC — {self.module} (v1.2: public schema)")
        rev = "llm_001"
        prev = self._get_head_revision()

        create_block = "\n\n".join([
            self._sql_providers(),
            self._sql_models(),
            self._sql_conversations(),
            self._sql_messages(),
            self._sql_usage_logs(),
        ])

        trigger_pairs = [
            ("llm_providers", "provider"),
            ("llm_models", "model"),
            ("llm_conversations", "conv"),
            ("llm_messages", "msg"),
            ("llm_usage_logs", "usage"),
        ]
        trigger_lines: list[str] = []
        for tbl, short in trigger_pairs:
            trigger_lines.append(
                '    op.execute(f"""\n'
                f'        DROP TRIGGER IF EXISTS trg_llm_{short}_updated\n'
                f'            ON {{SCHEMA}}.{tbl};\n'
                f'        CREATE TRIGGER trg_llm_{short}_updated\n'
                f'            BEFORE UPDATE ON {{SCHEMA}}.{tbl}\n'
                f'            FOR EACH ROW EXECUTE '
                f'FUNCTION public.set_updated_at_llm();\n'
                '    """)'
            )
        trigger_block = "\n".join(trigger_lines)

        rls_loop = "\n".join(
            f'        ("{tbl}", "{short}"),' for tbl, short in trigger_pairs
        )

        drop_lines: list[str] = []
        for tbl, short in reversed(trigger_pairs):
            drop_lines.append(
                f'    op.execute(f"DROP POLICY IF EXISTS '
                f'p_llm_{short} ON {{SCHEMA}}.{tbl};")'
            )
            drop_lines.append(
                f'    op.execute(f"DROP TRIGGER IF EXISTS '
                f'trg_llm_{short}_updated ON {{SCHEMA}}.{tbl};")'
            )
            drop_lines.append(
                f'    op.execute(f\'DROP TABLE IF EXISTS '
                f'"{SCHEMA}"."{tbl}" CASCADE;\')'
            )
        drop_block = "\n".join(drop_lines)

        content = f'''"""add llm tables

Revision ID: {rev}
Revises: {prev}
Create Date: {datetime.now(UTC).date().isoformat()}

TH: สร้างตาราง llm 5 ตาราง (schema: public, prefix: llm_)
EN: create 5 llm tables (public schema, llm_ prefix)
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "{rev}"
down_revision: Union[str, None] = "{prev}"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "public"


def upgrade() -> None:
    """TH: สร้างตาราง llm | EN: create llm tables"""

{create_block}

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_llm()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

{trigger_block}

    for tbl, short in (
{rls_loop}
    ):
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")
        op.execute(f\"\"\"
            DROP POLICY IF EXISTS p_llm_{{short}} ON {{SCHEMA}}.{{tbl}};
            CREATE POLICY p_llm_{{short}} ON {{SCHEMA}}.{{tbl}}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        \"\"\")


def downgrade() -> None:
    """TH: ลบตาราง llm | EN: drop llm tables"""

{drop_block}

    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_llm();")
'''
        self.writer.write(
            f"migrations/versions/{rev}_add_{self.module}_tables.py",
            content,
        )

    def _sql_providers(self) -> str:
        return '''    op.create_table(
        "llm_providers",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("provider_type", sa.String(50), nullable=False),
        sa.Column("api_key_encrypted", sa.Text, nullable=False,
                  server_default=""),
        sa.Column("base_url", sa.String(500), nullable=False,
                  server_default=""),
        sa.Column("timeout_seconds", sa.Integer, nullable=False,
                  server_default="60"),
        sa.Column("priority", sa.Integer, nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean, nullable=False,
                  server_default=sa.text("true")),
        sa.Column("config_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "provider_type IN ('openai','anthropic','local','azure')",
            name="ck_llm_provider_type",
        ),
        sa.UniqueConstraint("tenant_id", "name", name="uq_llm_provider_name"),
        schema=SCHEMA,
    )
    op.create_index("ix_llm_provider_tenant", "llm_providers",
                    ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_llm_provider_type", "llm_providers",
                    ["provider_type", "is_active"], schema=SCHEMA)'''

    def _sql_models(self) -> str:
        return '''    op.create_table(
        "llm_models",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False,
                  server_default=""),
        sa.Column("context_window", sa.Integer, nullable=False,
                  server_default="4096"),
        sa.Column("max_output_tokens", sa.Integer, nullable=False,
                  server_default="4096"),
        sa.Column("cost_per_1k_input", sa.Numeric(12, 8), nullable=False,
                  server_default="0"),
        sa.Column("cost_per_1k_output", sa.Numeric(12, 8), nullable=False,
                  server_default="0"),
        sa.Column("supports_streaming", sa.Boolean, nullable=False,
                  server_default=sa.text("true")),
        sa.Column("supports_tools", sa.Boolean, nullable=False,
                  server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean, nullable=False,
                  server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_llm_model_name"),
        schema=SCHEMA,
    )
    op.create_index("ix_llm_model_tenant", "llm_models",
                    ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_llm_model_provider", "llm_models",
                    ["provider_id", "is_active"], schema=SCHEMA)'''

    def _sql_conversations(self) -> str:
        return '''    op.create_table(
        "llm_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(500), nullable=False, server_default=""),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("system_prompt", sa.Text, nullable=False, server_default=""),
        sa.Column("metadata_json", sa.Text, nullable=False,
                  server_default="{}"),
        sa.Column("status", sa.String(20), nullable=False,
                  server_default="ACTIVE"),
        sa.Column("message_count", sa.Integer, nullable=False,
                  server_default="0"),
        sa.Column("total_tokens", sa.Integer, nullable=False,
                  server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('ACTIVE','ARCHIVED','DELETED')",
            name="ck_llm_conv_status",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_llm_conv_tenant", "llm_conversations",
                    ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_llm_conv_user", "llm_conversations",
                    ["user_id", "created_at"], schema=SCHEMA)'''

    def _sql_messages(self) -> str:
        return '''    op.create_table(
        "llm_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True),
                  nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("tool_calls_json", sa.Text, nullable=False,
                  server_default="[]"),
        sa.Column("tool_call_id", sa.String(100), nullable=False,
                  server_default=""),
        sa.Column("tokens_input", sa.Integer, nullable=False,
                  server_default="0"),
        sa.Column("tokens_output", sa.Integer, nullable=False,
                  server_default="0"),
        sa.Column("finish_reason", sa.String(30), nullable=False,
                  server_default=""),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "role IN ('system','user','assistant','tool')",
            name="ck_llm_msg_role",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_llm_msg_conv", "llm_messages",
                    ["conversation_id", "created_at"], schema=SCHEMA)'''

    def _sql_usage_logs(self) -> str:
        return '''    op.create_table(
        "llm_usage_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True),
                  nullable=True),
        sa.Column("tokens_input", sa.Integer, nullable=False,
                  server_default="0"),
        sa.Column("tokens_output", sa.Integer, nullable=False,
                  server_default="0"),
        sa.Column("cost_usd", sa.Numeric(12, 8), nullable=False,
                  server_default="0"),
        sa.Column("source", sa.String(50), nullable=False,
                  server_default="chat"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_llm_usage_tenant", "llm_usage_logs",
                    ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_llm_usage_user", "llm_usage_logs",
                    ["user_id", "created_at"], schema=SCHEMA)'''
    def _get_head_revision(self) -> str:
        """TH: หา head revision (ยกเว้นตัวเอง เพื่อกัน self-loop)
           EN: find head revision (exclude self to prevent self-loop)"""
        my_rev = "llm_001"  # ★ revision ของเรา
        for candidate in ("migrations/versions", "alembic/versions"):
            versions = self.root / candidate
            if not versions.exists():
                continue

            revisions: set[str] = set()
            down_revisions: set[str] = set()

            for f in versions.glob("*.py"):
                content = f.read_text(encoding="utf-8")

                m = re.search(
                    r'^revision\s*(?::\s*[^=]+)?\s*=\s*["\']([^"\']+)["\']',
                    content, re.M,
                )
                if not m:
                    continue
                rev_id = m.group(1)

                # ★★★ ข้ามไฟล์ตัวเอง — กัน self-loop ★★★
                if rev_id == my_rev:
                    continue

                revisions.add(rev_id)

                d = re.search(
                    r'^down_revision\s*(?::\s*[^=]+)?\s*=\s*["\']([^"\']+)["\']',
                    content, re.M,
                )
                if d:
                    down_revisions.add(d.group(1))

            heads = revisions - down_revisions
            if heads:
                # ★ เลือก deterministic (sorted) แทน next(iter())
                return sorted(heads)[0]

        return "None"

    # ═══════════════════════════════════════════════════════════
    #  7. SWAGGER
    # ═══════════════════════════════════════════════════════════
    def create_swagger(self) -> None:
        info(f"[7/10] SWAGGER — {self.module}")
        self.writer.write(
            f"{self.mod_root}/presentation/swagger.py",
            self._swagger_content(),
        )

    # ═══════════════════════════════════════════════════════════
    #  8. POSTMAN
    # ═══════════════════════════════════════════════════════════
    def create_postman(self) -> None:
        info(f"[8/10] POSTMAN — {self.module}")
        self.writer.write(
            f"docs/postman/{self.module}.json",
            self._postman_json(),
        )

    def _postman_json(self) -> str:
        return f'''{{
  "info": {{
    "name": "{self.module} API",
    "_postman_id": "{uuid.uuid4()}",
    "description": "LLM Module — Unified LLM Gateway (OpenAI / Anthropic / Local)",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  }},
  "variable": [
    {{ "key": "base_url", "value": "http://localhost:8000" }},
    {{ "key": "model", "value": "gpt-4o-mini" }},
    {{ "key": "conversation_id", "value": "" }}
  ],
  "item": [
    {{
      "name": "Chat",
      "item": [
        {{
          "name": "Chat Completion (sync)",
          "request": {{
            "method": "POST",
            "header": [
              {{ "key": "Content-Type", "value": "application/json" }},
              {{ "key": "Idempotency-Key", "value": "{{{{$guid}}}}" }}
            ],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/llm/chat",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "llm", "chat"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"model\\": \\"gpt-4o-mini\\",\\n  \\"message\\": \\"สวัสดี\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }},
        {{
          "name": "Chat Completion (SSE)",
          "request": {{
            "method": "POST",
            "header": [
              {{ "key": "Content-Type", "value": "application/json" }},
              {{ "key": "Accept", "value": "text/event-stream" }}
            ],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/llm/chat/stream",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "llm", "chat", "stream"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"model\\": \\"gpt-4o-mini\\",\\n  \\"message\\": \\"นับ 1 ถึง 5\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Conversations",
      "item": [
        {{
          "name": "List Conversations",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/llm/conversations?limit=50",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "llm", "conversations"],
              "query": [{{ "key": "limit", "value": "50" }}]
            }}
          }}
        }},
        {{
          "name": "Create Conversation",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/llm/conversations",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "llm", "conversations"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"model\\": \\"gpt-4o-mini\\",\\n  \\"title\\": \\"My Chat\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Providers & Models",
      "item": [
        {{
          "name": "List Providers",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/llm/providers",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "llm", "providers"]
            }}
          }}
        }},
        {{
          "name": "List Models",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/llm/models",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "llm", "models"]
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Usage",
      "item": [
        {{
          "name": "Usage (tenant + user)",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/llm/usage?days=30",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "llm", "usage"],
              "query": [{{ "key": "days", "value": "30" }}]
            }}
          }}
        }}
      ]
    }}
  ]
}}
'''

    # ═══════════════════════════════════════════════════════════
    #  9. VERIFY  ★ NEW v1.3 ★
    # ═══════════════════════════════════════════════════════════
    def verify(self) -> None:
        info("[VERIFY] ตรวจสอบ Swagger + Postman + SQL")
        issues: list[str] = []

        # 1) swagger.py
        swagger_py = self.root / f"{self.mod_root}/presentation/swagger.py"
        if swagger_py.exists():
            ok(f"swagger.py exists")
            sw_content = swagger_py.read_text(encoding="utf-8")
            if "def register_llm_openapi" in sw_content:
                ok("  ✓ has register_llm_openapi()")
            else:
                issues.append("swagger.py missing register_llm_openapi()")
        else:
            issues.append(f"swagger.py NOT FOUND: {swagger_py}")

        # 2) app.py checks
        app_file = self.root / self.app_py
        if app_file.exists():
            content = app_file.read_text(encoding="utf-8")
            if "register_llm_openapi(app)" in content:
                ok("app.py: register_llm_openapi(app) ✓")
            else:
                issues.append(
                    "app.py DOES NOT call register_llm_openapi(app)"
                )
            if "llm_router" in content:
                ok("app.py: llm_router imported ✓")
            else:
                issues.append("app.py missing llm_router import")
            if "register_llm_openapi" in content:
                ok("app.py: swagger import ✓")
            else:
                issues.append("app.py missing swagger import")
        else:
            issues.append(f"app.py NOT FOUND: {app_file}")

        # 3) postman.json
        postman = self.root / f"docs/postman/{self.module}.json"
        if postman.exists():
            try:
                data = _json_mod.loads(postman.read_text(encoding="utf-8"))
                n_items = len(data.get("item", []))
                ok(f"postman: valid JSON, {n_items} folders")
            except Exception as e:
                issues.append(f"postman.json invalid JSON: {e}")
        else:
            issues.append(f"postman.json NOT FOUND: {postman}")

        # 4) SQL files
        for ver in ("V001", "V002", "V003"):
            d = self.root / self.sql_dir
            pattern = f"{ver}__*{self.module}*.sql"
            matches = list(d.glob(pattern)) if d.exists() else []
            if matches:
                ok(f"SQL: {matches[0].name}")
            else:
                issues.append(f"SQL {ver} not found in {d}")

        # 5) summary
        print()
        if issues:
            info("═" * 60)
            warn(f"พบ {len(issues)} ปัญหา:")
            for i, msg in enumerate(issues, 1):
                err(f"  {i}. {msg}")
            info("═" * 60)
            print()
            print(f"  {C.YELLOW}แนะนำ:{C.RESET}")
            print(f"    python create_module_llm.py update llm --force")
            print(f"    python create_module_llm.py swagger llm --force")
            print(f"    python create_module_llm.py postman llm --force")
            print()
        else:
            info("═" * 60)
            ok("ALL CHECKS PASSED ✓")
            info("═" * 60)
            print()
            print(f"  {C.YELLOW}วิธีดูผลลัพธ์:{C.RESET}")
            print(f"    • Swagger:  http://localhost:8000/docs")
            print(f"    • Postman:  Import → {postman.relative_to(self.root)}")
            print()

    # ═══════════════════════════════════════════════════════════
    #  RUN ALL
    # ═══════════════════════════════════════════════════════════
    def run_all(self) -> None:
        self.create_module()
        self.create_sql()
        self.create_migration()
        self.create_swagger()
        self.create_postman()
        self.activate_module()

    # ═══════════════════════════════════════════════════════════
    #  SUMMARY
    # ═══════════════════════════════════════════════════════════
    def summary(self) -> None:
        print()
        info("═" * 60)
        ok(f"DONE — module: {self.module}  (v{VERSION})")
        info(f"  Schema  : {SCHEMA}")
        info(f"  Prefix  : {self.prefix}_")
        info(f"  Written : {len(self.writer.written)} files")
        info(f"  Skipped : {len(self.writer.skipped)} files")
        info(f"  Backups : {len(self.writer.backups)} files")
        info("═" * 60)
        print()
        print(f"  {C.YELLOW}Next steps:{C.RESET}")
        print(f"    1. Verify:    python create_module_llm.py verify llm")
        print(f"    2. Alembic:   alembic upgrade head")
        print(f"    3. Run:       uvicorn app.app:app --reload")
        print(f"    4. Swagger:   http://localhost:8000/docs")
        print(f"    5. Postman:   Import docs/postman/{self.module}.json")
        print()


# ═══════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════
HELP = f"""
═══════════════════════════════════════════════════════════════
  create_module_llm.py — LLM Module Generator v{VERSION}
  Schema: {SCHEMA}  ·  Prefix: llm_
═══════════════════════════════════════════════════════════════

  USAGE
    python create_module_llm.py <action> <module> [layer] [prefix] [options]

  ACTIONS (10)
    create      [1]  สร้าง module structure (4 layers)
    activate    [2]  Register router + swagger + models
    sql         [3]  สร้าง SQL migrations V001/V002/V003 (public schema)
    update      [4]  Update app/app.py (+ swagger hook)
    update-env  [5]  Update migrations/env.py
    alembic     [6]  สร้าง Alembic migration (5 tables + triggers + RLS)
    swagger     [7]  สร้าง OpenAPI docs (tag: LLM)
    postman     [8]  สร้าง Postman collection
    verify      [9]  ★ ตรวจสอบ Swagger + Postman + SQL
    all         ทำทั้งหมด
    help        แสดง help

  POSITIONAL
    module      ชื่อ module (default: llm)
    layer       Layer number 0-7 (default: 5)
    prefix      3-char DB prefix (default: llm)

  OPTIONS
    --force              เขียนทับไฟล์เดิม
    --template <A-G>     Template (default: A)
    --project-root <path> Project root path

  EXAMPLES
    # Full pipeline
    python create_module_llm.py all llm 5 llm --force

    # ตรวจสอบ
    python create_module_llm.py verify llm

    # Fix swagger เฉพาะ
    python create_module_llm.py update llm --force

    # Fix postman เฉพาะ
    python create_module_llm.py postman llm --force

  RESULTS
    Swagger:  http://localhost:8000/docs   → tag "LLM"
    Postman:  Import docs/postman/llm.json
═══════════════════════════════════════════════════════════════
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("module", nargs="?", default="llm")
    parser.add_argument("layer", nargs="?", default="5")
    parser.add_argument("prefix", nargs="?", default="llm")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--template", default="A")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--help", action="store_true")

    args, _ = parser.parse_known_args()

    if args.help or args.action == "help":
        print(HELP)
        return 0

    root = Path(args.project_root).resolve()
    if not root.exists():
        err(f"Project root not found: {root}")
        return 1

    gen = LLMModuleGenerator(
        project_root=root,
        module=args.module,
        layer=args.layer,
        prefix=args.prefix,
        template=args.template,
        force=args.force,
    )

    print()
    info("═" * 60)
    info(f"  MODULE  : {gen.module}")
    info(f"  LAYER   : {gen.layer} ({gen.layer_name})")
    info(f"  SCHEMA  : {SCHEMA}")
    info(f"  PREFIX  : {gen.prefix}_")
    info(f"  ACTION  : {args.action}")
    info(f"  FORCE   : {args.force}")
    info(f"  VERSION : {VERSION}")
    info("═" * 60)

    action_map = {
        "create": gen.create_module,
        "activate": gen.activate_module,
        "sql": gen.create_sql,
        "alembic": gen.create_migration,
        "swagger": gen.create_swagger,
        "postman": gen.create_postman,
        "update": gen.update_app,
        "update-env": gen.update_env,
        "verify": gen.verify,
        "all": gen.run_all,
    }

    if args.action not in action_map:
        err(f"Unknown action: {args.action}")
        print(HELP)
        return 1

    try:
        action_map[args.action]()
    except Exception as e:
        err(f"Aborted: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # verify action ไม่ต้องแสดง summary
    if args.action != "verify":
        gen.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
