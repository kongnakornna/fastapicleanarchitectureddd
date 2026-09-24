#!/usr/bin/env python3
"""
create_module_rag.py — RAG Module Generator v1.0.0

สร้าง module rag ตาม Clean Architecture + DDD + Event-Driven
Module: rag · Prefix: rag_ · Schema: public
Layer: 5-Intel · Depends: llm, embeddings, vector_db, hybrid_search

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
    "name": "rag",
    "title": "RAG Pipeline",
    "layer": "5-Intel",
    "prefix": "rag",
    "tag": "RAG",
    "tag_desc": "RAG — Retrieval Augmented Generation (ingest → retrieve → generate)",
    "depends": ["llm", "embeddings", "vector_db", "hybrid_search"],
    "tables": (
        "rag_documents",
        "rag_chunks",
        "rag_pipelines",
        "rag_runs",
        "rag_citations",
        "rag_retrieval_logs",
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
            """rag value objects"""
            from .chunk_config import ChunkConfig
            from .retrieval_config import RetrievalConfig
            from .citation import CitationVO

            __all__ = ["ChunkConfig", "RetrievalConfig", "CitationVO"]
        '''))

        self.writer.write(f"{base}/value_objects/chunk_config.py", dedent('''\
            """ChunkConfig VO"""
            from __future__ import annotations
            from typing import Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.rag.domain.enums import ChunkerType


            class ChunkConfig(BaseModel):
                """TH: การตั้งค่าการแบ่ง chunk | EN: Chunk config"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                chunker_type: ChunkerType = ChunkerType.RECURSIVE
                chunk_size: int = Field(default=512, ge=64, le=8192)
                chunk_overlap: int = Field(default=50, ge=0, le=2048)
                separators: Optional[list[str]] = None
                min_chunk_size: int = Field(default=64, ge=1, le=2048)
        '''))

        self.writer.write(f"{base}/value_objects/retrieval_config.py", dedent('''\
            """RetrievalConfig VO"""
            from __future__ import annotations
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.rag.domain.enums import RerankerType, RetrieverType


            class RetrievalConfig(BaseModel):
                """TH: การตั้งค่า retrieval | EN: Retrieval config"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                retriever_type: RetrieverType = RetrieverType.VECTOR
                top_k: int = Field(default=5, ge=1, le=100)
                score_threshold: float = Field(default=0.0, ge=-1.0, le=1.0)
                reranker_type: RerankerType = RerankerType.NONE
                mmr_lambda: float = Field(default=0.5, ge=0.0, le=1.0)
        '''))

        self.writer.write(f"{base}/value_objects/citation.py", dedent('''\
            """CitationVO"""
            from __future__ import annotations
            import uuid
            from pydantic import BaseModel, ConfigDict, Field


            class CitationVO(BaseModel):
                """TH: การอ้างอิง 1 รายการ | EN: Citation"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                chunk_id: uuid.UUID
                document_id: uuid.UUID
                score: float
                rank: int = Field(ge=1)
                snippet: str = ""
        '''))

        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """rag entities"""
            from .document import Document
            from .chunk import Chunk
            from .pipeline import Pipeline
            from .run import Run
            from .citation import Citation
            from .retrieval_log import RetrievalLog

            __all__ = [
                "Document", "Chunk", "Pipeline", "Run", "Citation",
                "RetrievalLog",
            ]
        '''))

        for name, cls, model in (
            ("document", "Document", "RAGDocumentModel"),
            ("chunk", "Chunk", "RAGChunkModel"),
            ("pipeline", "Pipeline", "RAGPipelineModel"),
            ("run", "Run", "RAGRunModel"),
            ("citation", "Citation", "RAGCitationModel"),
            ("retrieval_log", "RetrievalLog", "RAGRetrievalLogModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias to ORM"""
                from __future__ import annotations
                from app.modules.{self.module}.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """rag helpers"""
            from .chunkers import (
                chunk_fixed, chunk_recursive, chunk_markdown,
            )
            from .hasher import document_hash

            __all__ = [
                "chunk_fixed", "chunk_recursive", "chunk_markdown",
                "document_hash",
            ]
        '''))

        self.writer.write(f"{base}/helpers/chunkers.py", self._helper_chunkers())
        self.writer.write(f"{base}/helpers/hasher.py", dedent('''\
            """hasher"""
            from __future__ import annotations
            import hashlib


            def document_hash(content: str) -> str:
                """TH: hash เอกสาร | EN: document hash"""
                return hashlib.sha256(content.encode("utf-8")).hexdigest()
        '''))

    def _domain_enums(self) -> str:
        return dedent('''\
            """rag enums"""
            from __future__ import annotations
            from enum import Enum


            class ChunkerType(str, Enum):
                """TH: ประเภทการแบ่ง chunk | EN: Chunker type"""
                FIXED = "fixed"
                RECURSIVE = "recursive"
                SEMANTIC = "semantic"
                MARKDOWN = "markdown"
                CODE = "code"

                def __str__(self) -> str:
                    return str(self.value)


            class RetrieverType(str, Enum):
                """TH: ประเภท retriever | EN: Retriever type"""
                VECTOR = "vector"
                BM25 = "bm25"
                HYBRID = "hybrid"
                MMR = "mmr"

                def __str__(self) -> str:
                    return str(self.value)


            class RerankerType(str, Enum):
                """TH: ประเภท reranker | EN: Reranker type"""
                NONE = "none"
                CROSS_ENCODER = "cross_encoder"
                COHERE = "cohere"
                BGE = "bge"

                def __str__(self) -> str:
                    return str(self.value)


            class DocumentStatus(str, Enum):
                """TH: สถานะเอกสาร | EN: Document status"""
                PENDING = "PENDING"
                PROCESSING = "PROCESSING"
                READY = "READY"
                FAILED = "FAILED"
                DELETED = "DELETED"

                def __str__(self) -> str:
                    return str(self.value)


            class RunStatus(str, Enum):
                """TH: สถานะ run | EN: Run status"""
                QUEUED = "QUEUED"
                RETRIEVING = "RETRIEVING"
                RERANKING = "RERANKING"
                GENERATING = "GENERATING"
                DONE = "DONE"
                FAILED = "FAILED"

                def __str__(self) -> str:
                    return str(self.value)
        ''')

    def _domain_exceptions(self) -> str:
        return dedent('''\
            """rag domain exceptions"""
            from __future__ import annotations


            class RAGError(Exception):
                """TH: base | EN: base"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class DocumentNotFoundError(RAGError):
                code = "NOT_FOUND"


            class ChunkNotFoundError(RAGError):
                code = "NOT_FOUND"


            class PipelineNotFoundError(RAGError):
                code = "NOT_FOUND"


            class RunNotFoundError(RAGError):
                code = "NOT_FOUND"


            class IngestionFailedError(RAGError):
                code = "PROVIDER_ERROR"


            class ChunkingFailedError(RAGError):
                code = "PROVIDER_ERROR"


            class RetrievalFailedError(RAGError):
                code = "PROVIDER_ERROR"


            class GenerationFailedError(RAGError):
                code = "PROVIDER_ERROR"


            class DuplicateDocumentError(RAGError):
                code = "CONFLICT"


            class EmptyQueryError(RAGError):
                code = "VALIDATION_ERROR"
        ''')

    def _domain_events(self) -> str:
        return dedent('''\
            """rag domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import datetime, timezone


            def _now():
                return datetime.now(timezone.utc)


            @dataclass(frozen=True)
            class DocumentIngested:
                document_id: uuid.UUID
                tenant_id: uuid.UUID
                source_uri: str
                size_bytes: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class DocumentChunked:
                document_id: uuid.UUID
                tenant_id: uuid.UUID
                chunk_count: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class RetrievalCompleted:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                retriever_type: str
                top_k: int
                latency_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class RAGAnswerGenerated:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                model_name: str
                citation_count: int
                tokens_used: int
                cost_usd: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class PipelineCreated:
                pipeline_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                occurred_at: datetime = field(default_factory=_now)
        ''')

    def _helper_chunkers(self) -> str:
        return dedent('''\
            """chunkers"""
            from __future__ import annotations
            from typing import Optional


            def _overlap_slices(text: str, size: int, overlap: int) -> list[str]:
                if size <= 0:
                    return [text]
                step = max(1, size - max(0, overlap))
                return [text[i : i + size] for i in range(0, len(text), step)]


            def chunk_fixed(
                text: str, *, chunk_size: int = 512, chunk_overlap: int = 50,
            ) -> list[str]:
                if not text:
                    return []
                return [
                    c for c in _overlap_slices(text, chunk_size, chunk_overlap)
                    if c.strip()
                ]


            def chunk_recursive(
                text: str, *, chunk_size: int = 512, chunk_overlap: int = 50,
                separators: Optional[list[str]] = None,
            ) -> list[str]:
                if not text:
                    return []
                seps = separators or ["\\n\\n", "\\n", ". ", " "]

                def split_rec(segment: str, seps_left: list[str]) -> list[str]:
                    if len(segment) <= chunk_size or not seps_left:
                        return _overlap_slices(segment, chunk_size, chunk_overlap)
                    sep = seps_left[0]
                    parts = segment.split(sep)
                    out: list[str] = []
                    buf = ""
                    for p in parts:
                        candidate = (buf + sep + p) if buf else p
                        if len(candidate) <= chunk_size:
                            buf = candidate
                        else:
                            if buf:
                                out.append(buf)
                            if len(p) > chunk_size:
                                out.extend(split_rec(p, seps_left[1:]))
                                buf = ""
                            else:
                                buf = p
                    if buf:
                        out.append(buf)
                    return out

                chunks = split_rec(text, seps)
                return [c.strip() for c in chunks if c.strip()]


            def chunk_markdown(
                text: str, *, chunk_size: int = 512, chunk_overlap: int = 50,
            ) -> list[str]:
                if not text:
                    return []
                blocks: list[str] = []
                buf: list[str] = []
                for line in text.splitlines():
                    if line.startswith("#") and buf:
                        blocks.append("\\n".join(buf))
                        buf = [line]
                    else:
                        buf.append(line)
                if buf:
                    blocks.append("\\n".join(buf))

                out: list[str] = []
                for block in blocks:
                    if len(block) <= chunk_size:
                        out.append(block)
                    else:
                        out.extend(_overlap_slices(
                            block, chunk_size, chunk_overlap,
                        ))
                return [c.strip() for c in out if c.strip()]
        ''')

    # ─── APPLICATION LAYER ────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} application layer"""
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """rag application exceptions"""
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
            """rag application ports"""
            from __future__ import annotations
            import uuid
            from abc import ABC, abstractmethod
            from typing import Any, Optional, Protocol, runtime_checkable

            from app.modules.rag.domain.value_objects import CitationVO


            @runtime_checkable
            class RequestContext(Protocol):
                @property
                def tenant_id(self) -> uuid.UUID: ...
                @property
                def user_id(self) -> Optional[uuid.UUID]: ...


            class DocumentRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, d: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_hash(self, ctx: Any, h: str) -> Any | None: ...
                @abstractmethod
                async def list(
                    self, ctx: Any, limit: int, offset: int,
                ) -> list[Any]: ...
                @abstractmethod
                async def update(self, ctx: Any, d: Any) -> Any: ...


            class ChunkRepository(ABC):
                @abstractmethod
                async def create_many(
                    self, ctx: Any, chunks: list[Any],
                ) -> int: ...
                @abstractmethod
                async def find_by_document(
                    self, ctx: Any, document_id: uuid.UUID,
                ) -> list[Any]: ...
                @abstractmethod
                async def delete_by_document(
                    self, ctx: Any, document_id: uuid.UUID,
                ) -> int: ...


            class PipelineRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, p: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
                @abstractmethod
                async def find_all_active(self, ctx: Any) -> list[Any]: ...


            class RunRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, r: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def update(self, ctx: Any, r: Any) -> Any: ...


            class CitationRepository(ABC):
                @abstractmethod
                async def create_many(
                    self, ctx: Any, citations: list[Any],
                ) -> int: ...
                @abstractmethod
                async def find_by_run(
                    self, ctx: Any, run_id: uuid.UUID,
                ) -> list[Any]: ...


            class RetrievalLogRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, log: Any) -> Any: ...
                @abstractmethod
                async def find_by_run(
                    self, ctx: Any, run_id: uuid.UUID,
                ) -> list[Any]: ...


            class EmbeddingPort(Protocol):
                async def embed(
                    self, *, model: str, texts: list[str],
                    normalize: bool = True,
                ) -> list[Any]: ...


            class VectorStorePort(Protocol):
                async def upsert(
                    self, *, collection_id: uuid.UUID,
                    items: list[dict[str, Any]],
                ) -> int: ...

                async def query(
                    self, *, collection_id: uuid.UUID,
                    vector: list[float], top_k: int,
                ) -> list[Any]: ...


            class HybridSearchPort(Protocol):
                async def search(
                    self, *, query: str, top_k: int,
                ) -> list[Any]: ...


            class RerankerPort(Protocol):
                async def rerank(
                    self, *, query: str,
                    candidates: list[dict[str, Any]], top_k: int,
                ) -> list[dict[str, Any]]: ...


            class GeneratorPort(Protocol):
                async def chat(
                    self, *, model: str, messages: list[dict[str, Any]],
                    system_prompt: Optional[str] = None,
                ) -> Any: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...
        ''')

    def _mappers_content(self) -> str:
        return dedent('''\
            """rag mappers — ORM → dict"""
            from __future__ import annotations
            from typing import Any


            def document_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "source_uri": row.source_uri or "",
                    "mime_type": row.mime_type or "",
                    "title": row.title or "",
                    "status": row.status,
                    "size_bytes": row.size_bytes or 0,
                    "chunk_count": row.chunk_count or 0,
                }


            def chunk_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "document_id": str(row.document_id),
                    "ordinal": row.ordinal or 0,
                    "content": row.content or "",
                    "token_count": row.token_count or 0,
                }


            def pipeline_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "name": row.name,
                    "chunker_type": row.chunker_type,
                    "chunk_size": row.chunk_size or 512,
                    "chunk_overlap": row.chunk_overlap or 50,
                    "retriever_type": row.retriever_type,
                    "top_k": row.top_k or 5,
                    "reranker_type": row.reranker_type,
                    "embedding_model": row.embedding_model or "",
                    "generation_model": row.generation_model or "",
                    "is_active": bool(row.is_active),
                }


            def run_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "query": row.query or "",
                    "answer": row.answer or "",
                    "model_name": row.model_name or "",
                    "latency_ms": row.latency_ms or 0,
                    "total_tokens": row.total_tokens or 0,
                    "cost_usd": str(row.cost_usd or "0"),
                    "status": row.status,
                }


            def citation_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "run_id": str(row.run_id),
                    "chunk_id": str(row.chunk_id),
                    "document_id": str(row.document_id),
                    "score": float(row.score or 0.0),
                    "rank": row.rank or 0,
                    "snippet": row.snippet or "",
                }
        ''')

    def _utils_content(self) -> str:
        return dedent('''\
            """rag application utils"""
            from __future__ import annotations
            import hashlib
            import json
            import time
            from typing import Any


            def make_cache_key(
                tenant_id: str, model: str, query: str, top_k: int,
            ) -> str:
                raw = f"{tenant_id}|{model}|{query}|{top_k}"
                digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
                return f"rag:q:{digest}"


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


            def build_context_block(chunks: list[dict[str, Any]]) -> str:
                lines: list[str] = []
                for i, c in enumerate(chunks, start=1):
                    snippet = (c.get("content") or "").strip().replace("\\n", " ")
                    lines.append(f"[{i}] {snippet}")
                return "\\n\\n".join(lines)
        ''')

    def _use_case_content(self) -> str:
        return dedent('''\
            """rag use cases"""
            from __future__ import annotations
            import logging
            import uuid
            from decimal import Decimal
            from typing import Any, Optional

            from app.modules.rag.application.exceptions import (
                ConflictAppError, NotFoundAppError, ProviderAppError,
            )
            from app.modules.rag.application.utils import (
                build_context_block, json_dumps_safe, make_cache_key, ms_now,
            )
            from app.modules.rag.domain.enums import DocumentStatus, RunStatus
            from app.modules.rag.domain.events import (
                DocumentChunked, DocumentIngested, RAGAnswerGenerated,
                RetrievalCompleted,
            )
            from app.modules.rag.domain.helpers.chunkers import (
                chunk_fixed, chunk_markdown, chunk_recursive,
            )
            from app.modules.rag.domain.helpers.hasher import document_hash
            from app.modules.rag.domain.value_objects import (
                ChunkConfig, CitationVO,
            )

            logger = logging.getLogger(__name__)


            class RAGUseCase:
                """TH: use case หลักของ RAG | EN: core RAG use case"""

                def __init__(self, **deps: Any) -> None:
                    for key, value in deps.items():
                        setattr(self, f"_{key}", value)
                    self._collection_id = getattr(
                        self, "_collection_id", None,
                    ) or uuid.UUID(int=0)

                async def ingest(
                    self, ctx: Any, *,
                    content: str, source_uri: str = "",
                    mime_type: str = "text/plain", title: str = "",
                    pipeline_id: Optional[uuid.UUID] = None,
                    metadata: Optional[dict[str, Any]] = None,
                ) -> Any:
                    """TH: ingest document | EN: ingest document"""
                    from app.modules.rag.infrastructure.models import (
                        RAGChunkModel, RAGDocumentModel,
                    )

                    if not content:
                        raise ProviderAppError("empty document")

                    pipeline = await self._resolve_pipeline(ctx, pipeline_id)

                    h = document_hash(content)
                    existing = await self._documents.find_by_hash(ctx, h)
                    if existing is not None and existing.status != "DELETED":
                        return existing

                    doc = RAGDocumentModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id,
                        source_uri=source_uri, mime_type=mime_type,
                        title=title or source_uri or "untitled",
                        content=content, hash=h,
                        size_bytes=len(content.encode("utf-8")),
                        metadata_json=json_dumps_safe(metadata or {}),
                        status="PENDING",
                    )
                    saved = await self._documents.save(ctx, doc)

                    if self._bus:
                        try:
                            await self._bus.publish(DocumentIngested(
                                document_id=saved.id,
                                tenant_id=saved.tenant_id,
                                source_uri=saved.source_uri,
                                size_bytes=saved.size_bytes or 0,
                            ))
                        except Exception:
                            pass

                    saved.status = "PROCESSING"
                    saved = await self._documents.update(ctx, saved)

                    try:
                        chunk_texts = self._chunk(content, pipeline)
                        if not chunk_texts:
                            saved.status = "FAILED"
                            await self._documents.update(ctx, saved)
                            return saved

                        embeddings = await self._embedder.embed(
                            model=pipeline.embedding_model, texts=chunk_texts,
                        )

                        items: list[dict[str, Any]] = []
                        for i, ct in enumerate(chunk_texts):
                            vec = self._extract_vector(
                                embeddings[i],
                            ) if i < len(embeddings) else []
                            items.append({
                                "source_id": f"{saved.id}:{i}",
                                "vector": vec,
                                "metadata": {
                                    "document_id": str(saved.id),
                                    "ordinal": i,
                                },
                            })
                        if items:
                            await self._vector_store.upsert(
                                collection_id=self._collection_id, items=items,
                            )

                        chunk_rows = [
                            RAGChunkModel(
                                tenant_id=ctx.tenant_id,
                                document_id=saved.id,
                                ordinal=i, content=ct,
                                token_count=max(1, len(ct) // 4),
                                metadata_json="{}",
                            )
                            for i, ct in enumerate(chunk_texts)
                        ]
                        count = await self._chunks.create_many(ctx, chunk_rows)

                        saved.status = "READY"
                        saved.chunk_count = count
                        saved = await self._documents.update(ctx, saved)

                        if self._bus:
                            try:
                                await self._bus.publish(DocumentChunked(
                                    document_id=saved.id,
                                    tenant_id=saved.tenant_id,
                                    chunk_count=count,
                                ))
                            except Exception:
                                pass
                    except Exception as exc:
                        logger.exception("ingest failed: %s", exc)
                        saved.status = "FAILED"
                        await self._documents.update(ctx, saved)
                        raise ProviderAppError(
                            f"ingest failed: {exc}"
                        ) from exc
                    return saved

                async def query(
                    self, ctx: Any, *,
                    query: str, pipeline_id: Optional[uuid.UUID] = None,
                    conversation_id: Optional[uuid.UUID] = None,
                    use_cache: bool = True,
                ) -> dict[str, Any]:
                    """TH: query + generate | EN: query + generate"""
                    from app.modules.rag.infrastructure.models import (
                        RAGCitationModel, RAGRetrievalLogModel, RAGRunModel,
                    )

                    if not query.strip():
                        raise ProviderAppError("empty query")

                    pipeline = await self._resolve_pipeline(ctx, pipeline_id)

                    run = RAGRunModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id,
                        pipeline_id=pipeline.id,
                        conversation_id=conversation_id,
                        query=query,
                        model_name=pipeline.generation_model,
                        status="QUEUED",
                    )
                    saved_run = await self._runs.save(ctx, run)
                    started_ms = ms_now()

                    cache_key = make_cache_key(
                        str(ctx.tenant_id), pipeline.generation_model,
                        query, pipeline.top_k,
                    )
                    if use_cache and self._cache is not None:
                        try:
                            cached = await self._cache.get(cache_key)
                            if cached:
                                cached["cached"] = True
                                cached["run_id"] = str(saved_run.id)
                                return cached
                        except Exception as exc:
                            logger.debug("cache get failed: %s", exc)

                    try:
                        saved_run.status = "RETRIEVING"
                        await self._runs.update(ctx, saved_run)

                        retrieve_started = ms_now()
                        candidates = await self._retrieve(ctx, pipeline, query)
                        retrieve_ms = ms_now() - retrieve_started

                        await self._retrieval_logs.create(ctx, RAGRetrievalLogModel(
                            tenant_id=ctx.tenant_id, run_id=saved_run.id,
                            stage="retrieve", top_k=pipeline.top_k,
                            candidates_json=json_dumps_safe([
                                {
                                    "chunk_id": str(c.get("chunk_id", "")),
                                    "score": c.get("score", 0),
                                }
                                for c in candidates[:50]
                            ]),
                            latency_ms=retrieve_ms,
                        ))

                        if self._bus:
                            try:
                                await self._bus.publish(RetrievalCompleted(
                                    run_id=saved_run.id,
                                    tenant_id=ctx.tenant_id,
                                    retriever_type=str(pipeline.retriever_type),
                                    top_k=pipeline.top_k,
                                    latency_ms=retrieve_ms,
                                ))
                            except Exception:
                                pass

                        saved_run.status = "GENERATING"
                        await self._runs.update(ctx, saved_run)

                        context_block = build_context_block(candidates)
                        messages = [{"role": "user", "content": query}]
                        system_prompt = (
                            "You are a helpful assistant. "
                            "Answer using ONLY the following context. "
                            "Cite sources as [1], [2], etc.\\n\\n"
                            f"Context:\\n{context_block}"
                        )

                        answer, tokens, cost = await self._generate(
                            pipeline, messages, system_prompt,
                        )

                        saved_run.answer = answer
                        saved_run.total_tokens = tokens
                        saved_run.cost_usd = Decimal(str(cost))
                        saved_run.latency_ms = ms_now() - started_ms
                        saved_run.status = "DONE"
                        await self._runs.update(ctx, saved_run)

                        citations = self._build_citations(candidates)
                        if citations:
                            await self._citations.create_many(ctx, [
                                RAGCitationModel(
                                    tenant_id=ctx.tenant_id,
                                    run_id=saved_run.id,
                                    chunk_id=cv.chunk_id,
                                    document_id=cv.document_id,
                                    score=cv.score, rank=cv.rank,
                                    snippet=cv.snippet,
                                )
                                for cv in citations
                            ])

                        if self._bus:
                            try:
                                await self._bus.publish(RAGAnswerGenerated(
                                    run_id=saved_run.id,
                                    tenant_id=ctx.tenant_id,
                                    model_name=pipeline.generation_model,
                                    citation_count=len(citations),
                                    tokens_used=tokens,
                                    cost_usd=str(cost),
                                ))
                            except Exception:
                                pass

                        result = {
                            "run_id": str(saved_run.id),
                            "answer": answer,
                            "citations": [cv.model_dump() for cv in citations],
                            "usage": {
                                "total_tokens": tokens,
                                "cost_usd": str(cost),
                            },
                            "cached": False,
                        }

                        if use_cache and self._cache is not None:
                            try:
                                await self._cache.set(cache_key, {
                                    "answer": answer,
                                    "citations": [
                                        cv.model_dump() for cv in citations
                                    ],
                                    "usage": {
                                        "total_tokens": tokens,
                                        "cost_usd": str(cost),
                                    },
                                })
                            except Exception as exc:
                                logger.debug("cache set failed: %s", exc)
                        return result

                    except Exception as exc:
                        logger.exception("rag query failed: %s", exc)
                        saved_run.status = "FAILED"
                        saved_run.error_message = str(exc)[:500]
                        try:
                            await self._runs.update(ctx, saved_run)
                        except Exception:
                            pass
                        if isinstance(exc, (NotFoundAppError, ProviderAppError)):
                            raise
                        raise ProviderAppError(
                            f"rag query failed: {exc}"
                        ) from exc

                async def list_documents(
                    self, ctx: Any, *, limit: int = 50, offset: int = 0,
                ) -> list[Any]:
                    return await self._documents.list(
                        ctx, limit=limit, offset=offset,
                    )

                async def get_document(
                    self, ctx: Any, document_id: uuid.UUID,
                ) -> tuple[Any, list[Any]]:
                    doc = await self._documents.find_by_id(ctx, document_id)
                    if doc is None:
                        raise NotFoundAppError("document not found")
                    chunks = await self._chunks.find_by_document(
                        ctx, document_id,
                    )
                    return doc, chunks

                async def delete_document(
                    self, ctx: Any, document_id: uuid.UUID,
                ) -> bool:
                    doc = await self._documents.find_by_id(ctx, document_id)
                    if doc is None:
                        raise NotFoundAppError("document not found")
                    doc.status = "DELETED"
                    await self._documents.update(ctx, doc)
                    try:
                        await self._chunks.delete_by_document(ctx, document_id)
                    except Exception as exc:
                        logger.debug("delete chunks failed: %s", exc)
                    return True

                async def create_pipeline(
                    self, ctx: Any, **kwargs: Any,
                ) -> Any:
                    from app.modules.rag.infrastructure.models import (
                        RAGPipelineModel,
                    )
                    existing = await self._pipelines.find_by_name(
                        ctx, kwargs.get("name", ""),
                    )
                    if existing is not None:
                        raise ConflictAppError("pipeline name exists")
                    p = RAGPipelineModel(tenant_id=ctx.tenant_id, **kwargs)
                    return await self._pipelines.save(ctx, p)

                async def list_pipelines(self, ctx: Any) -> list[Any]:
                    return await self._pipelines.find_all_active(ctx)

                async def get_run(self, ctx: Any, run_id: uuid.UUID) -> Any:
                    r = await self._runs.find_by_id(ctx, run_id)
                    if r is None:
                        raise NotFoundAppError("run not found")
                    return r

                async def _resolve_pipeline(
                    self, ctx: Any, pipeline_id: Optional[uuid.UUID],
                ) -> Any:
                    from app.modules.rag.infrastructure.models import (
                        RAGPipelineModel,
                    )
                    if pipeline_id is not None:
                        p = await self._pipelines.find_by_id(ctx, pipeline_id)
                        if p is None:
                            raise NotFoundAppError("pipeline not found")
                        return p
                    existing = await self._pipelines.find_all_active(ctx)
                    if existing:
                        return existing[0]
                    default = RAGPipelineModel(
                        tenant_id=ctx.tenant_id, name="default",
                        chunker_type="recursive", chunk_size=512,
                        chunk_overlap=50, retriever_type="vector",
                        top_k=5, reranker_type="none",
                    )
                    return await self._pipelines.save(ctx, default)

                def _chunk(self, content: str, pipeline: Any) -> list[str]:
                    cfg = ChunkConfig(
                        chunker_type=pipeline.chunker_type,
                        chunk_size=pipeline.chunk_size,
                        chunk_overlap=pipeline.chunk_overlap,
                    )
                    ct = str(cfg.chunker_type)
                    if ct == "fixed":
                        return chunk_fixed(
                            content, chunk_size=cfg.chunk_size,
                            chunk_overlap=cfg.chunk_overlap,
                        )
                    if ct == "markdown":
                        return chunk_markdown(
                            content, chunk_size=cfg.chunk_size,
                            chunk_overlap=cfg.chunk_overlap,
                        )
                    return chunk_recursive(
                        content, chunk_size=cfg.chunk_size,
                        chunk_overlap=cfg.chunk_overlap,
                        separators=cfg.separators,
                    )

                @staticmethod
                def _extract_vector(item: Any) -> list[float]:
                    if item is None:
                        return []
                    if isinstance(item, list):
                        return [float(x) for x in item]
                    vec = getattr(item, "vector", None)
                    if vec is not None:
                        return [float(x) for x in vec]
                    return []

                async def _retrieve(
                    self, ctx: Any, pipeline: Any, query: str,
                ) -> list[dict[str, Any]]:
                    rt = str(pipeline.retriever_type)
                    if rt == "hybrid" and self._hybrid is not None:
                        try:
                            hits = await self._hybrid.search(
                                query=query, top_k=pipeline.top_k,
                            )
                            return [self._hit_to_dict(h) for h in hits]
                        except Exception as exc:
                            logger.debug("hybrid failed: %s", exc)

                    embeddings = await self._embedder.embed(
                        model=pipeline.embedding_model, texts=[query],
                    )
                    qv = self._extract_vector(embeddings[0]) if embeddings else []
                    if not qv:
                        return []
                    try:
                        hits = await self._vector_store.query(
                            collection_id=self._collection_id,
                            vector=qv, top_k=pipeline.top_k,
                        )
                    except Exception as exc:
                        logger.warning("vector query failed: %s", exc)
                        return []
                    return [self._hit_to_dict(h) for h in hits]

                @staticmethod
                def _hit_to_dict(hit: Any) -> dict[str, Any]:
                    if isinstance(hit, dict):
                        return hit
                    return {
                        "chunk_id": str(getattr(hit, "vector_id", "")),
                        "source_id": getattr(hit, "source_id", ""),
                        "score": float(getattr(hit, "score", 0.0)),
                        "metadata": getattr(hit, "metadata", {}) or {},
                    }

                def _build_citations(
                    self, candidates: list[dict[str, Any]],
                ) -> list[CitationVO]:
                    out: list[CitationVO] = []
                    for i, c in enumerate(candidates, start=1):
                        meta = c.get("metadata") or {}
                        chunk_id_raw = meta.get("chunk_id") or c.get("chunk_id")
                        doc_id_raw = meta.get("document_id") or ""
                        try:
                            chunk_uuid = (
                                uuid.UUID(str(chunk_id_raw))
                                if chunk_id_raw else uuid.uuid4()
                            )
                            doc_uuid = (
                                uuid.UUID(str(doc_id_raw))
                                if doc_id_raw else uuid.uuid4()
                            )
                        except ValueError:
                            continue
                        out.append(CitationVO(
                            chunk_id=chunk_uuid, document_id=doc_uuid,
                            score=float(c.get("score", 0.0)),
                            rank=i,
                            snippet=str(c.get("content", ""))[:240],
                        ))
                    return out

                async def _generate(
                    self, pipeline: Any, messages: list[dict[str, Any]],
                    system_prompt: str,
                ) -> tuple[str, int, Decimal]:
                    if self._generator is None:
                        return "", 0, Decimal("0")
                    try:
                        result = await self._generator.chat(
                            model=pipeline.generation_model,
                            messages=messages,
                            system_prompt=system_prompt,
                        )
                    except Exception as exc:
                        logger.warning("generation failed: %s", exc)
                        raise ProviderAppError(
                            f"generation failed: {exc}"
                        ) from exc

                    if isinstance(result, dict):
                        content = result.get("content", "")
                        usage = result.get("usage") or {}
                        tokens = int(usage.get("total_tokens", 0))
                        cost = Decimal(str(usage.get("cost_usd", "0")))
                    else:
                        content = getattr(result, "content", "")
                        usage_obj = getattr(result, "usage", None)
                        tokens = int(getattr(
                            usage_obj, "total_tokens", 0,
                        ) or 0)
                        cost = Decimal(str(
                            getattr(usage_obj, "cost_usd", "0") or "0",
                        ))
                    return content, tokens, cost
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
            """rag SQLAlchemy models — schema=public, prefix=rag_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal
            from typing import Optional

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Float, Index, Integer,
                Numeric, String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: base | EN: base"""


            class RAGDocumentModel(Base):
                __tablename__ = "rag_documents"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('PENDING','PROCESSING','READY','FAILED','DELETED')",
                        name="ck_rag_doc_status",
                    ),
                    Index("ix_rag_doc_tenant_status", "tenant_id", "status"),
                    Index("ix_rag_doc_tenant_hash", "tenant_id", "hash"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                source_uri: Mapped[str] = mapped_column(String(1000), nullable=False, server_default="")
                mime_type: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
                title: Mapped[str] = mapped_column(String(500), nullable=False, server_default="")
                content: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                hash: Mapped[str] = mapped_column(String(128), nullable=False, server_default="")
                status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
                size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class RAGChunkModel(Base):
                __tablename__ = "rag_chunks"
                __table_args__ = (
                    Index("ix_rag_chunk_doc_ordinal", "document_id", "ordinal"),
                    Index("ix_rag_chunk_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                ordinal: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                content: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                token_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                embedding_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
                metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class RAGPipelineModel(Base):
                __tablename__ = "rag_pipelines"
                __table_args__ = (
                    CheckConstraint(
                        "chunker_type IN ('fixed','recursive','semantic','markdown','code')",
                        name="ck_rag_pipe_chunker",
                    ),
                    CheckConstraint(
                        "retriever_type IN ('vector','bm25','hybrid','mmr')",
                        name="ck_rag_pipe_retriever",
                    ),
                    CheckConstraint(
                        "reranker_type IN ('none','cross_encoder','cohere','bge')",
                        name="ck_rag_pipe_reranker",
                    ),
                    UniqueConstraint("tenant_id", "name", name="uq_rag_pipe_name"),
                    Index("ix_rag_pipe_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                chunker_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="recursive")
                chunk_size: Mapped[int] = mapped_column(Integer, nullable=False, server_default="512")
                chunk_overlap: Mapped[int] = mapped_column(Integer, nullable=False, server_default="50")
                retriever_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="vector")
                top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
                reranker_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="none")
                embedding_model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="text-embedding-3-small")
                generation_model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="gpt-4o-mini")
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class RAGRunModel(Base):
                __tablename__ = "rag_runs"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('QUEUED','RETRIEVING','RERANKING','GENERATING','DONE','FAILED')",
                        name="ck_rag_run_status",
                    ),
                    Index("ix_rag_run_tenant_time", "tenant_id", "created_at"),
                    Index("ix_rag_run_user_time", "user_id", "created_at"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                pipeline_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
                conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
                query: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                answer: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                model_name: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
                latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False, server_default="0")
                status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="QUEUED")
                error_message: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class RAGCitationModel(Base):
                __tablename__ = "rag_citations"
                __table_args__ = (
                    Index("ix_rag_cit_run_rank", "run_id", "rank"),
                    Index("ix_rag_cit_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                chunk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                score: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
                rank: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                snippet: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class RAGRetrievalLogModel(Base):
                __tablename__ = "rag_retrieval_logs"
                __table_args__ = (
                    Index("ix_rag_rlog_run_stage", "run_id", "stage"),
                    Index("ix_rag_rlog_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                stage: Mapped[str] = mapped_column(String(50), nullable=False, server_default="retrieve")
                top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                candidates_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
                latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            __all__ = [
                "Base", "RAGDocumentModel", "RAGChunkModel", "RAGPipelineModel",
                "RAGRunModel", "RAGCitationModel", "RAGRetrievalLogModel",
            ]
        ''')

    def _repositories_content(self) -> str:
        return dedent('''\
            """rag repositories — SQLAlchemy 2.0 async"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.rag.application.exceptions import AppError
            from app.modules.rag.infrastructure.models import (
                RAGChunkModel, RAGCitationModel, RAGDocumentModel,
                RAGPipelineModel, RAGRetrievalLogModel, RAGRunModel,
            )


            class DocumentRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, d: RAGDocumentModel) -> RAGDocumentModel:
                    try:
                        self._session.add(d)
                        await self._session.flush()
                        return d
                    except SQLAlchemyError as exc:
                        logger.error(f"doc.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> RAGDocumentModel | None:
                    try:
                        r = await self._session.execute(
                            select(RAGDocumentModel).where(
                                RAGDocumentModel.id == id,
                                RAGDocumentModel.status != "DELETED",
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"doc.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_hash(self, ctx: object, h: str) -> RAGDocumentModel | None:
                    try:
                        r = await self._session.execute(
                            select(RAGDocumentModel).where(
                                RAGDocumentModel.hash == h,
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"doc.find_hash failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def list(self, ctx: object, limit: int, offset: int) -> list:
                    try:
                        r = await self._session.execute(
                            select(RAGDocumentModel)
                            .where(RAGDocumentModel.status != "DELETED")
                            .order_by(RAGDocumentModel.created_at.desc())
                            .limit(max(1, min(limit, 500)))
                            .offset(max(0, offset))
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"doc.list failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def update(self, ctx: object, d: RAGDocumentModel) -> RAGDocumentModel:
                    try:
                        await self._session.flush()
                        return d
                    except SQLAlchemyError as exc:
                        logger.error(f"doc.update failed: {exc}")
                        raise AppError(str(exc)) from exc


            class ChunkRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create_many(self, ctx: object, chunks: list) -> int:
                    try:
                        for c in chunks:
                            self._session.add(c)
                        await self._session.flush()
                        return len(chunks)
                    except SQLAlchemyError as exc:
                        logger.error(f"chunk.create failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_document(self, ctx: object, document_id: uuid.UUID) -> list:
                    try:
                        r = await self._session.execute(
                            select(RAGChunkModel)
                            .where(RAGChunkModel.document_id == document_id)
                            .order_by(RAGChunkModel.ordinal.asc())
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"chunk.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def delete_by_document(self, ctx: object, document_id: uuid.UUID) -> int:
                    try:
                        from sqlalchemy import delete
                        res = await self._session.execute(
                            delete(RAGChunkModel).where(
                                RAGChunkModel.document_id == document_id,
                            )
                        )
                        await self._session.flush()
                        return int(res.rowcount or 0)
                    except SQLAlchemyError as exc:
                        logger.error(f"chunk.delete failed: {exc}")
                        raise AppError(str(exc)) from exc


            class PipelineRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, p: RAGPipelineModel) -> RAGPipelineModel:
                    try:
                        self._session.add(p)
                        await self._session.flush()
                        return p
                    except SQLAlchemyError as exc:
                        logger.error(f"pipe.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> RAGPipelineModel | None:
                    try:
                        r = await self._session.execute(
                            select(RAGPipelineModel).where(
                                RAGPipelineModel.id == id,
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"pipe.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_name(self, ctx: object, name: str) -> RAGPipelineModel | None:
                    try:
                        r = await self._session.execute(
                            select(RAGPipelineModel).where(
                                RAGPipelineModel.name == name,
                            )
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"pipe.find_name failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_all_active(self, ctx: object) -> list:
                    try:
                        r = await self._session.execute(
                            select(RAGPipelineModel)
                            .where(RAGPipelineModel.is_active.is_(True))
                            .order_by(RAGPipelineModel.name.asc())
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"pipe.list failed: {exc}")
                        raise AppError(str(exc)) from exc


            class RunRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, r: RAGRunModel) -> RAGRunModel:
                    try:
                        self._session.add(r)
                        await self._session.flush()
                        return r
                    except SQLAlchemyError as exc:
                        logger.error(f"run.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> RAGRunModel | None:
                    try:
                        r = await self._session.execute(
                            select(RAGRunModel).where(RAGRunModel.id == id)
                        )
                        return r.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"run.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def update(self, ctx: object, r: RAGRunModel) -> RAGRunModel:
                    try:
                        await self._session.flush()
                        return r
                    except SQLAlchemyError as exc:
                        logger.error(f"run.update failed: {exc}")
                        raise AppError(str(exc)) from exc


            class CitationRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create_many(self, ctx: object, citations: list) -> int:
                    try:
                        for c in citations:
                            self._session.add(c)
                        await self._session.flush()
                        return len(citations)
                    except SQLAlchemyError as exc:
                        logger.error(f"cit.create failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_run(self, ctx: object, run_id: uuid.UUID) -> list:
                    try:
                        r = await self._session.execute(
                            select(RAGCitationModel)
                            .where(RAGCitationModel.run_id == run_id)
                            .order_by(RAGCitationModel.rank.asc())
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"cit.find failed: {exc}")
                        raise AppError(str(exc)) from exc


            class RetrievalLogRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, log: RAGRetrievalLogModel) -> RAGRetrievalLogModel:
                    try:
                        self._session.add(log)
                        await self._session.flush()
                        return log
                    except SQLAlchemyError as exc:
                        logger.error(f"log.create failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_run(self, ctx: object, run_id: uuid.UUID) -> list:
                    try:
                        r = await self._session.execute(
                            select(RAGRetrievalLogModel)
                            .where(RAGRetrievalLogModel.run_id == run_id)
                            .order_by(RAGRetrievalLogModel.created_at.asc())
                        )
                        return list(r.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"log.find failed: {exc}")
                        raise AppError(str(exc)) from exc
        ''')

    def _caches_content(self) -> str:
        return dedent('''\
            """rag caches — Redis (never-raise)"""
            from __future__ import annotations
            import json
            import logging
            from typing import Any, Optional

            logger = logging.getLogger(__name__)


            class RedisRAGCache:
                def __init__(
                    self, redis: Any, prefix: str = "rag:r:", ttl: int = 3600,
                ) -> None:
                    self._redis = redis
                    self._prefix = prefix
                    self._ttl = ttl

                async def get(self, key: str) -> Optional[dict[str, Any]]:
                    try:
                        raw = await self._redis.get(self._prefix + key)
                        if raw is None:
                            return None
                        if isinstance(raw, bytes):
                            raw = raw.decode("utf-8")
                        return json.loads(raw)
                    except Exception as exc:
                        logger.debug("cache get failed: %s", exc)
                        return None

                async def set(
                    self, key: str, value: Any, ttl: Optional[int] = None,
                ) -> bool:
                    try:
                        await self._redis.set(
                            self._prefix + key,
                            json.dumps(
                                value, default=str, ensure_ascii=False,
                            ),
                            ex=ttl or self._ttl,
                        )
                        return True
                    except Exception as exc:
                        logger.debug("cache set failed: %s", exc)
                        return False


            class NoopRAGCache:
                async def get(self, key: str) -> Optional[dict[str, Any]]:
                    return None

                async def set(
                    self, key: str, value: Any, ttl: Optional[int] = None,
                ) -> bool:
                    return False
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """rag services — cross-module adapters · event bus"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any, Optional

            logger = logging.getLogger(__name__)


            class EmbeddingModuleAdapter:
                """TH: adapter ไป embeddings module | EN: embeddings adapter"""

                def __init__(self, embedding_use_case: Any) -> None:
                    self._uc = embedding_use_case

                async def embed(
                    self, *, model: str, texts: list[str],
                    normalize: bool = True,
                ) -> list[Any]:
                    from app.modules.embeddings.domain.value_objects import (
                        EmbeddingRequest,
                    )
                    from app.shared.context import RequestContext as SharedCtx

                    if not texts:
                        return []
                    ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
                    req = EmbeddingRequest(
                        model=model, input=texts, normalize=normalize,
                    )
                    return await self._uc.embed(ctx, req)


            class VectorStoreModuleAdapter:
                """TH: adapter ไป vector_db | EN: vector_db adapter"""

                def __init__(self, vector_use_case: Any) -> None:
                    self._uc = vector_use_case

                async def upsert(
                    self, *, collection_id: uuid.UUID,
                    items: list[dict[str, Any]],
                ) -> int:
                    from app.shared.context import RequestContext as SharedCtx
                    ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
                    return await self._uc.upsert(
                        ctx, collection_id=collection_id, items=items,
                    )

                async def query(
                    self, *, collection_id: uuid.UUID,
                    vector: list[float], top_k: int,
                ) -> list[Any]:
                    from app.modules.vector_db.domain.value_objects import (
                        VectorQuery,
                    )
                    from app.shared.context import RequestContext as SharedCtx
                    ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
                    return await self._uc.query(
                        ctx, collection_id=collection_id,
                        query=VectorQuery(vector=vector, top_k=top_k),
                    )


            class HybridSearchModuleAdapter:
                """TH: adapter ไป hybrid_search | EN: hybrid adapter"""

                def __init__(self, hybrid_use_case: Any) -> None:
                    self._uc = hybrid_use_case

                async def search(
                    self, *, query: str, top_k: int,
                ) -> list[Any]:
                    from app.shared.context import RequestContext as SharedCtx
                    ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
                    return await self._uc.search(
                        ctx, query=query, top_k=top_k,
                    )


            class LLMGeneratorAdapter:
                """TH: adapter ไป llm module | EN: llm adapter"""

                def __init__(self, llm_port: Any) -> None:
                    self._llm = llm_port

                async def chat(
                    self, *, model: str, messages: list[dict[str, Any]],
                    system_prompt: Optional[str] = None,
                ) -> Any:
                    return await self._llm.chat(
                        tenant_id=uuid.UUID(int=0),
                        model=model, messages=messages,
                        system_prompt=system_prompt,
                    )


            class NoopReranker:
                async def rerank(
                    self, *, query: str,
                    candidates: list[dict[str, Any]], top_k: int,
                ) -> list[dict[str, Any]]:
                    return candidates[:top_k]


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
            """rag Pydantic schemas"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.rag.domain.enums import (
                ChunkerType, RerankerType, RetrieverType,
            )


            class IngestRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                content: str = Field(min_length=1)
                source_uri: str = Field(default="", max_length=1000)
                mime_type: str = "text/plain"
                title: str = Field(default="", max_length=500)
                pipeline_id: Optional[uuid.UUID] = None
                metadata: dict[str, Any] = Field(default_factory=dict)


            class IngestResponse(BaseModel):
                document_id: uuid.UUID
                status: str
                chunk_count: int
                size_bytes: int


            class QueryRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                query: str = Field(min_length=1)
                pipeline_id: Optional[uuid.UUID] = None
                conversation_id: Optional[uuid.UUID] = None
                use_cache: bool = True


            class CitationOut(BaseModel):
                chunk_id: uuid.UUID
                document_id: uuid.UUID
                score: float
                rank: int
                snippet: str = ""


            class UsageOut(BaseModel):
                total_tokens: int = 0
                cost_usd: Decimal = Decimal("0")


            class QueryResponse(BaseModel):
                run_id: str
                answer: str
                citations: list[CitationOut] = []
                usage: UsageOut
                cached: bool = False


            class DocumentOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                source_uri: str
                mime_type: str
                title: str
                status: str
                size_bytes: int
                chunk_count: int
                created_at: datetime


            class ChunkOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                ordinal: int
                content: str
                token_count: int


            class DocumentDetailOut(DocumentOut):
                chunks: list[ChunkOut] = []


            class PipelineCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(min_length=1, max_length=100)
                chunker_type: ChunkerType = ChunkerType.RECURSIVE
                chunk_size: int = Field(default=512, ge=64, le=8192)
                chunk_overlap: int = Field(default=50, ge=0, le=2048)
                retriever_type: RetrieverType = RetrieverType.VECTOR
                top_k: int = Field(default=5, ge=1, le=100)
                reranker_type: RerankerType = RerankerType.NONE
                embedding_model: str = "text-embedding-3-small"
                generation_model: str = "gpt-4o-mini"


            class PipelineOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                chunker_type: str
                chunk_size: int
                chunk_overlap: int
                retriever_type: str
                top_k: int
                reranker_type: str
                embedding_model: str
                generation_model: str
                is_active: bool


            class RunOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                query: str
                answer: str
                model_name: str
                latency_ms: int
                total_tokens: int
                cost_usd: Decimal
                status: str
                created_at: datetime
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """rag DI container"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass
            from typing import Annotated, Optional

            from fastapi import Depends, Header, HTTPException, Request, status
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.rag.application.use_case import RAGUseCase
            from app.modules.rag.infrastructure.caches import (
                NoopRAGCache, RedisRAGCache,
            )
            from app.modules.rag.infrastructure.repositories import (
                ChunkRepository, CitationRepository, DocumentRepository,
                PipelineRepository, RetrievalLogRepository, RunRepository,
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
                request: Request,
                db: AsyncSession = Depends(get_db),
            ) -> RAGUseCase:
                embedder = getattr(request.app.state, "rag_embedder", None)
                vector_store = getattr(
                    request.app.state, "rag_vector_store", None,
                )
                hybrid = getattr(request.app.state, "rag_hybrid", None)
                reranker = getattr(request.app.state, "rag_reranker", None)
                generator = getattr(request.app.state, "rag_generator", None)
                redis = getattr(request.app.state, "redis", None)
                event_bus = getattr(
                    request.app.state, "rag_event_bus", None,
                )
                collection_id = getattr(
                    request.app.state, "rag_collection_id", None,
                )
                cache = RedisRAGCache(redis) if redis else NoopRAGCache()

                return RAGUseCase(
                    documents=DocumentRepository(db),
                    chunks=ChunkRepository(db),
                    pipelines=PipelineRepository(db),
                    runs=RunRepository(db),
                    citations=CitationRepository(db),
                    retrieval_logs=RetrievalLogRepository(db),
                    embedder=embedder,
                    vector_store=vector_store,
                    hybrid=hybrid,
                    reranker=reranker,
                    generator=generator,
                    cache=cache,
                    event_bus=event_bus,
                    collection_id=collection_id,
                )
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """rag HTTP router"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException, Query

            from app.modules.rag.application.exceptions import AppError
            from app.modules.rag.application.use_case import RAGUseCase
            from app.modules.rag.domain.exceptions import RAGError
            from app.modules.rag.presentation.dependencies import (
                Ctx, get_ctx, get_use_case,
            )
            from app.modules.rag.presentation.schemas import (
                ChunkOut, CitationOut, DocumentDetailOut, DocumentOut,
                IngestRequest, IngestResponse, PipelineCreateRequest,
                PipelineOut, QueryRequest, QueryResponse, RunOut, UsageOut,
            )

            logger = logging.getLogger(__name__)

            router = APIRouter(prefix="/rag", tags=["RAG"])


            def _raise(exc: Exception) -> None:
                if isinstance(exc, RAGError):
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


            @router.post(
                "/ingest", response_model=IngestResponse, status_code=201,
            )
            async def ingest(
                req: IngestRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[RAGUseCase, Depends(get_use_case)],
            ) -> IngestResponse:
                try:
                    doc = await uc.ingest(
                        ctx, content=req.content,
                        source_uri=req.source_uri,
                        mime_type=req.mime_type, title=req.title,
                        pipeline_id=req.pipeline_id,
                        metadata=req.metadata,
                    )
                    return IngestResponse(
                        document_id=doc.id, status=str(doc.status),
                        chunk_count=doc.chunk_count or 0,
                        size_bytes=doc.size_bytes or 0,
                    )
                except (RAGError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/query", response_model=QueryResponse)
            async def query(
                req: QueryRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[RAGUseCase, Depends(get_use_case)],
            ) -> QueryResponse:
                try:
                    result = await uc.query(
                        ctx, query=req.query,
                        pipeline_id=req.pipeline_id,
                        conversation_id=req.conversation_id,
                        use_cache=req.use_cache,
                    )
                    return QueryResponse(
                        run_id=result["run_id"],
                        answer=result["answer"],
                        citations=[
                            CitationOut(**c)
                            for c in result.get("citations", [])
                        ],
                        usage=UsageOut(**result.get("usage", {})),
                        cached=bool(result.get("cached", False)),
                    )
                except (RAGError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/documents", response_model=list[DocumentOut])
            async def list_documents(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[RAGUseCase, Depends(get_use_case)],
                limit: int = Query(default=50, ge=1, le=500),
                offset: int = Query(default=0, ge=0),
            ) -> list[DocumentOut]:
                try:
                    items = await uc.list_documents(
                        ctx, limit=limit, offset=offset,
                    )
                    return [
                        DocumentOut.model_validate({
                            "id": d.id,
                            "source_uri": d.source_uri or "",
                            "mime_type": d.mime_type or "",
                            "title": d.title or "",
                            "status": d.status,
                            "size_bytes": d.size_bytes or 0,
                            "chunk_count": d.chunk_count or 0,
                            "created_at": d.created_at,
                        })
                        for d in items
                    ]
                except (RAGError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get(
                "/documents/{document_id}", response_model=DocumentDetailOut,
            )
            async def get_document(
                document_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[RAGUseCase, Depends(get_use_case)],
            ) -> DocumentDetailOut:
                try:
                    doc, chunks = await uc.get_document(ctx, document_id)
                    return DocumentDetailOut.model_validate({
                        "id": doc.id,
                        "source_uri": doc.source_uri or "",
                        "mime_type": doc.mime_type or "",
                        "title": doc.title or "",
                        "status": doc.status,
                        "size_bytes": doc.size_bytes or 0,
                        "chunk_count": doc.chunk_count or 0,
                        "created_at": doc.created_at,
                        "chunks": [
                            ChunkOut.model_validate({
                                "id": c.id,
                                "ordinal": c.ordinal or 0,
                                "content": c.content or "",
                                "token_count": c.token_count or 0,
                            })
                            for c in chunks
                        ],
                    })
                except (RAGError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.delete("/documents/{document_id}")
            async def delete_document(
                document_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[RAGUseCase, Depends(get_use_case)],
            ) -> dict:
                try:
                    ok_del = await uc.delete_document(ctx, document_id)
                    return {"deleted": ok_del,
                            "document_id": str(document_id)}
                except (RAGError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/pipelines", response_model=list[PipelineOut])
            async def list_pipelines(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[RAGUseCase, Depends(get_use_case)],
            ) -> list[PipelineOut]:
                try:
                    items = await uc.list_pipelines(ctx)
                    return [
                        PipelineOut.model_validate({
                            "id": p.id, "name": p.name,
                            "chunker_type": p.chunker_type,
                            "chunk_size": p.chunk_size or 512,
                            "chunk_overlap": p.chunk_overlap or 50,
                            "retriever_type": p.retriever_type,
                            "top_k": p.top_k or 5,
                            "reranker_type": p.reranker_type,
                            "embedding_model": p.embedding_model or "",
                            "generation_model": p.generation_model or "",
                            "is_active": bool(p.is_active),
                        })
                        for p in items
                    ]
                except (RAGError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post(
                "/pipelines", response_model=PipelineOut, status_code=201,
            )
            async def create_pipeline(
                req: PipelineCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[RAGUseCase, Depends(get_use_case)],
            ) -> PipelineOut:
                try:
                    p = await uc.create_pipeline(ctx, **req.model_dump())
                    return PipelineOut.model_validate({
                        "id": p.id, "name": p.name,
                        "chunker_type": p.chunker_type,
                        "chunk_size": p.chunk_size or 512,
                        "chunk_overlap": p.chunk_overlap or 50,
                        "retriever_type": p.retriever_type,
                        "top_k": p.top_k or 5,
                        "reranker_type": p.reranker_type,
                        "embedding_model": p.embedding_model or "",
                        "generation_model": p.generation_model or "",
                        "is_active": bool(p.is_active),
                    })
                except (RAGError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/runs/{run_id}", response_model=RunOut)
            async def get_run(
                run_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[RAGUseCase, Depends(get_use_case)],
            ) -> RunOut:
                try:
                    r = await uc.get_run(ctx, run_id)
                    return RunOut.model_validate({
                        "id": r.id, "query": r.query or "",
                        "answer": r.answer or "",
                        "model_name": r.model_name or "",
                        "latency_ms": r.latency_ms or 0,
                        "total_tokens": r.total_tokens or 0,
                        "cost_usd": r.cost_usd,
                        "status": r.status,
                        "created_at": r.created_at,
                    })
                except (RAGError, AppError) as exc:
                    _raise(exc)
                    raise
        ''')

    def _swagger_content(self) -> str:
        return dedent('''\
            """rag OpenAPI docs"""
            from __future__ import annotations
            from typing import Any


            def register_rag_openapi(app: object) -> None:
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "RAG" for t in tags):
                        tags.append({
                            "name": "RAG",
                            "description": (
                                "โมดูล rag — Retrieval Augmented Generation\\n\\n"
                                "• Ingest: chunk → embed → upsert vectors\\n"
                                "• Query: retrieve → rerank → generate\\n"
                                "• Citations with score + snippet\\n"
                                "• Multi-pipeline configs"
                            ),
                            "externalDocs": {
                                "description": "rag Module README",
                                "url": "/docs/README_rag.md",
                            },
                        })
                    info = schema.setdefault("info", {})
                    info.setdefault("x-module", "rag")
                    info.setdefault("x-layer", "5-Intel")
                    info.setdefault("x-prefix", "rag")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent(f'''\
            """{self.module} module"""
            from .presentation.router import router as rag_router

            __all__ = ["rag_router"]
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
-- V001__create_rag.sql | Module: rag | Prefix: rag
-- Schema: public | Tables: rag_documents, rag_chunks, rag_pipelines,
--                          rag_runs, rag_citations, rag_retrieval_logs
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."rag_documents";
CREATE TABLE "public"."rag_documents" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "user_id"        uuid NOT NULL,
  "source_uri"     varchar(1000) NOT NULL DEFAULT '',
  "mime_type"      varchar(100) NOT NULL DEFAULT '',
  "title"          varchar(500) NOT NULL DEFAULT '',
  "content"        text NOT NULL DEFAULT '',
  "hash"           varchar(128) NOT NULL DEFAULT '',
  "status"         varchar(20) NOT NULL DEFAULT 'PENDING',
  "size_bytes"     int4 NOT NULL DEFAULT 0,
  "chunk_count"    int4 NOT NULL DEFAULT 0,
  "metadata_json"  text NOT NULL DEFAULT '{}',
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "rag_documents_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_rag_doc_status" CHECK (
    status IN ('PENDING','PROCESSING','READY','FAILED','DELETED')
  )
);
CREATE INDEX "ix_rag_doc_tenant_status" ON "public"."rag_documents" ("tenant_id", "status");
CREATE INDEX "ix_rag_doc_tenant_hash"   ON "public"."rag_documents" ("tenant_id", "hash");

DROP TABLE IF EXISTS "public"."rag_chunks";
CREATE TABLE "public"."rag_chunks" (
  "id"            uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"     uuid NOT NULL,
  "document_id"   uuid NOT NULL,
  "ordinal"       int4 NOT NULL DEFAULT 0,
  "content"       text NOT NULL DEFAULT '',
  "token_count"   int4 NOT NULL DEFAULT 0,
  "embedding_id"  uuid NULL,
  "metadata_json" text NOT NULL DEFAULT '{}',
  "created_at"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"    timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "rag_chunks_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_rag_chunk_doc_ordinal" ON "public"."rag_chunks" ("document_id", "ordinal");
CREATE INDEX "ix_rag_chunk_tenant"      ON "public"."rag_chunks" ("tenant_id");

DROP TABLE IF EXISTS "public"."rag_pipelines";
CREATE TABLE "public"."rag_pipelines" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"          uuid NOT NULL,
  "name"               varchar(100) NOT NULL,
  "chunker_type"       varchar(20) NOT NULL DEFAULT 'recursive',
  "chunk_size"         int4 NOT NULL DEFAULT 512,
  "chunk_overlap"      int4 NOT NULL DEFAULT 50,
  "retriever_type"     varchar(20) NOT NULL DEFAULT 'vector',
  "top_k"              int4 NOT NULL DEFAULT 5,
  "reranker_type"      varchar(20) NOT NULL DEFAULT 'none',
  "embedding_model"    varchar(100) NOT NULL DEFAULT 'text-embedding-3-small',
  "generation_model"   varchar(100) NOT NULL DEFAULT 'gpt-4o-mini',
  "is_active"          bool NOT NULL DEFAULT true,
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"         timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "rag_pipelines_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_rag_pipe_name" UNIQUE ("tenant_id", "name"),
  CONSTRAINT "ck_rag_pipe_chunker" CHECK (
    chunker_type IN ('fixed','recursive','semantic','markdown','code')
  ),
  CONSTRAINT "ck_rag_pipe_retriever" CHECK (
    retriever_type IN ('vector','bm25','hybrid','mmr')
  ),
  CONSTRAINT "ck_rag_pipe_reranker" CHECK (
    reranker_type IN ('none','cross_encoder','cohere','bge')
  )
);
CREATE INDEX "ix_rag_pipe_tenant" ON "public"."rag_pipelines" ("tenant_id");

DROP TABLE IF EXISTS "public"."rag_runs";
CREATE TABLE "public"."rag_runs" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "user_id"          uuid NOT NULL,
  "pipeline_id"      uuid NULL,
  "conversation_id"  uuid NULL,
  "query"            text NOT NULL DEFAULT '',
  "answer"           text NOT NULL DEFAULT '',
  "model_name"       varchar(100) NOT NULL DEFAULT '',
  "latency_ms"       int4 NOT NULL DEFAULT 0,
  "total_tokens"     int4 NOT NULL DEFAULT 0,
  "cost_usd"         numeric(12,8) NOT NULL DEFAULT 0,
  "status"           varchar(20) NOT NULL DEFAULT 'QUEUED',
  "error_message"    text NOT NULL DEFAULT '',
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "rag_runs_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_rag_run_status" CHECK (
    status IN ('QUEUED','RETRIEVING','RERANKING','GENERATING','DONE','FAILED')
  )
);
CREATE INDEX "ix_rag_run_tenant_time" ON "public"."rag_runs" ("tenant_id", "created_at" DESC);
CREATE INDEX "ix_rag_run_user_time"   ON "public"."rag_runs" ("user_id", "created_at" DESC);

