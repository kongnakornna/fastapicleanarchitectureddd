#!/usr/bin/env python3
"""
create_module_embeddings.py — Embeddings Module Generator v1.0.0

สร้าง module embeddings ตาม Clean Architecture + DDD + Event-Driven
Module: embeddings · Prefix: emb_ · Schema: public
Layer: 5-Intel · Depends: (base)

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
#  MODULE CONFIG
# ═══════════════════════════════════════════════════════════════
MODULE = {
    "name": "embeddings",
    "title": "Embeddings Service",
    "layer": "5-Intel",
    "prefix": "emb",
    "tag": "Embeddings",
    "tag_desc": "Embeddings — Text to Vector (OpenAI / Cohere / HF / BGE)",
    "depends": [],
    "tables": (
        "emb_providers",
        "emb_models",
        "emb_vectors",
        "emb_batches",
        "emb_cache",
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
class AIModuleGenerator:
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
            """embeddings value objects"""
            from .embedding_request import EmbeddingRequest
            from .embedding_result import EmbeddingResult
            from .batch_config import BatchConfig

            __all__ = ["EmbeddingRequest", "EmbeddingResult", "BatchConfig"]
        '''))

        self.writer.write(f"{base}/value_objects/embedding_request.py", dedent('''\
            """EmbeddingRequest VO"""
            from __future__ import annotations
            from typing import Optional
            from pydantic import BaseModel, ConfigDict, Field


            class EmbeddingRequest(BaseModel):
                """TH: คำขอ embedding | EN: Embedding request"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                model: str = Field(min_length=1, max_length=100)
                input: list[str] = Field(min_length=1)
                normalize: bool = True
                dimensions: Optional[int] = Field(default=None, ge=1, le=8192)
                encoding_format: str = Field(
                    default="float", pattern="^(float|base64)$",
                )
        '''))

        self.writer.write(f"{base}/value_objects/embedding_result.py", dedent('''\
            """EmbeddingResult VO"""
            from __future__ import annotations
            from pydantic import BaseModel, ConfigDict, Field


            class EmbeddingResult(BaseModel):
                """TH: ผลลัพธ์ embedding | EN: Embedding result"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                vector: list[float]
                dimension: int = Field(ge=1)
                tokens: int = Field(ge=0, default=0)
                cached: bool = False

                @classmethod
                def from_vector(
                    cls, vector: list[float], *, tokens: int = 0,
                    cached: bool = False,
                ) -> "EmbeddingResult":
                    return cls(
                        vector=vector, dimension=len(vector),
                        tokens=tokens, cached=cached,
                    )
        '''))

        self.writer.write(f"{base}/value_objects/batch_config.py", dedent('''\
            """BatchConfig VO"""
            from __future__ import annotations
            from pydantic import BaseModel, ConfigDict, Field


            class BatchConfig(BaseModel):
                """TH: การตั้งค่า batch | EN: Batch config"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                batch_size: int = Field(default=64, ge=1, le=2048)
                max_concurrency: int = Field(default=4, ge=1, le=32)
                retry: int = Field(default=3, ge=0, le=10)
        '''))

        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """embeddings entities"""
            from .provider import EmbProvider
            from .model import EmbModel
            from .vector import EmbVector
            from .batch import EmbBatch
            from .cache import EmbCache

            __all__ = ["EmbProvider", "EmbModel", "EmbVector", "EmbBatch", "EmbCache"]
        '''))

        for name, cls, model in (
            ("provider", "EmbProvider", "EmbProviderModel"),
            ("model", "EmbModel", "EmbModelModel"),
            ("vector", "EmbVector", "EmbVectorModel"),
            ("batch", "EmbBatch", "EmbBatchModel"),
            ("cache", "EmbCache", "EmbCacheModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias to ORM"""
                from __future__ import annotations
                from app.modules.{self.module}.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """embeddings helpers"""
            from .hasher import content_hash
            from .normalizer import normalize_vector

            __all__ = ["content_hash", "normalize_vector"]
        '''))

        self.writer.write(f"{base}/helpers/hasher.py", dedent('''\
            """hasher"""
            from __future__ import annotations
            import hashlib


            def content_hash(text: str, prefix: str = "") -> str:
                """TH: hash ข้อความ | EN: content hash"""
                return hashlib.sha256(
                    (prefix + text).encode("utf-8")
                ).hexdigest()
        '''))

        self.writer.write(f"{base}/helpers/normalizer.py", dedent('''\
            """normalizer"""
            from __future__ import annotations
            import math


            def normalize_vector(vector: list[float]) -> list[float]:
                """TH: L2 normalize | EN: L2 normalize"""
                if not vector:
                    return vector
                norm = math.sqrt(sum(x * x for x in vector))
                if norm <= 0.0:
                    return vector
                return [x / norm for x in vector]
        '''))

    def _domain_enums(self) -> str:
        return dedent('''\
            """embeddings enums"""
            from __future__ import annotations
            from enum import Enum


            class EmbeddingProviderType(str, Enum):
                """TH: ประเภทผู้ให้บริการ | EN: Provider type"""
                OPENAI = "openai"
                COHERE = "cohere"
                VOYAGE = "voyage"
                HUGGINGFACE = "huggingface"
                BGE = "bge"
                LOCAL = "local"

                def __str__(self) -> str:
                    return str(self.value)


            class BatchStatus(str, Enum):
                """TH: สถานะ batch | EN: Batch status"""
                PENDING = "PENDING"
                RUNNING = "RUNNING"
                DONE = "DONE"
                FAILED = "FAILED"
                CANCELLED = "CANCELLED"

                def __str__(self) -> str:
                    return str(self.value)


            class DistanceMetric(str, Enum):
                """TH: metric วัดระยะ | EN: Distance metric"""
                COSINE = "cosine"
                L2 = "l2"
                IP = "ip"

                def __str__(self) -> str:
                    return str(self.value)
        ''')

    def _domain_exceptions(self) -> str:
        return dedent('''\
            """embeddings domain exceptions"""
            from __future__ import annotations


            class EmbeddingError(Exception):
                """TH: base | EN: base"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class ProviderNotFoundError(EmbeddingError):
                code = "NOT_FOUND"


            class ModelNotFoundError(EmbeddingError):
                code = "NOT_FOUND"


            class VectorNotFoundError(EmbeddingError):
                code = "NOT_FOUND"


            class DimensionMismatchError(EmbeddingError):
                code = "VALIDATION_ERROR"


            class ProviderError(EmbeddingError):
                code = "PROVIDER_ERROR"


            class RateLimitExceededError(EmbeddingError):
                code = "RATE_LIMITED"


            class BatchNotFoundError(EmbeddingError):
                code = "NOT_FOUND"


            class TokenLimitExceededError(EmbeddingError):
                code = "LIMIT_EXCEEDED"
        ''')

    def _domain_events(self) -> str:
        return dedent('''\
            """embeddings domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import datetime, timezone


            def _now():
                return datetime.now(timezone.utc)


            @dataclass(frozen=True)
            class EmbeddingCreated:
                vector_id: uuid.UUID
                tenant_id: uuid.UUID
                model_id: uuid.UUID
                dimension: int
                tokens: int
                cached: bool
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class BatchStarted:
                batch_id: uuid.UUID
                tenant_id: uuid.UUID
                total: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class BatchCompleted:
                batch_id: uuid.UUID
                tenant_id: uuid.UUID
                completed: int
                failed: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class BatchFailed:
                batch_id: uuid.UUID
                tenant_id: uuid.UUID
                error: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class CacheHit:
                tenant_id: uuid.UUID
                model_id: uuid.UUID
                hash: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class CacheMiss:
                tenant_id: uuid.UUID
                model_id: uuid.UUID
                hash: str
                occurred_at: datetime = field(default_factory=_now)
        ''')

    # ─── APPLICATION LAYER ────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} application layer"""
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """embeddings application exceptions"""
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


            class ProviderAppError(AppError):
                code = "PROVIDER_ERROR"
                http_status = 502


            class RateLimitAppError(AppError):
                code = "RATE_LIMITED"
                http_status = 429


            class TokenLimitAppError(AppError):
                code = "LIMIT_EXCEEDED"
                http_status = 402
        '''))

        self.writer.write(f"{base}/interfaces.py", self._interfaces_content())
        self.writer.write(f"{base}/mappers.py", self._mappers_content())
        self.writer.write(f"{base}/utils.py", self._utils_content())
        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _interfaces_content(self) -> str:
        return dedent('''\
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
        ''')

    def _mappers_content(self) -> str:
        return dedent('''\
            """embeddings mappers — ORM → dict"""
            from __future__ import annotations
            from typing import Any


            def provider_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "name": row.name,
                    "provider_type": row.provider_type,
                    "base_url": row.base_url or "",
                    "priority": row.priority or 100,
                    "is_active": bool(row.is_active),
                }


            def model_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "name": row.name,
                    "display_name": row.display_name or "",
                    "dimension": row.dimension,
                    "max_tokens": row.max_tokens or 8192,
                    "normalize": bool(row.normalize),
                    "is_active": bool(row.is_active),
                }


            def vector_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "model_id": str(row.model_id),
                    "source_hash": row.source_hash,
                    "dimension": row.dimension,
                }


            def batch_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "model_id": str(row.model_id),
                    "total": row.total or 0,
                    "completed": row.completed or 0,
                    "failed": row.failed or 0,
                    "status": row.status,
                }
        ''')

    def _utils_content(self) -> str:
        return dedent('''\
            """embeddings application utils"""
            from __future__ import annotations
            import json
            import time
            from typing import Any

            from app.modules.embeddings.domain.helpers.hasher import content_hash


            def make_cache_key(tenant_id: str, model: str, text: str) -> str:
                h = content_hash(text)
                return f"emb:cache:{tenant_id}:{model}:{h}"


            def make_vector_hash(text: str, model: str) -> str:
                return content_hash(text, prefix=f"{model}:")


            def vector_to_json(vec: list[float]) -> str:
                return json.dumps(vec, separators=(",", ":"))


            def json_to_vector(raw: Any) -> list[float]:
                if isinstance(raw, list):
                    return [float(x) for x in raw]
                if isinstance(raw, str):
                    try:
                        return [float(x) for x in json.loads(raw)]
                    except Exception:
                        return []
                return []


            def ms_now() -> int:
                return int(time.time() * 1000)
        ''')

    def _use_case_content(self) -> str:
        return dedent('''\
            """embeddings use cases"""
            from __future__ import annotations
            import asyncio
            import logging
            import time
            import uuid
            from typing import Any, Optional

            from app.modules.embeddings.application.exceptions import (
                NotFoundAppError, ProviderAppError, RateLimitAppError,
            )
            from app.modules.embeddings.application.utils import (
                make_cache_key, make_vector_hash, ms_now, vector_to_json,
            )
            from app.modules.embeddings.domain.events import (
                BatchStarted, EmbeddingCreated,
            )
            from app.modules.embeddings.domain.helpers.normalizer import (
                normalize_vector,
            )
            from app.modules.embeddings.domain.value_objects import (
                BatchConfig, EmbeddingRequest, EmbeddingResult,
            )

            logger = logging.getLogger(__name__)

            _MAX_RETRIES = 3
            _BACKOFF = [1.0, 2.0, 4.0]
            _CACHE_TTL = 86400


            class EmbeddingUseCase:
                """TH: use case หลัก | EN: core use case"""

                def __init__(self, **deps: Any) -> None:
                    for key, value in deps.items():
                        setattr(self, f"_{key}", value)

                async def embed(
                    self, ctx: Any, req: EmbeddingRequest,
                ) -> list[EmbeddingResult]:
                    """TH: embed หลายข้อความ | EN: embed many"""
                    if not req.input:
                        return []

                    model = await self._models.find_by_name(ctx, req.model)
                    if model is None or not model.is_active:
                        raise NotFoundAppError(f"model not found: {req.model}")

                    provider = await self._providers.find_by_id(ctx, model.provider_id)
                    if provider is None or not provider.is_active:
                        raise NotFoundAppError("provider not found")

                    try:
                        allowed = await self._rate.check(
                            ctx.tenant_id, ctx.user_id or ctx.tenant_id,
                            len(req.input),
                        )
                        if not allowed:
                            raise RateLimitAppError("rate limit exceeded")
                    except RateLimitAppError:
                        raise
                    except Exception as exc:
                        logger.debug("rate limiter fail-open: %s", exc)

                    results: list[Optional[EmbeddingResult]] = [None] * len(req.input)
                    pending_idx: list[int] = []
                    pending_text: list[str] = []

                    for i, text in enumerate(req.input):
                        key = make_cache_key(str(ctx.tenant_id), req.model, text)
                        try:
                            cached_vec = await self._cache.get(key)
                            if cached_vec:
                                results[i] = EmbeddingResult.from_vector(
                                    cached_vec, cached=True,
                                )
                                continue
                        except Exception as exc:
                            logger.debug("cache get failed: %s", exc)
                        pending_idx.append(i)
                        pending_text.append(text)

                    if pending_text:
                        client = self._registry.get_client(provider)
                        vectors = await self._call_with_retry(
                            client, pending_text, req.model,
                            normalize=req.normalize,
                            dimensions=req.dimensions,
                        )

                        for j, vec in enumerate(vectors):
                            idx = pending_idx[j]
                            text = pending_text[j]
                            if req.normalize:
                                vec = normalize_vector(vec)
                            if req.dimensions and len(vec) > req.dimensions:
                                vec = vec[: req.dimensions]

                            results[idx] = EmbeddingResult.from_vector(vec)
                            key = make_cache_key(
                                str(ctx.tenant_id), req.model, text,
                            )
                            try:
                                await self._cache.set(key, vec, ttl=_CACHE_TTL)
                            except Exception as exc:
                                logger.debug("cache set failed: %s", exc)

                            try:
                                h = make_vector_hash(text, req.model)
                                await self._vectors.save(ctx, {
                                    "tenant_id": ctx.tenant_id,
                                    "model_id": model.id,
                                    "source_hash": h,
                                    "source_text": text[:2000],
                                    "vector_json": vector_to_json(vec),
                                    "dimension": len(vec),
                                    "metadata_json": "{}",
                                })
                            except Exception as exc:
                                logger.debug("vector persist failed: %s", exc)

                        if self._bus:
                            try:
                                await self._bus.publish(EmbeddingCreated(
                                    vector_id=uuid.uuid4(),
                                    tenant_id=ctx.tenant_id,
                                    model_id=model.id,
                                    dimension=len(vectors[0]) if vectors else 0,
                                    tokens=sum(len(t) // 4 for t in pending_text),
                                    cached=False,
                                ))
                            except Exception as exc:
                                logger.debug("publish failed: %s", exc)

                    return [r for r in results if r is not None]

                async def embed_batch(
                    self, ctx: Any, *,
                    model_name: str, texts: list[str],
                    config: Optional[BatchConfig] = None,
                ) -> uuid.UUID:
                    """TH: batch embedding (async) | EN: batch embedding"""
                    cfg = config or BatchConfig()
                    model = await self._models.find_by_name(ctx, model_name)
                    if model is None or not model.is_active:
                        raise NotFoundAppError(f"model not found: {model_name}")

                    batch_data = {
                        "tenant_id": ctx.tenant_id,
                        "user_id": ctx.user_id or ctx.tenant_id,
                        "model_id": model.id,
                        "total": len(texts),
                    }
                    saved = await self._batches.create(ctx, batch_data)

                    if self._bus:
                        try:
                            await self._bus.publish(BatchStarted(
                                batch_id=saved.id,
                                tenant_id=ctx.tenant_id,
                                total=len(texts),
                            ))
                        except Exception as exc:
                            logger.debug("publish failed: %s", exc)

                    asyncio.create_task(
                        self._run_batch(ctx, saved.id, model_name, texts, cfg)
                    )
                    return saved.id

                async def _run_batch(
                    self, ctx: Any, batch_id: uuid.UUID,
                    model_name: str, texts: list[str], cfg: BatchConfig,
                ) -> None:
                    started = ms_now()
                    completed = 0
                    failed = 0
                    try:
                        sem = asyncio.Semaphore(cfg.max_concurrency)

                        async def one(text: str) -> bool:
                            async with sem:
                                try:
                                    await self.embed(ctx, EmbeddingRequest(
                                        model=model_name, input=[text],
                                    ))
                                    return True
                                except Exception as exc:
                                    logger.warning("batch item failed: %s", exc)
                                    return False

                        for i in range(0, len(texts), cfg.batch_size):
                            chunk = texts[i : i + cfg.batch_size]
                            outs = await asyncio.gather(*(one(t) for t in chunk))
                            completed += sum(1 for o in outs if o)
                            failed += sum(1 for o in outs if not o)

                            batch = await self._batches.find_by_id(ctx, batch_id)
                            if batch is not None:
                                batch.completed = completed
                                batch.failed = failed
                                if batch.status == "PENDING":
                                    batch.status = "RUNNING"
                                await self._batches.update(ctx, batch)

                        batch = await self._batches.find_by_id(ctx, batch_id)
                        if batch is not None:
                            batch.status = "DONE"
                            from datetime import datetime, timezone
                            batch.finished_at = datetime.now(timezone.utc)
                            batch.completed = completed
                            batch.failed = failed
                            await self._batches.update(ctx, batch)

                        logger.info(
                            "batch done id=%s ok=%d fail=%d ms=%d",
                            batch_id, completed, failed, ms_now() - started,
                        )
                    except Exception as exc:
                        logger.exception("batch failed: %s", exc)
                        try:
                            b = await self._batches.find_by_id(ctx, batch_id)
                            if b is not None:
                                b.status = "FAILED"
                                await self._batches.update(ctx, b)
                        except Exception:
                            pass

                async def list_models(self, ctx: Any) -> list[Any]:
                    return await self._models.find_all_active(ctx)

                async def list_providers(self, ctx: Any) -> list[Any]:
                    return await self._providers.find_all_active(ctx)

                async def _call_with_retry(
                    self, client: Any, texts: list[str], model_name: str,
                    *, normalize: bool, dimensions: Optional[int],
                ) -> list[list[float]]:
                    last_exc: Optional[Exception] = None
                    for attempt in range(_MAX_RETRIES):
                        try:
                            return await client.embed(
                                texts, model_name,
                                normalize=normalize, dimensions=dimensions,
                            )
                        except Exception as exc:
                            last_exc = exc
                            logger.warning(
                                "embed attempt=%d failed: %s", attempt + 1, exc,
                            )
                            if attempt < _MAX_RETRIES - 1:
                                await asyncio.sleep(_BACKOFF[attempt])
                    raise ProviderAppError(
                        f"embedding provider failed: {last_exc}"
                    )
        ''')

    # ─── INFRASTRUCTURE LAYER ─────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} infrastructure layer"""
        '''))

        self.writer.write(f"{base}/models.py", self._models_content())
        self.writer.write(f"{base}/repositories.py", self._repositories_content())
        self.writer.write(f"{base}/caches.py", self._caches_content())
        self.writer.write(f"{base}/services.py", self._services_content())

    def _models_content(self) -> str:
        return dedent(f'''\
            """embeddings SQLAlchemy models — schema=public, prefix=emb_"""
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


            class EmbProviderModel(Base):
                __tablename__ = "emb_providers"
                __table_args__ = (
                    CheckConstraint(
                        "provider_type IN ('openai','cohere','voyage','huggingface','bge','local')",
                        name="ck_emb_provider_type",
                    ),
                    UniqueConstraint("tenant_id", "name", name="uq_emb_provider_name"),
                    Index("ix_emb_provider_tenant", "tenant_id"),
                    Index("ix_emb_provider_type", "provider_type", "is_active"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                provider_type: Mapped[str] = mapped_column(String(50), nullable=False)
                api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                base_url: Mapped[str] = mapped_column(String(500), nullable=False, server_default="")
                timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="60")
                priority: Mapped[int] = mapped_column(Integer, nullable=False, server_default="100")
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
                config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class EmbModelModel(Base):
                __tablename__ = "emb_models"
                __table_args__ = (
                    UniqueConstraint("tenant_id", "name", name="uq_emb_model_name"),
                    Index("ix_emb_model_tenant", "tenant_id"),
                    Index("ix_emb_model_provider", "provider_id", "is_active"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                display_name: Mapped[str] = mapped_column(String(200), nullable=False, server_default="")
                dimension: Mapped[int] = mapped_column(Integer, nullable=False)
                max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="8191")
                cost_per_1k_tokens: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                normalize: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class EmbVectorModel(Base):
                __tablename__ = "emb_vectors"
                __table_args__ = (
                    UniqueConstraint(
                        "tenant_id", "model_id", "source_hash",
                        name="uq_emb_vector_hash",
                    ),
                    Index("ix_emb_vec_tenant_model", "tenant_id", "model_id"),
                    Index("ix_emb_vec_hash", "source_hash"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                source_hash: Mapped[str] = mapped_column(String(128), nullable=False)
                source_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                vector_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
                dimension: Mapped[int] = mapped_column(Integer, nullable=False)
                metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class EmbBatchModel(Base):
                __tablename__ = "emb_batches"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('PENDING','RUNNING','DONE','FAILED','CANCELLED')",
                        name="ck_emb_batch_status",
                    ),
                    Index("ix_emb_batch_tenant_status", "tenant_id", "status"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                total: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                completed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                failed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
                started_at: Mapped[Optional[datetime]] = mapped_column(
                    DateTime(timezone=True), nullable=True,
                )
                finished_at: Mapped[Optional[datetime]] = mapped_column(
                    DateTime(timezone=True), nullable=True,
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class EmbCacheModel(Base):
                __tablename__ = "emb_cache"
                __table_args__ = (
                    UniqueConstraint(
                        "tenant_id", "model_id", "hash", name="uq_emb_cache_hash",
                    ),
                    Index("ix_emb_cache_tenant_model", "tenant_id", "model_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                hash: Mapped[str] = mapped_column(String(128), nullable=False)
                vector_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
                dimension: Mapped[int] = mapped_column(Integer, nullable=False)
                hits: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            __all__ = [
                "Base", "EmbProviderModel", "EmbModelModel", "EmbVectorModel",
                "EmbBatchModel", "EmbCacheModel",
            ]
        ''')

    def _repositories_content(self) -> str:
        return dedent('''\
            """embeddings repositories — SQLAlchemy 2.0 async"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.embeddings.application.exceptions import AppError
            from app.modules.embeddings.infrastructure.models import (
                EmbBatchModel, EmbModelModel, EmbProviderModel, EmbVectorModel,
            )


            class EmbProviderRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, p: EmbProviderModel) -> EmbProviderModel:
                    try:
                        self._session.add(p)
                        await self._session.flush()
                        return p
                    except SQLAlchemyError as exc:
                        logger.error(f"provider.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> EmbProviderModel | None:
                    try:
                        r = await self._session.execute(
                            select(EmbProviderModel).where(EmbProviderModel.id == id)
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"provider.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_all_active(self, ctx: object) -> list[EmbProviderModel]:
                    try:
                        r = await self._session.execute(
                            select(EmbProviderModel)
                            .where(EmbProviderModel.is_active.is_(True))
                            .order_by(EmbProviderModel.priority.asc())
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"provider.list failed: {exc}")
                        raise AppError(str(exc)) from exc


            class EmbModelRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, m: EmbModelModel) -> EmbModelModel:
                    try:
                        self._session.add(m)
                        await self._session.flush()
                        return m
                    except SQLAlchemyError as exc:
                        logger.error(f"model.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> EmbModelModel | None:
                    try:
                        r = await self._session.execute(
                            select(EmbModelModel).where(EmbModelModel.id == id)
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_name(self, ctx: object, name: str) -> EmbModelModel | None:
                    try:
                        r = await self._session.execute(
                            select(EmbModelModel).where(
                                EmbModelModel.name == name,
                                EmbModelModel.is_active.is_(True),
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_by_name failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_all_active(self, ctx: object) -> list[EmbModelModel]:
                    try:
                        r = await self._session.execute(
                            select(EmbModelModel)
                            .where(EmbModelModel.is_active.is_(True))
                            .order_by(EmbModelModel.name.asc())
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"model.list failed: {exc}")
                        raise AppError(str(exc)) from exc


            class EmbVectorRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, v: dict) -> EmbVectorModel:
                    try:
                        row = EmbVectorModel(**v) if isinstance(v, dict) else v
                        self._session.add(row)
                        await self._session.flush()
                        return row
                    except SQLAlchemyError as exc:
                        logger.error(f"vector.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_hash(
                    self, ctx: object, model_id: uuid.UUID, h: str,
                ) -> EmbVectorModel | None:
                    try:
                        r = await self._session.execute(
                            select(EmbVectorModel).where(
                                EmbVectorModel.model_id == model_id,
                                EmbVectorModel.source_hash == h,
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"vector.find failed: {exc}")
                        raise AppError(str(exc)) from exc


            class EmbBatchRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, b: dict) -> EmbBatchModel:
                    try:
                        row = EmbBatchModel(**b) if isinstance(b, dict) else b
                        self._session.add(row)
                        await self._session.flush()
                        return row
                    except SQLAlchemyError as exc:
                        logger.error(f"batch.create failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def update(self, ctx: object, b: EmbBatchModel) -> EmbBatchModel:
                    try:
                        await self._session.flush()
                        return b
                    except SQLAlchemyError as exc:
                        logger.error(f"batch.update failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> EmbBatchModel | None:
                    try:
                        r = await self._session.execute(
                            select(EmbBatchModel).where(EmbBatchModel.id == id)
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"batch.find failed: {exc}")
                        raise AppError(str(exc)) from exc
        ''')

    def _caches_content(self) -> str:
        return dedent('''\
            """embeddings caches — Redis (never-raise)"""
            from __future__ import annotations
            import json
            import logging
            import uuid
            from typing import Any, Optional

            from app.modules.embeddings.application.interfaces import (
                EmbeddingCache, RateLimiter,
            )

            logger = logging.getLogger(__name__)


            class RedisEmbeddingCache(EmbeddingCache):
                def __init__(self, redis: Any, prefix: str = "emb:r:") -> None:
                    self._redis = redis
                    self._prefix = prefix

                async def get(self, key: str) -> Optional[list[float]]:
                    try:
                        raw = await self._redis.get(self._prefix + key)
                        if raw is None:
                            return None
                        if isinstance(raw, bytes):
                            raw = raw.decode("utf-8")
                        data = json.loads(raw)
                        if isinstance(data, list):
                            return [float(x) for x in data]
                        return None
                    except Exception as exc:
                        logger.debug("cache get failed: %s", exc)
                        return None

                async def set(
                    self, key: str, value: list[float], ttl: int = 86400,
                ) -> bool:
                    try:
                        await self._redis.set(
                            self._prefix + key,
                            json.dumps(value, separators=(",", ":")),
                            ex=ttl,
                        )
                        return True
                    except Exception as exc:
                        logger.debug("cache set failed: %s", exc)
                        return False

                async def invalidate(self, key: str) -> bool:
                    try:
                        await self._redis.delete(self._prefix + key)
                        return True
                    except Exception as exc:
                        logger.debug("cache invalidate failed: %s", exc)
                        return False


            class NoopCache(EmbeddingCache):
                async def get(self, key: str) -> Optional[list[float]]:
                    return None

                async def set(
                    self, key: str, value: list[float], ttl: int = 86400,
                ) -> bool:
                    return False

                async def invalidate(self, key: str) -> bool:
                    return False


            class RedisRateLimiter(RateLimiter):
                def __init__(self, redis: Any, limit_per_minute: int = 600) -> None:
                    self._redis = redis
                    self._limit = limit_per_minute

                def _key(self, tenant_id: uuid.UUID, user_id: uuid.UUID) -> str:
                    return f"emb:rl:{tenant_id}:{user_id}"

                async def check(
                    self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
                ) -> bool:
                    try:
                        raw = await self._redis.get(self._key(tenant_id, user_id))
                        current = int(raw or 0)
                        return (current + cost) <= self._limit
                    except Exception as exc:
                        logger.debug("rate check fail-open: %s", exc)
                        return True

                async def increment(
                    self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
                ) -> None:
                    try:
                        key = self._key(tenant_id, user_id)
                        pipe = self._redis.pipeline()
                        pipe.incrby(key, cost)
                        pipe.expire(key, 60)
                        await pipe.execute()
                    except Exception as exc:
                        logger.debug("rate increment failed: %s", exc)


            class NoopRateLimiter(RateLimiter):
                async def check(
                    self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
                ) -> bool:
                    return True

                async def increment(
                    self, tenant_id: uuid.UUID, user_id: uuid.UUID, cost: int,
                ) -> None:
                    return None
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """embeddings services — clients · registry · event bus"""
            from __future__ import annotations
            import logging
            from typing import Any, Optional

            from app.modules.embeddings.application.interfaces import (
                EmbeddingClient, EmbeddingRegistry, EventBus,
            )
            from app.modules.embeddings.domain.helpers.normalizer import (
                normalize_vector,
            )

            logger = logging.getLogger(__name__)


            class OpenAIEmbeddingClient(EmbeddingClient):
                provider_type = "openai"

                def __init__(
                    self, api_key: str = "", base_url: str = "", timeout: int = 60,
                ) -> None:
                    self._api_key = api_key
                    self._base_url = base_url
                    self._timeout = timeout

                async def embed(
                    self, texts: list[str], model: str,
                    *, normalize: bool = True,
                    dimensions: Optional[int] = None,
                ) -> list[list[float]]:
                    from openai import AsyncOpenAI
                    client = AsyncOpenAI(
                        api_key=self._api_key or "sk-placeholder",
                        base_url=self._base_url or None,
                        timeout=self._timeout,
                    )
                    kwargs: dict[str, Any] = {"model": model, "input": texts}
                    if dimensions is not None:
                        kwargs["dimensions"] = dimensions
                    resp = await client.embeddings.create(**kwargs)
                    vectors = [list(item.embedding) for item in resp.data]
                    if normalize:
                        vectors = [normalize_vector(v) for v in vectors]
                    return vectors


            class CohereEmbeddingClient(EmbeddingClient):
                provider_type = "cohere"

                def __init__(
                    self, api_key: str = "", base_url: str = "", timeout: int = 60,
                ) -> None:
                    self._api_key = api_key
                    self._base_url = base_url
                    self._timeout = timeout

                async def embed(
                    self, texts: list[str], model: str,
                    *, normalize: bool = True,
                    dimensions: Optional[int] = None,
                ) -> list[list[float]]:
                    import cohere
                    client = cohere.AsyncClient(
                        api_key=self._api_key or "placeholder",
                    )
                    resp = await client.embed(
                        texts=texts, model=model,
                        input_type="search_document",
                    )
                    vectors = [list(v) for v in resp.embeddings]
                    if normalize:
                        vectors = [normalize_vector(v) for v in vectors]
                    return vectors


            class LocalEmbeddingClient(EmbeddingClient):
                provider_type = "huggingface"

                def __init__(
                    self, api_key: str = "", base_url: str = "", timeout: int = 60,
                ) -> None:
                    self._api_key = api_key
                    self._base_url = base_url
                    self._timeout = timeout
                    self._model_cache: dict[str, Any] = {}

                @staticmethod
                def _model_name(name: str) -> str:
                    return name if "/" in name else f"sentence-transformers/{name}"

                def _get_model(self, name: str) -> Any:
                    if name not in self._model_cache:
                        from sentence_transformers import SentenceTransformer
                        self._model_cache[name] = SentenceTransformer(name)
                    return self._model_cache[name]

                async def embed(
                    self, texts: list[str], model: str,
                    *, normalize: bool = True,
                    dimensions: Optional[int] = None,
                ) -> list[list[float]]:
                    import asyncio
                    st_model = self._get_model(self._model_name(model))

                    def _run() -> list[list[float]]:
                        embs = st_model.encode(
                            texts, normalize_embeddings=normalize,
                            convert_to_numpy=True,
                        )
                        return [list(map(float, row)) for row in embs]

                    vectors = await asyncio.to_thread(_run)
                    if dimensions and vectors and len(vectors[0]) > dimensions:
                        vectors = [v[:dimensions] for v in vectors]
                    return vectors


            class DefaultEmbeddingRegistry(EmbeddingRegistry):
                _CLIENTS = {
                    "openai": OpenAIEmbeddingClient,
                    "cohere": CohereEmbeddingClient,
                    "voyage": OpenAIEmbeddingClient,
                    "huggingface": LocalEmbeddingClient,
                    "bge": LocalEmbeddingClient,
                    "local": LocalEmbeddingClient,
                }

                def get_client(self, provider: Any) -> EmbeddingClient:
                    cls = self._CLIENTS.get(
                        str(provider.provider_type), OpenAIEmbeddingClient,
                    )
                    return cls(
                        api_key=provider.api_key_encrypted or "",
                        base_url=provider.base_url,
                        timeout=provider.timeout_seconds,
                    )


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
            """embeddings Pydantic schemas"""
            from __future__ import annotations
            import uuid
            from typing import Optional
            from pydantic import BaseModel, ConfigDict, Field


            class EmbedRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                model: str = Field(min_length=1, max_length=100)
                input: list[str] = Field(min_length=1, max_length=2048)
                normalize: bool = True
                dimensions: Optional[int] = Field(default=None, ge=1, le=8192)


            class EmbedOneRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                model: str = Field(min_length=1, max_length=100)
                text: str = Field(min_length=1)
                normalize: bool = True
                dimensions: Optional[int] = Field(default=None, ge=1, le=8192)


            class BatchRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                model: str = Field(min_length=1, max_length=100)
                texts: list[str] = Field(min_length=1)
                batch_size: int = Field(default=64, ge=1, le=2048)
                max_concurrency: int = Field(default=4, ge=1, le=32)


            class EmbeddingOut(BaseModel):
                vector: list[float]
                dimension: int
                tokens: int = 0
                cached: bool = False


            class EmbedResponse(BaseModel):
                model: str
                embeddings: list[EmbeddingOut]
                count: int


            class BatchResponse(BaseModel):
                batch_id: uuid.UUID
                total: int
                status: str


            class EmbModelOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                display_name: str
                dimension: int
                max_tokens: int
                normalize: bool
                is_active: bool


            class EmbProviderOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                provider_type: str
                base_url: str
                priority: int
                is_active: bool
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """embeddings DI container"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass
            from typing import Annotated, Optional

            from fastapi import Depends, Header, HTTPException, Request, status
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.embeddings.application.use_case import (
                EmbeddingUseCase,
            )
            from app.modules.embeddings.infrastructure.caches import (
                NoopCache, NoopRateLimiter, RedisEmbeddingCache,
                RedisRateLimiter,
            )
            from app.modules.embeddings.infrastructure.repositories import (
                EmbBatchRepository, EmbModelRepository,
                EmbProviderRepository, EmbVectorRepository,
            )
            from app.modules.embeddings.infrastructure.services import (
                DefaultEmbeddingRegistry, LoggingEventBus,
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
                            detail={"code": "DB_ERROR",
                                    "message": "db session unavailable"},
                        )
                    session = sm()
                return session


            async def get_redis(request: Request) -> Optional[object]:
                return getattr(request.app.state, "redis", None)


            async def get_ctx(
                x_tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-Id"),
                x_user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
            ) -> Ctx:
                if not x_tenant_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail={"code": "AUTH_ERROR",
                                "message": "X-Tenant-Id required"},
                    )
                try:
                    tenant_id = uuid.UUID(x_tenant_id)
                except ValueError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={"code": "VALIDATION_ERROR",
                                "message": "invalid tenant id"},
                    ) from exc
                user_id: Optional[uuid.UUID] = None
                if x_user_id:
                    try:
                        user_id = uuid.UUID(x_user_id)
                    except ValueError:
                        user_id = None
                return Ctx(tenant_id=tenant_id, user_id=user_id)


            async def get_use_case(
                db: AsyncSession = Depends(get_db),
                redis: Optional[object] = Depends(get_redis),
            ) -> EmbeddingUseCase:
                cache = RedisEmbeddingCache(redis) if redis else NoopCache()
                rate = RedisRateLimiter(redis) if redis else NoopRateLimiter()
                return EmbeddingUseCase(
                    providers=EmbProviderRepository(db),
                    models=EmbModelRepository(db),
                    vectors=EmbVectorRepository(db),
                    batches=EmbBatchRepository(db),
                    registry=DefaultEmbeddingRegistry(),
                    cache=cache,
                    rate=rate,
                    event_bus=LoggingEventBus(),
                )
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """embeddings HTTP router"""
            from __future__ import annotations
            import logging
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException

            from app.modules.embeddings.application.exceptions import AppError
            from app.modules.embeddings.application.use_case import (
                EmbeddingUseCase,
            )
            from app.modules.embeddings.domain.exceptions import EmbeddingError
            from app.modules.embeddings.domain.value_objects import (
                BatchConfig, EmbeddingRequest,
            )
            from app.modules.embeddings.presentation.dependencies import (
                Ctx, get_ctx, get_use_case,
            )
            from app.modules.embeddings.presentation.schemas import (
                BatchRequest, BatchResponse, EmbeddingOut, EmbedOneRequest,
                EmbedRequest, EmbedResponse, EmbModelOut, EmbProviderOut,
            )

            logger = logging.getLogger(__name__)

            router = APIRouter(prefix="/embeddings", tags=["Embeddings"])


            def _raise(exc: Exception) -> None:
                if isinstance(exc, EmbeddingError):
                    http = 400
                    code = getattr(exc, "code", "DOMAIN_ERROR")
                    if code == "NOT_FOUND":
                        http = 404
                    elif code == "VALIDATION_ERROR":
                        http = 422
                    elif code == "LIMIT_EXCEEDED":
                        http = 402
                    elif code == "RATE_LIMITED":
                        http = 429
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


            @router.post("", response_model=EmbedResponse)
            async def embed(
                req: EmbedRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
            ) -> EmbedResponse:
                """TH: embed หลายข้อความ | EN: embed many"""
                try:
                    results = await uc.embed(ctx, EmbeddingRequest(
                        model=req.model, input=req.input,
                        normalize=req.normalize, dimensions=req.dimensions,
                    ))
                    return EmbedResponse(
                        model=req.model,
                        embeddings=[
                            EmbeddingOut(
                                vector=r.vector, dimension=r.dimension,
                                tokens=r.tokens, cached=r.cached,
                            )
                            for r in results
                        ],
                        count=len(results),
                    )
                except (EmbeddingError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/one", response_model=EmbeddingOut)
            async def embed_one(
                req: EmbedOneRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
            ) -> EmbeddingOut:
                """TH: embed ข้อความเดียว | EN: embed one"""
                try:
                    results = await uc.embed(ctx, EmbeddingRequest(
                        model=req.model, input=[req.text],
                        normalize=req.normalize, dimensions=req.dimensions,
                    ))
                    if not results:
                        raise HTTPException(
                            status_code=500,
                            detail={"code": "INTERNAL_ERROR",
                                    "message": "no result"},
                        )
                    r = results[0]
                    return EmbeddingOut(
                        vector=r.vector, dimension=r.dimension,
                        tokens=r.tokens, cached=r.cached,
                    )
                except (EmbeddingError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post(
                "/batch", response_model=BatchResponse, status_code=202,
            )
            async def embed_batch(
                req: BatchRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
            ) -> BatchResponse:
                """TH: batch embedding | EN: batch embedding"""
                try:
                    batch_id = await uc.embed_batch(
                        ctx, model_name=req.model, texts=req.texts,
                        config=BatchConfig(
                            batch_size=req.batch_size,
                            max_concurrency=req.max_concurrency,
                        ),
                    )
                    return BatchResponse(
                        batch_id=batch_id, total=len(req.texts),
                        status="PENDING",
                    )
                except (EmbeddingError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/models", response_model=list[EmbModelOut])
            async def list_models(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
            ) -> list[EmbModelOut]:
                try:
                    items = await uc.list_models(ctx)
                    return [
                        EmbModelOut.model_validate({
                            "id": m.id, "name": m.name,
                            "display_name": m.display_name or "",
                            "dimension": m.dimension,
                            "max_tokens": m.max_tokens or 8192,
                            "normalize": bool(m.normalize),
                            "is_active": bool(m.is_active),
                        })
                        for m in items
                    ]
                except (EmbeddingError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/providers", response_model=list[EmbProviderOut])
            async def list_providers(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[EmbeddingUseCase, Depends(get_use_case)],
            ) -> list[EmbProviderOut]:
                try:
                    items = await uc.list_providers(ctx)
                    return [
                        EmbProviderOut.model_validate({
                            "id": p.id, "name": p.name,
                            "provider_type": p.provider_type,
                            "base_url": p.base_url or "",
                            "priority": p.priority or 100,
                            "is_active": bool(p.is_active),
                        })
                        for p in items
                    ]
                except (EmbeddingError, AppError) as exc:
                    _raise(exc)
                    raise
        ''')

    def _swagger_content(self) -> str:
        return dedent('''\
            """embeddings OpenAPI docs"""
            from __future__ import annotations
            from typing import Any


            def register_embeddings_openapi(app: object) -> None:
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "Embeddings" for t in tags):
                        tags.append({
                            "name": "Embeddings",
                            "description": (
                                "โมดูล embeddings — Text → Vector\\n\\n"
                                "• Providers: OpenAI / Cohere / HF / BGE / Local\\n"
                                "• Single + Batch embedding\\n"
                                "• Hash-based cache (Redis)\\n"
                                "• Rate limiting + Retry"
                            ),
                            "externalDocs": {
                                "description": "embeddings Module README",
                                "url": "/docs/README_embeddings.md",
                            },
                        })
                    info = schema.setdefault("info", {})
                    info.setdefault("x-module", "embeddings")
                    info.setdefault("x-layer", "5-Intel")
                    info.setdefault("x-prefix", "emb")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent(f'''\
            """{self.module} module"""
            from .presentation.router import router as emb_router

            __all__ = ["emb_router"]
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
            f"{self.sql_dir}/V002__seed_{self.module}.sql",
            self._v002_sql(),
        )
        self.writer.write(
            f"{self.sql_dir}/V003__rollback_{self.module}.sql",
            self._v003_sql(),
        )

    def _v001_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V001__create_embeddings.sql | Module: embeddings | Prefix: emb
-- Schema: public | Tables: emb_providers, emb_models, emb_vectors,
--                          emb_batches, emb_cache
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."emb_providers";
CREATE TABLE "public"."emb_providers" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"          uuid NOT NULL,
  "name"               varchar(100) NOT NULL,
  "provider_type"      varchar(50)  NOT NULL,
  "api_key_encrypted"  text NOT NULL DEFAULT '',
  "base_url"           varchar(500) NOT NULL DEFAULT '',
  "timeout_seconds"    int4 NOT NULL DEFAULT 60,
  "priority"           int4 NOT NULL DEFAULT 100,
  "is_active"          bool NOT NULL DEFAULT true,
  "config_json"        text NOT NULL DEFAULT '{}',
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"         timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "emb_providers_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_emb_provider_type" CHECK (
    provider_type IN ('openai','cohere','voyage','huggingface','bge','local')
  ),
  CONSTRAINT "uq_emb_provider_name" UNIQUE ("tenant_id", "name")
);
CREATE INDEX "ix_emb_provider_tenant" ON "public"."emb_providers" ("tenant_id");
CREATE INDEX "ix_emb_provider_type"   ON "public"."emb_providers" ("provider_type", "is_active");

DROP TABLE IF EXISTS "public"."emb_models";
CREATE TABLE "public"."emb_models" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"          uuid NOT NULL,
  "provider_id"        uuid NOT NULL,
  "name"               varchar(100) NOT NULL,
  "display_name"       varchar(200) NOT NULL DEFAULT '',
  "dimension"          int4 NOT NULL,
  "max_tokens"         int4 NOT NULL DEFAULT 8191,
  "cost_per_1k_tokens" numeric(12,8) NOT NULL DEFAULT 0,
  "normalize"          bool NOT NULL DEFAULT true,
  "is_active"          bool NOT NULL DEFAULT true,
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"         timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "emb_models_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_emb_model_name" UNIQUE ("tenant_id", "name")
);
CREATE INDEX "ix_emb_model_tenant"   ON "public"."emb_models" ("tenant_id");
CREATE INDEX "ix_emb_model_provider" ON "public"."emb_models" ("provider_id", "is_active");

DROP TABLE IF EXISTS "public"."emb_vectors";
CREATE TABLE "public"."emb_vectors" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "model_id"       uuid NOT NULL,
  "source_hash"    varchar(128) NOT NULL,
  "source_text"    text NOT NULL DEFAULT '',
  "vector_json"    text NOT NULL DEFAULT '[]',
  "dimension"      int4 NOT NULL,
  "metadata_json"  text NOT NULL DEFAULT '{}',
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "emb_vectors_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_emb_vector_hash" UNIQUE ("tenant_id", "model_id", "source_hash")
);
CREATE INDEX "ix_emb_vec_tenant_model" ON "public"."emb_vectors" ("tenant_id", "model_id");
CREATE INDEX "ix_emb_vec_hash"         ON "public"."emb_vectors" ("source_hash");

DROP TABLE IF EXISTS "public"."emb_batches";
CREATE TABLE "public"."emb_batches" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "user_id"      uuid NOT NULL,
  "model_id"     uuid NOT NULL,
  "total"        int4 NOT NULL DEFAULT 0,
  "completed"    int4 NOT NULL DEFAULT 0,
  "failed"       int4 NOT NULL DEFAULT 0,
  "status"       varchar(20) NOT NULL DEFAULT 'PENDING',
  "started_at"   timestamptz(6) NULL,
  "finished_at"  timestamptz(6) NULL,
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "emb_batches_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_emb_batch_status" CHECK (
    status IN ('PENDING','RUNNING','DONE','FAILED','CANCELLED')
  )
);
CREATE INDEX "ix_emb_batch_tenant_status" ON "public"."emb_batches" ("tenant_id", "status");

DROP TABLE IF EXISTS "public"."emb_cache";
CREATE TABLE "public"."emb_cache" (
  "id"            uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"     uuid NOT NULL,
  "model_id"      uuid NOT NULL,
  "hash"          varchar(128) NOT NULL,
  "vector_json"   text NOT NULL DEFAULT '[]',
  "dimension"     int4 NOT NULL,
  "hits"          int4 NOT NULL DEFAULT 0,
  "expires_at"    timestamptz(6) NOT NULL,
  "created_at"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"    timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "emb_cache_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_emb_cache_hash" UNIQUE ("tenant_id", "model_id", "hash")
);
CREATE INDEX "ix_emb_cache_tenant_model" ON "public"."emb_cache" ("tenant_id", "model_id");

-- ═══ Trigger function ═══
CREATE OR REPLACE FUNCTION public.set_updated_at_emb()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_emb_provider_updated ON "public"."emb_providers";
CREATE TRIGGER trg_emb_provider_updated BEFORE UPDATE ON "public"."emb_providers"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_emb();

DROP TRIGGER IF EXISTS trg_emb_model_updated ON "public"."emb_models";
CREATE TRIGGER trg_emb_model_updated BEFORE UPDATE ON "public"."emb_models"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_emb();

DROP TRIGGER IF EXISTS trg_emb_vec_updated ON "public"."emb_vectors";
CREATE TRIGGER trg_emb_vec_updated BEFORE UPDATE ON "public"."emb_vectors"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_emb();

DROP TRIGGER IF EXISTS trg_emb_batch_updated ON "public"."emb_batches";
CREATE TRIGGER trg_emb_batch_updated BEFORE UPDATE ON "public"."emb_batches"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_emb();

DROP TRIGGER IF EXISTS trg_emb_cache_updated ON "public"."emb_cache";
CREATE TRIGGER trg_emb_cache_updated BEFORE UPDATE ON "public"."emb_cache"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_emb();

-- ═══ RLS ═══
ALTER TABLE "public"."emb_providers" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."emb_models"    ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."emb_vectors"   ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."emb_batches"   ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."emb_cache"     ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_emb_provider ON "public"."emb_providers";
CREATE POLICY p_emb_provider ON "public"."emb_providers"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_emb_model ON "public"."emb_models";
CREATE POLICY p_emb_model ON "public"."emb_models"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_emb_vector ON "public"."emb_vectors";
CREATE POLICY p_emb_vector ON "public"."emb_vectors"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_emb_batch ON "public"."emb_batches";
CREATE POLICY p_emb_batch ON "public"."emb_batches"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_emb_cache ON "public"."emb_cache";
CREATE POLICY p_emb_cache ON "public"."emb_cache"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_embeddings.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."emb_providers"
    (tenant_id, name, provider_type, base_url, priority)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'openai-emb', 'openai',
     'https://api.openai.com/v1', 10),
    ('00000000-0000-0000-0000-000000000001', 'cohere-emb', 'cohere',
     'https://api.cohere.ai', 20),
    ('00000000-0000-0000-0000-000000000001', 'local-hf', 'huggingface',
     '', 30)
ON CONFLICT DO NOTHING;

INSERT INTO "public"."emb_models"
    (tenant_id, provider_id, name, display_name, dimension,
     max_tokens, cost_per_1k_tokens, normalize)
SELECT
    '00000000-0000-0000-0000-000000000001',
    p.id, 'text-embedding-3-small', 'OpenAI 3-small', 1536,
    8191, 0.00002, TRUE
FROM "public"."emb_providers" p
WHERE p.name = 'openai-emb'
ON CONFLICT DO NOTHING;

INSERT INTO "public"."emb_models"
    (tenant_id, provider_id, name, display_name, dimension,
     max_tokens, cost_per_1k_tokens, normalize)
SELECT
    '00000000-0000-0000-0000-000000000001',
    p.id, 'text-embedding-3-large', 'OpenAI 3-large', 3072,
    8191, 0.00013, TRUE
FROM "public"."emb_providers" p
WHERE p.name = 'openai-emb'
ON CONFLICT DO NOTHING;

INSERT INTO "public"."emb_models"
    (tenant_id, provider_id, name, display_name, dimension,
     max_tokens, cost_per_1k_tokens, normalize)
SELECT
    '00000000-0000-0000-0000-000000000001',
    p.id, 'embed-multilingual-v3.0', 'Cohere Multi v3', 1024,
    512, 0.0001, TRUE
FROM "public"."emb_providers" p
WHERE p.name = 'cohere-emb'
ON CONFLICT DO NOTHING;

INSERT INTO "public"."emb_models"
    (tenant_id, provider_id, name, display_name, dimension,
     max_tokens, cost_per_1k_tokens, normalize)
SELECT
    '00000000-0000-0000-0000-000000000001',
    p.id, 'all-MiniLM-L6-v2', 'MiniLM L6', 384,
    512, 0, TRUE
FROM "public"."emb_providers" p
WHERE p.name = 'local-hf'
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_embeddings.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_emb_cache_updated    ON "public"."emb_cache";
DROP TRIGGER IF EXISTS trg_emb_batch_updated    ON "public"."emb_batches";
DROP TRIGGER IF EXISTS trg_emb_vec_updated      ON "public"."emb_vectors";
DROP TRIGGER IF EXISTS trg_emb_model_updated    ON "public"."emb_models";
DROP TRIGGER IF EXISTS trg_emb_provider_updated ON "public"."emb_providers";

DROP POLICY IF EXISTS p_emb_cache    ON "public"."emb_cache";
DROP POLICY IF EXISTS p_emb_batch    ON "public"."emb_batches";
DROP POLICY IF EXISTS p_emb_vector   ON "public"."emb_vectors";
DROP POLICY IF EXISTS p_emb_model    ON "public"."emb_models";
DROP POLICY IF EXISTS p_emb_provider ON "public"."emb_providers";

DROP TABLE IF EXISTS "public"."emb_cache"     CASCADE;
DROP TABLE IF EXISTS "public"."emb_batches"   CASCADE;
DROP TABLE IF EXISTS "public"."emb_vectors"   CASCADE;
DROP TABLE IF EXISTS "public"."emb_models"    CASCADE;
DROP TABLE IF EXISTS "public"."emb_providers" CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_emb();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "emb_001"
        content = f'''"""add embeddings tables

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
    """TH: สร้างตาราง embeddings | EN: create tables"""
    op.create_table(
        "emb_providers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("provider_type", sa.String(50), nullable=False),
        sa.Column("api_key_encrypted", sa.Text, nullable=False, server_default=""),
        sa.Column("base_url", sa.String(500), nullable=False, server_default=""),
        sa.Column("timeout_seconds", sa.Integer, nullable=False, server_default="60"),
        sa.Column("priority", sa.Integer, nullable=False, server_default="100"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("config_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_emb_provider_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "emb_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False, server_default=""),
        sa.Column("dimension", sa.Integer, nullable=False),
        sa.Column("max_tokens", sa.Integer, nullable=False, server_default="8191"),
        sa.Column("cost_per_1k_tokens", sa.Numeric(12, 8), nullable=False, server_default="0"),
        sa.Column("normalize", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_emb_model_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "emb_vectors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_hash", sa.String(128), nullable=False),
        sa.Column("source_text", sa.Text, nullable=False, server_default=""),
        sa.Column("vector_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("dimension", sa.Integer, nullable=False),
        sa.Column("metadata_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "model_id", "source_hash", name="uq_emb_vector_hash"),
        schema=SCHEMA,
    )
    op.create_table(
        "emb_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total", sa.Integer, nullable=False, server_default="0"),
        sa.Column("completed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "emb_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hash", sa.String(128), nullable=False),
        sa.Column("vector_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("dimension", sa.Integer, nullable=False),
        sa.Column("hits", sa.Integer, nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "model_id", "hash", name="uq_emb_cache_hash"),
        schema=SCHEMA,
    )

    op.create_index("ix_emb_provider_tenant", "emb_providers", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_emb_provider_type", "emb_providers", ["provider_type", "is_active"], schema=SCHEMA)
    op.create_index("ix_emb_model_tenant", "emb_models", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_emb_model_provider", "emb_models", ["provider_id", "is_active"], schema=SCHEMA)
    op.create_index("ix_emb_vec_tenant_model", "emb_vectors", ["tenant_id", "model_id"], schema=SCHEMA)
    op.create_index("ix_emb_vec_hash", "emb_vectors", ["source_hash"], schema=SCHEMA)
    op.create_index("ix_emb_batch_tenant_status", "emb_batches", ["tenant_id", "status"], schema=SCHEMA)
    op.create_index("ix_emb_cache_tenant_model", "emb_cache", ["tenant_id", "model_id"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_emb()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in ("emb_providers", "emb_models", "emb_vectors",
                "emb_batches", "emb_cache"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE TRIGGER trg_{{tbl}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_emb();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"DROP POLICY IF EXISTS p_{tbl}_tenant ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE POLICY p_{tbl}_tenant ON {{SCHEMA}}.{{tbl}}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        """)


def downgrade() -> None:
    """TH: ลบตาราง | EN: drop tables"""
    for tbl in ("emb_cache", "emb_batches", "emb_vectors",
                "emb_models", "emb_providers"):
        op.execute(f"DROP POLICY IF EXISTS p_{tbl}_tenant ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_emb();")
'''
        self.writer.write(
            f"migrations/versions/{rev}_add_{self.module}_tables.py",
            content,
        )

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
                {"key": "user_id", "value": "00000000-0000-0000-0000-000000000002"},
                {"key": "model", "value": "text-embedding-3-small"},
            ],
            "item": [
                {
                    "name": "Embed (many)",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                            {"key": "X-User-Id", "value": "{{user_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/embeddings",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "embeddings"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"model":"text-embedding-3-small","input":["hello world"]}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Embed (one)",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/embeddings/one",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "embeddings", "one"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"model":"text-embedding-3-small","text":"hello"}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Batch",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/embeddings/batch",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "embeddings", "batch"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"model":"text-embedding-3-small","texts":["a","b","c"]}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "List Models",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/embeddings/models",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "embeddings", "models"],
                        },
                    },
                },
                {
                    "name": "List Providers",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/embeddings/providers",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "embeddings", "providers"],
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

        if f"{self.prefix}_router," not in content:
            m = re.search(r"(routers\s*=\s*\[)(.*?)(\n\])", content, re.S)
            if m:
                inner = m.group(2)
                inner_new = (
                    inner.rstrip()
                    + f"\n    {self.prefix}_router,  # {self.module} module\n"
                )
                content = content[:m.start(2)] + inner_new + content[m.end(2):]

        if f"register_{self.module}_openapi(app)" not in content:
            m = re.search(
                rf"(app\.include_router\({self.prefix}_router[^\n]*\n)",
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
        EmbBatchModel,
        EmbCacheModel,
        EmbModelModel,
        EmbProviderModel,
        EmbVectorModel,
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
create_module_embeddings.py — Embeddings Module Generator v{VERSION}

USAGE
    python create_module_embeddings.py <action> [options]

MODULE
    name    : embeddings
    layer   : 5-Intel
    prefix  : emb
    schema  : public
    tables  : emb_providers, emb_models, emb_vectors, emb_batches, emb_cache

ACTIONS (9)
    create       สร้าง module structure (4 layers)
    sql          สร้าง SQL migrations V001/V002/V003
    alembic      สร้าง Alembic migration
    swagger      สร้าง OpenAPI docs
    postman      สร้าง Postman collection
    update       อัปเดต app/app.py
    update-env   อัปเดต migrations/env.py
    verify       ตรวจสอบ setup
    all          ทำทุกอย่าง

EXAMPLES
    python create_module_embeddings.py all
    python create_module_embeddings.py create --force
    python create_module_embeddings.py verify
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

    gen = AIModuleGenerator(root, force=args.force)

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