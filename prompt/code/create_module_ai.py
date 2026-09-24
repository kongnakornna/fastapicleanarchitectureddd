#!/usr/bin/env python3
"""
create_module_ai.py — AI Modules Generator v1.0.0

สร้าง 5 AI modules ตาม Clean Architecture + DDD + Event-Driven
Modules: rag · emb · tool · struct · eval
Schema: public · Prefix: rag_ / emb_ / tool_ / so_ / eval_

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
from datetime import UTC, datetime
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
#  MODULE REGISTRY — 5 AI modules
# ═══════════════════════════════════════════════════════════════
MODULES: dict[str, dict] = {
    "rag": {
        "name": "rag",
        "title": "RAG (Retrieval-Augmented Generation)",
        "layer": "5-Intel",
        "prefix": "rag",
        "tables": ("rag_documents", "rag_chunks", "rag_queries", "rag_retrievals"),
        "tag_desc": "Retrieval-Augmented Generation — ค้นหาเอกสาร + เสริมบริบทให้ LLM",
    },
    "emb": {
        "name": "emb",
        "title": "Embeddings",
        "layer": "5-Intel",
        "prefix": "emb",
        "tables": ("emb_models", "emb_vectors", "emb_batches"),
        "tag_desc": "Embeddings — แปลงข้อความเป็น vector สำหรับ semantic search",
    },
    "tool": {
        "name": "tool",
        "title": "Tool Calling (Function Calling)",
        "layer": "5-Intel",
        "prefix": "tool",
        "tables": ("tool_registry", "tool_invocations", "tool_permissions"),
        "tag_desc": "Tool Calling — ให้ LLM เรียกใช้ฟังก์ชัน/API ภายนอก",
    },
    "struct": {
        "name": "struct",
        "title": "Structured Outputs",
        "layer": "5-Intel",
        "prefix": "so",
        "tables": ("so_schemas", "so_generations", "so_validations"),
        "tag_desc": "Structured Outputs — บังคับ LLM ให้ตอบตาม JSON Schema",
    },
    "eval": {
        "name": "eval",
        "title": "AI Evaluation",
        "layer": "6-Monitor",
        "prefix": "eval",
        "tables": ("eval_datasets", "eval_cases", "eval_runs", "eval_scores"),
        "tag_desc": "AI Evaluation — วัดคุณภาพ AI (accuracy, faithfulness, safety)",
    },
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
class AIModuleGenerator:
    def __init__(self, project_root: Path, module_key: str, force: bool = False):
        if module_key not in MODULES:
            raise ValueError(
                f"unknown module: {module_key}. "
                f"Available: {', '.join(MODULES.keys())}"
            )
        self.cfg = MODULES[module_key]
        self.module = self.cfg["name"]
        self.prefix = self.cfg["prefix"]
        self.layer = self.cfg["layer"]
        self.tables = self.cfg["tables"]
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

        self.writer.write(f"{base}/value_objects/__init__.py", dedent(f'''\
            """{self.module} value objects"""
        '''))

        self.writer.write(f"{base}/entities/__init__.py", dedent(f'''\
            """{self.module} entities — alias to infrastructure models"""
            from app.modules.{self.module}.infrastructure.models import (
                {", ".join(self._model_classes())},
            )

            __all__ = {list(self._model_classes())!r}
        '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent(f'''\
            """{self.module} helpers"""
        '''))

    def _model_classes(self) -> list[str]:
        return [self._cls_name(t) for t in self.tables]

    def _cls_name(self, table: str) -> str:
        # rag_documents → RagDocumentsModel
        parts = table.split("_")
        return "".join(p.capitalize() for p in parts) + "Model"

    def _domain_enums(self) -> str:
        if self.module == "rag":
            return dedent('''\
                """RAG enums"""
                from __future__ import annotations
                from enum import Enum


                class DocumentStatus(str, Enum):
                    PENDING = "PENDING"
                    INDEXING = "INDEXING"
                    READY = "READY"
                    FAILED = "FAILED"

                    def __str__(self) -> str:
                        return str(self.value)


                class ChunkStrategy(str, Enum):
                    FIXED = "fixed"
                    SEMANTIC = "semantic"
                    RECURSIVE = "recursive"
                    MARKDOWN = "markdown"

                    def __str__(self) -> str:
                        return str(self.value)


                class RetrievalMode(str, Enum):
                    DENSE = "dense"
                    SPARSE = "sparse"
                    HYBRID = "hybrid"

                    def __str__(self) -> str:
                        return str(self.value)
            ''')
        if self.module == "emb":
            return dedent('''\
                """Embeddings enums"""
                from __future__ import annotations
                from enum import Enum


                class EmbeddingProvider(str, Enum):
                    OPENAI = "openai"
                    COHERE = "cohere"
                    LOCAL = "local"
                    HUGGINGFACE = "huggingface"

                    def __str__(self) -> str:
                        return str(self.value)


                class DistanceMetric(str, Enum):
                    COSINE = "cosine"
                    EUCLIDEAN = "euclidean"
                    DOT = "dot"

                    def __str__(self) -> str:
                        return str(self.value)
            ''')
        if self.module == "tool":
            return dedent('''\
                """Tool Calling enums"""
                from __future__ import annotations
                from enum import Enum


                class ToolStatus(str, Enum):
                    ACTIVE = "ACTIVE"
                    DEPRECATED = "DEPRECATED"
                    DISABLED = "DISABLED"

                    def __str__(self) -> str:
                        return str(self.value)


                class InvocationStatus(str, Enum):
                    PENDING = "PENDING"
                    SUCCESS = "SUCCESS"
                    FAILED = "FAILED"
                    TIMEOUT = "TIMEOUT"

                    def __str__(self) -> str:
                        return str(self.value)


                class RiskLevel(str, Enum):
                    LOW = "low"
                    MEDIUM = "medium"
                    HIGH = "high"
                    CRITICAL = "critical"

                    def __str__(self) -> str:
                        return str(self.value)
            ''')
        if self.module == "struct":
            return dedent('''\
                """Structured Outputs enums"""
                from __future__ import annotations
                from enum import Enum


                class SchemaFormat(str, Enum):
                    JSON_SCHEMA = "json_schema"
                    PYDANTIC = "pydantic"
                    TYPED_DICT = "typed_dict"

                    def __str__(self) -> str:
                        return str(self.value)


                class GenerationStatus(str, Enum):
                    PENDING = "PENDING"
                    VALID = "VALID"
                    INVALID = "INVALID"
                    RETRY = "RETRY"
                    FAILED = "FAILED"

                    def __str__(self) -> str:
                        return str(self.value)
            ''')
        # eval
        return dedent('''\
            """AI Evaluation enums"""
            from __future__ import annotations
            from enum import Enum


            class EvalMetric(str, Enum):
                ACCURACY = "accuracy"
                FAITHFULNESS = "faithfulness"
                RELEVANCE = "relevance"
                PRECISION = "precision"
                RECALL = "recall"
                F1 = "f1"
                ROUGE = "rouge"
                BLEU = "bleu"
                SAFETY = "safety"
                LATENCY = "latency"
                COST = "cost"

                def __str__(self) -> str:
                    return str(self.value)


            class RunStatus(str, Enum):
                PENDING = "PENDING"
                RUNNING = "RUNNING"
                COMPLETED = "COMPLETED"
                FAILED = "FAILED"

                def __str__(self) -> str:
                    return str(self.value)
        ''')

    def _domain_exceptions(self) -> str:
        return dedent(f'''\
            """{self.module} domain exceptions"""
            from __future__ import annotations


            class {self.module.capitalize()}Error(Exception):
                """TH: base error | EN: base error"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class NotFoundError({self.module.capitalize()}Error):
                code = "NOT_FOUND"


            class ValidationError({self.module.capitalize()}Error):
                code = "VALIDATION_ERROR"


            class ProviderError({self.module.capitalize()}Error):
                code = "PROVIDER_ERROR"


            class LimitExceededError({self.module.capitalize()}Error):
                code = "LIMIT_EXCEEDED"


            class SecurityError({self.module.capitalize()}Error):
                code = "SECURITY_ERROR"
        ''')

    def _domain_events(self) -> str:
        return dedent(f'''\
            """{self.module} domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import datetime, timezone


            def _now() -> datetime:
                return datetime.now(timezone.utc)


            @dataclass(frozen=True)
            class {self.module.capitalize()}Created:
                """TH: สร้าง entity | EN: entity created"""
                entity_id: uuid.UUID
                tenant_id: uuid.UUID
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class {self.module.capitalize()}Processed:
                """TH: ประมวลผลเสร็จ | EN: processing completed"""
                entity_id: uuid.UUID
                tenant_id: uuid.UUID
                status: str
                latency_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class {self.module.capitalize()}Failed:
                """TH: ล้มเหลว | EN: failure"""
                entity_id: uuid.UUID
                tenant_id: uuid.UUID
                error_code: str
                message: str
                occurred_at: datetime = field(default_factory=_now)
        ''')

    # ─── APPLICATION LAYER ────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} application layer"""
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent(f'''\
            """{self.module} application exceptions"""
            from __future__ import annotations


            class AppError(Exception):
                code: str = "APP_ERROR"
                http_status: int = 400


            class ValidationAppError(AppError):
                code = "VALIDATION_ERROR"
                http_status = 422


            class NotFoundAppError(AppError):
                code = "NOT_FOUND"
                http_status = 404


            class ConflictAppError(AppError):
                code = "CONFLICT"
                http_status = 409


            class ProviderAppError(AppError):
                code = "PROVIDER_ERROR"
                http_status = 502
        '''))

        self.writer.write(f"{base}/interfaces.py", self._interfaces_content())
        self.writer.write(f"{base}/mappers.py", self._mappers_content())
        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _interfaces_content(self) -> str:
        return dedent(f'''\
            """{self.module} application ports"""
            from __future__ import annotations
            import uuid
            from abc import ABC, abstractmethod
            from datetime import datetime
            from typing import Any, Optional, Protocol, runtime_checkable


            @runtime_checkable
            class RequestContext(Protocol):
                @property
                def tenant_id(self) -> uuid.UUID: ...
                @property
                def user_id(self) -> Optional[uuid.UUID]: ...


            class Repository(ABC):
                """TH: base repository | EN: base repository"""

                @abstractmethod
                async def save(self, ctx: RequestContext, entity: Any) -> Any: ...

                @abstractmethod
                async def find_by_id(
                    self, ctx: RequestContext, entity_id: uuid.UUID,
                ) -> Optional[Any]: ...

                @abstractmethod
                async def find_all(
                    self, ctx: RequestContext, limit: int = 100,
                ) -> list[Any]: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...


            class Cache(ABC):
                @abstractmethod
                async def get(self, key: str) -> Any: ...

                @abstractmethod
                async def set(self, key: str, value: Any, ttl: int = 3600) -> bool: ...
        ''')

    def _mappers_content(self) -> str:
        return dedent(f'''\
            """{self.module} mappers — ORM ↔ dict"""
            from __future__ import annotations
            from typing import Any


            def row_to_dict(row: Any) -> dict[str, Any]:
                """TH: ORM row → dict | EN: ORM row → dict"""
                if row is None:
                    return {{}}
                result: dict[str, Any] = {{}}
                for col in row.__table__.columns:
                    val = getattr(row, col.name, None)
                    result[col.name] = str(val) if val is not None else None
                return result


            def dict_to_row_kwargs(data: dict[str, Any]) -> dict[str, Any]:
                """TH: dict → kwargs สำหรับ ORM | EN: dict → ORM kwargs"""
                return {{k: v for k, v in data.items() if v is not None}}
        ''')

    def _use_case_content(self) -> str:
        base_usecase = dedent(f'''\
            """{self.module} use cases"""
            from __future__ import annotations

            import time
            import uuid
            from datetime import UTC, datetime
            from typing import Any

            import structlog

            from app.modules.{self.module}.application.interfaces import (
                Cache, EventBus, Repository, RequestContext,
            )
            from app.modules.{self.module}.domain.events import (
                {self.module.capitalize()}Created,
                {self.module.capitalize()}Failed,
                {self.module.capitalize()}Processed,
            )

            log = structlog.get_logger()


            class {self.module.capitalize()}UseCase:
                """TH: use cases ของ {self.module} | EN: {self.module} use cases"""

                def __init__(
                    self,
                    repo: Repository,
                    cache: Cache,
                    event_bus: EventBus,
                ) -> None:
                    self._repo = repo
                    self._cache = cache
                    self._bus = event_bus

                async def create(
                    self, ctx: RequestContext, payload: dict[str, Any],
                ) -> dict[str, Any]:
                    """TH: สร้าง entity | EN: create entity"""
                    log.info("{self.module}.create.start")
                    started = time.monotonic()
                    try:
                        entity = await self._repo.save(ctx, payload)
                        latency_ms = int((time.monotonic() - started) * 1000)
                        await self._bus.publish({self.module.capitalize()}Created(
                            entity_id=getattr(entity, "id", uuid.uuid4()),
                            tenant_id=ctx.tenant_id,
                        ))
                        await self._bus.publish({self.module.capitalize()}Processed(
                            entity_id=getattr(entity, "id", uuid.uuid4()),
                            tenant_id=ctx.tenant_id,
                            status="CREATED",
                            latency_ms=latency_ms,
                        ))
                        return {{
                            "id": str(getattr(entity, "id", "")),
                            "status": "CREATED",
                            "latency_ms": latency_ms,
                        }}
                    except Exception as exc:
                        await self._bus.publish({self.module.capitalize()}Failed(
                            entity_id=uuid.uuid4(),
                            tenant_id=ctx.tenant_id,
                            error_code="CREATE_FAILED",
                            message=str(exc),
                        ))
                        raise

                async def get(
                    self, ctx: RequestContext, entity_id: uuid.UUID,
                ) -> dict[str, Any] | None:
                    cached = await self._cache.get(f"{self.module}:{{entity_id}}")
                    if cached:
                        return cached
                    entity = await self._repo.find_by_id(ctx, entity_id)
                    if entity is None:
                        return None
                    from app.modules.{self.module}.application.mappers import row_to_dict
                    data = row_to_dict(entity)
                    await self._cache.set(f"{self.module}:{{entity_id}}", data, ttl=300)
                    return data

                async def list_all(
                    self, ctx: RequestContext, limit: int = 100,
                ) -> list[dict[str, Any]]:
                    rows = await self._repo.find_all(ctx, limit=limit)
                    from app.modules.{self.module}.application.mappers import row_to_dict
                    return [row_to_dict(r) for r in rows]
        ''')
        return base_usecase

    # ─── INFRASTRUCTURE LAYER ─────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} infrastructure layer"""
        '''))

        self.writer.write(f"{base}/models.py", self._models_content())
        self.writer.write(f"{base}/repository.py", self._repository_content())
        self.writer.write(f"{base}/caches.py", self._caches_content())
        self.writer.write(f"{base}/services.py", self._services_content())

    def _models_content(self) -> str:
        header = dedent(f'''\
            """{self.module} SQLAlchemy 2.0 models — schema=public, prefix={self.prefix}_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal
            from typing import Optional

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Float, Index, Integer,
                Numeric, String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: base | EN: base"""
        ''')

        models: list[str] = []
        for table in self.tables:
            cls = self._cls_name(table)
            models.append(self._model_class(table, cls))

        return header + "\n\n" + "\n\n\n".join(models) + "\n\n\n" + dedent(f'''\
            __all__ = {self._model_classes()!r}
        ''')

    def _model_class(self, table: str, cls: str) -> str:
        return dedent(f'''\
            class {cls}(Base):
                __tablename__ = "{table}"
                __table_args__ = (
                    Index("ix_{table}_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    PGUUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    PGUUID(as_uuid=True), nullable=False,
                )
                name: Mapped[str] = mapped_column(
                    String(200), nullable=False, server_default="",
                )
                status: Mapped[str] = mapped_column(
                    String(30), nullable=False, server_default="PENDING",
                )
                payload: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{{}}'::jsonb"),
                )
                error_message: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                latency_ms: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                cost_usd: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
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

    def _repository_content(self) -> str:
        return dedent(f'''\
            """{self.module} repository — SQLAlchemy 2.0 async"""
            from __future__ import annotations
            import uuid
            from typing import Any, Optional

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.{self.module}.application.exceptions import AppError
            from app.modules.{self.module}.application.interfaces import RequestContext


            class Repository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: RequestContext, payload: Any) -> Any:
                    try:
                        if hasattr(payload, "__table__"):
                            row = payload
                        else:
                            row = payload
                        self._session.add(row)
                        await self._session.flush()
                        return row
                    except SQLAlchemyError as exc:
                        logger.error(f"{self.module}.save failed: {{exc}}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(
                    self, ctx: RequestContext, entity_id: uuid.UUID,
                ) -> Optional[Any]:
                    try:
                        from app.modules.{self.module}.infrastructure import models
                        # dynamic — caller supplies model class via subclass
                        return None
                    except Exception as exc:
                        logger.error(f"{self.module}.find failed: {{exc}}")
                        raise AppError(str(exc)) from exc

                async def find_all(
                    self, ctx: RequestContext, limit: int = 100,
                ) -> list[Any]:
                    return []
        ''')

    def _caches_content(self) -> str:
        return dedent(f'''\
            """{self.module} cache — Redis (never-raise)"""
            from __future__ import annotations
            import json
            from typing import Any, Optional

            import structlog

            from app.modules.{self.module}.application.interfaces import Cache

            log = structlog.get_logger()


            class RedisCache(Cache):
                def __init__(self, redis: object, prefix: str = "{self.module}:") -> None:
                    self._redis = redis
                    self._prefix = prefix

                async def get(self, key: str) -> Optional[Any]:
                    try:
                        raw = await self._redis.get(self._prefix + key)
                        if raw is None:
                            return None
                        if isinstance(raw, bytes):
                            raw = raw.decode("utf-8")
                        return json.loads(raw)
                    except Exception as exc:
                        log.warning("cache.get_failed", key=key, err=str(exc))
                        return None

                async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
                    try:
                        await self._redis.set(
                            self._prefix + key,
                            json.dumps(value, default=str),
                            ex=ttl,
                        )
                        return True
                    except Exception as exc:
                        log.warning("cache.set_failed", key=key, err=str(exc))
                        return False


            class NoopCache(Cache):
                async def get(self, key: str) -> Optional[Any]:
                    return None

                async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
                    return False
        ''')

    def _services_content(self) -> str:
        return dedent(f'''\
            """{self.module} infrastructure services"""
            from __future__ import annotations
            from typing import Any

            import structlog

            from app.modules.{self.module}.application.interfaces import EventBus

            log = structlog.get_logger()


            class LoggingEventBus(EventBus):
                """TH: log event (dev) | EN: log event bus"""

                async def publish(self, event: object) -> None:
                    log.info("event.published", type=type(event).__name__)


            class KafkaEventBus(EventBus):
                def __init__(self, producer: object, topic: str = "{self.module}.events") -> None:
                    self._producer = producer
                    self._topic = topic

                async def publish(self, event: object) -> None:
                    try:
                        payload = {{
                            "type": type(event).__name__,
                            "data": {{k: str(v) for k, v in vars(event).items()}},
                        }}
                        await self._producer.send_and_wait(self._topic, payload)
                    except Exception as exc:
                        log.warning("event.publish_failed", err=str(exc))
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
        return dedent(f'''\
            """{self.module} Pydantic v2 schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class CreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(..., min_length=1, max_length=200)
                payload: dict[str, Any] = Field(default_factory=dict)


            class EntityResponse(BaseModel):
                model_config = ConfigDict(extra="forbid")
                id: str
                status: str = "CREATED"
                latency_ms: int = 0
                model_extra: dict[str, Any] = Field(default_factory=dict)


            class ListResponse(BaseModel):
                model_config = ConfigDict(extra="forbid")
                items: list[dict[str, Any]] = Field(default_factory=list)
                total: int = 0
        ''')

    def _dependencies_content(self) -> str:
        return dedent(f'''\
            """{self.module} DI container"""
            from __future__ import annotations
            from dataclasses import dataclass
            from typing import Annotated, Optional
            import uuid

            from fastapi import Depends, Header
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.{self.module}.application.use_case import (
                {self.module.capitalize()}UseCase,
            )
            from app.modules.{self.module}.infrastructure.caches import (
                NoopCache, RedisCache,
            )
            from app.modules.{self.module}.infrastructure.repository import Repository
            from app.modules.{self.module}.infrastructure.services import LoggingEventBus


            @dataclass
            class Ctx:
                tenant_id: uuid.UUID
                user_id: Optional[uuid.UUID]


            async def get_db() -> AsyncSession:
                """TH: override ผ่าน app.state | EN: override via app.state"""
                raise RuntimeError(
                    "get_db not configured — override with app.dependency_overrides"
                )


            async def get_ctx(
                x_tenant_id: Annotated[str, Header(alias="X-Tenant-Id")],
                x_user_id: Annotated[Optional[str], Header(alias="X-User-Id")] = None,
            ) -> Ctx:
                tenant_id = uuid.UUID(x_tenant_id)
                user_id = uuid.UUID(x_user_id) if x_user_id else None
                return Ctx(tenant_id=tenant_id, user_id=user_id)


            async def get_use_case(
                db: Annotated[AsyncSession, Depends(get_db)],
            ) -> {self.module.capitalize()}UseCase:
                return {self.module.capitalize()}UseCase(
                    repo=Repository(db),
                    cache=NoopCache(),
                    event_bus=LoggingEventBus(),
                )
        ''')

    def _router_content(self) -> str:
        return dedent(f'''\
            """{self.module} HTTP router"""
            from __future__ import annotations
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException, status

            from app.modules.{self.module}.application.use_case import (
                {self.module.capitalize()}UseCase,
            )
            from app.modules.{self.module}.presentation.dependencies import (
                Ctx, get_ctx, get_use_case,
            )
            from app.modules.{self.module}.presentation.schemas import (
                CreateRequest, EntityResponse, ListResponse,
            )

            router = APIRouter(prefix="/{self.module}", tags=["{self.module.upper()}"])


            @router.post(
                "",
                response_model=EntityResponse,
                status_code=status.HTTP_201_CREATED,
                summary="Create entity",
                operation_id="{self.module}_create",
            )
            async def create(
                payload: CreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[{self.module.capitalize()}UseCase, Depends(get_use_case)],
            ) -> EntityResponse:
                result = await uc.create(ctx, payload.model_dump())
                return EntityResponse(**result)


            @router.get(
                "/{{entity_id}}",
                response_model=dict,
                summary="Get entity",
                operation_id="{self.module}_get",
            )
            async def get(
                entity_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[{self.module.capitalize()}UseCase, Depends(get_use_case)],
            ) -> dict:
                data = await uc.get(ctx, entity_id)
                if data is None:
                    raise HTTPException(
                        status.HTTP_404_NOT_FOUND, detail="not found",
                    )
                return data


            @router.get(
                "",
                response_model=ListResponse,
                summary="List entities",
                operation_id="{self.module}_list",
            )
            async def list_all(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[{self.module.capitalize()}UseCase, Depends(get_use_case)],
                limit: int = 100,
            ) -> ListResponse:
                items = await uc.list_all(ctx, limit=limit)
                return ListResponse(items=items, total=len(items))
        ''')

    def _swagger_content(self) -> str:
        return dedent(f'''\
            """OpenAPI docs — {self.module}"""
            from __future__ import annotations
            from typing import Any


            def register_{self.module}_openapi(app: object) -> None:
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "{self.module.upper()}" for t in tags):
                        tags.append({{
                            "name": "{self.module.upper()}",
                            "description": "{self.cfg['tag_desc']}",
                            "externalDocs": {{
                                "description": "{self.module} module README",
                                "url": "/docs/README_{self.module}.md",
                            }},
                        }})
                    info = schema.setdefault("info", {{}})
                    info.setdefault("x-module", "{self.module}")
                    info.setdefault("x-layer", "{self.layer}")
                    info.setdefault("x-prefix", "{self.prefix}")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent(f'''\
            """{self.module} module"""
            from .presentation.router import router as {self.module}_router

            __all__ = ["{self.module}_router"]
        '''))

    # ═══════════════════════════════════════════════════════════
    #  2. SQL
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info(f"[SQL] {self.module} — {self.tables}")
        self.writer.write(
            f"{self.sql_dir}/V001__create_{self.module}.sql",
            self._v001_sql(),
        )
        self.writer.write(
            f"{self.sql_dir}/V003__rollback_{self.module}.sql",
            self._v003_sql(),
        )

    def _v001_sql(self) -> str:
        parts: list[str] = []
        for table in self.tables:
            parts.append(f'''DROP TABLE IF EXISTS "public"."{table}";
CREATE TABLE "public"."{table}" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "name"           varchar(200) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "status"         varchar(30) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'PENDING'::character varying,
  "payload"        jsonb NOT NULL DEFAULT '{{}}'::jsonb,
  "error_message"  text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "latency_ms"     int4 NOT NULL DEFAULT 0,
  "cost_usd"       numeric(12,8) NOT NULL DEFAULT 0,
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "{table}_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "ix_{table}_tenant"
    ON "public"."{table}" USING btree ("tenant_id");

DROP TRIGGER IF EXISTS trg_{table}_updated ON "public"."{table}";
CREATE TRIGGER trg_{table}_updated BEFORE UPDATE
    ON "public"."{table}"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{self.prefix}();

ALTER TABLE "public"."{table}" ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_{table} ON "public"."{table}";
CREATE POLICY p_{table} ON "public"."{table}"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);''')
        body = "\n\n".join(parts)

        return f'''-- ═══════════════════════════════════════════════════════════════
-- V001__create_{self.module}.sql | Module: {self.module} | Prefix: {self.prefix}_
-- Schema: public | Tables: {", ".join(self.tables)}
-- ═══════════════════════════════════════════════════════════════
BEGIN;

CREATE OR REPLACE FUNCTION public.set_updated_at_{self.prefix}()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

{body}

COMMIT;
'''

    def _v003_sql(self) -> str:
        drops: list[str] = []
        for table in reversed(self.tables):
            drops.append(
                f'DROP POLICY IF EXISTS p_{table} ON "public"."{table}";\n'
                f'DROP TRIGGER IF EXISTS trg_{table}_updated ON "public"."{table}";\n'
                f'DROP TABLE IF EXISTS "public"."{table}" CASCADE;'
            )
        body = "\n\n".join(drops)
        return f'''-- V003__rollback_{self.module}.sql
BEGIN;

{body}

DROP FUNCTION IF EXISTS public.set_updated_at_{self.prefix}();

COMMIT;
'''

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = f"{self.module}_001"
        content = f'''"""add {self.module} tables

Revision ID: {rev}
Revises: None
Create Date: {datetime.now(UTC).date().isoformat()}
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
    """Create {self.module} tables"""
    for tbl in {list(self.tables)!r}:
        op.create_table(
            tbl,
            sa.Column("id", postgresql.UUID(as_uuid=True),
                      primary_key=True,
                      server_default=sa.text("gen_random_uuid()")),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("name", sa.String(200), nullable=False, server_default=""),
            sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"),
            sa.Column("payload", postgresql.JSONB, nullable=False,
                      server_default=sa.text("'{{}}'::jsonb")),
            sa.Column("error_message", sa.Text, nullable=False, server_default=""),
            sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
            sa.Column("cost_usd", sa.Numeric(12, 8), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.func.now()),
            schema=SCHEMA,
        )
        op.create_index(f"ix_{{tbl}}_tenant", tbl, ["tenant_id"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_{self.prefix}()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in {list(self.tables)!r}:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE TRIGGER trg_{{tbl}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_{self.prefix}();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"DROP POLICY IF EXISTS p_{{tbl}} ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE POLICY p_{{tbl}} ON {{SCHEMA}}.{{tbl}}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        """)


def downgrade() -> None:
    """Drop {self.module} tables"""
    for tbl in reversed({list(self.tables)!r}):
        op.execute(f"DROP POLICY IF EXISTS p_{{tbl}} ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_{self.prefix}();")
'''
        self.writer.write(f"migrations/versions/{rev}_add_{self.module}_tables.py", content)

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
            ],
            "item": [
                {
                    "name": "Create",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.module}",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.module],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"example","payload":{}}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "List",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.module}",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.module],
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
            f"import router as {self.module}_router"
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

        if f"{self.module}_router," not in content:
            m = re.search(r"(routers\s*=\s*\[)(.*?)(\n\])", content, re.S)
            if m:
                inner = m.group(2)
                inner_new = (
                    inner.rstrip()
                    + f"\n    {self.module}_router,  # {self.module} module\n"
                )
                content = content[:m.start(2)] + inner_new + content[m.end(2):]

        if f"register_{self.module}_openapi(app)" not in content:
            m = re.search(
                rf"(app\.include_router\({self.module}_router[^\n]*\n)",
                content,
            )
            if m:
                insert_at = m.end(1)
                call = f"register_{self.module}_openapi(app)\n"
                content = content[:insert_at] + call + content[insert_at:]

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
        {", ".join(self._model_classes())},
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

        swagger_py = self.root / f"{self.mod_root}/presentation/swagger.py"
        if swagger_py.exists():
            ok("swagger.py exists")
        else:
            issues.append(f"swagger.py missing: {swagger_py}")

        app_file = self.root / self.app_py
        if app_file.exists():
            content = app_file.read_text(encoding="utf-8")
            for check in (
                f"{self.module}_router",
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
create_module_ai.py — AI Modules Generator v{VERSION}

USAGE
    python create_module_ai.py <action> <module> [options]

MODULES (5)
    rag      RAG (Retrieval-Augmented Generation)
    emb      Embeddings
    tool     Tool Calling (Function Calling)
    struct   Structured Outputs
    eval     AI Evaluation

ACTIONS (9)
    create       สร้าง module structure (4 layers)
    sql          สร้าง SQL migrations
    alembic      สร้าง Alembic migration
    swagger      สร้าง OpenAPI docs
    postman      สร้าง Postman collection
    update       อัปเดต app/app.py
    update-env   อัปเดต migrations/env.py
    verify       ตรวจสอบ setup
    all          ทำทุกอย่าง

EXAMPLES
    python create_module_ai.py all rag
    python create_module_ai.py create emb --force
    python create_module_ai.py verify tool
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("module", nargs="?", default="rag")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--help", action="store_true")

    args, _ = parser.parse_known_args()

    if args.help or args.action == "help":
        print(HELP)
        return 0

    if args.module not in MODULES:
        err(f"unknown module: {args.module}")
        print(f"Available: {', '.join(MODULES.keys())}")
        return 1

    if args.action not in ACTIONS:
        err(f"unknown action: {args.action}")
        print(HELP)
        return 1

    root = Path(args.project_root).resolve()
    if not root.exists():
        err(f"root not found: {root}")
        return 1

    gen = AIModuleGenerator(root, args.module, force=args.force)

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