DROP TABLE IF EXISTS "public"."rag_citations";
CREATE TABLE "public"."rag_citations" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "run_id"       uuid NOT NULL,
  "chunk_id"     uuid NOT NULL,
  "document_id"  uuid NOT NULL,
  "score"        float8 NOT NULL DEFAULT 0,
  "rank"         int4 NOT NULL DEFAULT 0,
  "snippet"      text NOT NULL DEFAULT '',
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "rag_citations_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_rag_cit_run_rank" ON "public"."rag_citations" ("run_id", "rank");
CREATE INDEX "ix_rag_cit_tenant"   ON "public"."rag_citations" ("tenant_id");

DROP TABLE IF EXISTS "public"."rag_retrieval_logs";
CREATE TABLE "public"."rag_retrieval_logs" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "run_id"           uuid NOT NULL,
  "stage"            varchar(50) NOT NULL DEFAULT 'retrieve',
  "top_k"            int4 NOT NULL DEFAULT 0,
  "candidates_json"  text NOT NULL DEFAULT '[]',
  "latency_ms"       int4 NOT NULL DEFAULT 0,
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "rag_retrieval_logs_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_rag_rlog_run_stage" ON "public"."rag_retrieval_logs" ("run_id", "stage");
CREATE INDEX "ix_rag_rlog_tenant"    ON "public"."rag_retrieval_logs" ("tenant_id");

