#!/usr/bin/env python3
"""
create_module_vector_db.py — Vector DB Module Generator v1.0.0

สร้าง module vector_db ตาม Clean Architecture + DDD + Event-Driven
Module: vector_db · Prefix: vdb_ · Schema: public
Layer: 5-Intel · Depends: embeddings

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
    "name": "vector_db",
    "title": "Vector Database",
    "layer": "5-Intel",
    "prefix": "vdb",
    "tag": "VectorDB",
    "tag_desc": "VectorDB — ANN Store (pgvector / Qdrant / Weaviate / Pinecone)",
    "depends": ["embeddings"],
    "tables": (
        "vdb_collections",
        "vdb_vectors",
        "vdb_indexes",
        "vdb_namespaces",
        "vdb_stats",
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
            """vector_db value objects"""
            from .vector_query import VectorQuery
            from .search_hit import SearchHit
            from .ann_params import HNSWParams, IVFFlatParams

            __all__ = ["VectorQuery", "SearchHit", "HNSWParams", "IVFFlatParams"]
        '''))

        self.writer.write(f"{base}/value_objects/vector_query.py", dedent('''\
            """VectorQuery VO"""
            from __future__ import annotations
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.vector_db.domain.enums import VectorMetric


            class VectorQuery(BaseModel):
                """TH: คำค้นเวกเตอร์ | EN: Vector query"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                vector: list[float] = Field(min_length=1)
                top_k: int = Field(default=10, ge=1, le=1000)
                metric: VectorMetric = VectorMetric.COSINE
                filter: Optional[dict[str, Any]] = None
                include_metadata: bool = True
                score_threshold: Optional[float] = None
        '''))

        self.writer.write(f"{base}/value_objects/search_hit.py", dedent('''\
            """SearchHit VO"""
            from __future__ import annotations
            import uuid
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict


            class SearchHit(BaseModel):
                """TH: ผลลัพธ์ 1 รายการ | EN: Search hit"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                vector_id: uuid.UUID
                source_id: str
                score: float
                metadata: Optional[dict[str, Any]] = None
                rank: int = 0
        '''))

        self.writer.write(f"{base}/value_objects/ann_params.py", dedent('''\
            """ANN Params VOs"""
            from __future__ import annotations
            from pydantic import BaseModel, ConfigDict, Field


            class HNSWParams(BaseModel):
                """TH: HNSW params | EN: HNSW params"""
                model_config = ConfigDict(frozen=True, extra="forbid")
                m: int = Field(default=16, ge=2, le=128)
                ef_construction: int = Field(default=64, ge=4, le=1024)
                ef_search: int = Field(default=40, ge=1, le=1024)


            class IVFFlatParams(BaseModel):
                """TH: IVFFlat params | EN: IVFFlat params"""
                model_config = ConfigDict(frozen=True, extra="forbid")
                lists: int = Field(default=100, ge=1, le=32768)
                probes: int = Field(default=1, ge=1, le=1024)
        '''))

        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """vector_db entities"""
            from .collection import VDBCollection
            from .vector import VDBVector
            from .index import VDBIndex
            from .namespace import VDBNamespace
            from .stats import VDBStats

            __all__ = [
                "VDBCollection", "VDBVector", "VDBIndex",
                "VDBNamespace", "VDBStats",
            ]
        '''))

        for name, cls, model in (
            ("collection", "VDBCollection", "VDBCollectionModel"),
            ("vector", "VDBVector", "VDBVectorModel"),
            ("index", "VDBIndex", "VDBIndexModel"),
            ("namespace", "VDBNamespace", "VDBNamespaceModel"),
            ("stats", "VDBStats", "VDBStatsModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias to ORM"""
                from __future__ import annotations
                from app.modules.{self.module}.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """vector_db helpers"""
            from .metrics import (
                cosine_similarity, l2_distance, inner_product, norm_l2,
            )

            __all__ = [
                "cosine_similarity", "l2_distance", "inner_product", "norm_l2",
            ]
        '''))

        self.writer.write(f"{base}/helpers/metrics.py", dedent('''\
            """similarity metrics"""
            from __future__ import annotations
            import math


            def norm_l2(v: list[float]) -> float:
                """TH: L2 norm | EN: L2 norm"""
                return math.sqrt(sum(x * x for x in v))


            def cosine_similarity(a: list[float], b: list[float]) -> float:
                """TH: cosine similarity | EN: cosine similarity"""
                if not a or not b or len(a) != len(b):
                    return 0.0
                dot = sum(x * y for x, y in zip(a, b))
                na = norm_l2(a)
                nb = norm_l2(b)
                if na <= 0 or nb <= 0:
                    return 0.0
                return dot / (na * nb)


            def l2_distance(a: list[float], b: list[float]) -> float:
                """TH: L2 distance | EN: L2 distance"""
                if not a or not b or len(a) != len(b):
                    return float("inf")
                return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


            def inner_product(a: list[float], b: list[float]) -> float:
                """TH: inner product | EN: inner product"""
                if not a or not b or len(a) != len(b):
                    return 0.0
                return sum(x * y for x, y in zip(a, b))
        '''))

    def _domain_enums(self) -> str:
        return dedent('''\
            """vector_db enums"""
            from __future__ import annotations
            from enum import Enum


            class VDBBackend(str, Enum):
                """TH: backend | EN: Vector DB backend"""
                PGVECTOR = "pgvector"
                QDRANT = "qdrant"
                WEAVIATE = "weaviate"
                PINECONE = "pinecone"
                CHROMA = "chroma"
                MILVUS = "milvus"

                def __str__(self) -> str:
                    return str(self.value)


            class VectorMetric(str, Enum):
                """TH: metric วัดระยะ | EN: Vector metric"""
                COSINE = "cosine"
                L2 = "l2"
                IP = "ip"

                def __str__(self) -> str:
                    return str(self.value)


            class ANNIndexType(str, Enum):
                """TH: ประเภท ANN index | EN: ANN index type"""
                HNSW = "hnsw"
                IVFFLAT = "ivfflat"
                FLAT = "flat"
                SCANN = "scann"
                DISKANN = "diskann"

                def __str__(self) -> str:
                    return str(self.value)


            class IndexBuildStatus(str, Enum):
                """TH: สถานะการสร้าง index | EN: Index build status"""
                PENDING = "PENDING"
                BUILDING = "BUILDING"
                READY = "READY"
                FAILED = "FAILED"

                def __str__(self) -> str:
                    return str(self.value)
        ''')

    def _domain_exceptions(self) -> str:
        return dedent('''\
            """vector_db domain exceptions"""
            from __future__ import annotations


            class VectorDBError(Exception):
                """TH: base | EN: base"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class CollectionNotFoundError(VectorDBError):
                code = "NOT_FOUND"


            class VectorNotFoundError(VectorDBError):
                code = "NOT_FOUND"


            class IndexNotFoundError(VectorDBError):
                code = "NOT_FOUND"


            class DimensionMismatchError(VectorDBError):
                code = "VALIDATION_ERROR"


            class CollectionConflictError(VectorDBError):
                code = "CONFLICT"


            class BackendError(VectorDBError):
                code = "PROVIDER_ERROR"


            class IndexBuildError(VectorDBError):
                code = "PROVIDER_ERROR"


            class NamespaceQuotaExceededError(VectorDBError):
                code = "LIMIT_EXCEEDED"
        ''')

    def _domain_events(self) -> str:
        return dedent('''\
            """vector_db domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import datetime, timezone


            def _now():
                return datetime.now(timezone.utc)


            @dataclass(frozen=True)
            class CollectionCreated:
                collection_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                dimension: int
                metric: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class CollectionDeleted:
                collection_id: uuid.UUID
                tenant_id: uuid.UUID
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class VectorsUpserted:
                collection_id: uuid.UUID
                tenant_id: uuid.UUID
                count: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class VectorDeleted:
                collection_id: uuid.UUID
                tenant_id: uuid.UUID
                vector_id: uuid.UUID
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class IndexBuilt:
                index_id: uuid.UUID
                collection_id: uuid.UUID
                index_type: str
                size_bytes: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class IndexBuildFailed:
                index_id: uuid.UUID
                collection_id: uuid.UUID
                error: str
                occurred_at: datetime = field(default_factory=_now)
        ''')

    # ─── APPLICATION LAYER ────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} application layer"""
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """vector_db application exceptions"""
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


            class BackendAppError(AppError):
                code = "PROVIDER_ERROR"
                http_status = 502


            class RateLimitAppError(AppError):
                code = "RATE_LIMITED"
                http_status = 429


            class LimitExceededAppError(AppError):
                code = "LIMIT_EXCEEDED"
                http_status = 402
        '''))

        self.writer.write(f"{base}/interfaces.py", self._interfaces_content())
        self.writer.write(f"{base}/mappers.py", self._mappers_content())
        self.writer.write(f"{base}/utils.py", self._utils_content())
        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _interfaces_content(self) -> str:
        return dedent('''\
            """vector_db application ports"""
            from __future__ import annotations
            import uuid
            from abc import ABC, abstractmethod
            from typing import Any, Optional, Protocol, runtime_checkable

            from app.modules.vector_db.domain.value_objects import (
                SearchHit, VectorQuery,
            )


            @runtime_checkable
            class RequestContext(Protocol):
                @property
                def tenant_id(self) -> uuid.UUID: ...
                @property
                def user_id(self) -> Optional[uuid.UUID]: ...


            class VDBCollectionRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, c: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
                @abstractmethod
                async def find_all(self, ctx: Any) -> list[Any]: ...
                @abstractmethod
                async def delete(self, ctx: Any, id: uuid.UUID) -> bool: ...


            class VDBVectorRepository(ABC):
                @abstractmethod
                async def upsert_many(self, ctx: Any, vectors: list[Any]) -> int: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def query_candidates(
                    self, ctx: Any, collection_id: uuid.UUID, limit: int,
                ) -> list[Any]: ...
                @abstractmethod
                async def delete(self, ctx: Any, id: uuid.UUID) -> bool: ...
                @abstractmethod
                async def delete_by_collection(
                    self, ctx: Any, collection_id: uuid.UUID,
                ) -> int: ...
                @abstractmethod
                async def count(self, ctx: Any, collection_id: uuid.UUID) -> int: ...


            class VDBIndexRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, i: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_collection(
                    self, ctx: Any, collection_id: uuid.UUID,
                ) -> list[Any]: ...


            class VDBNamespaceRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, n: Any) -> Any: ...
                @abstractmethod
                async def find_by_name(
                    self, ctx: Any, collection_id: uuid.UUID, name: str,
                ) -> Any | None: ...


            class VDBStatsRepository(ABC):
                @abstractmethod
                async def upsert(self, ctx: Any, s: Any) -> Any: ...
                @abstractmethod
                async def find_by_collection(
                    self, ctx: Any, collection_id: uuid.UUID,
                ) -> Any | None: ...


            class BackendAdapter(Protocol):
                """TH: port ของ vector backend | EN: backend port"""
                async def upsert(self, collection: Any, vectors: list[Any]) -> int: ...
                async def query(self, collection: Any, query: VectorQuery) -> list[SearchHit]: ...
                async def delete(self, collection: Any, vector_ids: list[uuid.UUID]) -> int: ...
                async def build_index(self, collection: Any, index: Any) -> int: ...


            class BackendRegistry(Protocol):
                def get_adapter(self, backend: str) -> BackendAdapter: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...
        ''')

    def _mappers_content(self) -> str:
        return dedent('''\
            """vector_db mappers — ORM → dict"""
            from __future__ import annotations
            from typing import Any


            def collection_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "name": row.name,
                    "dimension": row.dimension,
                    "metric": row.metric, "backend": row.backend,
                    "is_active": bool(row.is_active),
                }


            def vector_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "collection_id": str(row.collection_id),
                    "source_id": row.source_id,
                    "norm": float(row.norm or 0.0),
                }


            def index_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "collection_id": str(row.collection_id),
                    "name": row.name, "index_type": row.index_type,
                    "build_status": row.build_status,
                    "size_bytes": row.size_bytes or 0,
                }


            def stats_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "collection_id": str(row.collection_id),
                    "vector_count": row.vector_count or 0,
                    "size_bytes": row.size_bytes or 0,
                    "avg_latency_ms": float(row.avg_latency_ms or 0.0),
                }
        ''')

    def _utils_content(self) -> str:
        return dedent('''\
            """vector_db application utils"""
            from __future__ import annotations
            import json
            from typing import Any


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
        ''')

    def _use_case_content(self) -> str:
        return dedent('''\
            """vector_db use cases"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any, Optional

            from app.modules.vector_db.application.exceptions import (
                ConflictAppError, NotFoundAppError, ValidationAppError,
            )
            from app.modules.vector_db.application.utils import (
                json_dumps_safe, json_loads_safe, json_to_vector,
                vector_to_json,
            )
            from app.modules.vector_db.domain.enums import VectorMetric
            from app.modules.vector_db.domain.events import (
                CollectionCreated, IndexBuilt, VectorDeleted, VectorsUpserted,
            )
            from app.modules.vector_db.domain.helpers.metrics import (
                cosine_similarity, inner_product, l2_distance,
            )
            from app.modules.vector_db.domain.value_objects import (
                SearchHit, VectorQuery,
            )

            logger = logging.getLogger(__name__)


            class VectorDBUseCase:
                """TH: use case หลัก | EN: core use case"""

                def __init__(self, **deps: Any) -> None:
                    for key, value in deps.items():
                        setattr(self, f"_{key}", value)

                async def create_collection(
                    self, ctx: Any, *,
                    name: str, dimension: int,
                    metric: VectorMetric = VectorMetric.COSINE,
                    backend: str = "pgvector",
                    config: Optional[dict[str, Any]] = None,
                ) -> Any:
                    """TH: สร้าง collection | EN: create collection"""
                    from app.modules.vector_db.infrastructure.models import (
                        VDBCollectionModel,
                    )

                    existing = await self._collections.find_by_name(ctx, name)
                    if existing is not None:
                        raise ConflictAppError(f"collection exists: {name}")

                    coll = VDBCollectionModel(
                        tenant_id=ctx.tenant_id, name=name,
                        dimension=dimension, metric=str(metric),
                        backend=backend,
                        config_json=json_dumps_safe(config or {}),
                    )
                    saved = await self._collections.save(ctx, coll)

                    if self._bus:
                        try:
                            await self._bus.publish(CollectionCreated(
                                collection_id=saved.id,
                                tenant_id=saved.tenant_id,
                                name=saved.name,
                                dimension=saved.dimension,
                                metric=str(saved.metric),
                            ))
                        except Exception as exc:
                            logger.debug("publish failed: %s", exc)
                    return saved

                async def list_collections(self, ctx: Any) -> list[Any]:
                    return await self._collections.find_all(ctx)

                async def get_collection(
                    self, ctx: Any, id: uuid.UUID,
                ) -> Any:
                    coll = await self._collections.find_by_id(ctx, id)
                    if coll is None:
                        raise NotFoundAppError("collection not found")
                    return coll

                async def upsert(
                    self, ctx: Any, *,
                    collection_id: uuid.UUID,
                    items: list[dict[str, Any]],
                ) -> int:
                    """TH: upsert vectors | EN: upsert vectors"""
                    from app.modules.vector_db.infrastructure.models import (
                        VDBVectorModel,
                    )

                    coll = await self.get_collection(ctx, collection_id)
                    if not items:
                        return 0

                    prepared: list[Any] = []
                    for item in items:
                        vec = item.get("vector") or []
                        if len(vec) != coll.dimension:
                            raise ValidationAppError(
                                f"dimension mismatch: expected "
                                f"{coll.dimension}, got {len(vec)}"
                            )
                        prepared.append(VDBVectorModel(
                            tenant_id=ctx.tenant_id,
                            collection_id=coll.id,
                            source_id=str(item.get("source_id", "")),
                            vector_json=vector_to_json(
                                [float(x) for x in vec],
                            ),
                            metadata_json=json_dumps_safe(
                                item.get("metadata") or {},
                            ),
                            norm=float(sum(x * x for x in vec) ** 0.5),
                        ))

                    adapter = self._backends.get_adapter(str(coll.backend))
                    try:
                        count = await adapter.upsert(coll, prepared)
                    except Exception as exc:
                        logger.warning("backend upsert failed: %s", exc)
                        count = await self._vectors.upsert_many(ctx, prepared)

                    if self._bus:
                        try:
                            await self._bus.publish(VectorsUpserted(
                                collection_id=coll.id,
                                tenant_id=ctx.tenant_id,
                                count=count,
                            ))
                        except Exception:
                            pass
                    return count

                async def query(
                    self, ctx: Any, *,
                    collection_id: uuid.UUID, query: VectorQuery,
                ) -> list[SearchHit]:
                    """TH: query vectors | EN: query vectors"""
                    coll = await self.get_collection(ctx, collection_id)
                    if len(query.vector) != coll.dimension:
                        raise ValidationAppError(
                            f"dimension mismatch: expected {coll.dimension}"
                        )
                    adapter = self._backends.get_adapter(str(coll.backend))
                    try:
                        return await adapter.query(coll, query)
                    except Exception as exc:
                        logger.debug(
                            "backend query failed, in-memory fallback: %s", exc,
                        )
                        return await self._query_in_memory(ctx, coll, query)

                async def delete_vector(
                    self, ctx: Any, *,
                    collection_id: uuid.UUID, vector_id: uuid.UUID,
                ) -> bool:
                    await self.get_collection(ctx, collection_id)
                    ok_del = await self._vectors.delete(ctx, vector_id)
                    if ok_del and self._bus:
                        try:
                            await self._bus.publish(VectorDeleted(
                                collection_id=collection_id,
                                tenant_id=ctx.tenant_id,
                                vector_id=vector_id,
                            ))
                        except Exception:
                            pass
                    return ok_del

                async def stats(
                    self, ctx: Any, collection_id: uuid.UUID,
                ) -> dict[str, Any]:
                    await self.get_collection(ctx, collection_id)
                    s = await self._stats.find_by_collection(
                        ctx, collection_id,
                    )
                    count = await self._vectors.count(ctx, collection_id)
                    if s is None:
                        return {
                            "collection_id": str(collection_id),
                            "vector_count": count,
                            "size_bytes": 0,
                            "avg_latency_ms": 0.0,
                        }
                    return {
                        "collection_id": str(s.collection_id),
                        "vector_count": s.vector_count or count,
                        "size_bytes": s.size_bytes or 0,
                        "avg_latency_ms": float(s.avg_latency_ms or 0.0),
                    }

                async def build_index(
                    self, ctx: Any, *,
                    collection_id: uuid.UUID,
                    index_type: str, params: dict[str, Any],
                ) -> Any:
                    """TH: สร้าง ANN index | EN: build ANN index"""
                    from app.modules.vector_db.infrastructure.models import (
                        VDBIndexModel,
                    )

                    coll = await self.get_collection(ctx, collection_id)
                    idx = VDBIndexModel(
                        collection_id=coll.id,
                        name=f"idx_{index_type}_{uuid.uuid4().hex[:8]}",
                        index_type=index_type,
                        params_json=json_dumps_safe(params),
                    )
                    saved = await self._indexes.save(ctx, idx)
                    adapter = self._backends.get_adapter(str(coll.backend))
                    try:
                        size = await adapter.build_index(coll, saved)
                        saved.size_bytes = size
                        saved.build_status = "READY"
                        await self._indexes.save(ctx, saved)
                        if self._bus:
                            try:
                                await self._bus.publish(IndexBuilt(
                                    index_id=saved.id,
                                    collection_id=coll.id,
                                    index_type=index_type,
                                    size_bytes=size,
                                ))
                            except Exception:
                                pass
                    except Exception as exc:
                        logger.warning("index build failed: %s", exc)
                        saved.build_status = "FAILED"
                        await self._indexes.save(ctx, saved)
                    return saved

                async def list_indexes(
                    self, ctx: Any, collection_id: uuid.UUID,
                ) -> list[Any]:
                    await self.get_collection(ctx, collection_id)
                    return await self._indexes.find_by_collection(
                        ctx, collection_id,
                    )

                async def _query_in_memory(
                    self, ctx: Any, coll: Any, query: VectorQuery,
                ) -> list[SearchHit]:
                    candidates = await self._vectors.query_candidates(
                        ctx, coll.id, limit=max(query.top_k * 10, 100),
                    )
                    scored: list[tuple[float, Any]] = []
                    for cand in candidates:
                        vec = json_to_vector(cand.vector_json)
                        if query.metric == VectorMetric.COSINE:
                            score = cosine_similarity(query.vector, vec)
                        elif query.metric == VectorMetric.L2:
                            score = -l2_distance(query.vector, vec)
                        else:
                            score = inner_product(query.vector, vec)
                        if (query.score_threshold is not None
                                and score < query.score_threshold):
                            continue
                        scored.append((score, cand))

                    scored.sort(key=lambda x: x[0], reverse=True)
                    hits: list[SearchHit] = []
                    for rank, (score, cand) in enumerate(
                        scored[: query.top_k], start=1,
                    ):
                        hits.append(SearchHit(
                            vector_id=cand.id,
                            source_id=cand.source_id,
                            score=float(score),
                            metadata=(
                                json_loads_safe(cand.metadata_json, {})
                                if query.include_metadata else None
                            ),
                            rank=rank,
                        ))
                    return hits
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
            """vector_db SQLAlchemy models — schema=public, prefix=vdb_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from typing import Optional

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Float, Index, Integer,
                String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: base | EN: base"""


            class VDBCollectionModel(Base):
                __tablename__ = "vdb_collections"
                __table_args__ = (
                    CheckConstraint(
                        "metric IN ('cosine','l2','ip')",
                        name="ck_vdb_collection_metric",
                    ),
                    CheckConstraint(
                        "backend IN ('pgvector','qdrant','weaviate',"
                        "'pinecone','chroma','milvus')",
                        name="ck_vdb_collection_backend",
                    ),
                    UniqueConstraint("tenant_id", "name", name="uq_vdb_collection_name"),
                    Index("ix_vdb_collection_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                dimension: Mapped[int] = mapped_column(Integer, nullable=False)
                metric: Mapped[str] = mapped_column(String(20), nullable=False, server_default="cosine")
                backend: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pgvector")
                config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class VDBVectorModel(Base):
                __tablename__ = "vdb_vectors"
                __table_args__ = (
                    Index("ix_vdb_vec_tenant_coll", "tenant_id", "collection_id"),
                    Index("ix_vdb_vec_source", "collection_id", "source_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                source_id: Mapped[str] = mapped_column(String(200), nullable=False)
                vector_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
                metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                norm: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class VDBIndexModel(Base):
                __tablename__ = "vdb_indexes"
                __table_args__ = (
                    CheckConstraint(
                        "index_type IN ('hnsw','ivfflat','flat','scann','diskann')",
                        name="ck_vdb_index_type",
                    ),
                    CheckConstraint(
                        "build_status IN ('PENDING','BUILDING','READY','FAILED')",
                        name="ck_vdb_index_status",
                    ),
                    Index("ix_vdb_index_collection", "collection_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                index_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="hnsw")
                params_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                build_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class VDBNamespaceModel(Base):
                __tablename__ = "vdb_namespaces"
                __table_args__ = (
                    UniqueConstraint(
                        "tenant_id", "collection_id", "namespace",
                        name="uq_vdb_namespace",
                    ),
                    Index("ix_vdb_ns_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                namespace: Mapped[str] = mapped_column(String(100), nullable=False)
                prefix: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
                quota: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class VDBStatsModel(Base):
                __tablename__ = "vdb_stats"
                __table_args__ = (
                    UniqueConstraint("collection_id", name="uq_vdb_stats_collection"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                collection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                vector_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                avg_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            __all__ = [
                "Base", "VDBCollectionModel", "VDBVectorModel", "VDBIndexModel",
                "VDBNamespaceModel", "VDBStatsModel",
            ]
        ''')

    def _repositories_content(self) -> str:
        return dedent('''\
            """vector_db repositories — SQLAlchemy 2.0 async"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import delete, func, select, update
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.vector_db.application.exceptions import AppError
            from app.modules.vector_db.infrastructure.models import (
                VDBCollectionModel, VDBIndexModel, VDBNamespaceModel,
                VDBStatsModel, VDBVectorModel,
            )


            class VDBCollectionRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, c: VDBCollectionModel) -> VDBCollectionModel:
                    try:
                        self._session.add(c)
                        await self._session.flush()
                        return c
                    except SQLAlchemyError as exc:
                        logger.error(f"coll.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> VDBCollectionModel | None:
                    try:
                        r = await self._session.execute(
                            select(VDBCollectionModel).where(
                                VDBCollectionModel.id == id,
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"coll.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_name(self, ctx: object, name: str) -> VDBCollectionModel | None:
                    try:
                        r = await self._session.execute(
                            select(VDBCollectionModel).where(
                                VDBCollectionModel.name == name,
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"coll.find_name failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_all(self, ctx: object) -> list:
                    try:
                        r = await self._session.execute(
                            select(VDBCollectionModel)
                            .where(VDBCollectionModel.is_active.is_(True))
                            .order_by(VDBCollectionModel.name.asc())
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"coll.list failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def delete(self, ctx: object, id: uuid.UUID) -> bool:
                    try:
                        stmt = (
                            update(VDBCollectionModel)
                            .where(VDBCollectionModel.id == id)
                            .values(is_active=False)
                        )
                        res = await self._session.execute(stmt)
                        await self._session.flush()
                        return (res.rowcount or 0) > 0
                    except SQLAlchemyError as exc:
                        logger.error(f"coll.delete failed: {exc}")
                        raise AppError(str(exc)) from exc


            class VDBVectorRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def upsert_many(self, ctx: object, vectors: list) -> int:
                    try:
                        for v in vectors:
                            self._session.add(v)
                        await self._session.flush()
                        return len(vectors)
                    except SQLAlchemyError as exc:
                        logger.error(f"vec.upsert failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> VDBVectorModel | None:
                    try:
                        r = await self._session.execute(
                            select(VDBVectorModel).where(VDBVectorModel.id == id)
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"vec.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def query_candidates(
                    self, ctx: object, collection_id: uuid.UUID, limit: int,
                ) -> list:
                    try:
                        r = await self._session.execute(
                            select(VDBVectorModel)
                            .where(VDBVectorModel.collection_id == collection_id)
                            .limit(max(1, min(limit, 10000)))
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"vec.query failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def delete(self, ctx: object, id: uuid.UUID) -> bool:
                    try:
                        res = await self._session.execute(
                            delete(VDBVectorModel).where(VDBVectorModel.id == id)
                        )
                        await self._session.flush()
                        return (res.rowcount or 0) > 0
                    except SQLAlchemyError as exc:
                        logger.error(f"vec.delete failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def delete_by_collection(self, ctx: object, collection_id: uuid.UUID) -> int:
                    try:
                        res = await self._session.execute(
                            delete(VDBVectorModel).where(
                                VDBVectorModel.collection_id == collection_id,
                            )
                        )
                        await self._session.flush()
                        return int(res.rowcount or 0)
                    except SQLAlchemyError as exc:
                        logger.error(f"vec.delete_coll failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def count(self, ctx: object, collection_id: uuid.UUID) -> int:
                    try:
                        r = await self._session.execute(
                            select(func.count()).select_from(VDBVectorModel).where(
                                VDBVectorModel.collection_id == collection_id,
                            )
                        )
                        return int(r.scalar() or 0)
                    except SQLAlchemyError as exc:
                        logger.error(f"vec.count failed: {exc}")
                        raise AppError(str(exc)) from exc


            class VDBIndexRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, i: VDBIndexModel) -> VDBIndexModel:
                    try:
                        self._session.add(i)
                        await self._session.flush()
                        return i
                    except SQLAlchemyError as exc:
                        logger.error(f"idx.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> VDBIndexModel | None:
                    try:
                        r = await self._session.execute(
                            select(VDBIndexModel).where(VDBIndexModel.id == id)
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"idx.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_collection(self, ctx: object, collection_id: uuid.UUID) -> list:
                    try:
                        r = await self._session.execute(
                            select(VDBIndexModel).where(
                                VDBIndexModel.collection_id == collection_id,
                            )
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"idx.list failed: {exc}")
                        raise AppError(str(exc)) from exc


            class VDBNamespaceRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, n: VDBNamespaceModel) -> VDBNamespaceModel:
                    try:
                        self._session.add(n)
                        await self._session.flush()
                        return n
                    except SQLAlchemyError as exc:
                        logger.error(f"ns.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_name(
                    self, ctx: object, collection_id: uuid.UUID, name: str,
                ) -> VDBNamespaceModel | None:
                    try:
                        r = await self._session.execute(
                            select(VDBNamespaceModel).where(
                                VDBNamespaceModel.collection_id == collection_id,
                                VDBNamespaceModel.namespace == name,
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"ns.find failed: {exc}")
                        raise AppError(str(exc)) from exc


            class VDBStatsRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def upsert(self, ctx: object, s: VDBStatsModel) -> VDBStatsModel:
                    try:
                        self._session.add(s)
                        await self._session.flush()
                        return s
                    except SQLAlchemyError as exc:
                        logger.error(f"stats.upsert failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_collection(
                    self, ctx: object, collection_id: uuid.UUID,
                ) -> VDBStatsModel | None:
                    try:
                        r = await self._session.execute(
                            select(VDBStatsModel).where(
                                VDBStatsModel.collection_id == collection_id,
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"stats.find failed: {exc}")
                        raise AppError(str(exc)) from exc
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """vector_db services — backends · registry · event bus"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any

            from app.modules.vector_db.application.utils import (
                json_loads_safe, json_to_vector,
            )
            from app.modules.vector_db.domain.enums import VectorMetric
            from app.modules.vector_db.domain.helpers.metrics import (
                cosine_similarity, inner_product, l2_distance,
            )
            from app.modules.vector_db.domain.value_objects import SearchHit

            logger = logging.getLogger(__name__)


            class PgVectorAdapter:
                """TH: pgvector adapter (via JSON) | EN: pgvector adapter"""

                async def upsert(self, collection: Any, vectors: list[Any]) -> int:
                    return len(vectors)

                async def query(self, collection: Any, query: Any) -> list:
                    raise NotImplementedError("delegated to in-memory fallback")

                async def delete(self, collection: Any, vector_ids: list) -> int:
                    return len(vector_ids)

                async def build_index(self, collection: Any, index: Any) -> int:
                    return collection.dimension * 4 * 1000


            class QdrantAdapter:
                """TH: qdrant adapter (stub) | EN: qdrant adapter"""

                async def upsert(self, collection: Any, vectors: list) -> int:
                    logger.info("qdrant upsert %d vectors", len(vectors))
                    return len(vectors)

                async def query(self, collection: Any, query: Any) -> list:
                    return []

                async def delete(self, collection: Any, vector_ids: list) -> int:
                    return len(vector_ids)

                async def build_index(self, collection: Any, index: Any) -> int:
                    return 0


            class InMemoryAdapter:
                """TH: in-memory adapter (fallback) | EN: in-memory adapter"""

                def __init__(self) -> None:
                    self._store: dict[uuid.UUID, list] = {}

                async def upsert(self, collection: Any, vectors: list) -> int:
                    bucket = self._store.setdefault(collection.id, [])
                    for v in vectors:
                        vec = json_to_vector(v.vector_json)
                        meta = json_loads_safe(v.metadata_json, {})
                        bucket.append((v.id, vec, meta))
                    return len(vectors)

                async def query(self, collection: Any, query: Any) -> list:
                    bucket = self._store.get(collection.id, [])
                    scored: list = []
                    for vid, vec, meta in bucket:
                        if query.metric == VectorMetric.COSINE:
                            s = cosine_similarity(query.vector, vec)
                        elif query.metric == VectorMetric.L2:
                            s = -l2_distance(query.vector, vec)
                        else:
                            s = inner_product(query.vector, vec)
                        scored.append((s, vid, meta))
                    scored.sort(key=lambda x: x[0], reverse=True)
                    return [
                        SearchHit(
                            vector_id=vid, source_id=str(vid),
                            score=float(s),
                            metadata=meta if query.include_metadata else None,
                            rank=i + 1,
                        )
                        for i, (s, vid, meta) in enumerate(
                            scored[: query.top_k],
                        )
                    ]

                async def delete(self, collection: Any, vector_ids: list) -> int:
                    bucket = self._store.get(collection.id, [])
                    ids_set = set(vector_ids)
                    before = len(bucket)
                    self._store[collection.id] = [
                        r for r in bucket if r[0] not in ids_set
                    ]
                    return before - len(self._store[collection.id])

                async def build_index(self, collection: Any, index: Any) -> int:
                    bucket = self._store.get(collection.id, [])
                    return sum(len(v) * 4 for _, v, _ in bucket)


            class DefaultBackendRegistry:
                def __init__(self) -> None:
                    self._in_memory = InMemoryAdapter()

                def get_adapter(self, backend: str) -> Any:
                    b = (backend or "").lower()
                    if b == "qdrant":
                        return QdrantAdapter()
                    return self._in_memory


            class LoggingEventBus:
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
            """vector_db Pydantic schemas"""
            from __future__ import annotations
            import uuid
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.vector_db.domain.enums import (
                ANNIndexType, VectorMetric,
            )


            class CollectionCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(min_length=1, max_length=100)
                dimension: int = Field(ge=1, le=8192)
                metric: VectorMetric = VectorMetric.COSINE
                backend: str = "pgvector"
                config: dict[str, Any] = Field(default_factory=dict)


            class CollectionOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                dimension: int
                metric: str
                backend: str
                is_active: bool


            class VectorItem(BaseModel):
                model_config = ConfigDict(extra="forbid")
                source_id: str = Field(min_length=1, max_length=200)
                vector: list[float] = Field(min_length=1)
                metadata: dict[str, Any] = Field(default_factory=dict)


            class UpsertRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                items: list[VectorItem] = Field(min_length=1, max_length=10000)


            class UpsertResponse(BaseModel):
                collection_id: uuid.UUID
                upserted: int


            class QueryRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                vector: list[float] = Field(min_length=1)
                top_k: int = Field(default=10, ge=1, le=1000)
                metric: Optional[VectorMetric] = None
                filter: Optional[dict[str, Any]] = None
                include_metadata: bool = True
                score_threshold: Optional[float] = None


            class SearchHitOut(BaseModel):
                vector_id: uuid.UUID
                source_id: str
                score: float
                metadata: Optional[dict[str, Any]] = None
                rank: int = 0


            class QueryResponse(BaseModel):
                collection_id: uuid.UUID
                hits: list[SearchHitOut]


            class IndexCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                index_type: ANNIndexType = ANNIndexType.HNSW
                params: dict[str, Any] = Field(default_factory=dict)


            class IndexOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                collection_id: uuid.UUID
                name: str
                index_type: str
                build_status: str
                size_bytes: int


            class StatsOut(BaseModel):
                collection_id: uuid.UUID
                vector_count: int
                size_bytes: int
                avg_latency_ms: float
                updated_at: Optional[str] = None
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """vector_db DI container"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass
            from typing import Annotated, Optional

            from fastapi import Depends, Header, HTTPException, Request, status
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.vector_db.application.use_case import (
                VectorDBUseCase,
            )
            from app.modules.vector_db.infrastructure.repositories import (
                VDBCollectionRepository, VDBIndexRepository,
                VDBNamespaceRepository, VDBStatsRepository,
                VDBVectorRepository,
            )
            from app.modules.vector_db.infrastructure.services import (
                DefaultBackendRegistry, LoggingEventBus,
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
            ) -> VectorDBUseCase:
                return VectorDBUseCase(
                    collections=VDBCollectionRepository(db),
                    vectors=VDBVectorRepository(db),
                    indexes=VDBIndexRepository(db),
                    namespaces=VDBNamespaceRepository(db),
                    stats=VDBStatsRepository(db),
                    backends=DefaultBackendRegistry(),
                    event_bus=LoggingEventBus(),
                )
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """vector_db HTTP router"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException

            from app.modules.vector_db.application.exceptions import AppError
            from app.modules.vector_db.application.use_case import (
                VectorDBUseCase,
            )
            from app.modules.vector_db.domain.exceptions import VectorDBError
            from app.modules.vector_db.domain.value_objects import VectorQuery
            from app.modules.vector_db.presentation.dependencies import (
                Ctx, get_ctx, get_use_case,
            )
            from app.modules.vector_db.presentation.schemas import (
                CollectionCreateRequest, CollectionOut, IndexCreateRequest,
                IndexOut, QueryRequest, QueryResponse, SearchHitOut,
                StatsOut, UpsertRequest, UpsertResponse,
            )

            logger = logging.getLogger(__name__)

            router = APIRouter(prefix="/vdb", tags=["VectorDB"])


            def _raise(exc: Exception) -> None:
                if isinstance(exc, VectorDBError):
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
                    detail={"code": "INTERNAL_ERROR",
                            "message": "internal error"},
                )


            @router.get("/collections", response_model=list[CollectionOut])
            async def list_collections(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
            ) -> list[CollectionOut]:
                try:
                    items = await uc.list_collections(ctx)
                    return [
                        CollectionOut.model_validate({
                            "id": c.id, "name": c.name,
                            "dimension": c.dimension,
                            "metric": c.metric, "backend": c.backend,
                            "is_active": bool(c.is_active),
                        })
                        for c in items
                    ]
                except (VectorDBError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post(
                "/collections", response_model=CollectionOut, status_code=201,
            )
            async def create_collection(
                req: CollectionCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
            ) -> CollectionOut:
                try:
                    coll = await uc.create_collection(
                        ctx, name=req.name, dimension=req.dimension,
                        metric=req.metric, backend=req.backend,
                        config=req.config,
                    )
                    return CollectionOut.model_validate({
                        "id": coll.id, "name": coll.name,
                        "dimension": coll.dimension,
                        "metric": coll.metric, "backend": coll.backend,
                        "is_active": bool(coll.is_active),
                    })
                except (VectorDBError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post(
                "/collections/{collection_id}/upsert",
                response_model=UpsertResponse,
            )
            async def upsert(
                collection_id: uuid.UUID,
                req: UpsertRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
            ) -> UpsertResponse:
                try:
                    n = await uc.upsert(
                        ctx, collection_id=collection_id,
                        items=[item.model_dump() for item in req.items],
                    )
                    return UpsertResponse(
                        collection_id=collection_id, upserted=n,
                    )
                except (VectorDBError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post(
                "/collections/{collection_id}/query",
                response_model=QueryResponse,
            )
            async def query(
                collection_id: uuid.UUID,
                req: QueryRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
            ) -> QueryResponse:
                try:
                    from app.modules.vector_db.domain.enums import VectorMetric
                    q = VectorQuery(
                        vector=req.vector, top_k=req.top_k,
                        metric=req.metric or VectorMetric.COSINE,
                        filter=req.filter,
                        include_metadata=req.include_metadata,
                        score_threshold=req.score_threshold,
                    )
                    hits = await uc.query(
                        ctx, collection_id=collection_id, query=q,
                    )
                    return QueryResponse(
                        collection_id=collection_id,
                        hits=[
                            SearchHitOut.model_validate(h.model_dump())
                            for h in hits
                        ],
                    )
                except (VectorDBError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.delete(
                "/collections/{collection_id}/vectors/{vector_id}",
            )
            async def delete_vector(
                collection_id: uuid.UUID,
                vector_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
            ) -> dict:
                try:
                    ok_del = await uc.delete_vector(
                        ctx, collection_id=collection_id,
                        vector_id=vector_id,
                    )
                    return {"deleted": ok_del, "vector_id": str(vector_id)}
                except (VectorDBError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get(
                "/collections/{collection_id}/stats",
                response_model=StatsOut,
            )
            async def stats(
                collection_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
            ) -> StatsOut:
                try:
                    data = await uc.stats(ctx, collection_id)
                    return StatsOut(**data)
                except (VectorDBError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post(
                "/collections/{collection_id}/indexes",
                response_model=IndexOut, status_code=201,
            )
            async def build_index(
                collection_id: uuid.UUID,
                req: IndexCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
            ) -> IndexOut:
                try:
                    idx = await uc.build_index(
                        ctx, collection_id=collection_id,
                        index_type=str(req.index_type), params=req.params,
                    )
                    return IndexOut.model_validate({
                        "id": idx.id, "collection_id": idx.collection_id,
                        "name": idx.name, "index_type": idx.index_type,
                        "build_status": idx.build_status,
                        "size_bytes": idx.size_bytes or 0,
                    })
                except (VectorDBError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get(
                "/collections/{collection_id}/indexes",
                response_model=list[IndexOut],
            )
            async def list_indexes(
                collection_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[VectorDBUseCase, Depends(get_use_case)],
            ) -> list[IndexOut]:
                try:
                    items = await uc.list_indexes(ctx, collection_id)
                    return [
                        IndexOut.model_validate({
                            "id": i.id, "collection_id": i.collection_id,
                            "name": i.name, "index_type": i.index_type,
                            "build_status": i.build_status,
                            "size_bytes": i.size_bytes or 0,
                        })
                        for i in items
                    ]
                except (VectorDBError, AppError) as exc:
                    _raise(exc)
                    raise
        ''')

    def _swagger_content(self) -> str:
        return dedent('''\
            """vector_db OpenAPI docs"""
            from __future__ import annotations
            from typing import Any


            def register_vector_db_openapi(app: object) -> None:
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "VectorDB" for t in tags):
                        tags.append({
                            "name": "VectorDB",
                            "description": (
                                "โมดูล vector_db — ANN Store\\n\\n"
                                "• Collections + vectors\\n"
                                "• Query: cosine / L2 / IP\\n"
                                "• ANN indexes: HNSW / IVFFlat\\n"
                                "• Multi-backend: pgvector / Qdrant"
                            ),
                            "externalDocs": {
                                "description": "vector_db Module README",
                                "url": "/docs/README_vector_db.md",
                            },
                        })
                    info = schema.setdefault("info", {})
                    info.setdefault("x-module", "vector_db")
                    info.setdefault("x-layer", "5-Intel")
                    info.setdefault("x-prefix", "vdb")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent(f'''\
            """{self.module} module"""
            from .presentation.router import router as vdb_router

            __all__ = ["vdb_router"]
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
-- V001__create_vector_db.sql | Module: vector_db | Prefix: vdb
-- Schema: public | Tables: vdb_collections, vdb_vectors, vdb_indexes,
--                          vdb_namespaces, vdb_stats
-- ═══════════════════════════════════════════════════════════════
BEGIN;

CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS "public"."vdb_collections";
CREATE TABLE "public"."vdb_collections" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "name"         varchar(100) NOT NULL,
  "dimension"    int4 NOT NULL,
  "metric"       varchar(20) NOT NULL DEFAULT 'cosine',
  "backend"      varchar(20) NOT NULL DEFAULT 'pgvector',
  "config_json"  text NOT NULL DEFAULT '{}',
  "is_active"    bool NOT NULL DEFAULT true,
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "vdb_collections_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_vdb_collection_metric" CHECK (metric IN ('cosine','l2','ip')),
  CONSTRAINT "ck_vdb_collection_backend" CHECK (
    backend IN ('pgvector','qdrant','weaviate','pinecone','chroma','milvus')
  ),
  CONSTRAINT "uq_vdb_collection_name" UNIQUE ("tenant_id", "name")
);
CREATE INDEX "ix_vdb_collection_tenant" ON "public"."vdb_collections" ("tenant_id");

