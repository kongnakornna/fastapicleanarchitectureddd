#!/usr/bin/env python3
"""
create_module_llamaindex.py — LlamaIndex Wrapper Module Generator v1.0.0

สร้าง module llamaindex ตาม Clean Architecture + DDD + Event-Driven
Module: llamaindex · Prefix: li_ · Schema: public
Layer: 5-Intel · Depends: llm, embeddings, vector_db

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
    "name": "llamaindex",
    "title": "LlamaIndex Wrapper",
    "layer": "5-Intel",
    "prefix": "li",
    "tag": "LlamaIndex",
    "tag_desc": "LlamaIndex — Index · Node · QueryEngine · Response synthesis",
    "depends": ["llm", "embeddings", "vector_db"],
    "tables": (
        "li_indexes",
        "li_nodes",
        "li_query_engines",
        "li_documents",
        "li_runs",
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
class LlamaIndexGenerator:
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
            """llamaindex value objects"""
            from .index_spec import IndexSpec
            from .query_engine_spec import QueryEngineSpec
            from .node_relationship import NodeRelationship

            __all__ = ["IndexSpec", "QueryEngineSpec", "NodeRelationship"]
        '''))

        self.writer.write(f"{base}/value_objects/index_spec.py", dedent('''\
            """IndexSpec VO"""
            from __future__ import annotations
            from typing import Any
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.llamaindex.domain.enums import IndexType


            class IndexSpec(BaseModel):
                """TH: ข้อกำหนด index | EN: Index specification"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                name: str = Field(min_length=1, max_length=100)
                index_type: IndexType = IndexType.VECTOR_STORE
                embed_model: str = Field(default="text-embedding-3-small", max_length=100)
                storage_kind: str = Field(default="pgvector", max_length=50)
                config: dict[str, Any] = Field(default_factory=dict)
        '''))

        self.writer.write(f"{base}/value_objects/query_engine_spec.py", dedent('''\
            """QueryEngineSpec VO"""
            from __future__ import annotations
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.llamaindex.domain.enums import ResponseMode


            class QueryEngineSpec(BaseModel):
                """TH: ข้อกำหนด query engine | EN: Query engine spec"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                name: str = Field(min_length=1, max_length=100)
                retriever_type: str = Field(default="vector", max_length=30)
                top_k: int = Field(default=5, ge=1, le=100)
                response_mode: ResponseMode = ResponseMode.COMPACT
                similarity_top_k: int = Field(default=5, ge=1, le=100)
        '''))

        self.writer.write(f"{base}/value_objects/node_relationship.py", dedent('''\
            """NodeRelationship VO"""
            from __future__ import annotations
            import uuid
            from typing import Optional
            from pydantic import BaseModel, ConfigDict


            class NodeRelationship(BaseModel):
                """TH: ความสัมพันธ์ของ node | EN: Node relationship"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                parent_id: Optional[uuid.UUID] = None
                prev_id: Optional[uuid.UUID] = None
                next_id: Optional[uuid.UUID] = None
                child_ids: list[uuid.UUID] = []
        '''))

        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """llamaindex entities — aliases to ORM"""
            from .li_index import LIIndex
            from .li_node import LINode
            from .li_query_engine import LIQueryEngine
            from .li_document import LIDocument
            from .li_run import LIRun

            __all__ = ["LIIndex", "LINode", "LIQueryEngine", "LIDocument", "LIRun"]
        '''))

        for name, cls, model in (
            ("li_index", "LIIndex", "LIIndexModel"),
            ("li_node", "LINode", "LINodeModel"),
            ("li_query_engine", "LIQueryEngine", "LIQueryEngineModel"),
            ("li_document", "LIDocument", "LIDocumentModel"),
            ("li_run", "LIRun", "LIRunModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias to ORM"""
                from __future__ import annotations
                from app.modules.{self.module}.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """llamaindex helpers"""
            from .splitter import split_text, SentenceSplitter
            from .synthesizer import (
                synthesize_compact, synthesize_refine, synthesize_tree_summarize,
            )
            from .relationships import build_node_relationships

            __all__ = [
                "split_text", "SentenceSplitter",
                "synthesize_compact", "synthesize_refine", "synthesize_tree_summarize",
                "build_node_relationships",
            ]
        '''))

        self.writer.write(f"{base}/helpers/splitter.py", dedent('''\
            """splitter — sentence-aware text splitter"""
            from __future__ import annotations
            import re
            from typing import Optional


            _SENT_END = re.compile(r"(?<=[.!?])\\s+")


            def split_text(
                text: str, *, chunk_size: int = 512, chunk_overlap: int = 50,
                separators: Optional[list[str]] = None,
            ) -> list[str]:
                """TH: แบ่งข้อความเป็น chunk | EN: split text into chunks"""
                if not text:
                    return []
                if chunk_size <= 0:
                    return [text]
                step = max(1, chunk_size - max(0, chunk_overlap))

                sentences = _SENT_END.split(text)
                if len(sentences) <= 1:
                    return [
                        text[i : i + chunk_size]
                        for i in range(0, len(text), step)
                        if text[i : i + chunk_size].strip()
                    ]

                chunks: list[str] = []
                buf = ""
                for sent in sentences:
                    candidate = (buf + " " + sent) if buf else sent
                    if len(candidate) <= chunk_size:
                        buf = candidate
                    else:
                        if buf:
                            chunks.append(buf.strip())
                        if len(sent) > chunk_size:
                            for i in range(0, len(sent), step):
                                piece = sent[i : i + chunk_size]
                                if piece.strip():
                                    chunks.append(piece.strip())
                            buf = ""
                        else:
                            buf = sent
                if buf:
                    chunks.append(buf.strip())
                return chunks


            class SentenceSplitter:
                """TH: sentence splitter (stateless) | EN: sentence splitter"""

                def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50) -> None:
                    self.chunk_size = chunk_size
                    self.chunk_overlap = chunk_overlap

                def split(self, text: str) -> list[str]:
                    return split_text(
                        text, chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap,
                    )
        '''))

        self.writer.write(f"{base}/helpers/synthesizer.py", dedent('''\
            """synthesizer — response synthesis strategies"""
            from __future__ import annotations
            from typing import Any


            def build_context_block(nodes: list[dict[str, Any]]) -> str:
                lines: list[str] = []
                for i, n in enumerate(nodes, start=1):
                    snippet = str(n.get("content", "")).strip().replace("\\n", " ")
                    lines.append(f"[{i}] {snippet}")
                return "\\n\\n".join(lines)


            def build_synthesis_prompt(
                query: str, nodes: list[dict[str, Any]],
                *, mode: str = "compact",
            ) -> str:
                ctx = build_context_block(nodes)
                if mode == "refine":
                    return (
                        "Answer the question using the context. "
                        "Refine iteratively if needed.\\n\\n"
                        f"Question:\\n{query}\\n\\nContext:\\n{ctx}"
                    )
                if mode == "tree_summarize":
                    return (
                        "Summarize each context chunk then combine to answer.\\n\\n"
                        f"Question:\\n{query}\\n\\nContext:\\n{ctx}"
                    )
                # compact / simple_summarize / default
                return (
                    "Answer the question using ONLY the context. "
                    "Cite sources as [1], [2], etc.\\n\\n"
                    f"Question:\\n{query}\\n\\nContext:\\n{ctx}"
                )


            async def synthesize_compact(
                llm: Any, *, tenant_id: Any, model: str, query: str,
                nodes: list[dict[str, Any]],
            ) -> dict[str, Any]:
                prompt = build_synthesis_prompt(query, nodes, mode="compact")
                result = await llm.chat(
                    tenant_id=tenant_id, model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                return _to_output(result)


            async def synthesize_refine(
                llm: Any, *, tenant_id: Any, model: str, query: str,
                nodes: list[dict[str, Any]],
            ) -> dict[str, Any]:
                prompt = build_synthesis_prompt(query, nodes, mode="refine")
                result = await llm.chat(
                    tenant_id=tenant_id, model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                return _to_output(result)


            async def synthesize_tree_summarize(
                llm: Any, *, tenant_id: Any, model: str, query: str,
                nodes: list[dict[str, Any]],
            ) -> dict[str, Any]:
                prompt = build_synthesis_prompt(query, nodes, mode="tree_summarize")
                result = await llm.chat(
                    tenant_id=tenant_id, model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                return _to_output(result)


            def _to_output(result: Any) -> dict[str, Any]:
                if isinstance(result, dict):
                    return result
                content = getattr(result, "content", "") or ""
                usage = getattr(result, "usage", None)
                tokens = int(getattr(usage, "total_tokens", 0) or 0) \\
                    if usage is not None else 0
                return {"content": content, "tokens_used": tokens}
        '''))

        self.writer.write(f"{base}/helpers/relationships.py", dedent('''\
            """relationships — build parent/child/prev/next from node list"""
            from __future__ import annotations
            import uuid
            from typing import Any


            def build_node_relationships(
                node_ids: list[uuid.UUID],
            ) -> list[dict[str, Any]]:
                """TH: สร้าง prev/next | EN: build prev/next relationships"""
                out: list[dict[str, Any]] = []
                n = len(node_ids)
                for i, nid in enumerate(node_ids):
                    out.append({
                        "id": nid,
                        "prev_id": str(node_ids[i - 1]) if i > 0 else None,
                        "next_id": str(node_ids[i + 1]) if i < n - 1 else None,
                    })
                return out
        '''))

    def _domain_enums(self) -> str:
        return dedent('''\
            """llamaindex enums"""
            from __future__ import annotations
            from enum import Enum


            class IndexType(str, Enum):
                """TH: ประเภท index | EN: Index type"""
                VECTOR_STORE = "vector_store"
                SUMMARY = "summary"
                TREE = "tree"
                KEYWORD = "keyword"
                KG = "kg"
                DOCUMENT_SUMMARY = "document_summary"

                def __str__(self) -> str:
                    return str(self.value)


            class NodeType(str, Enum):
                """TH: ประเภท node | EN: Node type"""
                TEXT = "text"
                IMAGE = "image"
                INDEX = "index"
                MULTIMODAL = "multimodal"

                def __str__(self) -> str:
                    return str(self.value)


            class ResponseMode(str, Enum):
                """TH: โหมดการสังเคราะห์คำตอบ | EN: Response mode"""
                COMPACT = "compact"
                REFINE = "refine"
                TREE_SUMMARIZE = "tree_summarize"
                SIMPLE_SUMMARIZE = "simple_summarize"
                NO_TEXT = "no_text"
                GENERATION = "generation"
                ACCUMULATE = "accumulate"

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
        ''')

    def _domain_exceptions(self) -> str:
        return dedent('''\
            """llamaindex domain exceptions"""
            from __future__ import annotations


            class LIError(Exception):
                """TH: base | EN: base"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class IndexNotFoundError(LIError):
                code = "NOT_FOUND"


            class QueryEngineNotFoundError(LIError):
                code = "NOT_FOUND"


            class DocumentNotFoundError(LIError):
                code = "NOT_FOUND"


            class RunNotFoundError(LIError):
                code = "NOT_FOUND"


            class IndexConflictError(LIError):
                code = "CONFLICT"


            class QueryEngineConflictError(LIError):
                code = "CONFLICT"


            class InvalidIndexTypeError(LIError):
                code = "VALIDATION_ERROR"


            class IngestionError(LIError):
                code = "PROVIDER_ERROR"


            class QueryError(LIError):
                code = "PROVIDER_ERROR"


            class SynthesisError(LIError):
                code = "PROVIDER_ERROR"
        ''')

    def _domain_events(self) -> str:
        return dedent('''\
            """llamaindex domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import datetime, timezone


            def _now():
                return datetime.now(timezone.utc)


            @dataclass(frozen=True)
            class IndexCreated:
                index_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                index_type: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class DocumentIngested:
                document_id: uuid.UUID
                tenant_id: uuid.UUID
                index_id: uuid.UUID
                source_uri: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class NodesCreated:
                index_id: uuid.UUID
                tenant_id: uuid.UUID
                node_count: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class QueryExecuted:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                query_engine_id: uuid.UUID
                latency_ms: int
                source_count: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class ResponseSynthesized:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                response_mode: str
                tokens_used: int
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
            """llamaindex application exceptions"""
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


            class IngestionAppError(AppError):
                code = "PROVIDER_ERROR"
                http_status = 502


            class QueryAppError(AppError):
                code = "PROVIDER_ERROR"
                http_status = 502


            class LimitExceededAppError(AppError):
                code = "LIMIT_EXCEEDED"
                http_status = 402
        ''')

    def _interfaces_content(self) -> str:
        return dedent('''\
            """llamaindex application ports"""
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


            class LIIndexRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, i: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
                @abstractmethod
                async def find_all_active(self, ctx: Any) -> list[Any]: ...


            class LINodeRepository(ABC):
                @abstractmethod
                async def create_many(self, ctx: Any, nodes: list[Any]) -> int: ...
                @abstractmethod
                async def find_by_index(
                    self, ctx: Any, index_id: uuid.UUID,
                ) -> list[Any]: ...
                @abstractmethod
                async def delete_by_document(
                    self, ctx: Any, document_id: uuid.UUID,
                ) -> int: ...


            class LIQueryEngineRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, q: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_index(
                    self, ctx: Any, index_id: uuid.UUID,
                ) -> list[Any]: ...


            class LIDocumentRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, d: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_hash(self, ctx: Any, h: str) -> Any | None: ...
                @abstractmethod
                async def find_by_index(
                    self, ctx: Any, index_id: uuid.UUID,
                ) -> list[Any]: ...
                @abstractmethod
                async def update(self, ctx: Any, d: Any) -> Any: ...


            class LIRunRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, r: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def update(self, ctx: Any, r: Any) -> Any: ...


            class EmbeddingPort(Protocol):
                """TH: port ไปยัง embeddings module | EN: embeddings port"""
                async def embed(
                    self, *, model: str, texts: list[str], normalize: bool = True,
                ) -> list[Any]: ...


            class VectorStorePort(Protocol):
                """TH: port ไปยัง vector_db module | EN: vector store port"""
                async def upsert(
                    self, *, collection_id: uuid.UUID, items: list[dict[str, Any]],
                ) -> int: ...

                async def query(
                    self, *, collection_id: uuid.UUID, vector: list[float],
                    top_k: int,
                ) -> list[Any]: ...


            class LLMPort(Protocol):
                """TH: port ไปยัง llm module | EN: LLM port"""
                async def chat(
                    self, *, tenant_id: uuid.UUID, model: str,
                    messages: list[dict[str, Any]],
                    system_prompt: Optional[str] = None,
                ) -> Any: ...


            class NodeParserPort(Protocol):
                """TH: port ของ node parser | EN: node parser port"""
                def split(self, text: str) -> list[str]: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...
        ''')

    def _mappers_content(self) -> str:
        return dedent('''\
            """llamaindex mappers — ORM → dict"""
            from __future__ import annotations
            from typing import Any


            def index_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "index_type": row.index_type,
                    "embed_model": row.embed_model,
                    "storage_kind": row.storage_kind,
                    "is_active": bool(row.is_active),
                }


            def node_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "index_id": str(row.index_id),
                    "node_type": row.node_type,
                    "ordinal": int(row.ordinal or 0),
                    "content": (row.content or "")[:200],
                }


            def query_engine_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "index_id": str(row.index_id),
                    "name": row.name,
                    "retriever_type": row.retriever_type,
                    "top_k": int(row.top_k or 5),
                    "response_mode": row.response_mode,
                    "similarity_top_k": int(row.similarity_top_k or 5),
                }


            def document_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "index_id": str(row.index_id),
                    "source_uri": row.source_uri or "",
                    "mime_type": row.mime_type or "",
                    "title": row.title or "",
                    "hash": row.hash or "",
                    "status": row.status,
                }


            def run_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "query_engine_id": str(row.query_engine_id),
                    "query": (row.query or "")[:200],
                    "answer": (row.answer or "")[:200],
                    "latency_ms": int(row.latency_ms or 0),
                    "tokens_used": int(row.tokens_used or 0),
                }
        ''')

    def _utils_content(self) -> str:
        return dedent('''\
            """llamaindex application utils"""
            from __future__ import annotations
            import hashlib
            import json
            import time
            from typing import Any


            def document_hash(text: str) -> str:
                return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
            """llamaindex use cases"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any, Optional

            from app.modules.llamaindex.application.exceptions import (
                ConflictAppError, IngestionAppError, NotFoundAppError,
                QueryAppError, ValidationAppError,
            )
            from app.modules.llamaindex.application.utils import (
                document_hash, json_dumps_safe, json_loads_safe, ms_now,
            )
            from app.modules.llamaindex.domain.enums import (
                DocumentStatus, NodeType, ResponseMode,
            )
            from app.modules.llamaindex.domain.events import (
                DocumentIngested, IndexCreated, NodesCreated, QueryExecuted,
                ResponseSynthesized,
            )
            from app.modules.llamaindex.domain.helpers.relationships import (
                build_node_relationships,
            )
            from app.modules.llamaindex.domain.helpers.splitter import (
                SentenceSplitter,
            )
            from app.modules.llamaindex.domain.helpers.synthesizer import (
                synthesize_compact, synthesize_refine, synthesize_tree_summarize,
            )
            from app.modules.llamaindex.domain.value_objects import (
                IndexSpec, QueryEngineSpec,
            )

            logger = logging.getLogger(__name__)


            class LlamaIndexUseCase:
                """TH: use case หลัก | EN: core use case"""

                def __init__(self, **deps: Any) -> None:
                    for key, value in deps.items():
                        setattr(self, f"_{key}", value)

                # ─── Index ────────────────────────────────────
                async def create_index(
                    self, ctx: Any, spec: IndexSpec,
                ) -> Any:
                    from app.modules.llamaindex.infrastructure.models import (
                        LIIndexModel,
                    )
                    existing = await self._indexes.find_by_name(ctx, spec.name)
                    if existing is not None:
                        raise ConflictAppError(f"index exists: {spec.name}")

                    row = LIIndexModel(
                        tenant_id=ctx.tenant_id, name=spec.name,
                        index_type=str(spec.index_type),
                        embed_model=spec.embed_model,
                        storage_kind=spec.storage_kind,
                        config_json=json_dumps_safe(spec.config or {}),
                        is_active=True,
                    )
                    saved = await self._indexes.save(ctx, row)
                    if self._bus:
                        try:
                            await self._bus.publish(IndexCreated(
                                index_id=saved.id, tenant_id=ctx.tenant_id,
                                name=saved.name, index_type=str(spec.index_type),
                            ))
                        except Exception:
                            pass
                    return saved

                async def list_indexes(self, ctx: Any) -> list[Any]:
                    return await self._indexes.find_all_active(ctx)

                async def get_index(self, ctx: Any, index_id: uuid.UUID) -> Any:
                    idx = await self._indexes.find_by_id(ctx, index_id)
                    if idx is None:
                        raise NotFoundAppError("index not found")
                    return idx

                # ─── Ingest ───────────────────────────────────
                async def ingest(
                    self, ctx: Any, *, index_id: uuid.UUID,
                    content: str, source_uri: str = "",
                    mime_type: str = "text/plain", title: str = "",
                    chunk_size: int = 512, chunk_overlap: int = 50,
                ) -> Any:
                    """TH: ingest document → nodes | EN: ingest document"""
                    from app.modules.llamaindex.infrastructure.models import (
                        LIDocumentModel, LINodeModel,
                    )

                    if not content:
                        raise IngestionAppError("empty content")

                    index = await self.get_index(ctx, index_id)
                    h = document_hash(content)

                    existing = await self._documents.find_by_hash(ctx, h)
                    if existing is not None and existing.status == DocumentStatus.READY.value:
                        return existing

                    doc = LIDocumentModel(
                        tenant_id=ctx.tenant_id, index_id=index.id,
                        source_uri=source_uri, mime_type=mime_type,
                        title=title or source_uri or "untitled",
                        hash=h, status=DocumentStatus.PROCESSING.value,
                    )
                    saved_doc = await self._documents.save(ctx, doc)

                    try:
                        parser = SentenceSplitter(
                            chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                        )
                        chunks = parser.split(content)
                        if not chunks:
                            raise IngestionError("no chunks produced")

                        # embed chunks
                        embeddings: list[Any] = []
                        if self._embedder is not None:
                            try:
                                embeddings = await self._embedder.embed(
                                    model=index.embed_model, texts=chunks,
                                )
                            except Exception as exc:
                                logger.warning("embed failed: %s", exc)

                        # upsert to vector store
                        if self._vector_store is not None:
                            collection_id = self._collection_id(index)
                            try:
                                items = []
                                for i, chunk in enumerate(chunks):
                                    vec = self._extract_vector(
                                        embeddings[i] if i < len(embeddings) else None
                                    )
                                    items.append({
                                        "source_id": f"{saved_doc.id}:{i}",
                                        "vector": vec,
                                        "metadata": {
                                            "index_id": str(index.id),
                                            "document_id": str(saved_doc.id),
                                            "ordinal": i,
                                        },
                                    })
                                if items:
                                    await self._vector_store.upsert(
                                        collection_id=collection_id, items=items,
                                    )
                            except Exception as exc:
                                logger.warning("vector upsert failed: %s", exc)

                        # persist nodes
                        node_rows: list[LINodeModel] = []
                        for i, chunk in enumerate(chunks):
                            node_rows.append(LINodeModel(
                                tenant_id=ctx.tenant_id, index_id=index.id,
                                document_id=saved_doc.id,
                                node_type=NodeType.TEXT.value,
                                ordinal=i, content=chunk,
                                token_count=max(1, len(chunk) // 4),
                                relationships_json="{}",
                                metadata_json="{}",
                            ))
                        count = await self._nodes.create_many(ctx, node_rows)

                        saved_doc.status = DocumentStatus.READY.value
                        saved_doc.node_count = count
                        await self._documents.update(ctx, saved_doc)

                        if self._bus:
                            try:
                                await self._bus.publish(DocumentIngested(
                                    document_id=saved_doc.id,
                                    tenant_id=ctx.tenant_id,
                                    index_id=index.id,
                                    source_uri=source_uri,
                                ))
                                await self._bus.publish(NodesCreated(
                                    index_id=index.id,
                                    tenant_id=ctx.tenant_id,
                                    node_count=count,
                                ))
                            except Exception:
                                pass

                        return saved_doc
                    except Exception as exc:
                        logger.exception("ingest failed: %s", exc)
                        saved_doc.status = DocumentStatus.FAILED.value
                        try:
                            await self._documents.update(ctx, saved_doc)
                        except Exception:
                            pass
                        if isinstance(exc, IngestionError):
                            raise
                        raise IngestionAppError(f"ingest failed: {exc}") from exc

                # ─── Query ────────────────────────────────────
                async def query(
                    self, ctx: Any, *, index_id: uuid.UUID,
                    query: str, query_engine_id: Optional[uuid.UUID] = None,
                    top_k: Optional[int] = None,
                    response_mode: Optional[str] = None,
                    model: str = "gpt-4o-mini",
                ) -> dict[str, Any]:
                    """TH: query index | EN: query index"""
                    from app.modules.llamaindex.infrastructure.models import (
                        LIRunModel,
                    )

                    if not query.strip():
                        raise ValidationAppError("empty query")

                    index = await self.get_index(ctx, index_id)

                    # resolve query engine
                    engine = None
                    if query_engine_id is not None:
                        engine = await self._engines.find_by_id(ctx, query_engine_id)
                        if engine is None:
                            raise NotFoundAppError("query engine not found")
                    else:
                        engines = await self._engines.find_by_index(ctx, index.id)
                        engine = engines[0] if engines else None

                    eff_top_k = int(top_k or (engine.top_k if engine else 5))
                    eff_mode = response_mode or (
                        engine.response_mode if engine else ResponseMode.COMPACT.value
                    )

                    run = LIRunModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id,
                        index_id=index.id,
                        query_engine_id=engine.id if engine else None,
                        query=query,
                        status="RUNNING",
                    )
                    saved_run = await self._runs.create(ctx, run)
                    started = ms_now()

                    source_nodes: list[dict[str, Any]] = []
                    answer = ""
                    tokens = 0

                    try:
                        source_nodes = await self._retrieve(
                            ctx, index, query, top_k=eff_top_k,
                            model=index.embed_model,
                        )
                        result = await self._synthesize(
                            ctx, query=query, nodes=source_nodes,
                            mode=eff_mode, model=model,
                        )
                        answer = result.get("content", "")
                        tokens = int(result.get("tokens_used", 0) or 0)
                    except Exception as exc:
                        logger.exception("query failed: %s", exc)
                        saved_run.status = "FAILED"
                        saved_run.error_message = str(exc)[:500]
                        saved_run.latency_ms = ms_now() - started
                        await self._runs.update(ctx, saved_run)
                        if isinstance(exc, (NotFoundAppError, ValidationAppError)):
                            raise
                        raise QueryAppError(f"query failed: {exc}") from exc

                    latency = ms_now() - started
                    saved_run.answer = answer
                    saved_run.source_nodes_json = json_dumps_safe(source_nodes)
                    saved_run.latency_ms = latency
                    saved_run.tokens_used = tokens
                    saved_run.status = "DONE"
                    await self._runs.update(ctx, saved_run)

                    if self._bus:
                        try:
                            await self._bus.publish(QueryExecuted(
                                run_id=saved_run.id, tenant_id=ctx.tenant_id,
                                query_engine_id=engine.id if engine else uuid.uuid4(),
                                latency_ms=latency,
                                source_count=len(source_nodes),
                            ))
                            await self._bus.publish(ResponseSynthesized(
                                run_id=saved_run.id, tenant_id=ctx.tenant_id,
                                response_mode=eff_mode, tokens_used=tokens,
                            ))
                        except Exception:
                            pass

                    return {
                        "run_id": str(saved_run.id),
                        "answer": answer,
                        "source_nodes": source_nodes,
                        "latency_ms": latency,
                        "tokens_used": tokens,
                        "response_mode": eff_mode,
                    }

                # ─── Query Engines ────────────────────────────
                async def create_query_engine(
                    self, ctx: Any, *, index_id: uuid.UUID, spec: QueryEngineSpec,
                ) -> Any:
                    from app.modules.li.infrastructure.models import (
                        LIQueryEngineModel,
                    )
                    await self.get_index(ctx, index_id)
                    row = LIQueryEngineModel(
                        tenant_id=ctx.tenant_id, index_id=index_id,
                        name=spec.name,
                        retriever_type=spec.retriever_type,
                        top_k=spec.top_k,
                        response_mode=str(spec.response_mode),
                        similarity_top_k=spec.similarity_top_k,
                    )
                    return await self._engines.save(ctx, row)

                async def list_query_engines(
                    self, ctx: Any, index_id: uuid.UUID,
                ) -> list[Any]:
                    await self.get_index(ctx, index_id)
                    return await self._engines.find_by_index(ctx, index_id)

                # ─── Runs ─────────────────────────────────────
                async def get_run(self, ctx: Any, run_id: uuid.UUID) -> Any:
                    r = await self._runs.find_by_id(ctx, run_id)
                    if r is None:
                        raise NotFoundAppError("run not found")
                    return r

                # ─── Internal ─────────────────────────────────
                async def _retrieve(
                    self, ctx: Any, index: Any, query: str,
                    *, top_k: int, model: str,
                ) -> list[dict[str, Any]]:
                    if self._embedder is None or self._vector_store is None:
                        return []
                    try:
                        embeddings = await self._embedder.embed(
                            model=model, texts=[query],
                        )
                        qv = self._extract_vector(
                            embeddings[0] if embeddings else None,
                        )
                        if not qv:
                            return []
                        collection_id = self._collection_id(index)
                        hits = await self._vector_store.query(
                            collection_id=collection_id, vector=qv, top_k=top_k,
                        )
                        return [self._hit_to_dict(h) for h in hits]
                    except Exception as exc:
                        logger.warning("retrieve failed: %s", exc)
                        return []

                async def _synthesize(
                    self, ctx: Any, *, query: str,
                    nodes: list[dict[str, Any]],
                    mode: str, model: str,
                ) -> dict[str, Any]:
                    if self._llm is None:
                        return {"content": "", "tokens_used": 0}
                    if mode == ResponseMode.REFINE.value:
                        return await synthesize_refine(
                            self._llm, tenant_id=ctx.tenant_id, model=model,
                            query=query, nodes=nodes,
                        )
                    if mode == ResponseMode.TREE_SUMMARIZE.value:
                        return await synthesize_tree_summarize(
                            self._llm, tenant_id=ctx.tenant_id, model=model,
                            query=query, nodes=nodes,
                        )
                    return await synthesize_compact(
                        self._llm, tenant_id=ctx.tenant_id, model=model,
                        query=query, nodes=nodes,
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

                @staticmethod
                def _hit_to_dict(hit: Any) -> dict[str, Any]:
                    if isinstance(hit, dict):
                        return hit
                    return {
                        "source_id": str(getattr(hit, "source_id", "")),
                        "chunk_id": str(getattr(hit, "vector_id", "")),
                        "score": float(getattr(hit, "score", 0.0)),
                        "content": str(getattr(hit, "snippet", "")),
                        "metadata": getattr(hit, "metadata", {}) or {},
                    }

                @staticmethod
                def _collection_id(index: Any) -> uuid.UUID:
                    """TH: ดึง collection_id จาก config (fallback)"""
                    cfg = json_loads_safe(getattr(index, "config_json", "{}"), {})
                    cid = cfg.get("collection_id")
                    if cid:
                        try:
                            return uuid.UUID(str(cid))
                        except ValueError:
                            pass
                    return uuid.UUID(int=0)
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
            """llamaindex SQLAlchemy models — schema=public, prefix=li_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from typing import Optional

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Index, Integer, String, Text,
                UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: base | EN: base"""


            class LIIndexModel(Base):
                __tablename__ = "li_indexes"
                __table_args__ = (
                    CheckConstraint(
                        "index_type IN ('vector_store','summary','tree','keyword','kg','document_summary')",
                        name="ck_li_index_type",
                    ),
                    UniqueConstraint("tenant_id", "name", name="uq_li_index_name"),
                    Index("ix_li_index_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                index_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="vector_store")
                embed_model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="text-embedding-3-small")
                storage_kind: Mapped[str] = mapped_column(String(50), nullable=False, server_default="pgvector")
                config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class LINodeModel(Base):
                __tablename__ = "li_nodes"
                __table_args__ = (
                    Index("ix_li_node_index_ord", "index_id", "ordinal"),
                    Index("ix_li_node_doc", "document_id"),
                    Index("ix_li_node_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                index_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
                    UUID(as_uuid=True), nullable=True,
                )
                node_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="text")
                ordinal: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                content: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                token_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                relationships_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class LIQueryEngineModel(Base):
                __tablename__ = "li_query_engines"
                __table_args__ = (
                    CheckConstraint(
                        "response_mode IN ('compact','refine','tree_summarize','simple_summarize','no_text','generation','accumulate')",
                        name="ck_li_qe_response_mode",
                    ),
                    UniqueConstraint("tenant_id", "index_id", "name", name="uq_li_qe_name"),
                    Index("ix_li_qe_index", "index_id"),
                    Index("ix_li_qe_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                index_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                retriever_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="vector")
                top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
                response_mode: Mapped[str] = mapped_column(String(30), nullable=False, server_default="compact")
                similarity_top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="5")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class LIDocumentModel(Base):
                __tablename__ = "li_documents"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('PENDING','PROCESSING','READY','FAILED','DELETED')",
                        name="ck_li_doc_status",
                    ),
                    Index("ix_li_doc_index_hash", "index_id", "hash"),
                    Index("ix_li_doc_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                index_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                source_uri: Mapped[str] = mapped_column(String(1000), nullable=False, server_default="")
                mime_type: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
                title: Mapped[str] = mapped_column(String(500), nullable=False, server_default="")
                hash: Mapped[str] = mapped_column(String(128), nullable=False, server_default="")
                status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
                node_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class LIRunModel(Base):
                __tablename__ = "li_runs"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('QUEUED','RUNNING','DONE','FAILED','CANCELLED')",
                        name="ck_li_run_status",
                    ),
                    Index("ix_li_run_tenant_time", "tenant_id", "created_at"),
                    Index("ix_li_run_user_time", "user_id", "created_at"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                index_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                query_engine_id: Mapped[Optional[uuid.UUID]] = mapped_column(
                    UUID(as_uuid=True), nullable=True,
                )
                query: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                answer: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                source_nodes_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
                status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="QUEUED")
                latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                error_message: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            __all__ = [
                "Base", "LIIndexModel", "LINodeModel", "LIQueryEngineModel",
                "LIDocumentModel", "LIRunModel",
            ]
        ''')

    def _repositories_content(self) -> str:
        return dedent('''\
            """llamaindex repositories"""
            from __future__ import annotations
            import logging
            import uuid

            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.llamaindex.application.exceptions import AppError
            from app.modules.llamaindex.infrastructure.models import (
                LIDocumentModel, LIIndexModel, LINodeModel, LIQueryEngineModel,
                LIRunModel,
            )

            logger = logging.getLogger(__name__)


            class LIIndexRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, i: LIIndexModel) -> LIIndexModel:
                    try:
                        self._session.add(i)
                        await self._session.flush()
                        return i
                    except SQLAlchemyError as exc:
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> LIIndexModel | None:
                    r = await self._session.execute(
                        select(LIIndexModel).where(LIIndexModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def find_by_name(self, ctx: object, name: str) -> LIIndexModel | None:
                    r = await self._session.execute(
                        select(LIIndexModel).where(LIIndexModel.name == name)
                    )
                    return r.scalar_one_or_none()

                async def find_all_active(self, ctx: object) -> list[LIIndexModel]:
                    r = await self._session.execute(
                        select(LIIndexModel)
                        .where(LIIndexModel.is_active.is_(True))
                        .order_by(LIIndexModel.name)
                    )
                    return list(r.scalars().all())


            class LINodeRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create_many(self, ctx: object, nodes: list) -> int:
                    for n in nodes:
                        self._session.add(n)
                    await self._session.flush()
                    return len(nodes)

                async def find_by_index(
                    self, ctx: object, index_id: uuid.UUID,
                ) -> list[LINodeModel]:
                    r = await self._session.execute(
                        select(LINodeModel)
                        .where(LINodeModel.index_id == index_id)
                        .order_by(LINodeModel.ordinal)
                    )
                    return list(r.scalars().all())

                async def delete_by_document(
                    self, ctx: object, document_id: uuid.UUID,
                ) -> int:
                    from sqlalchemy import delete
                    r = await self._session.execute(
                        delete(LINodeModel).where(LINodeModel.document_id == document_id)
                    )
                    await self._session.flush()
                    return int(r.rowcount or 0)


            class LIQueryEngineRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, q: LIQueryEngineModel) -> LIQueryEngineModel:
                    self._session.add(q)
                    await self._session.flush()
                    return q

                async def find_by_id(
                    self, ctx: object, id: uuid.UUID,
                ) -> LIQueryEngineModel | None:
                    r = await self._session.execute(
                        select(LIQueryEngineModel).where(LIQueryEngineModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def find_by_index(
                    self, ctx: object, index_id: uuid.UUID,
                ) -> list[LIQueryEngineModel]:
                    r = await self._session.execute(
                        select(LIQueryEngineModel)
                        .where(LIQueryEngineModel.index_id == index_id)
                        .order_by(LIQueryEngineModel.name)
                    )
                    return list(r.scalars().all())


            class LIDocumentRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, d: LIDocumentModel) -> LIDocumentModel:
                    self._session.add(d)
                    await self._session.flush()
                    return d

                async def find_by_id(
                    self, ctx: object, id: uuid.UUID,
                ) -> LIDocumentModel | None:
                    r = await self._session.execute(
                        select(LIDocumentModel).where(LIDocumentModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def find_by_hash(
                    self, ctx: object, h: str,
                ) -> LIDocumentModel | None:
                    r = await self._session.execute(
                        select(LIDocumentModel).where(LIDocumentModel.hash == h)
                    )
                    return r.scalar_one_or_none()

                async def find_by_index(
                    self, ctx: object, index_id: uuid.UUID,
                ) -> list[LIDocumentModel]:
                    r = await self._session.execute(
                        select(LIDocumentModel)
                        .where(LIDocumentModel.index_id == index_id)
                        .order_by(LIDocumentModel.created_at.desc())
                    )
                    return list(r.scalars().all())

                async def update(self, ctx: object, d: LIDocumentModel) -> LIDocumentModel:
                    await self._session.flush()
                    return d


            class LIRunRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, r_: LIRunModel) -> LIRunModel:
                    self._session.add(r_)
                    await self._session.flush()
                    return r_

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> LIRunModel | None:
                    r = await self._session.execute(
                        select(LIRunModel).where(LIRunModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def update(self, ctx: object, r_: LIRunModel) -> LIRunModel:
                    await self._session.flush()
                    return r_
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """llamaindex services — adapters + bus"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any, Optional

            from app.modules.llamaindex.application.interfaces import EventBus

            logger = logging.getLogger(__name__)


            class EmbeddingModuleAdapter:
                """TH: adapter ไปยัง embeddings module | EN: embeddings adapter"""

                def __init__(self, embedding_use_case: Any) -> None:
                    self._uc = embedding_use_case

                async def embed(
                    self, *, model: str, texts: list[str], normalize: bool = True,
                ) -> list[Any]:
                    if not texts:
                        return []
                    try:
                        from app.modules.embeddings.domain.value_objects import (
                            EmbeddingRequest,
                        )
                        from app.shared.context import RequestContext as SharedCtx
                        ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
                        return await self._uc.embed(ctx, EmbeddingRequest(
                            model=model, input=texts, normalize=normalize,
                        ))
                    except Exception as exc:
                        logger.warning("embedding adapter failed: %s", exc)
                        return []


            class VectorStoreModuleAdapter:
                """TH: adapter ไปยัง vector_db module | EN: vector store adapter"""

                def __init__(self, vector_use_case: Any) -> None:
                    self._uc = vector_use_case

                async def upsert(
                    self, *, collection_id: uuid.UUID,
                    items: list[dict[str, Any]],
                ) -> int:
                    try:
                        from app.shared.context import RequestContext as SharedCtx
                        ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
                        return await self._uc.upsert(
                            ctx, collection_id=collection_id, items=items,
                        )
                    except Exception as exc:
                        logger.warning("vector upsert failed: %s", exc)
                        return 0

                async def query(
                    self, *, collection_id: uuid.UUID,
                    vector: list[float], top_k: int,
                ) -> list[Any]:
                    try:
                        from app.modules.vector_db.domain.value_objects import (
                            VectorQuery,
                        )
                        from app.shared.context import RequestContext as SharedCtx
                        ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
                        return await self._uc.query(
                            ctx, collection_id=collection_id,
                            query=VectorQuery(vector=vector, top_k=top_k),
                        )
                    except Exception as exc:
                        logger.warning("vector query failed: %s", exc)
                        return []


            class LLMPortAdapter:
                """TH: adapter ไปยัง llm module | EN: LLM port adapter"""

                def __init__(self, llm_use_case: Any) -> None:
                    self._uc = llm_use_case

                async def chat(
                    self, *, tenant_id: uuid.UUID, model: str,
                    messages: list[dict[str, Any]],
                    system_prompt: Optional[str] = None,
                ) -> Any:
                    from app.shared.context import RequestContext as SharedCtx
                    ctx = SharedCtx(tenant_id=tenant_id)
                    return await self._uc.chat(
                        ctx, model_name=model, messages=messages,
                        system_prompt=system_prompt,
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
            """llamaindex Pydantic schemas"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.llamaindex.domain.enums import (
                IndexType, ResponseMode,
            )


            class IndexCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(min_length=1, max_length=100)
                index_type: IndexType = IndexType.VECTOR_STORE
                embed_model: str = "text-embedding-3-small"
                storage_kind: str = "pgvector"
                config: dict[str, Any] = Field(default_factory=dict)


            class IndexOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                index_type: str
                embed_model: str
                storage_kind: str
                is_active: bool


            class IngestRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                content: str = Field(min_length=1)
                source_uri: str = ""
                mime_type: str = "text/plain"
                title: str = ""
                chunk_size: int = Field(default=512, ge=64, le=8192)
                chunk_overlap: int = Field(default=50, ge=0, le=2048)


            class IngestResponse(BaseModel):
                document_id: uuid.UUID
                index_id: uuid.UUID
                status: str
                node_count: int


            class QueryRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                query: str = Field(min_length=1)
                query_engine_id: Optional[uuid.UUID] = None
                top_k: Optional[int] = Field(default=None, ge=1, le=100)
                response_mode: Optional[ResponseMode] = None
                model: str = "gpt-4o-mini"


            class SourceNodeOut(BaseModel):
                source_id: str
                chunk_id: Optional[str] = None
                score: float = 0.0
                content: str = ""
                metadata: Optional[dict[str, Any]] = None


            class QueryResponse(BaseModel):
                run_id: uuid.UUID
                answer: str
                source_nodes: list[SourceNodeOut] = []
                latency_ms: int = 0
                tokens_used: int = 0
                response_mode: str = "compact"


            class QueryEngineCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(min_length=1, max_length=100)
                retriever_type: str = "vector"
                top_k: int = Field(default=5, ge=1, le=100)
                response_mode: ResponseMode = ResponseMode.COMPACT
                similarity_top_k: int = Field(default=5, ge=1, le=100)


            class QueryEngineOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                index_id: uuid.UUID
                name: str
                retriever_type: str
                top_k: int
                response_mode: str
                similarity_top_k: int


            class RunOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                index_id: uuid.UUID
                query: str
                answer: str
                status: str
                latency_ms: int
                tokens_used: int
                created_at: datetime


            class DocumentOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                index_id: uuid.UUID
                source_uri: str
                mime_type: str
                title: str
                status: str
                node_count: int
                created_at: datetime
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """llamaindex DI container"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass
            from typing import Annotated, Optional

            from fastapi import Depends, Header, HTTPException, Request, status
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.llamaindex.application.use_case import (
                LlamaIndexUseCase,
            )
            from app.modules.llamaindex.infrastructure.repositories import (
                LIDocumentRepository, LIIndexRepository, LINodeRepository,
                LIQueryEngineRepository, LIRunRepository,
            )
            from app.modules.llamaindex.infrastructure.services import (
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
            ) -> LlamaIndexUseCase:
                embedder = getattr(request.app.state, "li_embedder", None)
                vector_store = getattr(request.app.state, "li_vector_store", None)
                llm_port = getattr(request.app.state, "li_llm_port", None)
                parser = getattr(request.app.state, "li_parser", None)
                bus = getattr(request.app.state, "li_event_bus", None) \\
                    or LoggingEventBus()

                return LlamaIndexUseCase(
                    indexes=LIIndexRepository(db),
                    nodes=LINodeRepository(db),
                    engines=LIQueryEngineRepository(db),
                    documents=LIDocumentRepository(db),
                    runs=LIRunRepository(db),
                    embedder=embedder,
                    vector_store=vector_store,
                    llm=llm_port,
                    parser=parser,
                    bus=bus,
                )
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """llamaindex HTTP router"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException

            from app.modules.llamaindex.application.exceptions import AppError
            from app.modules.llamaindex.application.use_case import LlamaIndexUseCase
            from app.modules.llamaindex.domain.exceptions import LIError
            from app.modules.llamaindex.domain.value_objects import (
                IndexSpec, QueryEngineSpec,
            )
            from app.modules.llamaindex.presentation.dependencies import (
                Ctx, get_ctx, get_use_case,
            )
            from app.modules.llamaindex.presentation.schemas import (
                DocumentOut, IndexCreateRequest, IndexOut, IngestRequest,
                IngestResponse, QueryEngineCreateRequest, QueryEngineOut,
                QueryRequest, QueryResponse, RunOut, SourceNodeOut,
            )

            logger = logging.getLogger(__name__)

            router = APIRouter(prefix="/li", tags=["LlamaIndex"])


            def _raise(exc: Exception) -> None:
                if isinstance(exc, LIError):
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


            @router.get("/indexes", response_model=list[IndexOut])
            async def list_indexes(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
            ) -> list[IndexOut]:
                """TH: list indexes | EN: list indexes"""
                try:
                    items = await uc.list_indexes(ctx)
                    return [IndexOut.model_validate(i.model_dump()) for i in items]
                except (LIError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/indexes", response_model=IndexOut, status_code=201)
            async def create_index(
                req: IndexCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
            ) -> IndexOut:
                """TH: สร้าง index | EN: create index"""
                try:
                    spec = IndexSpec(
                        name=req.name, index_type=req.index_type,
                        embed_model=req.embed_model,
                        storage_kind=req.storage_kind, config=req.config,
                    )
                    row = await uc.create_index(ctx, spec)
                    return IndexOut.model_validate(row.model_dump())
                except (LIError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/indexes/{index_id}/ingest", response_model=IngestResponse)
            async def ingest(
                index_id: uuid.UUID,
                req: IngestRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
            ) -> IngestResponse:
                """TH: ingest document | EN: ingest document"""
                try:
                    doc = await uc.ingest(
                        ctx, index_id=index_id, content=req.content,
                        source_uri=req.source_uri, mime_type=req.mime_type,
                        title=req.title, chunk_size=req.chunk_size,
                        chunk_overlap=req.chunk_overlap,
                    )
                    return IngestResponse(
                        document_id=doc.id, index_id=doc.index_id,
                        status=doc.status,
                        node_count=int(doc.node_count or 0),
                    )
                except (LIError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/indexes/{index_id}/query", response_model=QueryResponse)
            async def query_index(
                index_id: uuid.UUID,
                req: QueryRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
            ) -> QueryResponse:
                """TH: query index | EN: query index"""
                try:
                    out = await uc.query(
                        ctx, index_id=index_id, query=req.query,
                        query_engine_id=req.query_engine_id,
                        top_k=req.top_k,
                        response_mode=str(req.response_mode) if req.response_mode else None,
                        model=req.model,
                    )
                    return QueryResponse(
                        run_id=out["run_id"],
                        answer=out.get("answer", ""),
                        source_nodes=[
                            SourceNodeOut(**{k: v for k, v in sn.items()
                                             if k in SourceNodeOut.model_fields})
                            for sn in out.get("source_nodes", [])
                        ],
                        latency_ms=int(out.get("latency_ms", 0)),
                        tokens_used=int(out.get("tokens_used", 0)),
                        response_mode=str(out.get("response_mode", "compact")),
                    )
                except (LIError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/indexes/{index_id}/query-engines",
                         response_model=QueryEngineOut, status_code=201)
            async def create_query_engine(
                index_id: uuid.UUID,
                req: QueryEngineCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
            ) -> QueryEngineOut:
                """TH: สร้าง query engine | EN: create query engine"""
                try:
                    spec = QueryEngineSpec(
                        name=req.name, retriever_type=req.retriever_type,
                        top_k=req.top_k, response_mode=req.response_mode,
                        similarity_top_k=req.similarity_top_k,
                    )
                    row = await uc.create_query_engine(
                        ctx, index_id=index_id, spec=spec,
                    )
                    return QueryEngineOut.model_validate(row.model_dump())
                except (LIError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/indexes/{index_id}/query-engines",
                        response_model=list[QueryEngineOut])
            async def list_query_engines(
                index_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
            ) -> list[QueryEngineOut]:
                """TH: list query engines | EN: list query engines"""
                try:
                    items = await uc.list_query_engines(ctx, index_id)
                    return [QueryEngineOut.model_validate(q.model_dump()) for q in items]
                except (LIError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/runs/{run_id}", response_model=RunOut)
            async def get_run(
                run_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[LlamaIndexUseCase, Depends(get_use_case)],
            ) -> RunOut:
                """TH: ดึง run | EN: get run"""
                try:
                    r = await uc.get_run(ctx, run_id)
                    return RunOut.model_validate(r.model_dump())
                except (LIError, AppError) as exc:
                    _raise(exc)
                    raise
        ''')

    def _swagger_content(self) -> str:
        return dedent(f'''\
            """llamaindex OpenAPI docs"""
            from __future__ import annotations
            from typing import Any


            def register_llamaindex_openapi(app: object) -> None:
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
                                "โมดูล llamaindex — Index + QueryEngine + Synthesis\\n\\n"
                                "• Index types: VectorStore, Summary, Tree, KG\\n"
                                "• Response modes: compact, refine, tree_summarize\\n"
                                "• Node relationships (parent/child/prev/next)\\n"
                                "• Source nodes + citations"
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
-- V001__create_llamaindex.sql | Module: llamaindex | Prefix: li
-- Schema: public | Tables: li_indexes, li_nodes, li_query_engines,
--                          li_documents, li_runs
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."li_indexes";
CREATE TABLE "public"."li_indexes" (
  "id"            uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"     uuid NOT NULL,
  "name"          varchar(100) NOT NULL,
  "index_type"    varchar(30) NOT NULL DEFAULT 'vector_store',
  "embed_model"   varchar(100) NOT NULL DEFAULT 'text-embedding-3-small',
  "storage_kind"  varchar(50) NOT NULL DEFAULT 'pgvector',
  "config_json"   text NOT NULL DEFAULT '{}',
  "is_active"     bool NOT NULL DEFAULT true,
  "created_at"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"    timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "li_indexes_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_li_index_name" UNIQUE ("tenant_id", "name"),
  CONSTRAINT "ck_li_index_type" CHECK (
    index_type IN ('vector_store','summary','tree','keyword','kg','document_summary')
  )
);
CREATE INDEX "ix_li_index_tenant" ON "public"."li_indexes" ("tenant_id");

DROP TABLE IF EXISTS "public"."li_nodes";
CREATE TABLE "public"."li_nodes" (
  "id"                  uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"           uuid NOT NULL,
  "index_id"            uuid NOT NULL,
  "document_id"         uuid NULL,
  "node_type"           varchar(20) NOT NULL DEFAULT 'text',
  "ordinal"             int4 NOT NULL DEFAULT 0,
  "content"             text NOT NULL DEFAULT '',
  "token_count"         int4 NOT NULL DEFAULT 0,
  "relationships_json"  text NOT NULL DEFAULT '{}',
  "metadata_json"       text NOT NULL DEFAULT '{}',
  "created_at"          timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"          timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "li_nodes_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_li_node_index_ord" ON "public"."li_nodes" ("index_id", "ordinal");
CREATE INDEX "ix_li_node_doc"       ON "public"."li_nodes" ("document_id");
CREATE INDEX "ix_li_node_tenant"    ON "public"."li_nodes" ("tenant_id");

DROP TABLE IF EXISTS "public"."li_query_engines";
CREATE TABLE "public"."li_query_engines" (
  "id"                uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"         uuid NOT NULL,
  "index_id"          uuid NOT NULL,
  "name"              varchar(100) NOT NULL,
  "retriever_type"    varchar(30) NOT NULL DEFAULT 'vector',
  "top_k"             int4 NOT NULL DEFAULT 5,
  "response_mode"     varchar(30) NOT NULL DEFAULT 'compact',
  "similarity_top_k"  int4 NOT NULL DEFAULT 5,
  "created_at"        timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"        timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "li_query_engines_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_li_qe_name" UNIQUE ("tenant_id", "index_id", "name"),
  CONSTRAINT "ck_li_qe_response_mode" CHECK (
    response_mode IN ('compact','refine','tree_summarize','simple_summarize','no_text','generation','accumulate')
  )
);
CREATE INDEX "ix_li_qe_index"  ON "public"."li_query_engines" ("index_id");
CREATE INDEX "ix_li_qe_tenant" ON "public"."li_query_engines" ("tenant_id");

DROP TABLE IF EXISTS "public"."li_documents";
CREATE TABLE "public"."li_documents" (
  "id"          uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"   uuid NOT NULL,
  "index_id"    uuid NOT NULL,
  "source_uri"  varchar(1000) NOT NULL DEFAULT '',
  "mime_type"   varchar(100) NOT NULL DEFAULT '',
  "title"       varchar(500) NOT NULL DEFAULT '',
  "hash"        varchar(128) NOT NULL DEFAULT '',
  "status"      varchar(20) NOT NULL DEFAULT 'PENDING',
  "node_count"  int4 NOT NULL DEFAULT 0,
  "created_at"  timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"  timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "li_documents_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_li_doc_status" CHECK (
    status IN ('PENDING','PROCESSING','READY','FAILED','DELETED')
  )
);
CREATE INDEX "ix_li_doc_index_hash" ON "public"."li_documents" ("index_id", "hash");
CREATE INDEX "ix_li_doc_tenant"     ON "public"."li_documents" ("tenant_id");

DROP TABLE IF EXISTS "public"."li_runs";
CREATE TABLE "public"."li_runs" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"          uuid NOT NULL,
  "user_id"            uuid NOT NULL,
  "index_id"           uuid NOT NULL,
  "query_engine_id"    uuid NULL,
  "query"              text NOT NULL DEFAULT '',
  "answer"             text NOT NULL DEFAULT '',
  "source_nodes_json"  text NOT NULL DEFAULT '[]',
  "status"             varchar(20) NOT NULL DEFAULT 'QUEUED',
  "latency_ms"         int4 NOT NULL DEFAULT 0,
  "tokens_used"        int4 NOT NULL DEFAULT 0,
  "error_message"      text NOT NULL DEFAULT '',
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"         timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "li_runs_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_li_run_status" CHECK (
    status IN ('QUEUED','RUNNING','DONE','FAILED','CANCELLED')
  )
);
CREATE INDEX "ix_li_run_tenant_time" ON "public"."li_runs" ("tenant_id", "created_at" DESC);
CREATE INDEX "ix_li_run_user_time"   ON "public"."li_runs" ("user_id", "created_at" DESC);

CREATE OR REPLACE FUNCTION public.set_updated_at_li()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_li_index_updated ON "public"."li_indexes";
CREATE TRIGGER trg_li_index_updated BEFORE UPDATE ON "public"."li_indexes"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_li();

DROP TRIGGER IF EXISTS trg_li_node_updated ON "public"."li_nodes";
CREATE TRIGGER trg_li_node_updated BEFORE UPDATE ON "public"."li_nodes"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_li();

DROP TRIGGER IF EXISTS trg_li_qe_updated ON "public"."li_query_engines";
CREATE TRIGGER trg_li_qe_updated BEFORE UPDATE ON "public"."li_query_engines"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_li();

DROP TRIGGER IF EXISTS trg_li_doc_updated ON "public"."li_documents";
CREATE TRIGGER trg_li_doc_updated BEFORE UPDATE ON "public"."li_documents"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_li();

DROP TRIGGER IF EXISTS trg_li_run_updated ON "public"."li_runs";
CREATE TRIGGER trg_li_run_updated BEFORE UPDATE ON "public"."li_runs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_li();

ALTER TABLE "public"."li_indexes"        ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."li_nodes"          ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."li_query_engines"  ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."li_documents"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."li_runs"           ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_li_index ON "public"."li_indexes";
CREATE POLICY p_li_index ON "public"."li_indexes"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_li_node ON "public"."li_nodes";
CREATE POLICY p_li_node ON "public"."li_nodes"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_li_qe ON "public"."li_query_engines";
CREATE POLICY p_li_qe ON "public"."li_query_engines"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_li_doc ON "public"."li_documents";
CREATE POLICY p_li_doc ON "public"."li_documents"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_li_run ON "public"."li_runs";
CREATE POLICY p_li_run ON "public"."li_runs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_llamaindex.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."li_indexes"
    (tenant_id, name, index_type, embed_model, storage_kind, config_json)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'default_vector',
     'vector_store', 'text-embedding-3-small', 'pgvector',
     '{"collection_id":"00000000-0000-0000-0000-000000000000"}'),
    ('00000000-0000-0000-0000-000000000001', 'summary_index',
     'summary', 'text-embedding-3-small', 'pgvector', '{}')
ON CONFLICT DO NOTHING;

INSERT INTO "public"."li_query_engines"
    (tenant_id, index_id, name, retriever_type, top_k, response_mode, similarity_top_k)
SELECT
    '00000000-0000-0000-0000-000000000001', i.id, 'default_compact',
    'vector', 5, 'compact', 5
FROM "public"."li_indexes" i
WHERE i.name = 'default_vector'
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_llamaindex.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_li_run_updated   ON "public"."li_runs";
DROP TRIGGER IF EXISTS trg_li_doc_updated   ON "public"."li_documents";
DROP TRIGGER IF EXISTS trg_li_qe_updated    ON "public"."li_query_engines";
DROP TRIGGER IF EXISTS trg_li_node_updated  ON "public"."li_nodes";
DROP TRIGGER IF EXISTS trg_li_index_updated ON "public"."li_indexes";

DROP POLICY IF EXISTS p_li_run   ON "public"."li_runs";
DROP POLICY IF EXISTS p_li_doc   ON "public"."li_documents";
DROP POLICY IF EXISTS p_li_qe    ON "public"."li_query_engines";
DROP POLICY IF EXISTS p_li_node  ON "public"."li_nodes";
DROP POLICY IF EXISTS p_li_index ON "public"."li_indexes";

DROP TABLE IF EXISTS "public"."li_runs"           CASCADE;
DROP TABLE IF EXISTS "public"."li_documents"      CASCADE;
DROP TABLE IF EXISTS "public"."li_query_engines"  CASCADE;
DROP TABLE IF EXISTS "public"."li_nodes"          CASCADE;
DROP TABLE IF EXISTS "public"."li_indexes"        CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_li();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "li_001"
        content = f'''"""add llamaindex tables

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
    """TH: สร้างตาราง llamaindex | EN: create tables"""
    op.create_table(
        "li_indexes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("index_type", sa.String(30), nullable=False, server_default="vector_store"),
        sa.Column("embed_model", sa.String(100), nullable=False, server_default="text-embedding-3-small"),
        sa.Column("storage_kind", sa.String(50), nullable=False, server_default="pgvector"),
        sa.Column("config_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_li_index_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "li_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("index_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("node_type", sa.String(20), nullable=False, server_default="text"),
        sa.Column("ordinal", sa.Integer, nullable=False, server_default="0"),
        sa.Column("content", sa.Text, nullable=False, server_default=""),
        sa.Column("token_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("relationships_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("metadata_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "li_query_engines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("index_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("retriever_type", sa.String(30), nullable=False, server_default="vector"),
        sa.Column("top_k", sa.Integer, nullable=False, server_default="5"),
        sa.Column("response_mode", sa.String(30), nullable=False, server_default="compact"),
        sa.Column("similarity_top_k", sa.Integer, nullable=False, server_default="5"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "index_id", "name", name="uq_li_qe_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "li_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("index_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_uri", sa.String(1000), nullable=False, server_default=""),
        sa.Column("mime_type", sa.String(100), nullable=False, server_default=""),
        sa.Column("title", sa.String(500), nullable=False, server_default=""),
        sa.Column("hash", sa.String(128), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("node_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "li_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("index_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_engine_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("query", sa.Text, nullable=False, server_default=""),
        sa.Column("answer", sa.Text, nullable=False, server_default=""),
        sa.Column("source_nodes_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("status", sa.String(20), nullable=False, server_default="QUEUED"),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("tokens_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )

    op.create_index("ix_li_index_tenant", "li_indexes", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_li_node_index_ord", "li_nodes", ["index_id", "ordinal"], schema=SCHEMA)
    op.create_index("ix_li_node_doc", "li_nodes", ["document_id"], schema=SCHEMA)
    op.create_index("ix_li_node_tenant", "li_nodes", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_li_qe_index", "li_query_engines", ["index_id"], schema=SCHEMA)
    op.create_index("ix_li_qe_tenant", "li_query_engines", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_li_doc_index_hash", "li_documents", ["index_id", "hash"], schema=SCHEMA)
    op.create_index("ix_li_doc_tenant", "li_documents", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_li_run_tenant_time", "li_runs", ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_li_run_user_time", "li_runs", ["user_id", "created_at"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_li()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in ("li_indexes", "li_nodes", "li_query_engines",
                "li_documents", "li_runs"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE TRIGGER trg_{{tbl}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_li();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """TH: ลบตาราง | EN: drop tables"""
    for tbl in ("li_runs", "li_documents", "li_query_engines",
                "li_nodes", "li_indexes"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_li();")
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
                {"key": "index_id", "value": "REPLACE_WITH_INDEX_UUID"},
                {"key": "engine_id", "value": "REPLACE_WITH_ENGINE_UUID"},
            ],
            "item": [
                {
                    "name": "List Indexes",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "X-Tenant-Id", "value": "{{tenant_id}}"}],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/indexes",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "indexes"],
                        },
                    },
                },
                {
                    "name": "Create Index",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/indexes",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "indexes"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"docs_vector","index_type":"vector_store","embed_model":"text-embedding-3-small","config":{"collection_id":"00000000-0000-0000-0000-000000000000"}}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Ingest Document",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/indexes/{{{{index_id}}}}/ingest",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "indexes",
                                     "{{index_id}}", "ingest"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"content":"LlamaIndex is a data framework for LLM apps.","source_uri":"doc://intro","chunk_size":512}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Create Query Engine",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/indexes/{{{{index_id}}}}/query-engines",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "indexes",
                                     "{{index_id}}", "query-engines"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"compact_5","retriever_type":"vector","top_k":5,"response_mode":"compact","similarity_top_k":5}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Query Index",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/indexes/{{{{index_id}}}}/query",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "indexes",
                                     "{{index_id}}", "query"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"query":"What is LlamaIndex?","top_k":5,"response_mode":"compact"}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Get Run",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "X-Tenant-Id", "value": "{{tenant_id}}"}],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/runs/REPLACE",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "runs", "REPLACE"],
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
        LIDocumentModel,
        LIIndexModel,
        LINodeModel,
        LIQueryEngineModel,
        LIRunModel,
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
            f"{self.mod_root}/domain/helpers/splitter.py",
            f"{self.mod_root}/domain/helpers/synthesizer.py",
            f"{self.mod_root}/domain/helpers/relationships.py",
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
create_module_llamaindex.py — LlamaIndex Wrapper Module Generator v{VERSION}

USAGE
    python create_module_llamaindex.py <action> [options]

MODULE
    name    : llamaindex
    layer   : 5-Intel
    prefix  : li
    schema  : public
    tables  : li_indexes, li_nodes, li_query_engines, li_documents, li_runs

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
    python create_module_llamaindex.py all
    python create_module_llamaindex.py create --force
    python create_module_llamaindex.py verify
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

    gen = LlamaIndexGenerator(root, force=args.force)

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