-- ═══ Trigger ═══
CREATE OR REPLACE FUNCTION public.set_updated_at_rag()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_rag_doc_updated ON "public"."rag_documents";
CREATE TRIGGER trg_rag_doc_updated BEFORE UPDATE ON "public"."rag_documents"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_rag();

DROP TRIGGER IF EXISTS trg_rag_chunk_updated ON "public"."rag_chunks";
CREATE TRIGGER trg_rag_chunk_updated BEFORE UPDATE ON "public"."rag_chunks"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_rag();

DROP TRIGGER IF EXISTS trg_rag_pipe_updated ON "public"."rag_pipelines";
CREATE TRIGGER trg_rag_pipe_updated BEFORE UPDATE ON "public"."rag_pipelines"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_rag();

DROP TRIGGER IF EXISTS trg_rag_run_updated ON "public"."rag_runs";
CREATE TRIGGER trg_rag_run_updated BEFORE UPDATE ON "public"."rag_runs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_rag();

DROP TRIGGER IF EXISTS trg_rag_cit_updated ON "public"."rag_citations";
CREATE TRIGGER trg_rag_cit_updated BEFORE UPDATE ON "public"."rag_citations"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_rag();

DROP TRIGGER IF EXISTS trg_rag_rlog_updated ON "public"."rag_retrieval_logs";
CREATE TRIGGER trg_rag_rlog_updated BEFORE UPDATE ON "public"."rag_retrieval_logs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_rag();