DROP TABLE IF EXISTS "public"."vdb_vectors";
CREATE TABLE "public"."vdb_vectors" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "collection_id"  uuid NOT NULL,
  "source_id"      varchar(200) NOT NULL,
  "vector_json"    text NOT NULL DEFAULT '[]',
  "metadata_json"  text NOT NULL DEFAULT '{}',
  "norm"           float8 NOT NULL DEFAULT 0,
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "vdb_vectors_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_vdb_vec_tenant_coll" ON "public"."vdb_vectors" ("tenant_id", "collection_id");
CREATE INDEX "ix_vdb_vec_source"      ON "public"."vdb_vectors" ("collection_id", "source_id");

DROP TABLE IF EXISTS "public"."vdb_indexes";
CREATE TABLE "public"."vdb_indexes" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "collection_id"  uuid NOT NULL,
  "name"           varchar(100) NOT NULL,
  "index_type"     varchar(20) NOT NULL DEFAULT 'hnsw',
  "params_json"    text NOT NULL DEFAULT '{}',
  "size_bytes"     int4 NOT NULL DEFAULT 0,
  "build_status"   varchar(20) NOT NULL DEFAULT 'PENDING',
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "vdb_indexes_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_vdb_index_type" CHECK (index_type IN ('hnsw','ivfflat','flat','scann','diskann')),
  CONSTRAINT "ck_vdb_index_status" CHECK (build_status IN ('PENDING','BUILDING','READY','FAILED'))
);
CREATE INDEX "ix_vdb_index_collection" ON "public"."vdb_indexes" ("collection_id");

