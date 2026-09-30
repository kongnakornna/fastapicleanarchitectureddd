#!/usr/bin/env python3
"""
create_module_hybrid_search.py — Hybrid Search Module Generator v1.0.0

สร้าง module hybrid_search ตาม Clean Architecture + DDD + Event-Driven
Module: hybrid_search · Prefix: hs_ · Schema: public
Layer: 5-Intel · Depends: embeddings, vector_db

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
    "name": "hybrid_search",
    "title": "Hybrid Search",
    "layer": "5-Intel",
    "prefix": "hs",
    "tag": "HybridSearch",
    "tag_desc": "Hybrid Search — BM25 + Vector + Fusion (RRF) + Rerank",
    "depends": ["embeddings", "vector_db"],
    "tables": (
        "hs_configs",
        "hs_queries",
        "hs_results",
        "hs_rankings",
        "hs_rerank_logs",
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
class HybridSearchGenerator:
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

        # ─── Value Objects ─────────────────────────────
        self.writer.write(f"{base}/value_objects/__init__.py", dedent('''\
            """hybrid_search value objects"""
            from .hybrid_query import HybridQuery
            from .fusion_config import FusionConfig
            from .search_hit import SearchHit
            from .metrics import MetricScore

            __all__ = ["HybridQuery", "FusionConfig", "SearchHit", "MetricScore"]
        '''))

        self.writer.write(f"{base}/value_objects/hybrid_query.py", dedent('''\
            """HybridQuery VO"""
            from __future__ import annotations
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.hybrid_search.domain.enums import RerankerType


            class HybridQuery(BaseModel):
                """TH: คำค้นแบบ hybrid | EN: Hybrid query"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                text: str = Field(min_length=1, max_length=2000)
                top_k: int = Field(default=10, ge=1, le=500)
                filters: Optional[dict[str, Any]] = None
                reranker_type: RerankerType = RerankerType.NONE
                score_threshold: Optional[float] = None
        '''))

        self.writer.write(f"{base}/value_objects/fusion_config.py", dedent('''\
            """FusionConfig VO"""
            from __future__ import annotations
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.hybrid_search.domain.enums import FusionType


            class FusionConfig(BaseModel):
                """TH: การตั้งค่า fusion | EN: Fusion config"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                fusion_type: FusionType = FusionType.RRF
                rrf_k: int = Field(default=60, ge=1, le=1000)
                bm25_weight: float = Field(default=0.5, ge=0.0, le=1.0)
                vector_weight: float = Field(default=0.5, ge=0.0, le=1.0)
        '''))

        self.writer.write(f"{base}/value_objects/search_hit.py", dedent('''\
            """SearchHit VO"""
            from __future__ import annotations
            import uuid
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field


            class SearchHit(BaseModel):
                """TH: ผลลัพธ์ 1 รายการ | EN: Search hit"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                source_id: str = Field(min_length=1)
                chunk_id: Optional[uuid.UUID] = None
                score: float = 0.0
                rank: int = Field(default=0, ge=0)
                source_kind: str = "hybrid"
                snippet: str = ""
                metadata: Optional[dict[str, Any]] = None
        '''))

        self.writer.write(f"{base}/value_objects/metrics.py", dedent('''\
            """MetricScore VO"""
            from __future__ import annotations
            from pydantic import BaseModel, ConfigDict, Field


            class MetricScore(BaseModel):
                """TH: คะแนนของ metric | EN: Metric score"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                name: str = Field(min_length=1, max_length=50)
                value: float
                k: int = Field(default=0, ge=0)
        '''))

        # ─── Entities (aliases to ORM) ─────────────────
        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """hybrid_search entities — aliases to ORM"""
            from .hs_config import HSConfig
            from .hs_query import HSQuery
            from .hs_result import HSResult
            from .hs_ranking import HSRanking
            from .hs_rerank_log import HSRerankLog

            __all__ = ["HSConfig", "HSQuery", "HSResult", "HSRanking", "HSRerankLog"]
        '''))

        for name, cls, model in (
            ("hs_config", "HSConfig", "HSConfigModel"),
            ("hs_query", "HSQuery", "HSQueryModel"),
            ("hs_result", "HSResult", "HSResultModel"),
            ("hs_ranking", "HSRanking", "HSRankingModel"),
            ("hs_rerank_log", "HSRerankLog", "HSRerankLogModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias to ORM"""
                from __future__ import annotations
                from app.modules.{self.module}.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

        # ─── Helpers ───────────────────────────────────
        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """hybrid_search helpers"""
            from .fusion import rrf_fuse, weighted_sum_fuse, comb_sum_fuse, comb_mnz_fuse
            from .metrics import mrr, ndcg, recall_at_k, precision_at_k
            from .bm25 import bm25_score

            __all__ = [
                "rrf_fuse", "weighted_sum_fuse", "comb_sum_fuse", "comb_mnz_fuse",
                "mrr", "ndcg", "recall_at_k", "precision_at_k",
                "bm25_score",
            ]
        '''))

        self.writer.write(f"{base}/helpers/fusion.py", dedent('''\
            """fusion — RRF, WeightedSum, CombSUM, CombMNZ"""
            from __future__ import annotations
            from typing import Any


            def _ranked(lists: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
                merged: dict[str, dict[str, Any]] = {}
                for src_i, lst in enumerate(lists):
                    for rank, hit in enumerate(lst, start=1):
                        sid = str(hit.get("source_id") or hit.get("id") or "")
                        if not sid:
                            continue
                        entry = merged.setdefault(sid, {
                            "source_id": sid, "doc": hit, "ranks": [], "scores": [],
                        })
                        entry["ranks"].append(rank)
                        entry["scores"].append(float(hit.get("score", 0.0)))
                return list(merged.values())


            def rrf_fuse(
                ranked_lists: list[list[dict[str, Any]]], k: int = 60,
            ) -> list[dict[str, Any]]:
                """TH: Reciprocal Rank Fusion | EN: RRF"""
                if not ranked_lists:
                    return []
                merged = _ranked(ranked_lists)
                out = []
                for entry in merged:
                    score = sum(1.0 / (k + r) for r in entry["ranks"])
                    doc = dict(entry["doc"])
                    doc["score"] = score
                    doc["source_id"] = entry["source_id"]
                    out.append(doc)
                out.sort(key=lambda x: x["score"], reverse=True)
                for i, h in enumerate(out, start=1):
                    h["rank"] = i
                return out


            def weighted_sum_fuse(
                ranked_lists: list[list[dict[str, Any]]], weights: list[float],
            ) -> list[dict[str, Any]]:
                """TH: Weighted Sum Fusion | EN: WeightedSum"""
                if not ranked_lists:
                    return []
                # normalize weights per source
                norm_lists: list[dict[str, float]] = []
                for lst in ranked_lists:
                    if not lst:
                        norm_lists.append({})
                        continue
                    scores = [float(h.get("score", 0.0)) for h in lst]
                    lo, hi = min(scores), max(scores)
                    span = (hi - lo) or 1.0
                    norm_lists.append({
                        str(h.get("source_id") or h.get("id") or ""):
                            (float(h.get("score", 0.0)) - lo) / span
                        for h in lst
                    })

                merged: dict[str, dict[str, Any]] = {}
                for src_i, lst in enumerate(ranked_lists):
                    w = weights[src_i] if src_i < len(weights) else 1.0
                    for h in lst:
                        sid = str(h.get("source_id") or h.get("id") or "")
                        if not sid:
                            continue
                        entry = merged.setdefault(sid, {
                            "source_id": sid, "doc": h, "score": 0.0,
                        })
                        entry["score"] += w * norm_lists[src_i].get(sid, 0.0)
                out = [dict(v["doc"], score=v["score"], source_id=v["source_id"])
                       for v in merged.values()]
                out.sort(key=lambda x: x["score"], reverse=True)
                for i, h in enumerate(out, start=1):
                    h["rank"] = i
                return out


            def comb_sum_fuse(
                ranked_lists: list[list[dict[str, Any]]],
            ) -> list[dict[str, Any]]:
                """TH: CombSUM | EN: CombSUM"""
                merged: dict[str, dict[str, Any]] = {}
                for lst in ranked_lists:
                    for h in lst:
                        sid = str(h.get("source_id") or h.get("id") or "")
                        if not sid:
                            continue
                        entry = merged.setdefault(sid, {
                            "source_id": sid, "doc": h, "score": 0.0,
                        })
                        entry["score"] += float(h.get("score", 0.0))
                out = [dict(v["doc"], score=v["score"], source_id=v["source_id"])
                       for v in merged.values()]
                out.sort(key=lambda x: x["score"], reverse=True)
                for i, h in enumerate(out, start=1):
                    h["rank"] = i
                return out


            def comb_mnz_fuse(
                ranked_lists: list[list[dict[str, Any]]],
            ) -> list[dict[str, Any]]:
                """TH: CombMNZ = CombSUM * |{i: score_i > 0}| | EN: CombMNZ"""
                merged: dict[str, dict[str, Any]] = {}
                for lst in ranked_lists:
                    for h in lst:
                        sid = str(h.get("source_id") or h.get("id") or "")
                        if not sid:
                            continue
                        entry = merged.setdefault(sid, {
                            "source_id": sid, "doc": h, "score": 0.0, "nz": 0,
                        })
                        s = float(h.get("score", 0.0))
                        entry["score"] += s
                        if s > 0:
                            entry["nz"] += 1
                out = [
                    dict(v["doc"], score=v["score"] * v["nz"], source_id=v["source_id"])
                    for v in merged.values()
                ]
                out.sort(key=lambda x: x["score"], reverse=True)
                for i, h in enumerate(out, start=1):
                    h["rank"] = i
                return out
        '''))

        self.writer.write(f"{base}/helpers/metrics.py", dedent('''\
            """metrics — MRR, NDCG, Recall@k, Precision@k"""
            from __future__ import annotations
            import math


            def mrr(ranks: list[int]) -> float:
                """TH: Mean Reciprocal Rank | EN: MRR"""
                valid = [r for r in ranks if r > 0]
                if not valid:
                    return 0.0
                return sum(1.0 / r for r in valid) / len(valid)


            def ndcg(relevances: list[float], k: int = 10) -> float:
                """TH: NDCG@k | EN: NDCG@k"""
                if not relevances:
                    return 0.0
                top = relevances[:k]
                dcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(top))
                ideal = sorted(relevances, reverse=True)[:k]
                idcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(ideal))
                if idcg == 0:
                    return 0.0
                return dcg / idcg


            def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
                """TH: Recall@k | EN: Recall@k"""
                if not relevant:
                    return 0.0
                top = retrieved[:k]
                return sum(1 for x in top if x in relevant) / len(relevant)


            def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
                """TH: Precision@k | EN: Precision@k"""
                if k <= 0:
                    return 0.0
                top = retrieved[:k]
                if not top:
                    return 0.0
                return sum(1 for x in top if x in relevant) / len(top)
        '''))

        self.writer.write(f"{base}/helpers/bm25.py", dedent('''\
            """bm25 — in-memory BM25 (fallback if DB ts_rank ไม่พร้อม)"""
            from __future__ import annotations
            import math
            import re
            from collections import Counter
            from typing import Any

            _TOKEN = re.compile(r"\\w+")


            def _tok(text: str) -> list[str]:
                return _TOKEN.findall((text or "").lower())


            def bm25_score(
                query: str, documents: list[dict[str, Any]],
                *, k1: float = 1.5, b: float = 0.75,
            ) -> list[dict[str, Any]]:
                """TH: คำนวณ BM25 (in-memory) | EN: BM25 (in-memory)"""
                q_terms = _tok(query)
                if not q_terms or not documents:
                    return []

                docs_tokens = [_tok(str(d.get("text", ""))) for d in documents]
                n = len(docs_tokens)
                avgdl = sum(len(t) for t in docs_tokens) / max(1, n)

                df: Counter = Counter()
                for toks in docs_tokens:
                    for t in set(toks):
                        df[t] += 1

                idf = {
                    t: math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                    for t in df
                }

                out: list[dict[str, Any]] = []
                for i, toks in enumerate(docs_tokens):
                    tf = Counter(toks)
                    dl = len(toks)
                    score = 0.0
                    for q in q_terms:
                        if q not in tf:
                            continue
                        f = tf[q]
                        score += idf.get(q, 0.0) * (
                            (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / (avgdl or 1)))
                        )
                    if score > 0:
                        out.append(dict(documents[i], score=score, source_id=
                                        str(documents[i].get("source_id") or i)))
                out.sort(key=lambda x: x["score"], reverse=True)
                for i, h in enumerate(out, start=1):
                    h["rank"] = i
                return out
        '''))

    def _domain_enums(self) -> str:
        return dedent('''\
            """hybrid_search enums"""
            from __future__ import annotations
            from enum import Enum


            class FusionType(str, Enum):
                """TH: ประเภท fusion | EN: Fusion type"""
                RRF = "rrf"
                WEIGHTED_SUM = "weighted_sum"
                COMB_SUM = "comb_sum"
                COMB_MNZ = "comb_mnz"
                BORDA = "borda"
                DBSF = "dbsf"

                def __str__(self) -> str:
                    return str(self.value)


            class SourceKind(str, Enum):
                """TH: แหล่งที่มา | EN: Source kind"""
                BM25 = "bm25"
                VECTOR = "vector"
                HYBRID = "hybrid"
                RERANK = "rerank"

                def __str__(self) -> str:
                    return str(self.value)


            class RerankerType(str, Enum):
                """TH: ประเภท reranker | EN: Reranker type"""
                NONE = "none"
                CROSS_ENCODER = "cross_encoder"
                COHERE = "cohere"
                BGE = "bge"
                COLBERT = "colbert"

                def __str__(self) -> str:
                    return str(self.value)
        ''')

    def _domain_exceptions(self) -> str:
        return dedent('''\
            """hybrid_search domain exceptions"""
            from __future__ import annotations


            class HSError(Exception):
                """TH: base | EN: base"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class ConfigNotFoundError(HSError):
                code = "NOT_FOUND"


            class ConfigConflictError(HSError):
                code = "CONFLICT"


            class QueryNotFoundError(HSError):
                code = "NOT_FOUND"


            class EmptyQueryError(HSError):
                code = "VALIDATION_ERROR"


            class InvalidFusionError(HSError):
                code = "VALIDATION_ERROR"


            class RetrieverError(HSError):
                code = "PROVIDER_ERROR"


            class RerankerError(HSError):
                code = "PROVIDER_ERROR"


            class NoResultsError(HSError):
                code = "NOT_FOUND"
        ''')

    def _domain_events(self) -> str:
        return dedent('''\
            """hybrid_search domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import datetime, timezone


            def _now():
                return datetime.now(timezone.utc)


            @dataclass(frozen=True)
            class ConfigCreated:
                config_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                fusion_type: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class SearchExecuted:
                query_id: uuid.UUID
                tenant_id: uuid.UUID
                query_text: str
                result_count: int
                latency_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class RerankCompleted:
                query_id: uuid.UUID
                tenant_id: uuid.UUID
                reranker_type: str
                input_count: int
                output_count: int
                latency_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class MetricsComputed:
                query_id: uuid.UUID
                tenant_id: uuid.UUID
                mrr: float
                ndcg: float
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
            """hybrid_search application exceptions"""
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


            class RetrieverAppError(AppError):
                code = "PROVIDER_ERROR"
                http_status = 502


            class RateLimitAppError(AppError):
                code = "RATE_LIMITED"
                http_status = 429
        ''')

    def _interfaces_content(self) -> str:
        return dedent('''\
            """hybrid_search application ports"""
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


            class HSConfigRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, c: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
                @abstractmethod
                async def find_all_active(self, ctx: Any) -> list[Any]: ...


            class HSQueryRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, q: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def list_recent(self, ctx: Any, limit: int = 50) -> list[Any]: ...


            class HSResultRepository(ABC):
                @abstractmethod
                async def create_many(self, ctx: Any, results: list[Any]) -> int: ...
                @abstractmethod
                async def find_by_query(self, ctx: Any, query_id: uuid.UUID) -> list[Any]: ...


            class HSRankingRepository(ABC):
                @abstractmethod
                async def create_many(self, ctx: Any, rows: list[Any]) -> int: ...
                @abstractmethod
                async def find_by_query(self, ctx: Any, query_id: uuid.UUID) -> list[Any]: ...


            class HSRerankLogRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, log: Any) -> Any: ...
                @abstractmethod
                async def find_by_query(self, ctx: Any, query_id: uuid.UUID) -> list[Any]: ...


            class EmbeddingPort(Protocol):
                """TH: port ไปยัง embeddings module | EN: embeddings port"""
                async def embed(
                    self, *, model: str, texts: list[str], normalize: bool = True,
                ) -> list[Any]: ...


            class VectorStorePort(Protocol):
                """TH: port ไปยัง vector_db module | EN: vector store port"""
                async def query(
                    self, *, collection_id: uuid.UUID, vector: list[float],
                    top_k: int,
                ) -> list[Any]: ...


            class SparseRetrieverPort(Protocol):
                """TH: port BM25 retriever | EN: sparse retriever port"""
                async def search(
                    self, *, corpus: str, query: str, top_k: int,
                ) -> list[dict[str, Any]]: ...


            class RerankerPort(Protocol):
                """TH: port reranker | EN: reranker port"""
                async def rerank(
                    self, *, query: str, candidates: list[dict[str, Any]],
                    top_k: int,
                ) -> list[dict[str, Any]]: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...
        ''')

    def _mappers_content(self) -> str:
        return dedent('''\
            """hybrid_search mappers — ORM → dict"""
            from __future__ import annotations
            from typing import Any


            def config_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "fusion_type": row.fusion_type,
                    "rrf_k": int(row.rrf_k or 60),
                    "bm25_weight": float(row.bm25_weight or 0.5),
                    "vector_weight": float(row.vector_weight or 0.5),
                    "top_k": int(row.top_k or 10),
                    "reranker_type": row.reranker_type,
                    "is_active": bool(row.is_active),
                }


            def query_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "config_id": str(row.config_id),
                    "query_text": row.query_text or "",
                    "latency_ms": int(row.latency_ms or 0),
                    "result_count": int(row.result_count or 0),
                }


            def result_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "query_id": str(row.query_id),
                    "rank": int(row.rank or 0),
                    "score": float(row.score or 0.0),
                    "source_kind": row.source_kind,
                    "source_id": row.source_id,
                    "snippet": row.snippet or "",
                }


            def ranking_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "query_id": str(row.query_id),
                    "stage": row.stage,
                    "source_kind": row.source_kind,
                    "source_id": row.source_id,
                    "raw_score": float(row.raw_score or 0.0),
                    "normalized_score": float(row.normalized_score or 0.0),
                    "rank": int(row.rank or 0),
                }


            def rerank_log_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "query_id": str(row.query_id),
                    "reranker_type": row.reranker_type,
                    "input_count": int(row.input_count or 0),
                    "output_count": int(row.output_count or 0),
                    "latency_ms": int(row.latency_ms or 0),
                }
        ''')

    def _utils_content(self) -> str:
        return dedent('''\
            """hybrid_search application utils"""
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


            def hit_to_dict(hit: Any) -> dict[str, Any]:
                """TH: แปลง hit → dict | EN: normalize hit"""
                if isinstance(hit, dict):
                    return hit
                return {
                    "source_id": str(getattr(hit, "source_id", "")),
                    "score": float(getattr(hit, "score", 0.0)),
                    "metadata": getattr(hit, "metadata", None) or {},
                    "snippet": getattr(hit, "snippet", "") or "",
                }
        ''')

    def _use_case_content(self) -> str:
        return dedent('''\
            """hybrid_search use cases"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any, Optional

            from app.modules.hybrid_search.application.exceptions import (
                ConflictAppError, NotFoundAppError, RetrieverAppError,
                ValidationAppError,
            )
            from app.modules.hybrid_search.application.utils import (
                hit_to_dict, json_dumps_safe, ms_now,
            )
            from app.modules.hybrid_search.domain.enums import (
                FusionType, SourceKind,
            )
            from app.modules.hybrid_search.domain.events import (
                ConfigCreated, MetricsComputed, RerankCompleted, SearchExecuted,
            )
            from app.modules.hybrid_search.domain.helpers.bm25 import bm25_score
            from app.modules.hybrid_search.domain.helpers.fusion import (
                comb_mnz_fuse, comb_sum_fuse, rrf_fuse, weighted_sum_fuse,
            )
            from app.modules.hybrid_search.domain.helpers.metrics import (
                mrr, ndcg, precision_at_k, recall_at_k,
            )
            from app.modules.hybrid_search.domain.value_objects import (
                FusionConfig, HybridQuery,
            )

            logger = logging.getLogger(__name__)

            _DEFAULT_CORPUS = "default"


            class HybridSearchUseCase:
                """TH: use case หลัก | EN: core use case"""

                def __init__(self, **deps: Any) -> None:
                    for key, value in deps.items():
                        setattr(self, f"_{key}", value)

                # ─── Configs ─────────────────────────────────
                async def create_config(
                    self, ctx: Any, *,
                    name: str,
                    fusion_type: str = "rrf",
                    rrf_k: int = 60,
                    bm25_weight: float = 0.5,
                    vector_weight: float = 0.5,
                    top_k: int = 10,
                    reranker_type: str = "none",
                ) -> Any:
                    """TH: สร้าง config | EN: create config"""
                    from app.modules.hybrid_search.infrastructure.models import (
                        HSConfigModel,
                    )

                    existing = await self._configs.find_by_name(ctx, name)
                    if existing is not None:
                        raise ConflictAppError(f"config exists: {name}")

                    row = HSConfigModel(
                        tenant_id=ctx.tenant_id, name=name,
                        fusion_type=fusion_type, rrf_k=rrf_k,
                        bm25_weight=bm25_weight, vector_weight=vector_weight,
                        top_k=top_k, reranker_type=reranker_type,
                        is_active=True,
                    )
                    saved = await self._configs.save(ctx, row)

                    if self._bus:
                        try:
                            await self._bus.publish(ConfigCreated(
                                config_id=saved.id, tenant_id=ctx.tenant_id,
                                name=saved.name, fusion_type=fusion_type,
                            ))
                        except Exception:
                            pass
                    return saved

                async def list_configs(self, ctx: Any) -> list[Any]:
                    return await self._configs.find_all_active(ctx)

                async def get_config(self, ctx: Any, config_id: uuid.UUID) -> Any:
                    c = await self._configs.find_by_id(ctx, config_id)
                    if c is None:
                        raise NotFoundAppError("config not found")
                    return c

                # ─── Search ──────────────────────────────────
                async def search(
                    self, ctx: Any, *,
                    query: str,
                    config_id: Optional[uuid.UUID] = None,
                    top_k: Optional[int] = None,
                    collection_id: Optional[uuid.UUID] = None,
                    embedding_model: str = "text-embedding-3-small",
                    corpus: Optional[list[dict[str, Any]]] = None,
                ) -> dict[str, Any]:
                    """TH: hybrid search | EN: hybrid search"""
                    if not query or not query.strip():
                        raise ValidationAppError("empty query")

                    config = await self._resolve_config(ctx, config_id)
                    effective_top_k = int(top_k or config.top_k or 10)
                    fusion_type = str(config.fusion_type)
                    reranker_type = str(config.reranker_type)

                    started = ms_now()

                    # 1) Dense retrieval
                    dense_hits: list[dict[str, Any]] = []
                    if self._embedder is not None and self._vector_store is not None \\
                            and collection_id is not None:
                        try:
                            embeddings = await self._embedder.embed(
                                model=embedding_model, texts=[query],
                            )
                            qv = self._extract_vector(embeddings[0] if embeddings else None)
                            if qv:
                                raw = await self._vector_store.query(
                                    collection_id=collection_id, vector=qv,
                                    top_k=effective_top_k * 2,
                                )
                                dense_hits = [hit_to_dict(h) for h in raw]
                        except Exception as exc:
                            logger.warning("dense retrieval failed: %s", exc)

                    # 2) Sparse retrieval
                    sparse_hits: list[dict[str, Any]] = []
                    if corpus:
                        try:
                            if self._sparse is not None:
                                sparse_hits = await self._sparse.search(
                                    corpus=_DEFAULT_CORPUS, query=query,
                                    top_k=effective_top_k * 2,
                                )
                            else:
                                sparse_hits = bm25_score(query, corpus)
                        except Exception as exc:
                            logger.warning("sparse retrieval failed: %s", exc)

                    # 3) Fusion
                    ranked_lists = [sparse_hits, dense_hits]
                    fused = self._fuse(ranked_lists, config)
                    fused = fused[: effective_top_k]

                    # 4) Rerank
                    rerank_input_count = len(fused)
                    if reranker_type != "none" and self._reranker is not None:
                        try:
                            rerank_started = ms_now()
                            fused = await self._reranker.rerank(
                                query=query, candidates=fused,
                                top_k=effective_top_k,
                            )
                            rerank_latency = ms_now() - rerank_started
                            if self._rerank_logs:
                                from app.modules.hybrid_search.infrastructure.models import (
                                    HSRerankLogModel,
                                )
                                # log after we have query_id (below)
                            if self._bus:
                                try:
                                    await self._bus.publish(RerankCompleted(
                                        query_id=uuid.uuid4(),
                                        tenant_id=ctx.tenant_id,
                                        reranker_type=reranker_type,
                                        input_count=rerank_input_count,
                                        output_count=len(fused),
                                        latency_ms=rerank_latency,
                                    ))
                                except Exception:
                                    pass
                        except Exception as exc:
                            logger.warning("reranker failed: %s", exc)

                    latency = ms_now() - started

                    # 5) Persist query + results + rankings
                    from app.modules.hybrid_search.infrastructure.models import (
                        HSQueryModel, HSRankingModel, HSResultModel,
                    )
                    query_row = HSQueryModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id,
                        config_id=config.id,
                        query_text=query,
                        latency_ms=latency,
                        result_count=len(fused),
                    )
                    saved_query = await self._queries.create(ctx, query_row)

                    # persist results
                    if fused:
                        try:
                            result_rows = [
                                HSResultModel(
                                    tenant_id=ctx.tenant_id,
                                    query_id=saved_query.id,
                                    rank=int(h.get("rank", i + 1)),
                                    score=float(h.get("score", 0.0)),
                                    source_kind=str(h.get("source_kind", "hybrid")),
                                    source_id=str(h.get("source_id", "")),
                                    snippet=str(h.get("snippet", ""))[:1000],
                                    metadata_json=json_dumps_safe(
                                        h.get("metadata") or {}
                                    ),
                                )
                                for i, h in enumerate(fused)
                            ]
                            await self._results.create_many(ctx, result_rows)
                        except Exception as exc:
                            logger.debug("persist results failed: %s", exc)

                    # persist rankings (intermediates)
                    if self._rankings:
                        try:
                            rank_rows: list[Any] = []
                            for src_kind, lst in (("bm25", sparse_hits),
                                                   ("vector", dense_hits)):
                                for h in lst:
                                    rank_rows.append(HSRankingModel(
                                        tenant_id=ctx.tenant_id,
                                        query_id=saved_query.id,
                                        stage="retrieve",
                                        source_kind=src_kind,
                                        source_id=str(h.get("source_id", "")),
                                        raw_score=float(h.get("score", 0.0)),
                                        normalized_score=float(h.get("score", 0.0)),
                                        rank=int(h.get("rank", 0)),
                                    ))
                            if rank_rows:
                                await self._rankings.create_many(ctx, rank_rows)
                        except Exception as exc:
                            logger.debug("persist rankings failed: %s", exc)

                    # publish SearchExecuted
                    if self._bus:
                        try:
                            await self._bus.publish(SearchExecuted(
                                query_id=saved_query.id,
                                tenant_id=ctx.tenant_id,
                                query_text=query,
                                result_count=len(fused),
                                latency_ms=latency,
                            ))
                        except Exception:
                            pass

                    # metrics (if relevant set provided)
                    metrics = self._compute_metrics(
                        fused, relevant_set=None, k=effective_top_k,
                    )

                    return {
                        "query_id": str(saved_query.id),
                        "config_id": str(config.id),
                        "fusion_type": fusion_type,
                        "reranker_type": reranker_type,
                        "top_k": effective_top_k,
                        "results": fused,
                        "sparse_count": len(sparse_hits),
                        "dense_count": len(dense_hits),
                        "latency_ms": latency,
                        "metrics": metrics,
                    }

                async def get_query(self, ctx: Any, query_id: uuid.UUID) -> Any:
                    q = await self._queries.find_by_id(ctx, query_id)
                    if q is None:
                        raise NotFoundAppError("query not found")
                    return q

                async def get_query_results(
                    self, ctx: Any, query_id: uuid.UUID,
                ) -> list[Any]:
                    return await self._results.find_by_query(ctx, query_id)

                async def get_query_rankings(
                    self, ctx: Any, query_id: uuid.UUID,
                ) -> list[Any]:
                    return await self._rankings.find_by_query(ctx, query_id)

                async def compute_metrics(
                    self, ctx: Any, *,
                    retrieved_ids: list[str], relevant_ids: list[str],
                    relevances: Optional[list[float]] = None,
                    k: int = 10,
                ) -> dict[str, float]:
                    """TH: คำนวณ MRR/NDCG/Recall/Precision | EN: compute metrics"""
                    relevant = set(relevant_ids)
                    ranks = [
                        i + 1 for i, rid in enumerate(retrieved_ids)
                        if rid in relevant
                    ]
                    rel_list = relevances or [
                        1.0 if rid in relevant else 0.0 for rid in retrieved_ids
                    ]
                    return {
                        "mrr": round(mrr(ranks), 4),
                        "ndcg": round(ndcg(rel_list, k=k), 4),
                        "recall_at_k": round(recall_at_k(retrieved_ids, relevant, k), 4),
                        "precision_at_k": round(
                            precision_at_k(retrieved_ids, relevant, k), 4
                        ),
                    }

                # ─── Internal ────────────────────────────────
                async def _resolve_config(
                    self, ctx: Any, config_id: Optional[uuid.UUID],
                ) -> Any:
                    if config_id is not None:
                        return await self.get_config(ctx, config_id)

                    existing = await self._configs.find_all_active(ctx)
                    if existing:
                        return existing[0]

                    return await self.create_config(
                        ctx, name="default", fusion_type="rrf", rrf_k=60,
                        bm25_weight=0.5, vector_weight=0.5, top_k=10,
                        reranker_type="none",
                    )

                def _fuse(
                    self, ranked_lists: list[list[dict[str, Any]]], config: Any,
                ) -> list[dict[str, Any]]:
                    fusion_type = str(config.fusion_type)
                    weights = [
                        float(config.bm25_weight or 0.5),
                        float(config.vector_weight or 0.5),
                    ]
                    k = int(config.rrf_k or 60)

                    if fusion_type == "rrf":
                        return rrf_fuse(ranked_lists, k=k)
                    if fusion_type == "weighted_sum":
                        return weighted_sum_fuse(ranked_lists, weights=weights)
                    if fusion_type == "comb_sum":
                        return comb_sum_fuse(ranked_lists)
                    if fusion_type == "comb_mnz":
                        return comb_mnz_fuse(ranked_lists)
                    # fallback
                    return rrf_fuse(ranked_lists, k=k)

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

                def _compute_metrics(
                    self, hits: list[dict[str, Any]],
                    relevant_set: Optional[set[str]], k: int,
                ) -> dict[str, float]:
                    if not relevant_set:
                        return {}
                    retrieved = [str(h.get("source_id", "")) for h in hits]
                    return {
                        "mrr": round(mrr([
                            i + 1 for i, rid in enumerate(retrieved)
                            if rid in relevant_set
                        ]), 4),
                        "recall_at_k": round(
                            recall_at_k(retrieved, relevant_set, k), 4
                        ),
                        "precision_at_k": round(
                            precision_at_k(retrieved, relevant_set, k), 4
                        ),
                    }
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
            """hybrid_search SQLAlchemy models — schema=public, prefix=hs_"""
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


            class HSConfigModel(Base):
                __tablename__ = "hs_configs"
                __table_args__ = (
                    CheckConstraint(
                        "fusion_type IN ('rrf','weighted_sum','comb_sum','comb_mnz','borda','dbsf')",
                        name="ck_hs_config_fusion",
                    ),
                    CheckConstraint(
                        "reranker_type IN ('none','cross_encoder','cohere','bge','colbert')",
                        name="ck_hs_config_reranker",
                    ),
                    UniqueConstraint("tenant_id", "name", name="uq_hs_config_name"),
                    Index("ix_hs_cfg_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                fusion_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="rrf")
                rrf_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="60")
                bm25_weight: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.5")
                vector_weight: Mapped[float] = mapped_column(Float, nullable=False, server_default="0.5")
                top_k: Mapped[int] = mapped_column(Integer, nullable=False, server_default="10")
                reranker_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="none")
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class HSQueryModel(Base):
                __tablename__ = "hs_queries"
                __table_args__ = (
                    Index("ix_hs_q_tenant_time", "tenant_id", "created_at"),
                    Index("ix_hs_q_config", "config_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                config_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                query_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                result_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class HSResultModel(Base):
                __tablename__ = "hs_results"
                __table_args__ = (
                    Index("ix_hs_res_query_rank", "query_id", "rank"),
                    Index("ix_hs_res_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                rank: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                score: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
                source_kind: Mapped[str] = mapped_column(String(20), nullable=False, server_default="hybrid")
                source_id: Mapped[str] = mapped_column(String(200), nullable=False, server_default="")
                snippet: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class HSRankingModel(Base):
                __tablename__ = "hs_rankings"
                __table_args__ = (
                    Index("ix_hs_rank_query_stage", "query_id", "stage"),
                    Index("ix_hs_rank_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                stage: Mapped[str] = mapped_column(String(30), nullable=False, server_default="retrieve")
                source_kind: Mapped[str] = mapped_column(String(20), nullable=False, server_default="hybrid")
                source_id: Mapped[str] = mapped_column(String(200), nullable=False, server_default="")
                raw_score: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
                normalized_score: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
                rank: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class HSRerankLogModel(Base):
                __tablename__ = "hs_rerank_logs"
                __table_args__ = (
                    Index("ix_hs_rr_query", "query_id"),
                    Index("ix_hs_rr_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                reranker_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="none")
                input_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                output_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            __all__ = [
                "Base", "HSConfigModel", "HSQueryModel", "HSResultModel",
                "HSRankingModel", "HSRerankLogModel",
            ]
        ''')

    def _repositories_content(self) -> str:
        return dedent('''\
            """hybrid_search repositories"""
            from __future__ import annotations
            import logging
            import uuid

            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.hybrid_search.application.exceptions import AppError
            from app.modules.hybrid_search.infrastructure.models import (
                HSConfigModel, HSQueryModel, HSRankingModel, HSRerankLogModel,
                HSResultModel,
            )

            logger = logging.getLogger(__name__)


            class HSConfigRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, c: HSConfigModel) -> HSConfigModel:
                    try:
                        self._session.add(c)
                        await self._session.flush()
                        return c
                    except SQLAlchemyError as exc:
                        logger.exception("config.save failed")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> HSConfigModel | None:
                    r = await self._session.execute(
                        select(HSConfigModel).where(HSConfigModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def find_by_name(self, ctx: object, name: str) -> HSConfigModel | None:
                    r = await self._session.execute(
                        select(HSConfigModel).where(HSConfigModel.name == name)
                    )
                    return r.scalar_one_or_none()

                async def find_all_active(self, ctx: object) -> list[HSConfigModel]:
                    r = await self._session.execute(
                        select(HSConfigModel)
                        .where(HSConfigModel.is_active.is_(True))
                        .order_by(HSConfigModel.name)
                    )
                    return list(r.scalars().all())


            class HSQueryRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, q: HSQueryModel) -> HSQueryModel:
                    self._session.add(q)
                    await self._session.flush()
                    return q

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> HSQueryModel | None:
                    r = await self._session.execute(
                        select(HSQueryModel).where(HSQueryModel.id == id)
                    )
                    return r.scalar_one_or_none()

                async def list_recent(self, ctx: object, limit: int = 50) -> list[HSQueryModel]:
                    r = await self._session.execute(
                        select(HSQueryModel)
                        .order_by(HSQueryModel.created_at.desc())
                        .limit(max(1, min(limit, 500)))
                    )
                    return list(r.scalars().all())


            class HSResultRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create_many(self, ctx: object, results: list) -> int:
                    for r in results:
                        self._session.add(r)
                    await self._session.flush()
                    return len(results)

                async def find_by_query(
                    self, ctx: object, query_id: uuid.UUID,
                ) -> list[HSResultModel]:
                    r = await self._session.execute(
                        select(HSResultModel)
                        .where(HSResultModel.query_id == query_id)
                        .order_by(HSResultModel.rank)
                    )
                    return list(r.scalars().all())


            class HSRankingRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create_many(self, ctx: object, rows: list) -> int:
                    for r in rows:
                        self._session.add(r)
                    await self._session.flush()
                    return len(rows)

                async def find_by_query(
                    self, ctx: object, query_id: uuid.UUID,
                ) -> list[HSRankingModel]:
                    r = await self._session.execute(
                        select(HSRankingModel)
                        .where(HSRankingModel.query_id == query_id)
                        .order_by(HSRankingModel.stage, HSRankingModel.rank)
                    )
                    return list(r.scalars().all())


            class HSRerankLogRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(self, ctx: object, log: HSRerankLogModel) -> HSRerankLogModel:
                    self._session.add(log)
                    await self._session.flush()
                    return log

                async def find_by_query(
                    self, ctx: object, query_id: uuid.UUID,
                ) -> list[HSRerankLogModel]:
                    r = await self._session.execute(
                        select(HSRerankLogModel).where(HSRerankLogModel.query_id == query_id)
                    )
                    return list(r.scalars().all())
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """hybrid_search services — adapters + reranker + bus"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any

            from app.modules.hybrid_search.application.interfaces import (
                EventBus, RerankerPort,
            )

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

                async def query(
                    self, *, collection_id: uuid.UUID, vector: list[float],
                    top_k: int,
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
                        logger.warning("vector adapter failed: %s", exc)
                        return []


            class ScoreBasedReranker(RerankerPort):
                """TH: reranker ด้วย score | EN: score-based reranker"""

                async def rerank(
                    self, *, query: str, candidates: list[dict[str, Any]],
                    top_k: int,
                ) -> list[dict[str, Any]]:
                    ordered = sorted(
                        candidates,
                        key=lambda c: float(c.get("score", 0.0)),
                        reverse=True,
                    )[:top_k]
                    for i, h in enumerate(ordered, start=1):
                        h["rank"] = i
                    return ordered


            class NoopReranker(RerankerPort):
                async def rerank(
                    self, *, query: str, candidates: list[dict[str, Any]],
                    top_k: int,
                ) -> list[dict[str, Any]]:
                    return candidates[:top_k]


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
            """hybrid_search Pydantic schemas"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.hybrid_search.domain.enums import (
                FusionType, RerankerType,
            )


            class ConfigCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(min_length=1, max_length=100)
                fusion_type: FusionType = FusionType.RRF
                rrf_k: int = Field(default=60, ge=1, le=1000)
                bm25_weight: float = Field(default=0.5, ge=0.0, le=1.0)
                vector_weight: float = Field(default=0.5, ge=0.0, le=1.0)
                top_k: int = Field(default=10, ge=1, le=500)
                reranker_type: RerankerType = RerankerType.NONE


            class ConfigOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                fusion_type: str
                rrf_k: int
                bm25_weight: float
                vector_weight: float
                top_k: int
                reranker_type: str
                is_active: bool


            class SearchRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                query: str = Field(min_length=1, max_length=2000)
                config_id: Optional[uuid.UUID] = None
                top_k: Optional[int] = Field(default=None, ge=1, le=500)
                collection_id: Optional[uuid.UUID] = None
                embedding_model: str = "text-embedding-3-small"
                corpus: Optional[list[dict[str, Any]]] = None


            class SearchHitOut(BaseModel):
                source_id: str
                chunk_id: Optional[uuid.UUID] = None
                score: float
                rank: int
                source_kind: str
                snippet: str = ""
                metadata: Optional[dict[str, Any]] = None


            class SearchResponse(BaseModel):
                query_id: uuid.UUID
                config_id: uuid.UUID
                fusion_type: str
                reranker_type: str
                top_k: int
                results: list[SearchHitOut] = []
                sparse_count: int = 0
                dense_count: int = 0
                latency_ms: int = 0
                metrics: dict[str, float] = Field(default_factory=dict)


            class QueryOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                config_id: uuid.UUID
                query_text: str
                latency_ms: int
                result_count: int
                created_at: datetime


            class RankingOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                stage: str
                source_kind: str
                source_id: str
                raw_score: float
                normalized_score: float
                rank: int


            class MetricsRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                retrieved_ids: list[str] = Field(default_factory=list)
                relevant_ids: list[str] = Field(default_factory=list)
                relevances: list[float] = Field(default_factory=list)
                k: int = Field(default=10, ge=1, le=200)


            class MetricsResponse(BaseModel):
                mrr: float = 0.0
                ndcg: float = 0.0
                recall_at_k: float = 0.0
                precision_at_k: float = 0.0
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """hybrid_search DI container"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass
            from typing import Annotated, Optional

            from fastapi import Depends, Header, HTTPException, Request, status
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.hybrid_search.application.use_case import (
                HybridSearchUseCase,
            )
            from app.modules.hybrid_search.infrastructure.repositories import (
                HSConfigRepository, HSQueryRepository, HSRankingRepository,
                HSRerankLogRepository, HSResultRepository,
            )
            from app.modules.hybrid_search.infrastructure.services import (
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
            ) -> HybridSearchUseCase:
                embedder = getattr(request.app.state, "hs_embedder", None)
                vector_store = getattr(request.app.state, "hs_vector_store", None)
                sparse = getattr(request.app.state, "hs_sparse", None)
                reranker = getattr(request.app.state, "hs_reranker", None)
                bus = getattr(request.app.state, "hs_event_bus", None) \\
                    or LoggingEventBus()

                return HybridSearchUseCase(
                    configs=HSConfigRepository(db),
                    queries=HSQueryRepository(db),
                    results=HSResultRepository(db),
                    rankings=HSRankingRepository(db),
                    rerank_logs=HSRerankLogRepository(db),
                    embedder=embedder,
                    vector_store=vector_store,
                    sparse=sparse,
                    reranker=reranker,
                    bus=bus,
                )
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """hybrid_search HTTP router"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException

            from app.modules.hybrid_search.application.exceptions import AppError
            from app.modules.hybrid_search.application.use_case import (
                HybridSearchUseCase,
            )
            from app.modules.hybrid_search.domain.exceptions import HSError
            from app.modules.hybrid_search.presentation.dependencies import (
                Ctx, get_ctx, get_use_case,
            )
            from app.modules.hybrid_search.presentation.schemas import (
                ConfigCreateRequest, ConfigOut, MetricsRequest, MetricsResponse,
                QueryOut, RankingOut, SearchHitOut, SearchRequest, SearchResponse,
            )

            logger = logging.getLogger(__name__)

            router = APIRouter(prefix="/hs", tags=["HybridSearch"])


            def _raise(exc: Exception) -> None:
                if isinstance(exc, HSError):
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


            @router.get("/configs", response_model=list[ConfigOut])
            async def list_configs(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
            ) -> list[ConfigOut]:
                """TH: list configs | EN: list configs"""
                try:
                    items = await uc.list_configs(ctx)
                    return [ConfigOut.model_validate(c.model_dump()) for c in items]
                except (HSError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/configs", response_model=ConfigOut, status_code=201)
            async def create_config(
                req: ConfigCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
            ) -> ConfigOut:
                """TH: สร้าง config | EN: create config"""
                try:
                    c = await uc.create_config(
                        ctx, name=req.name,
                        fusion_type=str(req.fusion_type),
                        rrf_k=req.rrf_k,
                        bm25_weight=req.bm25_weight,
                        vector_weight=req.vector_weight,
                        top_k=req.top_k,
                        reranker_type=str(req.reranker_type),
                    )
                    return ConfigOut.model_validate(c.model_dump())
                except (HSError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/search", response_model=SearchResponse)
            async def search(
                req: SearchRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
            ) -> SearchResponse:
                """TH: hybrid search | EN: hybrid search"""
                try:
                    out = await uc.search(
                        ctx, query=req.query,
                        config_id=req.config_id,
                        top_k=req.top_k,
                        collection_id=req.collection_id,
                        embedding_model=req.embedding_model,
                        corpus=req.corpus,
                    )
                    return SearchResponse(
                        query_id=out["query_id"],
                        config_id=out["config_id"],
                        fusion_type=out["fusion_type"],
                        reranker_type=out["reranker_type"],
                        top_k=out["top_k"],
                        results=[
                            SearchHitOut(**{k: v for k, v in h.items()
                                            if k in SearchHitOut.model_fields})
                            for h in out.get("results", [])
                        ],
                        sparse_count=out.get("sparse_count", 0),
                        dense_count=out.get("dense_count", 0),
                        latency_ms=out.get("latency_ms", 0),
                        metrics=out.get("metrics", {}) or {},
                    )
                except (HSError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/queries/{query_id}", response_model=QueryOut)
            async def get_query(
                query_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
            ) -> QueryOut:
                """TH: ดึง query | EN: get query"""
                try:
                    q = await uc.get_query(ctx, query_id)
                    return QueryOut.model_validate(q.model_dump())
                except (HSError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/queries/{query_id}/ranking", response_model=list[RankingOut])
            async def get_ranking(
                query_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
            ) -> list[RankingOut]:
                """TH: ดึง ranking intermediates | EN: get ranking"""
                try:
                    rows = await uc.get_query_rankings(ctx, query_id)
                    return [RankingOut.model_validate(r.model_dump()) for r in rows]
                except (HSError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/metrics", response_model=MetricsResponse)
            async def compute_metrics(
                req: MetricsRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[HybridSearchUseCase, Depends(get_use_case)],
            ) -> MetricsResponse:
                """TH: คำนวณ metrics | EN: compute metrics"""
                try:
                    out = await uc.compute_metrics(
                        ctx, retrieved_ids=req.retrieved_ids,
                        relevant_ids=req.relevant_ids,
                        relevances=req.relevances or None,
                        k=req.k,
                    )
                    return MetricsResponse(**out)
                except (HSError, AppError) as exc:
                    _raise(exc)
                    raise
        ''')

    def _swagger_content(self) -> str:
        return dedent(f'''\
            """hybrid_search OpenAPI docs"""
            from __future__ import annotations
            from typing import Any


            def register_hybrid_search_openapi(app: object) -> None:
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
                                "โมดูล hybrid_search — BM25 + Vector + Fusion\\n\\n"
                                "• Fusion: RRF, WeightedSum, CombSUM, CombMNZ\\n"
                                "• Rerank: cross_encoder, cohere, bge\\n"
                                "• Metrics: MRR, NDCG, Recall@k, Precision@k"
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
-- V001__create_hybrid_search.sql | Module: hybrid_search | Prefix: hs
-- Schema: public | Tables: hs_configs, hs_queries, hs_results,
--                          hs_rankings, hs_rerank_logs
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."hs_configs";
CREATE TABLE "public"."hs_configs" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "name"           varchar(100) NOT NULL,
  "fusion_type"    varchar(20) NOT NULL DEFAULT 'rrf',
  "rrf_k"          int4 NOT NULL DEFAULT 60,
  "bm25_weight"    float8 NOT NULL DEFAULT 0.5,
  "vector_weight"  float8 NOT NULL DEFAULT 0.5,
  "top_k"          int4 NOT NULL DEFAULT 10,
  "reranker_type"  varchar(20) NOT NULL DEFAULT 'none',
  "is_active"      bool NOT NULL DEFAULT true,
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "hs_configs_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_hs_config_name" UNIQUE ("tenant_id", "name"),
  CONSTRAINT "ck_hs_config_fusion" CHECK (
    fusion_type IN ('rrf','weighted_sum','comb_sum','comb_mnz','borda','dbsf')
  ),
  CONSTRAINT "ck_hs_config_reranker" CHECK (
    reranker_type IN ('none','cross_encoder','cohere','bge','colbert')
  )
);
CREATE INDEX "ix_hs_cfg_tenant" ON "public"."hs_configs" ("tenant_id");

DROP TABLE IF EXISTS "public"."hs_queries";
CREATE TABLE "public"."hs_queries" (
  "id"            uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"     uuid NOT NULL,
  "user_id"       uuid NOT NULL,
  "config_id"     uuid NOT NULL,
  "query_text"    text NOT NULL DEFAULT '',
  "latency_ms"    int4 NOT NULL DEFAULT 0,
  "result_count"  int4 NOT NULL DEFAULT 0,
  "created_at"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"    timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "hs_queries_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_hs_q_tenant_time" ON "public"."hs_queries" ("tenant_id", "created_at" DESC);
CREATE INDEX "ix_hs_q_config"      ON "public"."hs_queries" ("config_id");

DROP TABLE IF EXISTS "public"."hs_results";
CREATE TABLE "public"."hs_results" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "query_id"       uuid NOT NULL,
  "rank"           int4 NOT NULL DEFAULT 0,
  "score"          float8 NOT NULL DEFAULT 0,
  "source_kind"    varchar(20) NOT NULL DEFAULT 'hybrid',
  "source_id"      varchar(200) NOT NULL DEFAULT '',
  "snippet"        text NOT NULL DEFAULT '',
  "metadata_json"  text NOT NULL DEFAULT '{}',
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "hs_results_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_hs_res_query_rank" ON "public"."hs_results" ("query_id", "rank");
CREATE INDEX "ix_hs_res_tenant"     ON "public"."hs_results" ("tenant_id");

DROP TABLE IF EXISTS "public"."hs_rankings";
CREATE TABLE "public"."hs_rankings" (
  "id"                uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"         uuid NOT NULL,
  "query_id"          uuid NOT NULL,
  "stage"             varchar(30) NOT NULL DEFAULT 'retrieve',
  "source_kind"       varchar(20) NOT NULL DEFAULT 'hybrid',
  "source_id"         varchar(200) NOT NULL DEFAULT '',
  "raw_score"         float8 NOT NULL DEFAULT 0,
  "normalized_score"  float8 NOT NULL DEFAULT 0,
  "rank"              int4 NOT NULL DEFAULT 0,
  "created_at"        timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"        timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "hs_rankings_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_hs_rank_query_stage" ON "public"."hs_rankings" ("query_id", "stage");
CREATE INDEX "ix_hs_rank_tenant"      ON "public"."hs_rankings" ("tenant_id");

DROP TABLE IF EXISTS "public"."hs_rerank_logs";
CREATE TABLE "public"."hs_rerank_logs" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "query_id"       uuid NOT NULL,
  "reranker_type"  varchar(20) NOT NULL DEFAULT 'none',
  "input_count"    int4 NOT NULL DEFAULT 0,
  "output_count"   int4 NOT NULL DEFAULT 0,
  "latency_ms"     int4 NOT NULL DEFAULT 0,
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "hs_rerank_logs_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_hs_rr_query"  ON "public"."hs_rerank_logs" ("query_id");
CREATE INDEX "ix_hs_rr_tenant" ON "public"."hs_rerank_logs" ("tenant_id");

CREATE OR REPLACE FUNCTION public.set_updated_at_hs()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_hs_cfg_updated ON "public"."hs_configs";
CREATE TRIGGER trg_hs_cfg_updated BEFORE UPDATE ON "public"."hs_configs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_hs();

DROP TRIGGER IF EXISTS trg_hs_q_updated ON "public"."hs_queries";
CREATE TRIGGER trg_hs_q_updated BEFORE UPDATE ON "public"."hs_queries"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_hs();

DROP TRIGGER IF EXISTS trg_hs_res_updated ON "public"."hs_results";
CREATE TRIGGER trg_hs_res_updated BEFORE UPDATE ON "public"."hs_results"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_hs();

DROP TRIGGER IF EXISTS trg_hs_rank_updated ON "public"."hs_rankings";
CREATE TRIGGER trg_hs_rank_updated BEFORE UPDATE ON "public"."hs_rankings"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_hs();

DROP TRIGGER IF EXISTS trg_hs_rr_updated ON "public"."hs_rerank_logs";
CREATE TRIGGER trg_hs_rr_updated BEFORE UPDATE ON "public"."hs_rerank_logs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_hs();

ALTER TABLE "public"."hs_configs"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."hs_queries"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."hs_results"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."hs_rankings"     ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."hs_rerank_logs"  ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_hs_cfg  ON "public"."hs_configs";
CREATE POLICY p_hs_cfg ON "public"."hs_configs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_hs_q    ON "public"."hs_queries";
CREATE POLICY p_hs_q ON "public"."hs_queries"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_hs_res  ON "public"."hs_results";
CREATE POLICY p_hs_res ON "public"."hs_results"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_hs_rank ON "public"."hs_rankings";
CREATE POLICY p_hs_rank ON "public"."hs_rankings"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_hs_rr   ON "public"."hs_rerank_logs";
CREATE POLICY p_hs_rr ON "public"."hs_rerank_logs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_hybrid_search.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."hs_configs"
    (tenant_id, name, fusion_type, rrf_k, bm25_weight, vector_weight,
     top_k, reranker_type)
VALUES
    ('00000000-0000-0000-0000-000000000001', 'default',
     'rrf', 60, 0.5, 0.5, 10, 'none'),
    ('00000000-0000-0000-0000-000000000001', 'balanced_weighted',
     'weighted_sum', 60, 0.5, 0.5, 10, 'none'),
    ('00000000-0000-0000-0000-000000000001', 'quality',
     'rrf', 60, 0.4, 0.6, 20, 'cross_encoder')
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_hybrid_search.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_hs_rr_updated    ON "public"."hs_rerank_logs";
DROP TRIGGER IF EXISTS trg_hs_rank_updated  ON "public"."hs_rankings";
DROP TRIGGER IF EXISTS trg_hs_res_updated   ON "public"."hs_results";
DROP TRIGGER IF EXISTS trg_hs_q_updated     ON "public"."hs_queries";
DROP TRIGGER IF EXISTS trg_hs_cfg_updated   ON "public"."hs_configs";

DROP POLICY IF EXISTS p_hs_rr   ON "public"."hs_rerank_logs";
DROP POLICY IF EXISTS p_hs_rank ON "public"."hs_rankings";
DROP POLICY IF EXISTS p_hs_res  ON "public"."hs_results";
DROP POLICY IF EXISTS p_hs_q    ON "public"."hs_queries";
DROP POLICY IF EXISTS p_hs_cfg  ON "public"."hs_configs";

DROP TABLE IF EXISTS "public"."hs_rerank_logs" CASCADE;
DROP TABLE IF EXISTS "public"."hs_rankings"    CASCADE;
DROP TABLE IF EXISTS "public"."hs_results"     CASCADE;
DROP TABLE IF EXISTS "public"."hs_queries"     CASCADE;
DROP TABLE IF EXISTS "public"."hs_configs"     CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_hs();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "hs_001"
        content = f'''"""add hybrid_search tables

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
    """TH: สร้างตาราง hybrid_search | EN: create tables"""
    op.create_table(
        "hs_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("fusion_type", sa.String(20), nullable=False, server_default="rrf"),
        sa.Column("rrf_k", sa.Integer, nullable=False, server_default="60"),
        sa.Column("bm25_weight", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("vector_weight", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("top_k", sa.Integer, nullable=False, server_default="10"),
        sa.Column("reranker_type", sa.String(20), nullable=False, server_default="none"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_hs_config_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "hs_queries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("config_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_text", sa.Text, nullable=False, server_default=""),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("result_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "hs_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rank", sa.Integer, nullable=False, server_default="0"),
        sa.Column("score", sa.Float, nullable=False, server_default="0"),
        sa.Column("source_kind", sa.String(20), nullable=False, server_default="hybrid"),
        sa.Column("source_id", sa.String(200), nullable=False, server_default=""),
        sa.Column("snippet", sa.Text, nullable=False, server_default=""),
        sa.Column("metadata_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "hs_rankings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage", sa.String(30), nullable=False, server_default="retrieve"),
        sa.Column("source_kind", sa.String(20), nullable=False, server_default="hybrid"),
        sa.Column("source_id", sa.String(200), nullable=False, server_default=""),
        sa.Column("raw_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("normalized_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("rank", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "hs_rerank_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reranker_type", sa.String(20), nullable=False, server_default="none"),
        sa.Column("input_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("output_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )

    op.create_index("ix_hs_cfg_tenant", "hs_configs", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_hs_q_tenant_time", "hs_queries", ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_hs_q_config", "hs_queries", ["config_id"], schema=SCHEMA)
    op.create_index("ix_hs_res_query_rank", "hs_results", ["query_id", "rank"], schema=SCHEMA)
    op.create_index("ix_hs_res_tenant", "hs_results", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_hs_rank_query_stage", "hs_rankings", ["query_id", "stage"], schema=SCHEMA)
    op.create_index("ix_hs_rank_tenant", "hs_rankings", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_hs_rr_query", "hs_rerank_logs", ["query_id"], schema=SCHEMA)
    op.create_index("ix_hs_rr_tenant", "hs_rerank_logs", ["tenant_id"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_hs()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in ("hs_configs", "hs_queries", "hs_results",
                "hs_rankings", "hs_rerank_logs"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE TRIGGER trg_{{tbl}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_hs();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """TH: ลบตาราง | EN: drop tables"""
    for tbl in ("hs_rerank_logs", "hs_rankings", "hs_results",
                "hs_queries", "hs_configs"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_hs();")
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
                {"key": "config_id", "value": "REPLACE_WITH_CONFIG_UUID"},
            ],
            "item": [
                {
                    "name": "List Configs",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "X-Tenant-Id", "value": "{{tenant_id}}"}],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/configs",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "configs"],
                        },
                    },
                },
                {
                    "name": "Create Config (RRF)",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/configs",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "configs"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"balanced","fusion_type":"rrf","rrf_k":60,"bm25_weight":0.5,"vector_weight":0.5,"top_k":10,"reranker_type":"none"}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Search (with corpus)",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/search",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "search"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"query":"what is BM25","config_id":"{{config_id}}","top_k":5,"corpus":[{"source_id":"d1","text":"BM25 is a ranking function"},{"source_id":"d2","text":"Vector search uses embeddings"}]}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Get Query Ranking",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "X-Tenant-Id", "value": "{{tenant_id}}"}],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/queries/REPLACE/ranking",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "queries", "REPLACE", "ranking"],
                        },
                    },
                },
                {
                    "name": "Compute Metrics",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/metrics",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "metrics"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"retrieved_ids":["d1","d3","d2"],"relevant_ids":["d1","d2"],"k":3}',
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
        HSConfigModel,
        HSQueryModel,
        HSRankingModel,
        HSRerankLogModel,
        HSResultModel,
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
            f"{self.mod_root}/domain/helpers/fusion.py",
            f"{self.mod_root}/domain/helpers/metrics.py",
            f"{self.mod_root}/domain/helpers/bm25.py",
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
create_module_hybrid_search.py — Hybrid Search Module Generator v{VERSION}

USAGE
    python create_module_hybrid_search.py <action> [options]

MODULE
    name    : hybrid_search
    layer   : 5-Intel
    prefix  : hs
    schema  : public
    tables  : hs_configs, hs_queries, hs_results, hs_rankings, hs_rerank_logs

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
    python create_module_hybrid_search.py all
    python create_module_hybrid_search.py create --force
    python create_module_hybrid_search.py verify
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

    gen = HybridSearchGenerator(root, force=args.force)

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