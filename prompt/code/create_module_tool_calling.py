#!/usr/bin/env python3
"""
create_module_tool_calling.py — Tool Calling Module Generator v1.0.0

สร้าง tool_calling module ตาม Clean Architecture + DDD + Event-Driven
Schema: public · Prefix: tool_ · Tables: tool_*
Layer: 5-Intel · Depends: llm

Actions (9):
  1. create      — สร้าง module structure (4 layers)
  2. sql         — สร้าง SQL migrations V001/V002/V003
  3. alembic     — สร้าง Alembic migration (4 tables + triggers + RLS)
  4. swagger     — สร้าง OpenAPI docs
  5. postman     — สร้าง Postman collection
  6. update      — อัปเดต app/app.py
  7. update-env  — อัปเดต migrations/env.py
  8. verify      — ตรวจสอบ setup ★
  9. all         — ทำทุกอย่าง
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
VERSION = "1.0.0"

LAYER_NAMES = {
    "0": "0-Core", "1": "1-Foundation", "2": "2-Money",
    "3": "3-Goods", "4": "4-Ops", "5": "5-Intel",
    "6": "6-Monitor", "7": "7-Template",
}

SCHEMA = "public"
PREFIX = "tool"
MODULE_NAME = "tool_calling"
TABLE_NAMES = (
    "tool_definitions",
    "tool_registrations",
    "tool_invocations",
    "tool_permissions",
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
class ToolCallingModuleGenerator:
    def __init__(
        self,
        project_root: Path,
        module: str = MODULE_NAME,
        layer: str = "5",
        prefix: str = PREFIX,
        force: bool = False,
    ):
        self.root = project_root
        self.module = module.lower()
        self.layer = layer
        self.prefix = prefix.lower()
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
            """tool_calling domain layer — ชั้นโดเมน"""
            from .entities import (
                ToolDefinition, ToolInvocation, ToolPermission, ToolRegistration,
            )
            from .enums import RiskLevel, ToolKind, ToolStatus, ToolVisibility
            from .events import (
                PermissionDenied, ToolFailed, ToolInvoked, ToolRegistered,
            )
            from .exceptions import (
                InvalidArgumentsError, InvocationNotFoundError,
                PermissionDeniedError, RateLimitExceededError, ToolConflictError,
                ToolError, ToolExecutionError, ToolNotFoundError,
            )

            __all__ = [
                "ToolDefinition", "ToolInvocation", "ToolPermission",
                "ToolRegistration", "RiskLevel", "ToolKind", "ToolStatus",
                "ToolVisibility", "PermissionDenied", "ToolFailed",
                "ToolInvoked", "ToolRegistered", "InvalidArgumentsError",
                "InvocationNotFoundError", "PermissionDeniedError",
                "RateLimitExceededError", "ToolConflictError", "ToolError",
                "ToolExecutionError", "ToolNotFoundError",
            ]
        '''))

        self.writer.write(f"{base}/enums.py", dedent('''\
            """tool_calling enums"""
            from __future__ import annotations
            from enum import StrEnum


            class ToolKind(StrEnum):
                """TH: ประเภท tool | EN: Tool kind"""
                HTTP = "http"
                PYTHON = "python"
                SQL = "sql"
                SHELL = "shell"
                MCP = "mcp"
                OPENAPI = "openapi"


            class ToolStatus(StrEnum):
                """TH: สถานะการเรียก | EN: Invocation status"""
                SUCCESS = "SUCCESS"
                ERROR = "ERROR"
                TIMEOUT = "TIMEOUT"
                DENIED = "DENIED"
                RATE_LIMITED = "RATE_LIMITED"


            class RiskLevel(StrEnum):
                """TH: ความเสี่ยง | EN: Risk level"""
                LOW = "low"
                MEDIUM = "medium"
                HIGH = "high"
                CRITICAL = "critical"


            class ToolVisibility(StrEnum):
                """TH: การมองเห็น | EN: Visibility"""
                PRIVATE = "private"
                TENANT = "tenant"
                PUBLIC = "public"
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """tool_calling domain exceptions"""
            from __future__ import annotations


            class ToolError(Exception):
                """TH: base | EN: base"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class ToolNotFoundError(ToolError):
                code = "NOT_FOUND"


            class InvocationNotFoundError(ToolError):
                code = "NOT_FOUND"


            class ToolConflictError(ToolError):
                code = "CONFLICT"


            class PermissionDeniedError(ToolError):
                code = "PERMISSION_DENIED"


            class RateLimitExceededError(ToolError):
                code = "RATE_LIMITED"


            class InvocationTimeoutError(ToolError):
                code = "TIMEOUT"


            class InvalidArgumentsError(ToolError):
                code = "VALIDATION_ERROR"


            class ToolExecutionError(ToolError):
                code = "PROVIDER_ERROR"


            class SecretNotFoundError(ToolError):
                code = "NOT_FOUND"
        '''))

        self.writer.write(f"{base}/events.py", dedent('''\
            """tool_calling domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import UTC, datetime


            def _now() -> datetime:
                return datetime.now(UTC)


            @dataclass(frozen=True, slots=True)
            class ToolRegistered:
                tool_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                kind: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class ToolInvoked:
                invocation_id: uuid.UUID
                tool_id: uuid.UUID
                tenant_id: uuid.UUID
                user_id: uuid.UUID
                status: str
                latency_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class ToolFailed:
                invocation_id: uuid.UUID
                tool_id: uuid.UUID
                tenant_id: uuid.UUID
                error_code: str
                message: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class PermissionDenied:
                tool_id: uuid.UUID
                tenant_id: uuid.UUID
                user_id: uuid.UUID
                role: str
                occurred_at: datetime = field(default_factory=_now)
        '''))

        self.writer.write(f"{base}/value_objects/__init__.py", dedent('''\
            """tool_calling value objects"""
            from .invocation import InvocationRequest, InvocationResult
            from .tool_spec import ToolSpec

            __all__ = ["InvocationRequest", "InvocationResult", "ToolSpec"]
        '''))

        self.writer.write(f"{base}/value_objects/tool_spec.py", dedent('''\
            """ToolSpec value object"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.tool_calling.domain.enums import (
                RiskLevel, ToolKind, ToolVisibility,
            )


            class ToolSpec(BaseModel):
                """TH: spec ของ tool | EN: tool spec VO"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                name: str = Field(
                    min_length=1, max_length=100,
                    pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                )
                description: str = Field(default="", max_length=2000)
                parameters_json: dict[str, Any] = Field(default_factory=dict)
                returns_json: dict[str, Any] = Field(default_factory=dict)
                kind: ToolKind = ToolKind.HTTP
                risk_level: RiskLevel = RiskLevel.LOW
                visibility: ToolVisibility = ToolVisibility.TENANT
                timeout_seconds: int = Field(default=30, ge=1, le=600)
        '''))

        self.writer.write(f"{base}/value_objects/invocation.py", dedent('''\
            """Invocation VOs"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class InvocationRequest(BaseModel):
                """TH: คำขอ | EN: request"""
                model_config = ConfigDict(extra="forbid")
                tool_name: str = Field(min_length=1, max_length=100)
                arguments: dict[str, Any] = Field(default_factory=dict)
                idempotency_key: str | None = Field(default=None, max_length=100)


            class InvocationResult(BaseModel):
                """TH: ผลลัพธ์ | EN: result"""
                model_config = ConfigDict(extra="forbid")
                invocation_id: str
                tool_name: str
                status: str
                output: Any = None
                error: str = ""
                latency_ms: int = 0
        '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """tool_calling helpers"""
            from .validators import is_safe_sql, redact_secrets, validate_arguments

            __all__ = ["is_safe_sql", "redact_secrets", "validate_arguments"]
        '''))

        self.writer.write(f"{base}/helpers/validators.py", dedent('''\
            """validators — never-raise"""
            from __future__ import annotations
            import re
            from typing import Any

            _SQL_DANGEROUS = re.compile(
                r"\\b(DROP|TRUNCATE|DELETE|ALTER|GRANT|REVOKE|CREATE\\s+USER)\\b",
                re.IGNORECASE,
            )
            _SECRET_KEYS = re.compile(
                r"(api_?key|secret|password|token|bearer)", re.IGNORECASE,
            )


            def validate_arguments(args: dict[str, Any], schema: dict[str, Any]) -> list[str]:
                """TH: validate args (minimal) | EN: minimal schema validation"""
                errors: list[str] = []
                required = schema.get("required", []) or []
                properties = schema.get("properties", {}) or {}
                for key in required:
                    if key not in args:
                        errors.append(f"missing required: {key}")
                for key, val in args.items():
                    if key in properties:
                        expected = properties[key].get("type")
                        if expected == "string" and not isinstance(val, str):
                            errors.append(f"{key} must be string")
                        elif expected == "integer" and not isinstance(val, int):
                            errors.append(f"{key} must be integer")
                        elif expected == "number" and not isinstance(val, (int, float)):
                            errors.append(f"{key} must be number")
                        elif expected == "boolean" and not isinstance(val, bool):
                            errors.append(f"{key} must be boolean")
                        elif expected == "array" and not isinstance(val, list):
                            errors.append(f"{key} must be array")
                return errors


            def is_safe_sql(sql: str) -> bool:
                """TH: check SQL | EN: check SQL for danger"""
                return not bool(_SQL_DANGEROUS.search(sql or ""))


            def redact_secrets(data: Any) -> Any:
                """TH: ซ่อน secret | EN: redact secrets"""
                if isinstance(data, dict):
                    return {
                        k: ("***REDACTED***" if _SECRET_KEYS.search(str(k))
                            else redact_secrets(v))
                        for k, v in data.items()
                    }
                if isinstance(data, list):
                    return [redact_secrets(x) for x in data]
                return data
        '''))

        # entities (alias to ORM)
        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """tool_calling entities"""
            from .invocation import ToolInvocation
            from .permission import ToolPermission
            from .registration import ToolRegistration
            from .tool import ToolDefinition

            __all__ = [
                "ToolDefinition", "ToolInvocation",
                "ToolPermission", "ToolRegistration",
            ]
        '''))

        for name, cls, model in (
            ("tool", "ToolDefinition", "ToolDefinitionModel"),
            ("registration", "ToolRegistration", "ToolRegistrationModel"),
            ("invocation", "ToolInvocation", "ToolInvocationModel"),
            ("permission", "ToolPermission", "ToolPermissionModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias to ORM"""
                from __future__ import annotations
                from app.modules.tool_calling.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

    # ─── APPLICATION LAYER ──────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """tool_calling application layer"""
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """tool_calling application exceptions"""
            from __future__ import annotations


            class ApplicationError(Exception):
                code: str = "APP_ERROR"
                http_status: int = 400


            class NotFoundAppError(ApplicationError):
                code = "NOT_FOUND"
                http_status = 404


            class ConflictAppError(ApplicationError):
                code = "CONFLICT"
                http_status = 409


            class ValidationAppError(ApplicationError):
                code = "VALIDATION_ERROR"
                http_status = 422


            class PermissionAppError(ApplicationError):
                code = "PERMISSION_DENIED"
                http_status = 403


            class RateLimitAppError(ApplicationError):
                code = "RATE_LIMITED"
                http_status = 429


            class TimeoutAppError(ApplicationError):
                code = "TIMEOUT"
                http_status = 504


            class ExecutionAppError(ApplicationError):
                code = "PROVIDER_ERROR"
                http_status = 502
        '''))

        self.writer.write(f"{base}/interfaces.py", dedent('''\
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
        '''))

        self.writer.write(f"{base}/utils.py", dedent('''\
            """tool_calling application utils"""
            from __future__ import annotations
            import json
            import time
            from typing import Any


            def json_dumps_safe(obj: Any, max_len: int = 10000) -> str:
                try:
                    s = json.dumps(
                        obj, separators=(",", ":"),
                        default=str, ensure_ascii=False,
                    )
                except Exception:
                    s = "{}"
                if len(s) > max_len:
                    s = s[:max_len] + "...[truncated]"
                return s


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
        '''))

        self.writer.write(f"{base}/mappers.py", dedent('''\
            """tool_calling mappers — ORM → dict"""
            from __future__ import annotations
            from typing import Any


            def tool_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "description": row.description or "",
                    "kind": row.kind,
                    "risk_level": row.risk_level,
                    "visibility": row.visibility,
                    "timeout_seconds": row.timeout_seconds,
                    "is_active": row.is_active,
                }


            def invocation_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "tool_id": str(row.tool_id),
                    "tool_name": row.tool_name or "",
                    "status": row.status,
                    "latency_ms": row.latency_ms or 0,
                    "error_code": row.error_code or "",
                }


            def permission_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "tool_id": str(row.tool_id),
                    "role": row.role,
                    "allowed": row.allowed,
                }
        '''))

        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _use_case_content(self) -> str:
        return dedent('''\
            """tool_calling use cases"""
            from __future__ import annotations
            import asyncio
            import time
            import uuid
            from typing import Any

            import structlog

            from app.modules.tool_calling.application.exceptions import (
                ConflictAppError, ExecutionAppError, NotFoundAppError,
                PermissionAppError, RateLimitAppError, TimeoutAppError,
                ValidationAppError,
            )
            from app.modules.tool_calling.application.interfaces import (
                EventBus, InvocationRepository, PermissionRepository,
                RateLimiter, RegistrationRepository, RequestContext,
                ToolClientRegistry, ToolRepository,
            )
            from app.modules.tool_calling.application.utils import (
                json_dumps_safe, json_loads_safe, ms_now,
            )
            from app.modules.tool_calling.domain.enums import ToolStatus
            from app.modules.tool_calling.domain.events import (
                PermissionDenied, ToolFailed, ToolInvoked, ToolRegistered,
            )
            from app.modules.tool_calling.domain.helpers import (
                redact_secrets, validate_arguments,
            )
            from app.modules.tool_calling.domain.value_objects import (
                InvocationResult, ToolSpec,
            )
            from app.modules.tool_calling.infrastructure.models import (
                ToolDefinitionModel, ToolInvocationModel,
            )

            log = structlog.get_logger()


            class ToolCallingUseCase:
                """TH: use cases ของ tool_calling | EN: tool calling use cases"""

                def __init__(
                    self,
                    tool_repo: ToolRepository,
                    registration_repo: RegistrationRepository,
                    invocation_repo: InvocationRepository,
                    permission_repo: PermissionRepository,
                    clients: ToolClientRegistry,
                    rate_limiter: RateLimiter | None = None,
                    event_bus: EventBus | None = None,
                ) -> None:
                    self._tools = tool_repo
                    self._regs = registration_repo
                    self._invs = invocation_repo
                    self._perms = permission_repo
                    self._clients = clients
                    self._rate = rate_limiter
                    self._bus = event_bus

                async def register_tool(
                    self, ctx: RequestContext, spec: ToolSpec,
                ) -> dict[str, Any]:
                    """TH: ลงทะเบียน tool | EN: register tool"""
                    log.info("tool.register.start", name=spec.name)
                    existing = await self._tools.find_by_name(ctx, spec.name)
                    if existing is not None:
                        raise ConflictAppError(f"tool exists: {spec.name}")

                    tool = ToolDefinitionModel(
                        tenant_id=ctx.tenant_id,
                        name=spec.name,
                        description=spec.description,
                        parameters_json=json_dumps_safe(spec.parameters_json),
                        returns_json=json_dumps_safe(spec.returns_json),
                        kind=str(spec.kind),
                        risk_level=str(spec.risk_level),
                        visibility=str(spec.visibility),
                        timeout_seconds=spec.timeout_seconds,
                    )
                    saved = await self._tools.save(ctx, tool)

                    if self._bus:
                        try:
                            await self._bus.publish(ToolRegistered(
                                tool_id=saved.id,
                                tenant_id=ctx.tenant_id,
                                name=saved.name,
                                kind=saved.kind,
                            ))
                        except Exception as exc:
                            log.warning("tool.register.publish_failed", err=str(exc))

                    log.info("tool.register.success", name=spec.name)
                    return {
                        "id": str(saved.id),
                        "name": saved.name,
                        "kind": saved.kind,
                        "is_active": saved.is_active,
                    }

                async def list_tools(
                    self, ctx: RequestContext, limit: int = 100, offset: int = 0,
                ) -> list[dict[str, Any]]:
                    rows = await self._tools.find_all(ctx, limit, offset)
                    return [
                        {
                            "id": str(r.id), "name": r.name,
                            "description": r.description or "",
                            "kind": r.kind, "risk_level": r.risk_level,
                            "visibility": r.visibility,
                            "timeout_seconds": r.timeout_seconds,
                            "is_active": r.is_active,
                        }
                        for r in rows
                    ]

                async def get_tool(
                    self, ctx: RequestContext, tool_id: uuid.UUID,
                ) -> dict[str, Any]:
                    t = await self._tools.find_by_id(ctx, tool_id)
                    if t is None:
                        raise NotFoundAppError("tool not found")
                    return {
                        "id": str(t.id), "name": t.name,
                        "description": t.description or "",
                        "parameters_json": json_loads_safe(t.parameters_json, {}),
                        "kind": t.kind, "is_active": t.is_active,
                    }

                async def delete_tool(
                    self, ctx: RequestContext, tool_id: uuid.UUID,
                ) -> bool:
                    t = await self._tools.find_by_id(ctx, tool_id)
                    if t is None:
                        raise NotFoundAppError("tool not found")
                    return await self._tools.delete(ctx, tool_id)

                async def invoke(
                    self, ctx: RequestContext, *,
                    tool_name: str, arguments: dict[str, Any],
                    idempotency_key: str = "",
                    role: str = "user",
                ) -> InvocationResult:
                    """TH: เรียก tool | EN: invoke tool"""
                    log.info("tool.invoke.start", name=tool_name)

                    tool = await self._tools.find_by_name(ctx, tool_name)
                    if tool is None or not tool.is_active:
                        raise NotFoundAppError(f"tool not found: {tool_name}")

                    # permission
                    perm = await self._perms.check(ctx, tool.id, role)
                    if perm is not None and not perm.allowed:
                        if self._bus:
                            try:
                                await self._bus.publish(PermissionDenied(
                                    tool_id=tool.id,
                                    tenant_id=ctx.tenant_id,
                                    user_id=ctx.user_id or ctx.tenant_id,
                                    role=role,
                                ))
                            except Exception:
                                pass
                        raise PermissionAppError(
                            f"role '{role}' not allowed to invoke {tool_name}",
                        )

                    # rate limit
                    if self._rate is not None:
                        reg = await self._regs.find_by_tool(ctx, tool.id)
                        limit = reg.rate_limit_per_min if reg else 60
                        try:
                            allowed = await self._rate.check_and_incr(
                                ctx.tenant_id, ctx.user_id or ctx.tenant_id,
                                tool.id, limit,
                            )
                            if not allowed:
                                raise RateLimitAppError(
                                    f"rate limit exceeded for {tool_name}",
                                )
                        except RateLimitAppError:
                            raise
                        except Exception as exc:
                            log.warning("ratelimit.fail_open", err=str(exc))

                    # validate
                    schema = json_loads_safe(tool.parameters_json, {})
                    errors = validate_arguments(arguments, schema)
                    if errors:
                        raise ValidationAppError(
                            f"invalid arguments: {'; '.join(errors)}",
                        )

                    started = ms_now()
                    invocation = ToolInvocationModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id,
                        tool_id=tool.id,
                        tool_name=tool.name,
                        args_json=json_dumps_safe(redact_secrets(arguments)),
                        status=ToolStatus.SUCCESS.value,
                        idempotency_key=idempotency_key or "",
                    )

                    try:
                        client = self._clients.get(str(tool.kind))
                        output = await asyncio.wait_for(
                            client.invoke(
                                spec=tool, args=arguments, secrets={},
                                timeout=tool.timeout_seconds,
                            ),
                            timeout=tool.timeout_seconds + 5,
                        )
                        invocation.result_json = json_dumps_safe(output)
                        invocation.status = ToolStatus.SUCCESS.value

                    except asyncio.TimeoutError as exc:
                        invocation.status = ToolStatus.TIMEOUT.value
                        invocation.error_code = "TIMEOUT"
                        invocation.error_message = str(exc)[:500]
                        invocation.latency_ms = ms_now() - started
                        await self._invs.save(ctx, invocation)
                        await self._publish_failure(invocation, str(exc))
                        raise TimeoutAppError(
                            f"tool {tool_name} timed out",
                        ) from exc

                    except Exception as exc:
                        log.warning("tool.invoke.failed", err=str(exc))
                        invocation.status = ToolStatus.ERROR.value
                        invocation.error_code = "EXECUTION_ERROR"
                        invocation.error_message = str(exc)[:500]
                        invocation.latency_ms = ms_now() - started
                        await self._invs.save(ctx, invocation)
                        await self._publish_failure(invocation, str(exc))
                        raise ExecutionAppError(
                            f"tool {tool_name} failed: {exc}",
                        ) from exc

                    invocation.latency_ms = ms_now() - started
                    saved = await self._invs.save(ctx, invocation)

                    if self._bus:
                        try:
                            await self._bus.publish(ToolInvoked(
                                invocation_id=saved.id,
                                tool_id=tool.id,
                                tenant_id=ctx.tenant_id,
                                user_id=ctx.user_id or ctx.tenant_id,
                                status=saved.status,
                                latency_ms=saved.latency_ms,
                            ))
                        except Exception:
                            pass

                    log.info(
                        "tool.invoke.success",
                        name=tool_name, latency_ms=saved.latency_ms,
                    )
                    return InvocationResult(
                        invocation_id=str(saved.id),
                        tool_name=tool.name,
                        status=saved.status,
                        output=json_loads_safe(saved.result_json, {}),
                        latency_ms=saved.latency_ms,
                    )

                async def list_invocations(
                    self, ctx: RequestContext,
                    limit: int = 50, offset: int = 0,
                ) -> list[dict[str, Any]]:
                    rows = await self._invs.list(ctx, limit, offset)
                    return [
                        {
                            "id": str(r.id),
                            "tool_id": str(r.tool_id),
                            "tool_name": r.tool_name or "",
                            "status": r.status,
                            "latency_ms": r.latency_ms or 0,
                            "created_at": (
                                r.created_at.isoformat()
                                if r.created_at else ""
                            ),
                        }
                        for r in rows
                    ]

                async def _publish_failure(
                    self, inv: ToolInvocationModel, msg: str,
                ) -> None:
                    if self._bus is None:
                        return
                    try:
                        await self._bus.publish(ToolFailed(
                            invocation_id=inv.id,
                            tool_id=inv.tool_id,
                            tenant_id=inv.tenant_id,
                            error_code=inv.error_code,
                            message=msg,
                        ))
                    except Exception:
                        pass
        ''')

    # ─── INFRASTRUCTURE LAYER ───────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """tool_calling infrastructure layer"""
        '''))

        self.writer.write(f"{base}/models.py", self._models_content())
        self.writer.write(f"{base}/tool_repository.py", self._tool_repo_content())
        self.writer.write(f"{base}/invocation_repository.py", self._invocation_repo_content())
        self.writer.write(f"{base}/permission_repository.py", self._permission_repo_content())
        self.writer.write(f"{base}/caches.py", self._caches_content())
        self.writer.write(f"{base}/services.py", self._services_content())

    def _models_content(self) -> str:
        return dedent('''\
            """tool_calling SQLAlchemy 2.0 models — schema=public, prefix=tool_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Index, Integer, Numeric,
                String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: declarative base | EN: declarative base"""


            class ToolDefinitionModel(Base):
                __tablename__ = "tool_definitions"
                __table_args__ = (
                    CheckConstraint(
                        "kind IN ('http','python','sql','shell','mcp','openapi')",
                        name="ck_tool_kind",
                    ),
                    CheckConstraint(
                        "risk_level IN ('low','medium','high','critical')",
                        name="ck_tool_risk",
                    ),
                    CheckConstraint(
                        "visibility IN ('private','tenant','public')",
                        name="ck_tool_visibility",
                    ),
                    UniqueConstraint(
                        "tenant_id", "name", name="uq_tool_name",
                    ),
                    Index("ix_tool_def_tenant", "tenant_id"),
                    Index("ix_tool_def_kind", "kind", "is_active"),
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
                description: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                parameters_json: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="{}",
                )
                returns_json: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="{}",
                )
                version: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="1.0.0",
                )
                kind: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="http",
                )
                risk_level: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="low",
                )
                visibility: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="tenant",
                )
                timeout_seconds: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="30",
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


            class ToolRegistrationModel(Base):
                __tablename__ = "tool_registrations"
                __table_args__ = (
                    UniqueConstraint("tool_id", name="uq_tool_reg_tool"),
                    Index("ix_tool_reg_tenant", "tenant_id"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                tool_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                enabled: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("true"),
                )
                rate_limit_per_min: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="60",
                )
                scopes_json: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="[]",
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class ToolInvocationModel(Base):
                __tablename__ = "tool_invocations"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('SUCCESS','ERROR','TIMEOUT','DENIED','RATE_LIMITED')",
                        name="ck_tool_inv_status",
                    ),
                    Index("ix_tool_inv_tenant", "tenant_id", "created_at"),
                    Index("ix_tool_inv_tool", "tool_id", "created_at"),
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
                tool_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                tool_name: Mapped[str] = mapped_column(
                    String(100), nullable=False, server_default="",
                )
                args_json: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="{}",
                )
                result_json: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="{}",
                )
                status: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="SUCCESS",
                )
                latency_ms: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                error_code: Mapped[str] = mapped_column(
                    String(50), nullable=False, server_default="",
                )
                error_message: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                tokens_used: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                cost_usd: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                idempotency_key: Mapped[str] = mapped_column(
                    String(100), nullable=False, server_default="",
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class ToolPermissionModel(Base):
                __tablename__ = "tool_permissions"
                __table_args__ = (
                    UniqueConstraint(
                        "tool_id", "role", name="uq_tool_perm_role",
                    ),
                    Index("ix_tool_perm_tenant", "tenant_id"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                tool_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                role: Mapped[str] = mapped_column(String(50), nullable=False)
                allowed: Mapped[bool] = mapped_column(
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
        ''')

    def _tool_repo_content(self) -> str:
        return dedent('''\
            """ToolDefinition repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select, update
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.tool_calling.application.exceptions import (
                ApplicationError,
            )
            from app.modules.tool_calling.infrastructure.models import (
                ToolDefinitionModel,
            )


            class ToolRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(
                    self, ctx: object, tool: ToolDefinitionModel,
                ) -> ToolDefinitionModel:
                    try:
                        self._session.add(tool)
                        await self._session.flush()
                        return tool
                    except SQLAlchemyError as exc:
                        logger.error(f"tool.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_id(
                    self, ctx: object, tool_id: uuid.UUID,
                ) -> ToolDefinitionModel | None:
                    try:
                        result = await self._session.execute(
                            select(ToolDefinitionModel).where(
                                ToolDefinitionModel.id == tool_id,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"tool.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_name(
                    self, ctx: object, name: str,
                ) -> ToolDefinitionModel | None:
                    try:
                        result = await self._session.execute(
                            select(ToolDefinitionModel).where(
                                ToolDefinitionModel.name == name,
                                ToolDefinitionModel.is_active.is_(True),
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"tool.find_by_name failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_all(
                    self, ctx: object, limit: int = 100, offset: int = 0,
                ) -> list[ToolDefinitionModel]:
                    try:
                        result = await self._session.execute(
                            select(ToolDefinitionModel)
                            .where(ToolDefinitionModel.is_active.is_(True))
                            .order_by(ToolDefinitionModel.name.asc())
                            .limit(limit).offset(offset)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"tool.find_all failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def delete(
                    self, ctx: object, tool_id: uuid.UUID,
                ) -> bool:
                    try:
                        stmt = (
                            update(ToolDefinitionModel)
                            .where(ToolDefinitionModel.id == tool_id)
                            .values(is_active=False)
                        )
                        res = await self._session.execute(stmt)
                        await self._session.flush()
                        return (res.rowcount or 0) > 0
                    except SQLAlchemyError as exc:
                        logger.error(f"tool.delete failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _invocation_repo_content(self) -> str:
        return dedent('''\
            """ToolInvocation repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.tool_calling.application.exceptions import (
                ApplicationError,
            )
            from app.modules.tool_calling.infrastructure.models import (
                ToolInvocationModel,
            )


            class InvocationRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(
                    self, ctx: object, inv: ToolInvocationModel,
                ) -> ToolInvocationModel:
                    try:
                        self._session.add(inv)
                        await self._session.flush()
                        return inv
                    except SQLAlchemyError as exc:
                        logger.error(f"inv.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_id(
                    self, ctx: object, inv_id: uuid.UUID,
                ) -> ToolInvocationModel | None:
                    try:
                        result = await self._session.execute(
                            select(ToolInvocationModel).where(
                                ToolInvocationModel.id == inv_id,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"inv.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def list(
                    self, ctx: object, limit: int = 50, offset: int = 0,
                ) -> list[ToolInvocationModel]:
                    try:
                        result = await self._session.execute(
                            select(ToolInvocationModel)
                            .order_by(ToolInvocationModel.created_at.desc())
                            .limit(limit).offset(offset)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"inv.list failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _permission_repo_content(self) -> str:
        return dedent('''\
            """ToolPermission repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.tool_calling.application.exceptions import (
                ApplicationError,
            )
            from app.modules.tool_calling.infrastructure.models import (
                ToolPermissionModel,
            )


            class PermissionRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(
                    self, ctx: object, perm: ToolPermissionModel,
                ) -> ToolPermissionModel:
                    try:
                        self._session.add(perm)
                        await self._session.flush()
                        return perm
                    except SQLAlchemyError as exc:
                        logger.error(f"perm.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def check(
                    self, ctx: object, tool_id: uuid.UUID, role: str,
                ) -> ToolPermissionModel | None:
                    try:
                        result = await self._session.execute(
                            select(ToolPermissionModel).where(
                                ToolPermissionModel.tool_id == tool_id,
                                ToolPermissionModel.role == role,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"perm.check failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _caches_content(self) -> str:
        return dedent('''\
            """tool_calling caches — Redis (never-raise)"""
            from __future__ import annotations
            import json
            from typing import Any

            import structlog

            log = structlog.get_logger()


            class RedisToolCache:
                def __init__(self, redis: object, ttl: int = 300) -> None:
                    self._redis = redis
                    self._ttl = ttl

                async def get(self, key: str) -> Any | None:
                    try:
                        raw = await self._redis.get(key)
                        return json.loads(raw) if raw else None
                    except Exception as e:
                        log.warning("toolcache.get_failed", key=key, err=str(e))
                        return None

                async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
                    try:
                        await self._redis.set(
                            key, json.dumps(value, default=str),
                            ex=(ttl or self._ttl),
                        )
                        return True
                    except Exception as e:
                        log.warning("toolcache.set_failed", err=str(e))
                        return False
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """tool_calling services — clients · registry · event bus"""
            from __future__ import annotations
            import asyncio
            import json
            import uuid
            from typing import Any

            import structlog

            from app.modules.tool_calling.application.interfaces import (
                EventBus, ToolClient, ToolClientRegistry,
            )
            from app.modules.tool_calling.domain.exceptions import (
                ToolExecutionError,
            )

            log = structlog.get_logger()


            class HttpToolClient:
                """TH: HTTP tool client | EN: HTTP tool client"""
                kind = "http"

                async def invoke(
                    self, *, spec: Any, args: dict[str, Any],
                    secrets: dict[str, str], timeout: int,
                ) -> Any:
                    try:
                        import httpx
                    except ImportError as exc:
                        raise ToolExecutionError("httpx not installed") from exc

                    config = {}
                    try:
                        config = json.loads(spec.parameters_json or "{}")
                    except Exception:
                        config = {}

                    url = config.get("url", "")
                    method = config.get("method", "POST").upper()
                    headers = config.get("headers", {}) or {}
                    headers.update({k: v for k, v in secrets.items()})

                    async with httpx.AsyncClient(timeout=timeout) as client:
                        if method == "GET":
                            resp = await client.get(url, params=args, headers=headers)
                        else:
                            resp = await client.request(
                                method, url, json=args, headers=headers,
                            )
                        resp.raise_for_status()
                        try:
                            return resp.json()
                        except Exception:
                            return {"text": resp.text}


            class PythonToolClient:
                """TH: stub — ต้อง register handler เอง | EN: python tool stub"""
                kind = "python"

                def __init__(self, handlers: dict[str, Any] | None = None) -> None:
                    self._handlers = handlers or {}

                async def invoke(
                    self, *, spec: Any, args: dict[str, Any],
                    secrets: dict[str, str], timeout: int,
                ) -> Any:
                    handler = self._handlers.get(spec.name)
                    if handler is None:
                        raise ToolExecutionError(
                            f"no python handler for {spec.name}",
                        )
                    if asyncio.iscoroutinefunction(handler):
                        return await handler(**args)
                    return handler(**args)


            class DefaultToolClientRegistry(ToolClientRegistry):
                def __init__(self) -> None:
                    self._clients: dict[str, ToolClient] = {
                        "http": HttpToolClient(),
                        "openapi": HttpToolClient(),
                        "python": PythonToolClient(),
                        "sql": PythonToolClient(),
                        "shell": PythonToolClient(),
                        "mcp": PythonToolClient(),
                    }

                def register(self, kind: str, client: ToolClient) -> None:
                    self._clients[kind] = client

                def get(self, kind: str) -> ToolClient:
                    client = self._clients.get(kind)
                    if client is None:
                        raise ToolExecutionError(f"unknown tool kind: {kind}")
                    return client


            class RedisRateLimiter:
                def __init__(self, redis: object) -> None:
                    self._redis = redis

                async def check_and_incr(
                    self, tenant_id: uuid.UUID, user_id: uuid.UUID,
                    tool_id: uuid.UUID, limit_per_min: int,
                ) -> bool:
                    try:
                        key = f"tool:rl:{tenant_id}:{user_id}:{tool_id}"
                        pipe = self._redis.pipeline()
                        pipe.incr(key)
                        pipe.expire(key, 60)
                        results = await pipe.execute()
                        current = int(results[0])
                        return current <= limit_per_min
                    except Exception as e:
                        log.warning("ratelimit.check_failed", err=str(e))
                        return True


            class KafkaEventBus(EventBus):
                def __init__(self, producer: object, topic: str = "tool.events") -> None:
                    self._producer = producer
                    self._topic = topic

                async def publish(self, event: object) -> None:
                    try:
                        payload = {
                            "type": type(event).__name__,
                            "data": {k: str(v) for k, v in vars(event).items()},
                        }
                        await self._producer.send_and_wait(self._topic, payload)
                    except Exception as e:
                        log.warning("event.publish_failed", err=str(e))


            class NoopEventBus(EventBus):
                async def publish(self, event: object) -> None:
                    log.debug("event.noop", type=type(event).__name__)
        ''')

    # ─── PRESENTATION LAYER ─────────────────────────────────────
    def _create_presentation(self) -> None:
        base = f"{self.mod_root}/presentation"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """tool_calling presentation layer"""
        '''))

        self.writer.write(f"{base}/schemas.py", self._schemas_content())
        self.writer.write(f"{base}/docs.py", self._docs_content())
        self.writer.write(f"{base}/dependencies.py", self._dependencies_content())
        self.writer.write(f"{base}/router.py", self._router_content())
        self.writer.write(f"{base}/swagger.py", self._swagger_content())

    def _schemas_content(self) -> str:
        return dedent('''\
            """tool_calling Pydantic v2 schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.tool_calling.domain.enums import (
                RiskLevel, ToolKind, ToolVisibility,
            )


            class ToolCreateRequest(BaseModel):
                name: str = Field(
                    ..., min_length=1, max_length=100,
                    pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
                )
                description: str = Field(default="", max_length=2000)
                parameters_json: dict[str, Any] = Field(default_factory=dict)
                returns_json: dict[str, Any] = Field(default_factory=dict)
                kind: ToolKind = ToolKind.HTTP
                risk_level: RiskLevel = RiskLevel.LOW
                visibility: ToolVisibility = ToolVisibility.TENANT
                timeout_seconds: int = Field(default=30, ge=1, le=600)
                model_config = ConfigDict(extra="forbid")


            class ToolResponse(BaseModel):
                id: str
                name: str
                description: str = ""
                kind: str = "http"
                risk_level: str = "low"
                visibility: str = "tenant"
                timeout_seconds: int = 30
                is_active: bool = True
                model_config = ConfigDict(extra="forbid")


            class ToolDetailResponse(BaseModel):
                id: str
                name: str
                description: str = ""
                parameters_json: dict[str, Any] = Field(default_factory=dict)
                kind: str = "http"
                is_active: bool = True
                model_config = ConfigDict(extra="forbid")


            class InvokeRequest(BaseModel):
                arguments: dict[str, Any] = Field(default_factory=dict)
                role: str = "user"
                model_config = ConfigDict(extra="forbid")


            class InvokeResponse(BaseModel):
                invocation_id: str
                tool_name: str
                status: str
                output: Any = None
                error: str = ""
                latency_ms: int = 0
                model_config = ConfigDict(extra="forbid")


            class InvocationResponse(BaseModel):
                id: str
                tool_id: str
                tool_name: str = ""
                status: str = "SUCCESS"
                latency_ms: int = 0
                created_at: str = ""
                model_config = ConfigDict(extra="forbid")
        ''')

    def _docs_content(self) -> str:
        return dedent('''\
            """tool_calling OpenAPI response examples"""
            from __future__ import annotations

            RESPONSE_TOOL_200 = {
                "description": "Tool detail",
                "content": {"application/json": {"example": {
                    "id": "uuid", "name": "get_weather",
                    "description": "Get weather by city",
                    "parameters_json": {"type": "object"},
                    "kind": "http", "is_active": True,
                }}},
            }
            RESPONSE_INVOKE_200 = {
                "description": "Tool invoked",
                "content": {"application/json": {"example": {
                    "invocation_id": "uuid",
                    "tool_name": "get_weather",
                    "status": "SUCCESS",
                    "output": {"temp": 32},
                    "latency_ms": 145,
                }}},
            }
            RESPONSE_ERROR_403 = {
                "description": "Permission denied",
                "content": {"application/json": {"example": {
                    "detail": "role 'guest' not allowed to invoke get_weather",
                    "code": "PERMISSION_DENIED",
                }}},
            }
            RESPONSE_ERROR_404 = {
                "description": "Not found",
                "content": {"application/json": {"example": {
                    "detail": "tool not found", "code": "NOT_FOUND",
                }}},
            }
            RESPONSE_ERROR_409 = {
                "description": "Conflict",
                "content": {"application/json": {"example": {
                    "detail": "tool exists: get_weather", "code": "CONFLICT",
                }}},
            }
            RESPONSE_ERROR_422 = {
                "description": "Validation error",
                "content": {"application/json": {"example": {
                    "detail": "invalid arguments: missing required: city",
                    "code": "VALIDATION_ERROR",
                }}},
            }
            RESPONSE_ERROR_429 = {
                "description": "Rate limit exceeded",
                "content": {"application/json": {"example": {
                    "detail": "rate limit exceeded for get_weather",
                    "code": "RATE_LIMITED",
                }}},
            }
            RESPONSE_ERROR_504 = {
                "description": "Timeout",
                "content": {"application/json": {"example": {
                    "detail": "tool get_weather timed out",
                    "code": "TIMEOUT",
                }}},
            }
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """tool_calling DI container"""
            from __future__ import annotations
            from typing import Annotated, Any

            from fastapi import Depends
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.core.db import get_session
            from app.modules.tool_calling.application.use_case import (
                ToolCallingUseCase,
            )
            from app.modules.tool_calling.infrastructure.invocation_repository import (
                InvocationRepository,
            )
            from app.modules.tool_calling.infrastructure.permission_repository import (
                PermissionRepository,
            )
            from app.modules.tool_calling.infrastructure.services import (
                DefaultToolClientRegistry, NoopEventBus, RedisRateLimiter,
            )
            from app.modules.tool_calling.infrastructure.tool_repository import (
                ToolRepository,
            )

            _registry: DefaultToolClientRegistry | None = None


            def _get_registry() -> DefaultToolClientRegistry:
                global _registry
                if _registry is None:
                    _registry = DefaultToolClientRegistry()
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


            async def get_tool_use_case(
                session: Annotated[AsyncSession, Depends(get_session)],
            ) -> ToolCallingUseCase:
                redis = await _get_redis()
                bus = await _get_event_bus()
                rate_limiter = RedisRateLimiter(redis) if redis else _NoopRateLimiter()
                return ToolCallingUseCase(
                    tool_repo=ToolRepository(session),
                    registration_repo=_NoopRegistrationRepo(),
                    invocation_repo=InvocationRepository(session),
                    permission_repo=PermissionRepository(session),
                    clients=_get_registry(),
                    rate_limiter=rate_limiter,
                    event_bus=bus,
                )


            class _NoopRateLimiter:
                async def check_and_incr(
                    self, tenant_id: Any, user_id: Any,
                    tool_id: Any, limit_per_min: int,
                ) -> bool:
                    return True


            class _NoopRegistrationRepo:
                async def save(self, ctx: Any, r: Any) -> Any:
                    return r

                async def find_by_tool(self, ctx: Any, tool_id: Any) -> Any | None:
                    return None
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """tool_calling HTTP routers"""
            from __future__ import annotations
            import uuid
            from typing import Annotated, Any

            from fastapi import APIRouter, Depends, HTTPException, Header, status

            from app.modules.tool_calling.application.exceptions import (
                ApplicationError,
            )
            from app.modules.tool_calling.application.use_case import (
                ToolCallingUseCase,
            )
            from app.modules.tool_calling.domain.exceptions import ToolError
            from app.modules.tool_calling.domain.value_objects import ToolSpec
            from app.modules.tool_calling.presentation.dependencies import (
                get_tool_use_case,
            )
            from app.modules.tool_calling.presentation.docs import (
                RESPONSE_ERROR_403, RESPONSE_ERROR_404, RESPONSE_ERROR_409,
                RESPONSE_ERROR_422, RESPONSE_ERROR_429, RESPONSE_ERROR_504,
                RESPONSE_INVOKE_200, RESPONSE_TOOL_200,
            )
            from app.modules.tool_calling.presentation.schemas import (
                InvocationResponse, InvokeRequest, InvokeResponse,
                ToolCreateRequest, ToolDetailResponse, ToolResponse,
            )

            router = APIRouter(prefix="/tools", tags=["Tools"])


            class _CtxStub:
                def __init__(self, tenant_id: uuid.UUID, user_id: uuid.UUID) -> None:
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


            def _raise_http(exc: Exception) -> None:
                if isinstance(exc, ToolError):
                    code = getattr(exc, "code", "DOMAIN_ERROR")
                    http = 400
                    if code == "NOT_FOUND":
                        http = 404
                    elif code == "CONFLICT":
                        http = 409
                    elif code == "PERMISSION_DENIED":
                        http = 403
                    elif code == "VALIDATION_ERROR":
                        http = 422
                    elif code == "RATE_LIMITED":
                        http = 429
                    elif code == "TIMEOUT":
                        http = 504
                    elif code == "PROVIDER_ERROR":
                        http = 502
                    raise HTTPException(
                        status_code=http,
                        detail={"code": code, "message": str(exc)},
                    )
                if isinstance(exc, ApplicationError):
                    raise HTTPException(
                        status_code=getattr(exc, "http_status", 400),
                        detail={
                            "code": getattr(exc, "code", "APP_ERROR"),
                            "message": str(exc),
                        },
                    )
                raise HTTPException(
                    status_code=500,
                    detail={"code": "INTERNAL_ERROR", "message": "internal error"},
                )


            @router.get("", response_model=list[ToolResponse])
            async def list_tools(
                uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
                limit: int = 100,
                offset: int = 0,
            ) -> list[ToolResponse]:
                """TH: list tools | EN: list tools"""
                ctx = await _get_ctx()
                rows = await uc.list_tools(ctx, limit, offset)
                return [ToolResponse(**r) for r in rows]


            @router.post(
                "", response_model=ToolResponse,
                status_code=status.HTTP_201_CREATED,
            )
            async def create_tool(
                payload: ToolCreateRequest,
                uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
            ) -> ToolResponse:
                """TH: register tool | EN: register tool"""
                ctx = await _get_ctx()
                try:
                    spec = ToolSpec(**payload.model_dump())
                    result = await uc.register_tool(ctx, spec)
                    return ToolResponse(**result)
                except (ToolError, ApplicationError) as e:
                    _raise_http(e)
                    raise


            @router.get(
                "/{tool_id}", response_model=ToolDetailResponse,
                responses={200: RESPONSE_TOOL_200, 404: RESPONSE_ERROR_404},
            )
            async def get_tool(
                tool_id: uuid.UUID,
                uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
            ) -> ToolDetailResponse:
                """TH: get tool | EN: get tool"""
                ctx = await _get_ctx()
                try:
                    result = await uc.get_tool(ctx, tool_id)
                    return ToolDetailResponse(**result)
                except (ToolError, ApplicationError) as e:
                    _raise_http(e)
                    raise


            @router.delete("/{tool_id}")
            async def delete_tool(
                tool_id: uuid.UUID,
                uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
            ) -> dict[str, Any]:
                """TH: delete tool (soft) | EN: soft delete"""
                ctx = await _get_ctx()
                try:
                    ok_del = await uc.delete_tool(ctx, tool_id)
                    return {"deleted": ok_del, "tool_id": str(tool_id)}
                except (ToolError, ApplicationError) as e:
                    _raise_http(e)
                    raise


            @router.post(
                "/{tool_id}/invoke",
                response_model=InvokeResponse,
                responses={
                    200: RESPONSE_INVOKE_200,
                    403: RESPONSE_ERROR_403,
                    404: RESPONSE_ERROR_404,
                    422: RESPONSE_ERROR_422,
                    429: RESPONSE_ERROR_429,
                    504: RESPONSE_ERROR_504,
                },
            )
            async def invoke_tool(
                tool_id: uuid.UUID,
                payload: InvokeRequest,
                uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
                idem_key: Annotated[
                    str, Header(alias="Idempotency-Key", min_length=8),
                ] = "",
            ) -> InvokeResponse:
                """TH: invoke tool | EN: invoke tool"""
                ctx = await _get_ctx()
                try:
                    tool = await uc.get_tool(ctx, tool_id)
                    result = await uc.invoke(
                        ctx,
                        tool_name=tool["name"],
                        arguments=payload.arguments,
                        idempotency_key=idem_key,
                        role=payload.role,
                    )
                    return InvokeResponse(
                        invocation_id=result.invocation_id,
                        tool_name=result.tool_name,
                        status=result.status,
                        output=result.output,
                        error=result.error,
                        latency_ms=result.latency_ms,
                    )
                except (ToolError, ApplicationError) as e:
                    _raise_http(e)
                    raise


            @router.get(
                "/invocations/list",
                response_model=list[InvocationResponse],
            )
            async def list_invocations(
                uc: Annotated[ToolCallingUseCase, Depends(get_tool_use_case)],
                limit: int = 50,
                offset: int = 0,
            ) -> list[InvocationResponse]:
                """TH: list invocations | EN: list invocations"""
                ctx = await _get_ctx()
                rows = await uc.list_invocations(ctx, limit, offset)
                return [InvocationResponse(**r) for r in rows]
        ''')

    def _swagger_content(self) -> str:
        return dedent('''\
            """OpenAPI docs — tool_calling module"""
            from __future__ import annotations
            from typing import Any


            def register_tool_calling_openapi(app: object) -> None:
                """TH: register OpenAPI metadata | EN: register OpenAPI metadata"""
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "Tools" for t in tags):
                        tags.append({
                            "name": "Tools",
                            "description": (
                                "โมดูล tool_calling — Function/Tool Calling\\n\\n"
                                "• Tool registry (HTTP / Python / SQL / MCP)\\n"
                                "• Invocation + permissions + rate limit\\n"
                                "• Idempotency-Key support\\n"
                                "• ReAct loop compatible (ใช้กับ llm module)"
                            ),
                            "externalDocs": {
                                "description": "tool_calling Module README",
                                "url": "/docs/README_tool_calling.md",
                            },
                        })
                    info = schema.setdefault("info", {})
                    info.setdefault("x-module", "tool_calling")
                    info.setdefault("x-layer", "5-Intel")
                    info.setdefault("x-prefix", "tool")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent('''\
            """tool_calling module"""
            from .presentation.router import router as tools_router

            __all__ = ["tools_router"]
        '''))

    # ═══════════════════════════════════════════════════════════
    #  2. SQL
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info(f"[SQL] {self.module} — 4 tables + RLS + triggers")
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
-- V001__create_tool_calling.sql | Module: tool_calling | Prefix: tool
-- Schema: public | Tables: tool_definitions, tool_registrations,
--                          tool_invocations, tool_permissions
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."tool_definitions";
CREATE TABLE "public"."tool_definitions" (
  "id"                uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"         uuid NOT NULL,
  "name"              varchar(100) NOT NULL,
  "description"       text NOT NULL DEFAULT '',
  "parameters_json"   text NOT NULL DEFAULT '{}',
  "returns_json"      text NOT NULL DEFAULT '{}',
  "version"           varchar(20) NOT NULL DEFAULT '1.0.0',
  "kind"              varchar(20) NOT NULL DEFAULT 'http',
  "risk_level"        varchar(20) NOT NULL DEFAULT 'low',
  "visibility"        varchar(20) NOT NULL DEFAULT 'tenant',
  "timeout_seconds"   int4 NOT NULL DEFAULT 30,
  "is_active"         bool NOT NULL DEFAULT true,
  "created_at"        timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"        timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "tool_definitions_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_tool_name" UNIQUE ("tenant_id", "name"),
  CONSTRAINT "ck_tool_kind" CHECK (
    kind IN ('http','python','sql','shell','mcp','openapi')
  ),
  CONSTRAINT "ck_tool_risk" CHECK (
    risk_level IN ('low','medium','high','critical')
  ),
  CONSTRAINT "ck_tool_visibility" CHECK (
    visibility IN ('private','tenant','public')
  )
);

CREATE INDEX "ix_tool_def_tenant"
    ON "public"."tool_definitions" USING btree ("tenant_id");
CREATE INDEX "ix_tool_def_kind"
    ON "public"."tool_definitions" USING btree ("kind", "is_active");

DROP TABLE IF EXISTS "public"."tool_registrations";
CREATE TABLE "public"."tool_registrations" (
  "id"                  uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"           uuid NOT NULL,
  "tool_id"             uuid NOT NULL,
  "enabled"             bool NOT NULL DEFAULT true,
  "rate_limit_per_min"  int4 NOT NULL DEFAULT 60,
  "scopes_json"         text NOT NULL DEFAULT '[]',
  "created_at"          timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"          timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "tool_registrations_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_tool_reg_tool" UNIQUE ("tool_id")
);

CREATE INDEX "ix_tool_reg_tenant"
    ON "public"."tool_registrations" USING btree ("tenant_id");

DROP TABLE IF EXISTS "public"."tool_invocations";
CREATE TABLE "public"."tool_invocations" (
  "id"                uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"         uuid NOT NULL,
  "user_id"           uuid NOT NULL,
  "tool_id"           uuid NOT NULL,
  "tool_name"         varchar(100) NOT NULL DEFAULT '',
  "args_json"         text NOT NULL DEFAULT '{}',
  "result_json"       text NOT NULL DEFAULT '{}',
  "status"            varchar(20) NOT NULL DEFAULT 'SUCCESS',
  "latency_ms"        int4 NOT NULL DEFAULT 0,
  "error_code"        varchar(50) NOT NULL DEFAULT '',
  "error_message"     text NOT NULL DEFAULT '',
  "tokens_used"       int4 NOT NULL DEFAULT 0,
  "cost_usd"          numeric(12,8) NOT NULL DEFAULT 0,
  "idempotency_key"   varchar(100) NOT NULL DEFAULT '',
  "created_at"        timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"        timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "tool_invocations_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_tool_inv_status" CHECK (
    status IN ('SUCCESS','ERROR','TIMEOUT','DENIED','RATE_LIMITED')
  )
);

CREATE INDEX "ix_tool_inv_tenant"
    ON "public"."tool_invocations" USING btree ("tenant_id", "created_at" DESC);
CREATE INDEX "ix_tool_inv_tool"
    ON "public"."tool_invocations" USING btree ("tool_id", "created_at" DESC);

DROP TABLE IF EXISTS "public"."tool_permissions";
CREATE TABLE "public"."tool_permissions" (
  "id"          uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"   uuid NOT NULL,
  "tool_id"     uuid NOT NULL,
  "role"        varchar(50) NOT NULL,
  "allowed"     bool NOT NULL DEFAULT true,
  "created_at"  timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"  timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "tool_permissions_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_tool_perm_role" UNIQUE ("tool_id", "role")
);

CREATE INDEX "ix_tool_perm_tenant"
    ON "public"."tool_permissions" USING btree ("tenant_id");

-- ═══ Trigger fn ═══
CREATE OR REPLACE FUNCTION public.set_updated_at_tool()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_tool_def_updated ON "public"."tool_definitions";
CREATE TRIGGER trg_tool_def_updated BEFORE UPDATE
    ON "public"."tool_definitions"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_tool();

DROP TRIGGER IF EXISTS trg_tool_reg_updated ON "public"."tool_registrations";
CREATE TRIGGER trg_tool_reg_updated BEFORE UPDATE
    ON "public"."tool_registrations"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_tool();

DROP TRIGGER IF EXISTS trg_tool_inv_updated ON "public"."tool_invocations";
CREATE TRIGGER trg_tool_inv_updated BEFORE UPDATE
    ON "public"."tool_invocations"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_tool();

DROP TRIGGER IF EXISTS trg_tool_perm_updated ON "public"."tool_permissions";
CREATE TRIGGER trg_tool_perm_updated BEFORE UPDATE
    ON "public"."tool_permissions"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_tool();

-- ═══ RLS ═══
ALTER TABLE "public"."tool_definitions"    ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."tool_registrations"  ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."tool_invocations"    ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."tool_permissions"    ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_tool_def ON "public"."tool_definitions";
CREATE POLICY p_tool_def ON "public"."tool_definitions"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_tool_reg ON "public"."tool_registrations";
CREATE POLICY p_tool_reg ON "public"."tool_registrations"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_tool_inv ON "public"."tool_invocations";
CREATE POLICY p_tool_inv ON "public"."tool_invocations"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_tool_perm ON "public"."tool_permissions";
CREATE POLICY p_tool_perm ON "public"."tool_permissions"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_tool_calling.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."tool_definitions"
    (tenant_id, name, description, parameters_json, kind, risk_level)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'get_current_time',
     'Return current time (demo)', '{"type":"object"}',
     'python', 'low'),
    ('00000000-0000-0000-0000-000000000001', 'get_weather',
     'Get weather for a city (demo)',
     '{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}',
     'http', 'low')
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_tool_calling.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_tool_perm_updated ON "public"."tool_permissions";
DROP TRIGGER IF EXISTS trg_tool_inv_updated  ON "public"."tool_invocations";
DROP TRIGGER IF EXISTS trg_tool_reg_updated  ON "public"."tool_registrations";
DROP TRIGGER IF EXISTS trg_tool_def_updated  ON "public"."tool_definitions";

DROP POLICY IF EXISTS p_tool_perm ON "public"."tool_permissions";
DROP POLICY IF EXISTS p_tool_inv  ON "public"."tool_invocations";
DROP POLICY IF EXISTS p_tool_reg  ON "public"."tool_registrations";
DROP POLICY IF EXISTS p_tool_def  ON "public"."tool_definitions";

DROP TABLE IF EXISTS "public"."tool_permissions"    CASCADE;
DROP TABLE IF EXISTS "public"."tool_invocations"    CASCADE;
DROP TABLE IF EXISTS "public"."tool_registrations"  CASCADE;
DROP TABLE IF EXISTS "public"."tool_definitions"    CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_tool();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "tool_001"
        prev = self._get_head_revision()
        content = f'''"""add tool_calling tables

Revision ID: {rev}
Revises: {prev}
Create Date: {datetime.now(UTC).date().isoformat()}

TH: สร้างตาราง tool_calling 4 ตาราง (schema: public, prefix: tool_)
EN: create 4 tool_calling tables (public schema, tool_ prefix)
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
    op.create_table(
        "tool_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("parameters_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("returns_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("version", sa.String(20), nullable=False, server_default="1.0.0"),
        sa.Column("kind", sa.String(20), nullable=False, server_default="http"),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="low"),
        sa.Column("visibility", sa.String(20), nullable=False, server_default="tenant"),
        sa.Column("timeout_seconds", sa.Integer, nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_tool_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "tool_registrations",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("rate_limit_per_min", sa.Integer, nullable=False, server_default="60"),
        sa.Column("scopes_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tool_id", name="uq_tool_reg_tool"),
        schema=SCHEMA,
    )
    op.create_table(
        "tool_invocations",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("args_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("result_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="SUCCESS"),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(50), nullable=False, server_default=""),
        sa.Column("error_message", sa.Text, nullable=False, server_default=""),
        sa.Column("tokens_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Numeric(12, 8), nullable=False, server_default="0"),
        sa.Column("idempotency_key", sa.String(100), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "tool_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("allowed", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tool_id", "role", name="uq_tool_perm_role"),
        schema=SCHEMA,
    )

    op.create_index("ix_tool_def_tenant", "tool_definitions", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_tool_def_kind", "tool_definitions", ["kind", "is_active"], schema=SCHEMA)
    op.create_index("ix_tool_reg_tenant", "tool_registrations", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_tool_inv_tenant", "tool_invocations", ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_tool_inv_tool", "tool_invocations", ["tool_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_tool_perm_tenant", "tool_permissions", ["tenant_id"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_tool()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl, short in (
        ("tool_definitions", "def"),
        ("tool_registrations", "reg"),
        ("tool_invocations", "inv"),
        ("tool_permissions", "perm"),
    ):
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")
        op.execute(f\"\"\"
            DROP POLICY IF EXISTS p_tool_{{short}} ON {{SCHEMA}}.{{tbl}};
            CREATE POLICY p_tool_{{short}} ON {{SCHEMA}}.{{tbl}}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        \"\"\")
        op.execute(f\"\"\"
            DROP TRIGGER IF EXISTS trg_tool_{{short}}_updated ON {{SCHEMA}}.{{tbl}};
            CREATE TRIGGER trg_tool_{{short}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_tool();
        \"\"\")


def downgrade() -> None:
    for tbl, short in reversed([
        ("tool_definitions", "def"),
        ("tool_registrations", "reg"),
        ("tool_invocations", "inv"),
        ("tool_permissions", "perm"),
    ]):
        op.execute(f"DROP POLICY IF EXISTS p_tool_{{short}} ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"DROP TRIGGER IF EXISTS trg_tool_{{short}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_tool();")
'''
        self.writer.write(
            f"migrations/versions/{rev}_add_{self.module}_tables.py",
            content,
        )

    def _get_head_revision(self) -> str:
        """TH: หา head revision (ข้ามตัวเอง) | EN: find head (exclude self)"""
        my_rev = "tool_001"
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
                return sorted(heads)[0]
        return "None"

    # ═══════════════════════════════════════════════════════════
    #  4. SWAGGER
    # ═══════════════════════════════════════════════════════════
    def create_swagger(self) -> None:
        info(f"[SWAGGER] {self.module}")
        self.writer.write(
            f"{self.mod_root}/presentation/swagger.py",
            self._swagger_content(),
        )

    # ═══════════════════════════════════════════════════════════
    #  5. POSTMAN
    # ═══════════════════════════════════════════════════════════
    def create_postman(self) -> None:
        info(f"[POSTMAN] {self.module}")
        self.writer.write(
            f"docs/postman/{self.module}.json",
            self._postman_json(),
        )

    def _postman_json(self) -> str:
        return f'''{{
  "info": {{
    "name": "{self.module} API",
    "_postman_id": "{uuid.uuid4()}",
    "description": "Tool Calling Module — registry + invoke + permissions",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  }},
  "variable": [
    {{ "key": "base_url", "value": "http://localhost:8000" }},
    {{ "key": "tool_id", "value": "" }}
  ],
  "item": [
    {{
      "name": "Tools",
      "item": [
        {{
          "name": "List Tools",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/tools?limit=100",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "tools"],
              "query": [{{ "key": "limit", "value": "100" }}]
            }}
          }}
        }},
        {{
          "name": "Register Tool",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/tools",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "tools"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"name\\": \\"get_weather\\",\\n  \\"description\\": \\"Get weather by city\\",\\n  \\"parameters_json\\": {{\\n    \\"type\\": \\"object\\",\\n    \\"properties\\": {{\\"city\\": {{\\"type\\": \\"string\\"}}}},\\n    \\"required\\": [\\"city\\"]\\n  }},\\n  \\"kind\\": \\"http\\",\\n  \\"risk_level\\": \\"low\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }},
        {{
          "name": "Invoke Tool",
          "request": {{
            "method": "POST",
            "header": [
              {{ "key": "Content-Type", "value": "application/json" }},
              {{ "key": "Idempotency-Key", "value": "{{{{$guid}}}}" }}
            ],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/tools/{{{{tool_id}}}}/invoke",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "tools", "{{{{tool_id}}}}", "invoke"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"arguments\\": {{\\"city\\": \\"Bangkok\\"}},\\n  \\"role\\": \\"user\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Invocations",
      "item": [
        {{
          "name": "List Invocations",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/tools/invocations/list?limit=50",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "tools", "invocations", "list"],
              "query": [{{ "key": "limit", "value": "50" }}]
            }}
          }}
        }}
      ]
    }}
  ]
}}
'''

    # ═══════════════════════════════════════════════════════════
    #  6. UPDATE APP
    # ═══════════════════════════════════════════════════════════
    def update_app(self) -> None:
        info(f"[UPDATE APP] {self.module}")
        app_file = self.root / self.app_py
        if not app_file.exists():
            warn(f"{self.app_py} not found — skipping")
            return

        content = app_file.read_text(encoding="utf-8")
        original = content

        router_import = (
            "from app.modules.tool_calling.presentation.router "
            "import router as tools_router"
        )
        swagger_import = (
            "from app.modules.tool_calling.presentation.swagger "
            "import register_tool_calling_openapi"
        )

        # 1) router import
        if router_import not in content:
            lines = content.split("\n")
            last = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    last = i
            lines.insert(last + 1, router_import)
            content = "\n".join(lines)
            ok(f"added import: {router_import}")

        # 2) swagger import
        if swagger_import not in content:
            if router_import in content:
                content = content.replace(
                    router_import, router_import + "\n" + swagger_import, 1,
                )
            ok(f"added import: {swagger_import}")

        # 3) add tools_router to routers list
        m = re.search(r"(routers\s*=\s*\[)(.*?)(\n\])", content, re.S)
        if m:
            inner = m.group(2)
            if "tools_router" not in inner:
                inner_new = (
                    inner.rstrip()
                    + "\n    tools_router,  # tool_calling module (Layer 5-Intel)\n"
                )
                content = content[:m.start(2)] + inner_new + content[m.end(2):]
                ok("added tools_router to routers list")

        # 4) OpenAPI tag
        if '"name": "Tools"' not in content:
            tag_line = (
                '            {"name": "Tools", "description": '
                '"Tool Calling — registry + invoke + permissions."},\n'
            )
            m = re.search(
                r'(\{"name":\s*"(?:Health|LLM|RAG|VectorDB)"[^\}]*\},\s*\n)',
                content,
            )
            if m:
                content = content[:m.end(1)] + tag_line + content[m.end(1):]
                ok("added OpenAPI tag: Tools")

        # 5) swagger hook call
        if "register_tool_calling_openapi(app)" not in content:
            include_match = re.search(
                r"(app\.include_router\(tools_router[^\n]*\n)", content,
            )
            call = (
                "\n# TH: Register Tool Calling OpenAPI metadata\n"
                "register_tool_calling_openapi(app)\n"
            )
            if include_match:
                insert_at = include_match.end(1)
                content = content[:insert_at] + call + content[insert_at:]
                ok("called register_tool_calling_openapi(app)")
            else:
                content = (
                    content.rstrip()
                    + "\n\n# Register Tool Calling OpenAPI metadata\n"
                    + "register_tool_calling_openapi(app)\n"
                )
                ok("called register_tool_calling_openapi(app) (end of file)")

        # 6) Save
        if content != original:
            bak = app_file.with_suffix(".py.bak")
            bak.write_bytes(app_file.read_bytes())
            ok(f"backup: {self.app_py}.bak")
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
            warn(f"{self.env_py} not found — skipping")
            return

        content = env_file.read_text(encoding="utf-8")
        original = content

        marker = (
            "# --- module tool_calling "
            "(ToolDefinition / ToolRegistration / ToolInvocation / ToolPermission) ---"
        )
        if marker in content:
            skip("tool_calling block already present in env.py")
            return

        block = f'''{marker}
# TH: tool_calling — 4 models (Layer 5-Intel, schema=public, prefix=tool_)
# EN: tool_calling — 4 models
try:
    from app.modules.tool_calling.infrastructure.models import (  # noqa: F401
        ToolDefinitionModel,
        ToolInvocationModel,
        ToolPermissionModel,
        ToolRegistrationModel,
    )
except ImportError:
    pass


'''
        anchor = "config = context.config"
        idx = content.find(anchor)
        if idx == -1:
            warn("anchor not found — skipping")
            return
        content = content[:idx] + block + content[idx:]

        if content != original:
            bak = env_file.with_suffix(".py.bak")
            bak.write_bytes(env_file.read_bytes())
            ok(f"backup: {self.env_py}.bak")
            env_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.env_py} updated")

    # ═══════════════════════════════════════════════════════════
    #  8. VERIFY
    # ═══════════════════════════════════════════════════════════
    def verify(self) -> None:
        info("[VERIFY] ตรวจสอบ setup")
        issues: list[str] = []

        # 1) swagger.py
        swagger_py = self.root / f"{self.mod_root}/presentation/swagger.py"
        if swagger_py.exists():
            ok("swagger.py exists")
            if "def register_tool_calling_openapi" in swagger_py.read_text(encoding="utf-8"):
                ok("  ✓ has register_tool_calling_openapi()")
            else:
                issues.append("swagger.py missing register_tool_calling_openapi()")
        else:
            issues.append(f"swagger.py NOT FOUND: {swagger_py}")

        # 2) app.py
        app_file = self.root / self.app_py
        if app_file.exists():
            content = app_file.read_text(encoding="utf-8")
            for check in (
                "tools_router",
                "register_tool_calling_openapi",
            ):
                if check in content:
                    ok(f"app.py: {check} ✓")
                else:
                    issues.append(f"app.py missing: {check}")
        else:
            issues.append(f"app.py NOT FOUND: {app_file}")

        # 3) postman.json
        postman = self.root / f"docs/postman/{self.module}.json"
        if postman.exists():
            try:
                data = _json_mod.loads(postman.read_text(encoding="utf-8"))
                ok(f"postman: valid JSON, {len(data.get('item', []))} folders")
            except Exception as e:
                issues.append(f"postman.json invalid: {e}")
        else:
            issues.append(f"postman.json NOT FOUND: {postman}")

        # 4) SQL
        for ver in ("V001", "V002", "V003"):
            d = self.root / self.sql_dir
            matches = list(d.glob(f"{ver}__*{self.module}*.sql")) if d.exists() else []
            if matches:
                ok(f"SQL: {matches[0].name}")
            else:
                issues.append(f"SQL {ver} not found")

        # 5) summary
        print()
        if issues:
            info("═" * 60)
            warn(f"พบ {len(issues)} ปัญหา:")
            for i, msg in enumerate(issues, 1):
                err(f"  {i}. {msg}")
            info("═" * 60)
        else:
            info("═" * 60)
            ok("ALL CHECKS PASSED ✓")
            info("═" * 60)

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
        ok(f"DONE — module: {self.module}  (v{VERSION})")
        info(f"  Schema  : {SCHEMA}")
        info(f"  Prefix  : {self.prefix}_")
        info(f"  Tables  : {len(TABLE_NAMES)}")
        info(f"  Written : {len(self.writer.written)} files")
        info(f"  Skipped : {len(self.writer.skipped)} files")
        info(f"  Backups : {len(self.writer.backups)} files")
        info("═" * 60)
        print()
        print(f"  {C.YELLOW}Next steps:{C.RESET}")
        print(f"    1. Verify:    python create_module_tool_calling.py verify")
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
  create_module_tool_calling.py — Generator v{VERSION}
  Schema: {SCHEMA}  ·  Prefix: tool_
═══════════════════════════════════════════════════════════════

  USAGE
    python create_module_tool_calling.py <action> [options]

  ACTIONS (9)
    create       สร้าง module structure (4 layers)
    sql          สร้าง SQL migrations V001/V002/V003
    alembic      สร้าง Alembic migration
    swagger      สร้าง OpenAPI docs
    postman      สร้าง Postman collection
    update       Update app/app.py
    update-env   Update migrations/env.py
    verify       ตรวจสอบ setup
    all          ทำทุกอย่าง

  OPTIONS
    --force              เขียนทับไฟล์เดิม
    --project-root <p>   Project root (default: .)

  EXAMPLES
    python create_module_tool_calling.py all --force
    python create_module_tool_calling.py verify

  RESULTS
    Swagger:  http://localhost:8000/docs   → tag "Tools"
    Postman:  docs/postman/tool_calling.json
═══════════════════════════════════════════════════════════════
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("module", nargs="?", default=MODULE_NAME)
    parser.add_argument("layer", nargs="?", default="5")
    parser.add_argument("prefix", nargs="?", default=PREFIX)
    parser.add_argument("--force", action="store_true")
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

    gen = ToolCallingModuleGenerator(
        project_root=root,
        module=args.module,
        layer=args.layer,
        prefix=args.prefix,
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

    if args.action != "verify":
        gen.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())