DROP TABLE IF EXISTS "public"."vdb_namespaces";
CREATE TABLE "public"."vdb_namespaces" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "collection_id"  uuid NOT NULL,
  "namespace"      varchar(100) NOT NULL,
  "prefix"         varchar(100) NOT NULL DEFAULT '',
  "quota"          int4 NOT NULL DEFAULT 0,
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "vdb_namespaces_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_vdb_namespace" UNIQUE ("tenant_id", "collection_id", "namespace")
);
CREATE INDEX "ix_vdb_ns_tenant" ON "public"."vdb_namespaces" ("tenant_id");

DROP TABLE IF EXISTS "public"."vdb_stats";
CREATE TABLE "public"."vdb_stats" (
  "id"              uuid NOT NULL DEFAULT gen_random_uuid(),
  "collection_id"   uuid NOT NULL,
  "vector_count"    int4 NOT NULL DEFAULT 0,
  "size_bytes"      int4 NOT NULL DEFAULT 0,
  "avg_latency_ms"  float8 NOT NULL DEFAULT 0,
  "updated_at"      timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "vdb_stats_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_vdb_stats_collection" UNIQUE ("collection_id")
);

CREATE OR REPLACE FUNCTION public.set_updated_at_vdb()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_vdb_collection_updated ON "public"."vdb_collections";
CREATE TRIGGER trg_vdb_collection_updated BEFORE UPDATE ON "public"."vdb_collections"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_vdb();