-- ═══ RLS ═══
ALTER TABLE "public"."rag_documents"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."rag_chunks"          ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."rag_pipelines"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."rag_runs"            ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."rag_citations"       ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."rag_retrieval_logs"  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_rag_doc ON "public"."rag_documents";
CREATE POLICY p_rag_doc ON "public"."rag_documents"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_rag_chunk ON "public"."rag_chunks";
CREATE POLICY p_rag_chunk ON "public"."rag_chunks"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_rag_pipe ON "public"."rag_pipelines";
CREATE POLICY p_rag_pipe ON "public"."rag_pipelines"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_rag_run ON "public"."rag_runs";
CREATE POLICY p_rag_run ON "public"."rag_runs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_rag_cit ON "public"."rag_citations";
CREATE POLICY p_rag_cit ON "public"."rag_citations"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_rag_rlog ON "public"."rag_retrieval_logs";
CREATE POLICY p_rag_rlog ON "public"."rag_retrieval_logs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_rag.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."rag_pipelines"
    (tenant_id, name, chunker_type, chunk_size, chunk_overlap,
     retriever_type, top_k, reranker_type,
     embedding_model, generation_model)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'default',
     'recursive', 512, 50, 'vector', 5, 'none',
     'text-embedding-3-small', 'gpt-4o-mini'),
    ('00000000-0000-0000-0000-000000000001', 'hybrid-quality',
     'recursive', 768, 100, 'hybrid', 10, 'cross_encoder',
     'text-embedding-3-large', 'gpt-4o')
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_rag.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_rag_rlog_updated ON "public"."rag_retrieval_logs";
DROP TRIGGER IF EXISTS trg_rag_cit_updated  ON "public"."rag_citations";
DROP TRIGGER IF EXISTS trg_rag_run_updated  ON "public"."rag_runs";
DROP TRIGGER IF EXISTS trg_rag_pipe_updated ON "public"."rag_pipelines";
DROP TRIGGER IF EXISTS trg_rag_chunk_updated ON "public"."rag_chunks";
DROP TRIGGER IF EXISTS trg_rag_doc_updated  ON "public"."rag_documents";