DROP TRIGGER IF EXISTS trg_vdb_vector_updated ON "public"."vdb_vectors";
CREATE TRIGGER trg_vdb_vector_updated BEFORE UPDATE ON "public"."vdb_vectors"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_vdb();

DROP TRIGGER IF EXISTS trg_vdb_index_updated ON "public"."vdb_indexes";
CREATE TRIGGER trg_vdb_index_updated BEFORE UPDATE ON "public"."vdb_indexes"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_vdb();

DROP TRIGGER IF EXISTS trg_vdb_ns_updated ON "public"."vdb_namespaces";
CREATE TRIGGER trg_vdb_ns_updated BEFORE UPDATE ON "public"."vdb_namespaces"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_vdb();

DROP TRIGGER IF EXISTS trg_vdb_stats_updated ON "public"."vdb_stats";
CREATE TRIGGER trg_vdb_stats_updated BEFORE UPDATE ON "public"."vdb_stats"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_vdb();

ALTER TABLE "public"."vdb_collections" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."vdb_vectors"     ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."vdb_indexes"     ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."vdb_namespaces"  ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."vdb_stats"       ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_vdb_collection ON "public"."vdb_collections";
CREATE POLICY p_vdb_collection ON "public"."vdb_collections"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_vdb_vector ON "public"."vdb_vectors";
CREATE POLICY p_vdb_vector ON "public"."vdb_vectors"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_vdb_index ON "public"."vdb_indexes";
CREATE POLICY p_vdb_index ON "public"."vdb_indexes"
    USING (collection_id IN (
        SELECT id FROM "public"."vdb_collections"
        WHERE tenant_id = current_setting('app.current_tenant', true)::uuid
    ));

DROP POLICY IF EXISTS p_vdb_ns ON "public"."vdb_namespaces";
CREATE POLICY p_vdb_ns ON "public"."vdb_namespaces"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_vdb_stats ON "public"."vdb_stats";
CREATE POLICY p_vdb_stats ON "public"."vdb_stats"
    USING (collection_id IN (
        SELECT id FROM "public"."vdb_collections"
        WHERE tenant_id = current_setting('app.current_tenant', true)::uuid
    ));

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_vector_db.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."vdb_collections"
    (tenant_id, name, dimension, metric, backend)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'default_1536',
     1536, 'cosine', 'pgvector')
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_vector_db.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_vdb_stats_updated      ON "public"."vdb_stats";
DROP TRIGGER IF EXISTS trg_vdb_ns_updated         ON "public"."vdb_namespaces";
DROP TRIGGER IF EXISTS trg_vdb_index_updated      ON "public"."vdb_indexes";
DROP TRIGGER IF EXISTS trg_vdb_vector_updated     ON "public"."vdb_vectors";
DROP TRIGGER IF EXISTS trg_vdb_collection_updated ON "public"."vdb_collections";

DROP POLICY IF EXISTS p_vdb_stats      ON "public"."vdb_stats";
DROP POLICY IF EXISTS p_vdb_ns         ON "public"."vdb_namespaces";
DROP POLICY IF EXISTS p_vdb_index      ON "public"."vdb_indexes";
DROP POLICY IF EXISTS p_vdb_vector     ON "public"."vdb_vectors";
DROP POLICY IF EXISTS p_vdb_collection ON "public"."vdb_collections";