DROP POLICY IF EXISTS p_rag_rlog ON "public"."rag_retrieval_logs";
DROP POLICY IF EXISTS p_rag_cit  ON "public"."rag_citations";
DROP POLICY IF EXISTS p_rag_run  ON "public"."rag_runs";
DROP POLICY IF EXISTS p_rag_pipe ON "public"."rag_pipelines";
DROP POLICY IF EXISTS p_rag_chunk ON "public"."rag_chunks";
DROP POLICY IF EXISTS p_rag_doc  ON "public"."rag_documents";

DROP TABLE IF EXISTS "public"."rag_retrieval_logs" CASCADE;
DROP TABLE IF EXISTS "public"."rag_citations"      CASCADE;
DROP TABLE IF EXISTS "public"."rag_runs"           CASCADE;
DROP TABLE IF EXISTS "public"."rag_pipelines"      CASCADE;
DROP TABLE IF EXISTS "public"."rag_chunks"         CASCADE;
DROP TABLE IF EXISTS "public"."rag_documents"      CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_rag();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "rag_001"
        content = f'''"""add rag tables

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
    """TH: สร้างตาราง rag | EN: create tables"""
    op.create_table(
        "rag_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_uri", sa.String(1000), nullable=False, server_default=""),
        sa.Column("mime_type", sa.String(100), nullable=False, server_default=""),
        sa.Column("title", sa.String(500), nullable=False, server_default=""),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("hash", sa.String(128), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("size_bytes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("chunk_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "rag_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ordinal", sa.Integer, nullable=False, server_default="0"),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("token_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("embedding_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "rag_pipelines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("chunker_type", sa.String(20), nullable=False, server_default="recursive"),
        sa.Column("chunk_size", sa.Integer, nullable=False, server_default="512"),
        sa.Column("chunk_overlap", sa.Integer, nullable=False, server_default="50"),
        sa.Column("retriever_type", sa.String(20), nullable=False, server_default="vector"),
        sa.Column("top_k", sa.Integer, nullable=False, server_default="5"),
        sa.Column("reranker_type", sa.String(20), nullable=False, server_default="none"),
        sa.Column("embedding_model", sa.String(100), nullable=False, server_default="text-embedding-3-small"),
        sa.Column("generation_model", sa.String(100), nullable=False, server_default="gpt-4o-mini"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_rag_pipe_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "rag_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("pipeline_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("query", sa.Text, nullable=False, server_default=""),
        sa.Column("answer", sa.Text, nullable=False, server_default=""),
        sa.Column("model_name", sa.String(100), nullable=False, server_default=""),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Numeric(12, 8), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="QUEUED"),
        sa.Column("error_message", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "rag_citations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Float, nullable=False, server_default="0"),
        sa.Column("rank", sa.Integer, nullable=False, server_default="0"),
        sa.Column("snippet", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "rag_retrieval_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage", sa.String(50), nullable=False, server_default="retrieve"),
        sa.Column("top_k", sa.Integer, nullable=False, server_default="0"),
        sa.Column("candidates_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )

    op.create_index("ix_rag_doc_tenant_status", "rag_documents", ["tenant_id", "status"], schema=SCHEMA)
    op.create_index("ix_rag_doc_tenant_hash", "rag_documents", ["tenant_id", "hash"], schema=SCHEMA)
    op.create_index("ix_rag_chunk_doc_ordinal", "rag_chunks", ["document_id", "ordinal"], schema=SCHEMA)
    op.create_index("ix_rag_chunk_tenant", "rag_chunks", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_rag_pipe_tenant", "rag_pipelines", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_rag_run_tenant_time", "rag_runs", ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_rag_run_user_time", "rag_runs", ["user_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_rag_cit_run_rank", "rag_citations", ["run_id", "rank"], schema=SCHEMA)
    op.create_index("ix_rag_cit_tenant", "rag_citations", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_rag_rlog_run_stage", "rag_retrieval_logs", ["run_id", "stage"], schema=SCHEMA)
    op.create_index("ix_rag_rlog_tenant", "rag_retrieval_logs", ["tenant_id"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_rag()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in ("rag_documents", "rag_chunks", "rag_pipelines",
                "rag_runs", "rag_citations", "rag_retrieval_logs"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE TRIGGER trg_{{tbl}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_rag();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """TH: ลบตาราง | EN: drop tables"""
    for tbl in ("rag_retrieval_logs", "rag_citations", "rag_runs",
                "rag_pipelines", "rag_chunks", "rag_documents"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_rag();")
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
            ],
            "item": [
                {
                    "name": "Ingest",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                            {"key": "X-User-Id", "value": "{{user_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/rag/ingest",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "rag", "ingest"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"content":"This is a test document.","source_uri":"test://doc1","title":"Test"}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Query",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                            {"key": "X-User-Id", "value": "{{user_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/rag/query",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "rag", "query"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"query":"What is this document about?"}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "List Documents",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/rag/documents?limit=20",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "rag", "documents"],
                            "query": [{"key": "limit", "value": "20"}],
                        },
                    },
                },
                {
                    "name": "List Pipelines",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/rag/pipelines",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "rag", "pipelines"],
                        },
                    },
                },
                {
                    "name": "Create Pipeline",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": "{{base_url}}/api/v1/rag/pipelines",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", "rag", "pipelines"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"quality","chunker_type":"recursive","retriever_type":"hybrid","top_k":10}',
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
        RAGChunkModel,
        RAGCitationModel,
        RAGDocumentModel,
        RAGPipelineModel,
        RAGRetrievalLogModel,
        RAGRunModel,
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
create_module_rag.py — RAG Module Generator v{VERSION}

USAGE
    python create_module_rag.py <action> [options]

MODULE
    name    : rag
    layer   : 5-Intel
    prefix  : rag
    schema  : public
    tables  : rag_documents, rag_chunks, rag_pipelines,
              rag_runs, rag_citations, rag_retrieval_logs
    depends : llm, embeddings, vector_db, hybrid_search

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
    python create_module_rag.py all
    python create_module_rag.py create --force
    python create_module_rag.py verify
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