DROP TABLE IF EXISTS "public"."vdb_stats"       CASCADE;
DROP TABLE IF EXISTS "public"."vdb_namespaces"  CASCADE;
DROP TABLE IF EXISTS "public"."vdb_indexes"     CASCADE;
DROP TABLE IF EXISTS "public"."vdb_vectors"     CASCADE;
DROP TABLE IF EXISTS "public"."vdb_collections" CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_vdb();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "vdb_001"
        content = f'''"""add vector_db tables

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
    """TH: สร้างตาราง vector_db | EN: create tables"""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        "vdb_collections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("dimension", sa.Integer, nullable=False),
        sa.Column("metric", sa.String(20), nullable=False, server_default="cosine"),
        sa.Column("backend", sa.String(20), nullable=False, server_default="pgvector"),
        sa.Column("config_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_vdb_collection_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "vdb_vectors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", sa.String(200), nullable=False),
        sa.Column("vector_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("metadata_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("norm", sa.Float, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "vdb_indexes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("index_type", sa.String(20), nullable=False, server_default="hnsw"),
        sa.Column("params_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("size_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("build_status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "vdb_namespaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("namespace", sa.String(100), nullable=False),
        sa.Column("prefix", sa.String(100), nullable=False, server_default=""),
        sa.Column("quota", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "collection_id", "namespace", name="uq_vdb_namespace"),
        schema=SCHEMA,
    )
    op.create_table(
        "vdb_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vector_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("size_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("avg_latency_ms", sa.Float, nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("collection_id", name="uq_vdb_stats_collection"),
        schema=SCHEMA,
    )

    op.create_index("ix_vdb_collection_tenant", "vdb_collections", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_vdb_vec_tenant_coll", "vdb_vectors", ["tenant_id", "collection_id"], schema=SCHEMA)
    op.create_index("ix_vdb_vec_source", "vdb_vectors", ["collection_id", "source_id"], schema=SCHEMA)
    op.create_index("ix_vdb_index_collection", "vdb_indexes", ["collection_id"], schema=SCHEMA)
    op.create_index("ix_vdb_ns_tenant", "vdb_namespaces", ["tenant_id"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_vdb()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in ("vdb_collections", "vdb_vectors", "vdb_indexes",
                "vdb_namespaces", "vdb_stats"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE TRIGGER trg_{{tbl}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_vdb();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """TH: ลบตาราง | EN: drop tables"""
    for tbl in ("vdb_stats", "vdb_namespaces", "vdb_indexes",
                "vdb_vectors", "vdb_collections"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_vdb();")
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
                {"key": "collection_id", "value": "REPLACE_WITH_COLLECTION_UUID"},
            ],
            "item": [
                {
                    "name": "List Collections",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/vdb/collections",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "vdb", "collections"],
                        },
                    },
                },
                {
                    "name": "Create Collection",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/vdb/collections",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "vdb", "collections"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"my_collection","dimension":1536,"metric":"cosine","backend":"pgvector"}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Upsert Vectors",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/vdb/collections/{{collection_id}}/upsert",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "vdb", "collections",
                                     "{{collection_id}}", "upsert"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"items":[{"source_id":"doc1","vector":[0.1,0.2],"metadata":{"tag":"a"}}]}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Query Vectors",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/vdb/collections/{{collection_id}}/query",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "vdb", "collections",
                                     "{{collection_id}}", "query"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"vector":[0.1,0.2],"top_k":5,"metric":"cosine"}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Build Index",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/vdb/collections/{{collection_id}}/indexes",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "vdb", "collections",
                                     "{{collection_id}}", "indexes"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"index_type":"hnsw","params":{"m":16,"ef_construction":64}}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Stats",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/vdb/collections/{{collection_id}}/stats",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "vdb", "collections",
                                     "{{collection_id}}", "stats"],
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
        VDBCollectionModel,
        VDBIndexModel,
        VDBNamespaceModel,
        VDBStatsModel,
        VDBVectorModel,
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
create_module_vector_db.py — Vector DB Module Generator v{VERSION}

USAGE
    python create_module_vector_db.py <action> [options]

MODULE
    name    : vector_db
    layer   : 5-Intel
    prefix  : vdb
    schema  : public
    tables  : vdb_collections, vdb_vectors, vdb_indexes,
              vdb_namespaces, vdb_stats
    depends : embeddings

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
    python create_module_vector_db.py all
    python create_module_vector_db.py create --force
    python create_module_vector_db.py verify
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