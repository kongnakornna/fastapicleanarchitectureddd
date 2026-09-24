#!/usr/bin/env python3
"""
create_module_ai_evaluation.py — AI Evaluation Module Generator v1.0.0

สร้าง module ai_evaluation ตาม Clean Architecture + DDD + Event-Driven
Module: ai_evaluation · Prefix: eval_ · Schema: public
Layer: 5-Intel · Depends: llm, rag

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
    "name": "ai_evaluation",
    "title": "AI Evaluation",
    "layer": "5-Intel",
    "prefix": "eval",
    "tag": "AIEvaluation",
    "tag_desc": "AI Evaluation — RAGAS, faithfulness, MRR, NDCG, hallucination",
    "depends": ["llm", "rag"],
    "tables": (
        "eval_datasets",
        "eval_test_cases",
        "eval_runs",
        "eval_metrics",
        "eval_results",
        "eval_reports",
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

        self.writer.write(f"{base}/value_objects/__init__.py", dedent(f'''\
            """{self.module} value objects"""
            from .metric_score import MetricScore
            from .eval_config import EvalConfig
            from .eval_target import EvalTarget

            __all__ = ["MetricScore", "EvalConfig", "EvalTarget"]
        '''))

        self.writer.write(f"{base}/value_objects/metric_score.py", dedent('''\
            """MetricScore VO"""
            from __future__ import annotations
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field


            class MetricScore(BaseModel):
                """TH: คะแนน 1 metric | EN: Single metric score"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                name: str = Field(min_length=1, max_length=50)
                value: float
                confidence: float = Field(default=1.0, ge=0.0, le=1.0)
                higher_is_better: bool = True
                details: Optional[dict[str, Any]] = None
        '''))

        self.writer.write(f"{base}/value_objects/eval_config.py", dedent('''\
            """EvalConfig VO"""
            from __future__ import annotations
            from typing import Optional
            from pydantic import BaseModel, ConfigDict, Field


            class EvalConfig(BaseModel):
                """TH: การตั้งค่าการประเมิน | EN: Evaluation config"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                metrics: list[str] = Field(
                    default_factory=lambda: ["faithfulness", "answer_relevance"],
                )
                sample_size: int = Field(default=0, ge=0)
                temperature: float = Field(default=0.0, ge=0.0, le=2.0)
                seed: Optional[int] = None
                concurrency: int = Field(default=4, ge=1, le=32)
                timeout_seconds: int = Field(default=120, ge=10, le=3600)
        '''))

        self.writer.write(f"{base}/value_objects/eval_target.py", dedent('''\
            """EvalTarget VO"""
            from __future__ import annotations
            from typing import Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.ai_evaluation.domain.enums import TargetKind


            class EvalTarget(BaseModel):
                """TH: เป้าหมายการประเมิน | EN: Evaluation target"""
                model_config = ConfigDict(frozen=True, extra="forbid")

                kind: TargetKind = TargetKind.MODEL
                ref: str = Field(min_length=1, max_length=200)
                pipeline_id: Optional[str] = None
        '''))

        self.writer.write(f"{base}/entities/__init__.py", dedent(f'''\
            """{self.module} entities"""
            from .dataset import EvalDataset
            from .test_case import EvalTestCase
            from .run import EvalRun
            from .metric import EvalMetric
            from .result import EvalResult
            from .report import EvalReport

            __all__ = [
                "EvalDataset", "EvalTestCase", "EvalRun",
                "EvalMetric", "EvalResult", "EvalReport",
            ]
        '''))

        for name, cls, model in (
            ("dataset", "EvalDataset", "EvalDatasetModel"),
            ("test_case", "EvalTestCase", "EvalTestCaseModel"),
            ("run", "EvalRun", "EvalRunModel"),
            ("metric", "EvalMetric", "EvalMetricModel"),
            ("result", "EvalResult", "EvalResultModel"),
            ("report", "EvalReport", "EvalReportModel"),
        ):
            self.writer.write(f"{base}/entities/{name}.py", dedent(f'''\
                """{cls} entity — alias to ORM"""
                from __future__ import annotations
                from app.modules.{self.module}.infrastructure.models import {model}


                class {cls}({model}):
                    """TH: {cls} | EN: {cls} entity (alias)"""
            '''))

        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """ai_evaluation helpers"""
            from .metrics import (
                exact_match, f1_score, rouge_l, mrr, ndcg,
                precision_at_k, recall_at_k, ragas_score, pass_threshold,
            )

            __all__ = [
                "exact_match", "f1_score", "rouge_l", "mrr", "ndcg",
                "precision_at_k", "recall_at_k", "ragas_score", "pass_threshold",
            ]
        '''))

        self.writer.write(f"{base}/helpers/metrics.py", self._helper_metrics())

    def _domain_enums(self) -> str:
        return dedent('''\
            """ai_evaluation enums"""
            from __future__ import annotations
            from enum import Enum


            class MetricKind(str, Enum):
                """TH: ประเภท metric | EN: Metric kind"""
                EXACT_MATCH = "exact_match"
                F1 = "f1"
                ROUGE = "rouge"
                BLEU = "bleu"
                BERTSCORE = "bertscore"
                FAITHFULNESS = "faithfulness"
                ANSWER_RELEVANCE = "answer_relevance"
                CONTEXT_PRECISION = "context_precision"
                CONTEXT_RECALL = "context_recall"
                MRR = "mrr"
                NDCG = "ndcg"
                RAGAS = "ragas"
                HALLUCINATION = "hallucination"
                LATENCY = "latency"
                COST = "cost"

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


            class TaskType(str, Enum):
                """TH: ประเภทงาน | EN: Task type"""
                QA = "qa"
                SUMMARIZATION = "summarization"
                CLASSIFICATION = "classification"
                RAG = "rag"
                AGENT = "agent"

                def __str__(self) -> str:
                    return str(self.value)


            class TargetKind(str, Enum):
                """TH: เป้าหมาย | EN: Target kind"""
                MODEL = "model"
                PIPELINE = "pipeline"

                def __str__(self) -> str:
                    return str(self.value)
        ''')

    def _domain_exceptions(self) -> str:
        return dedent('''\
            """ai_evaluation domain exceptions"""
            from __future__ import annotations


            class EvalError(Exception):
                """TH: base | EN: base"""
                code: str = "DOMAIN_ERROR"

                def __init__(self, message: str = "", *, code: str | None = None) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class DatasetNotFoundError(EvalError):
                code = "NOT_FOUND"


            class CaseNotFoundError(EvalError):
                code = "NOT_FOUND"


            class RunNotFoundError(EvalError):
                code = "NOT_FOUND"


            class ReportNotFoundError(EvalError):
                code = "NOT_FOUND"


            class MetricNotFoundError(EvalError):
                code = "NOT_FOUND"


            class DatasetConflictError(EvalError):
                code = "CONFLICT"


            class EvaluatorError(EvalError):
                code = "PROVIDER_ERROR"


            class InsufficientDataError(EvalError):
                code = "VALIDATION_ERROR"
        ''')

    def _domain_events(self) -> str:
        return dedent('''\
            """ai_evaluation domain events"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import datetime, timezone


            def _now():
                return datetime.now(timezone.utc)


            @dataclass(frozen=True)
            class DatasetCreated:
                dataset_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                task_type: str
                case_count: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class EvalRunStarted:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                dataset_id: uuid.UUID
                target_model: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class EvalRunCompleted:
                run_id: uuid.UUID
                tenant_id: uuid.UUID
                status: str
                metrics_json: str
                duration_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class MetricComputed:
                run_id: uuid.UUID
                case_id: uuid.UUID
                metric_name: str
                score: float
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True)
            class HallucinationDetected:
                run_id: uuid.UUID
                case_id: uuid.UUID
                severity: str
                occurred_at: datetime = field(default_factory=_now)
        ''')

    def _helper_metrics(self) -> str:
        return dedent('''\
            """metric helpers"""
            from __future__ import annotations
            import math
            import re
            from collections import Counter


            def _tokenize(text: str) -> list[str]:
                return re.findall(r"\\w+", (text or "").lower())


            def exact_match(pred: str, ref: str) -> float:
                return 1.0 if (pred or "").strip().lower() == (ref or "").strip().lower() else 0.0


            def f1_score(pred: str, ref: str) -> float:
                p = _tokenize(pred)
                r = _tokenize(ref)
                if not p or not r:
                    return 0.0
                common = Counter(p) & Counter(r)
                overlap = sum(common.values())
                if overlap == 0:
                    return 0.0
                precision = overlap / len(p)
                recall = overlap / len(r)
                return 2 * precision * recall / (precision + recall)


            def _lcs(a: list[str], b: list[str]) -> int:
                if not a or not b:
                    return 0
                dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
                for i in range(1, len(a) + 1):
                    for j in range(1, len(b) + 1):
                        if a[i - 1] == b[j - 1]:
                            dp[i][j] = dp[i - 1][j - 1] + 1
                        else:
                            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
                return dp[-1][-1]


            def rouge_l(pred: str, ref: str) -> float:
                p = _tokenize(pred)
                r = _tokenize(ref)
                if not p or not r:
                    return 0.0
                lcs = _lcs(p, r)
                if lcs == 0:
                    return 0.0
                precision = lcs / len(p)
                recall = lcs / len(r)
                return 2 * precision * recall / (precision + recall)


            def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
                if k <= 0:
                    return 0.0
                top = retrieved[:k]
                if not top:
                    return 0.0
                return sum(1 for x in top if x in relevant) / len(top)


            def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
                if not relevant:
                    return 0.0
                top = retrieved[:k]
                return sum(1 for x in top if x in relevant) / len(relevant)


            def mrr(ranks: list[int]) -> float:
                if not ranks:
                    return 0.0
                return sum(1.0 / r for r in ranks if r > 0) / len(ranks)


            def ndcg(relevances: list[float], k: int = 10) -> float:
                if not relevances:
                    return 0.0
                top = relevances[:k]
                dcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(top))
                ideal = sorted(relevances, reverse=True)[:k]
                idcg = sum((2 ** r - 1) / math.log2(i + 2) for i, r in enumerate(ideal))
                if idcg == 0:
                    return 0.0
                return dcg / idcg


            def ragas_score(
                faithfulness: float, answer_relevance: float,
                context_precision: float, context_recall: float,
            ) -> float:
                vals = [faithfulness, answer_relevance, context_precision, context_recall]
                if any(v <= 0 for v in vals):
                    return 0.0
                return 4 / sum(1.0 / v for v in vals)


            def pass_threshold(score: float, threshold: float) -> bool:
                return score >= threshold
        ''')

    # ─── APPLICATION LAYER ────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent(f'''\
            """{self.module} application layer"""
        '''))

        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """ai_evaluation application exceptions"""
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


            class EvaluatorAppError(AppError):
                code = "PROVIDER_ERROR"
                http_status = 502


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
            """ai_evaluation application ports"""
            from __future__ import annotations
            import uuid
            from abc import ABC, abstractmethod
            from typing import Any, Optional, Protocol, runtime_checkable

            from app.modules.ai_evaluation.domain.entities import (
                EvalDataset, EvalMetric, EvalReport, EvalResult, EvalRun,
                EvalTestCase,
            )
            from app.modules.ai_evaluation.domain.value_objects import (
                EvalTarget, MetricScore,
            )


            @runtime_checkable
            class RequestContext(Protocol):
                @property
                def tenant_id(self) -> uuid.UUID: ...
                @property
                def user_id(self) -> Optional[uuid.UUID]: ...


            class EvalDatasetRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, d: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
                @abstractmethod
                async def find_all(self, ctx: Any) -> list[Any]: ...


            class EvalTestCaseRepository(ABC):
                @abstractmethod
                async def create_many(self, ctx: Any, cases: list[Any]) -> int: ...
                @abstractmethod
                async def find_by_dataset(self, ctx: Any, dataset_id: uuid.UUID) -> list[Any]: ...
                @abstractmethod
                async def count_by_dataset(self, ctx: Any, dataset_id: uuid.UUID) -> int: ...


            class EvalRunRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, r: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> Any | None: ...
                @abstractmethod
                async def update(self, ctx: Any, r: Any) -> Any: ...
                @abstractmethod
                async def list_by_tenant(self, ctx: Any, limit: int = 50) -> list[Any]: ...


            class EvalMetricRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, m: Any) -> Any: ...
                @abstractmethod
                async def find_by_name(self, ctx: Any, name: str) -> Any | None: ...
                @abstractmethod
                async def find_all(self, ctx: Any) -> list[Any]: ...


            class EvalResultRepository(ABC):
                @abstractmethod
                async def create_many(self, ctx: Any, results: list[Any]) -> int: ...
                @abstractmethod
                async def find_by_run(self, ctx: Any, run_id: uuid.UUID) -> list[Any]: ...


            class EvalReportRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, r: Any) -> Any: ...
                @abstractmethod
                async def find_by_run(self, ctx: Any, run_id: uuid.UUID) -> Any | None: ...


            class MetricEvaluator(Protocol):
                """TH: port ของ metric evaluator | EN: metric evaluator port"""
                name: str

                async def evaluate(
                    self, *, case: Any, answer: str,
                    context: Optional[list[str]] = None,
                ) -> MetricScore: ...


            class LLMJudgePort(Protocol):
                """TH: port LLM-as-judge | EN: LLM judge port"""
                async def judge(
                    self, *, model: str, prompt: str, context: str = "",
                ) -> dict[str, Any]: ...


            class TargetInvokerPort(Protocol):
                """TH: port target invoker | EN: target invoker port"""
                async def invoke(
                    self, *, target: EvalTarget, question: str,
                    context: Optional[list[str]] = None,
                ) -> dict[str, Any]: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...
        ''')

    def _mappers_content(self) -> str:
        return dedent('''\
            """ai_evaluation mappers — ORM → dict"""
            from __future__ import annotations
            from typing import Any


            def dataset_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "name": row.name,
                    "description": row.description or "",
                    "task_type": row.task_type,
                    "case_count": row.case_count or 0,
                }


            def case_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "dataset_id": str(row.dataset_id),
                    "question": row.question or "",
                    "ground_truth": row.ground_truth or "",
                }


            def run_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id),
                    "dataset_id": str(row.dataset_id),
                    "target_kind": row.target_kind,
                    "target_model": row.target_model or "",
                    "status": row.status,
                    "case_count": row.case_count or 0,
                    "completed_count": row.completed_count or 0,
                    "failed_count": row.failed_count or 0,
                    "duration_ms": row.duration_ms or 0,
                    "total_cost_usd": str(row.total_cost_usd or "0"),
                }


            def metric_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "name": row.name,
                    "kind": row.kind,
                    "higher_is_better": bool(row.higher_is_better),
                    "range_min": float(row.range_min or 0.0),
                    "range_max": float(row.range_max or 1.0),
                    "description": row.description or "",
                }


            def result_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "run_id": str(row.run_id),
                    "case_id": str(row.case_id),
                    "metric_name": row.metric_name,
                    "score": float(row.score or 0.0),
                    "confidence": float(row.confidence or 1.0),
                }


            def report_to_dict(row: Any) -> dict[str, Any]:
                return {
                    "id": str(row.id), "run_id": str(row.run_id),
                    "summary_json": row.summary_json or "{}",
                    "passed": bool(row.passed),
                }
        ''')

    def _utils_content(self) -> str:
        return dedent('''\
            """ai_evaluation application utils"""
            from __future__ import annotations
            import json
            import random
            import time
            from typing import Any, Optional


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


            def sample_cases(
                cases: list, sample_size: int, seed: Optional[int] = None,
            ) -> list:
                if sample_size <= 0 or sample_size >= len(cases):
                    return cases
                rng = random.Random(seed)
                return rng.sample(cases, sample_size)


            def ms_now() -> int:
                return int(time.time() * 1000)


            def aggregate_scores(
                results: list[dict[str, Any]],
            ) -> dict[str, dict[str, float]]:
                buckets: dict[str, list[float]] = {}
                for r in results:
                    name = r.get("metric_name", "")
                    if not name:
                        continue
                    buckets.setdefault(name, []).append(float(r.get("score", 0.0)))

                summary: dict[str, dict[str, float]] = {}
                for name, scores in buckets.items():
                    if not scores:
                        continue
                    summary[name] = {
                        "mean": round(sum(scores) / len(scores), 4),
                        "min": round(min(scores), 4),
                        "max": round(max(scores), 4),
                        "count": float(len(scores)),
                    }
                return summary
        ''')

    def _use_case_content(self) -> str:
        return dedent('''\
            """ai_evaluation use cases"""
            from __future__ import annotations
            import asyncio
            import logging
            import uuid
            from decimal import Decimal
            from typing import Any, Optional

            from app.modules.ai_evaluation.application.exceptions import (
                ConflictAppError, NotFoundAppError, ValidationAppError,
            )
            from app.modules.ai_evaluation.application.utils import (
                aggregate_scores, json_dumps_safe, json_loads_safe, ms_now,
                sample_cases,
            )
            from app.modules.ai_evaluation.domain.events import (
                DatasetCreated, EvalRunCompleted, EvalRunStarted,
            )
            from app.modules.ai_evaluation.domain.value_objects import (
                EvalConfig, EvalTarget,
            )

            logger = logging.getLogger(__name__)

            _DEFAULT_PASS_THRESHOLD = 0.7


            class AIEvaluationUseCase:
                """TH: use case หลัก | EN: core use case"""

                def __init__(self, **deps: Any) -> None:
                    for key, value in deps.items():
                        setattr(self, f"_{key}", value)
                    self._pass_threshold = _DEFAULT_PASS_THRESHOLD

                async def create_dataset(
                    self, ctx: Any, *,
                    name: str, description: str = "",
                    task_type: str = "qa",
                    cases: Optional[list[dict[str, Any]]] = None,
                    metadata: Optional[dict[str, Any]] = None,
                ) -> Any:
                    """TH: สร้าง dataset | EN: create dataset"""
                    from app.modules.ai_evaluation.infrastructure.models import (
                        EvalDatasetModel, EvalTestCaseModel,
                    )

                    existing = await self._datasets.find_by_name(ctx, name)
                    if existing is not None:
                        raise ConflictAppError(f"dataset exists: {name}")

                    ds = EvalDatasetModel(
                        tenant_id=ctx.tenant_id, name=name,
                        description=description, task_type=task_type,
                        metadata_json=json_dumps_safe(metadata or {}),
                    )
                    saved = await self._datasets.save(ctx, ds)

                    if cases:
                        rows = [
                            EvalTestCaseModel(
                                tenant_id=ctx.tenant_id, dataset_id=saved.id,
                                question=c.get("question", ""),
                                ground_truth=c.get("ground_truth", ""),
                                context_json=json_dumps_safe(c.get("context") or []),
                            )
                            for c in cases
                        ]
                        count = await self._cases.create_many(ctx, rows)
                        saved.case_count = count
                        saved = await self._datasets.save(ctx, saved)

                    if self._bus:
                        try:
                            await self._bus.publish(DatasetCreated(
                                dataset_id=saved.id, tenant_id=ctx.tenant_id,
                                name=saved.name, task_type=task_type,
                                case_count=saved.case_count or 0,
                            ))
                        except Exception as exc:
                            logger.debug("publish failed: %s", exc)
                    return saved

                async def list_datasets(self, ctx: Any) -> list[Any]:
                    return await self._datasets.find_all(ctx)

                async def get_dataset(self, ctx: Any, dataset_id: uuid.UUID) -> Any:
                    ds = await self._datasets.find_by_id(ctx, dataset_id)
                    if ds is None:
                        raise NotFoundAppError("dataset not found")
                    return ds

                async def run_evaluation(
                    self, ctx: Any, *,
                    dataset_id: uuid.UUID,
                    target: EvalTarget,
                    config: Optional[EvalConfig] = None,
                ) -> Any:
                    """TH: รันการประเมิน | EN: run evaluation"""
                    from app.modules.ai_evaluation.infrastructure.models import (
                        EvalResultModel, EvalRunModel, EvalReportModel,
                    )

                    cfg = config or EvalConfig()
                    ds = await self.get_dataset(ctx, dataset_id)
                    cases = await self._cases.find_by_dataset(ctx, dataset_id)
                    if not cases:
                        raise ValidationAppError("dataset has no cases")

                    selected = sample_cases(cases, cfg.sample_size, cfg.seed)

                    run = EvalRunModel(
                        tenant_id=ctx.tenant_id,
                        user_id=ctx.user_id or ctx.tenant_id,
                        dataset_id=ds.id,
                        target_kind=str(target.kind),
                        target_model=target.ref,
                        target_pipeline=target.pipeline_id or "",
                        config_json=json_dumps_safe(cfg.model_dump()),
                        case_count=len(selected),
                        status="QUEUED",
                    )
                    saved_run = await self._runs.save(ctx, run)

                    if self._bus:
                        try:
                            await self._bus.publish(EvalRunStarted(
                                run_id=saved_run.id, tenant_id=ctx.tenant_id,
                                dataset_id=dataset_id, target_model=target.ref,
                            ))
                        except Exception:
                            pass

                    saved_run.status = "RUNNING"
                    saved_run.started_at = datetime.now(UTC)
                    saved_run = await self._runs.update(ctx, saved_run)

                    started = ms_now()
                    all_results: list[Any] = []
                    completed = 0
                    failed = 0
                    total_cost = Decimal("0")

                    for case in selected:
                        try:
                            results = await self._evaluate_case(
                                ctx, saved_run, case, target, cfg,
                            )
                            for r in results:
                                all_results.append(r)
                                total_cost += r.cost_usd
                            completed += 1
                        except Exception as exc:
                            logger.warning("case failed: %s", exc)
                            failed += 1

                    if all_results:
                        await self._results.create_many(ctx, all_results)

                    saved_run.status = "DONE"
                    saved_run.completed_count = completed
                    saved_run.failed_count = failed
                    saved_run.total_cost_usd = total_cost
                    saved_run.finished_at = datetime.now(UTC)
                    saved_run.duration_ms = ms_now() - started
                    saved_run = await self._runs.update(ctx, saved_run)

                    summary = aggregate_scores([
                        {"metric_name": r.metric_name, "score": r.score}
                        for r in all_results
                    ])
                    passed = self._evaluate_pass(summary)

                    report = EvalReportModel(
                        tenant_id=ctx.tenant_id, run_id=saved_run.id,
                        summary_json=json_dumps_safe(summary),
                        passed=passed,
                    )
                    await self._reports.save(ctx, report)

                    if self._bus:
                        try:
                            await self._bus.publish(EvalRunCompleted(
                                run_id=saved_run.id, tenant_id=ctx.tenant_id,
                                status="DONE",
                                metrics_json=json_dumps_safe(summary),
                                duration_ms=saved_run.duration_ms or 0,
                            ))
                        except Exception:
                            pass
                    return saved_run

                async def get_run(self, ctx: Any, run_id: uuid.UUID) -> Any:
                    r = await self._runs.find_by_id(ctx, run_id)
                    if r is None:
                        raise NotFoundAppError("run not found")
                    return r

                async def get_report(self, ctx: Any, run_id: uuid.UUID) -> Any:
                    r = await self._reports.find_by_run(ctx, run_id)
                    if r is None:
                        raise NotFoundAppError("report not found")
                    return r

                async def list_metrics(self, ctx: Any) -> list[Any]:
                    return await self._metrics.find_all(ctx)

                async def _evaluate_case(
                    self, ctx: Any, run: Any, case: Any,
                    target: EvalTarget, cfg: EvalConfig,
                ) -> list[Any]:
                    from app.modules.ai_evaluation.infrastructure.models import (
                        EvalResultModel,
                    )

                    context = json_loads_safe(case.context_json, [])
                    answer = ""
                    tokens = 0
                    cost = Decimal("0")
                    latency = 0

                    if self._target is not None:
                        st = ms_now()
                        try:
                            out = await self._target.invoke(
                                target=target, question=case.question,
                                context=context,
                            )
                            answer = out.get("answer", "")
                            tokens = int(out.get("total_tokens", 0))
                            cost = Decimal(str(out.get("cost_usd", "0")))
                        except Exception as exc:
                            logger.warning("target invoke failed: %s", exc)
                        latency = ms_now() - st

                    results: list[Any] = []
                    for metric_name in cfg.metrics:
                        evaluator = self._evaluators.get(metric_name)
                        if evaluator is None:
                            continue
                        try:
                            score = await evaluator.evaluate(
                                case=case, answer=answer, context=context,
                            )
                        except Exception as exc:
                            logger.warning("metric %s failed: %s", metric_name, exc)
                            continue

                        results.append(EvalResultModel(
                            tenant_id=ctx.tenant_id, run_id=run.id,
                            case_id=case.id, metric_name=metric_name,
                            score=score.value,
                            confidence=score.confidence,
                            details_json=json_dumps_safe(score.details or {}),
                            answer_text=answer[:2000],
                            latency_ms=latency, tokens_used=tokens,
                            cost_usd=cost,
                        ))
                    return results

                def _evaluate_pass(self, summary: dict[str, dict[str, float]]) -> bool:
                    if not summary:
                        return False
                    means = [v.get("mean", 0.0) for v in summary.values()]
                    if not means:
                        return False
                    return (sum(means) / len(means)) >= self._pass_threshold
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
            """ai_evaluation SQLAlchemy models — schema=public, prefix=eval_"""
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


            class EvalDatasetModel(Base):
                __tablename__ = "eval_datasets"
                __table_args__ = (
                    CheckConstraint(
                        "task_type IN ('qa','summarization','classification','rag','agent')",
                        name="ck_eval_dataset_task",
                    ),
                    UniqueConstraint("tenant_id", "name", name="uq_eval_dataset_name"),
                    Index("ix_eval_ds_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                name: Mapped[str] = mapped_column(String(100), nullable=False)
                description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                task_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default="qa")
                version: Mapped[str] = mapped_column(String(20), nullable=False, server_default="1.0.0")
                case_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class EvalTestCaseModel(Base):
                __tablename__ = "eval_test_cases"
                __table_args__ = (
                    Index("ix_eval_case_dataset", "dataset_id"),
                    Index("ix_eval_case_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                question: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                ground_truth: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                context_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="[]")
                metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class EvalRunModel(Base):
                __tablename__ = "eval_runs"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('QUEUED','RUNNING','DONE','FAILED','CANCELLED')",
                        name="ck_eval_run_status",
                    ),
                    CheckConstraint(
                        "target_kind IN ('model','pipeline')",
                        name="ck_eval_run_target_kind",
                    ),
                    Index("ix_eval_run_tenant_time", "tenant_id", "created_at"),
                    Index("ix_eval_run_status", "status"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                target_kind: Mapped[str] = mapped_column(String(20), nullable=False, server_default="model")
                target_model: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
                target_pipeline: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")
                config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="QUEUED")
                case_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                completed_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                failed_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                started_at: Mapped[Optional[datetime]] = mapped_column(
                    DateTime(timezone=True), nullable=True,
                )
                finished_at: Mapped[Optional[datetime]] = mapped_column(
                    DateTime(timezone=True), nullable=True,
                )
                duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                total_cost_usd: Mapped[Decimal] = mapped_column(
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


            class EvalMetricModel(Base):
                __tablename__ = "eval_metrics"
                __table_args__ = (
                    UniqueConstraint("name", name="uq_eval_metric_name"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                name: Mapped[str] = mapped_column(String(50), nullable=False)
                kind: Mapped[str] = mapped_column(String(30), nullable=False)
                higher_is_better: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("true"),
                )
                range_min: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
                range_max: Mapped[float] = mapped_column(Float, nullable=False, server_default="1")
                description: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class EvalResultModel(Base):
                __tablename__ = "eval_results"
                __table_args__ = (
                    Index("ix_eval_res_run_metric", "run_id", "metric_name"),
                    Index("ix_eval_res_case", "case_id"),
                    Index("ix_eval_res_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                metric_name: Mapped[str] = mapped_column(String(50), nullable=False)
                score: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
                confidence: Mapped[float] = mapped_column(Float, nullable=False, server_default="1")
                details_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                answer_text: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
                latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
                cost_usd: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            class EvalReportModel(Base):
                __tablename__ = "eval_reports"
                __table_args__ = (
                    UniqueConstraint("run_id", name="uq_eval_report_run"),
                    Index("ix_eval_rep_tenant", "tenant_id"),
                    {{"schema": SCHEMA}},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
                summary_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{{}}")
                passed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
                generated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now(),
                )


            __all__ = [
                "Base", "EvalDatasetModel", "EvalTestCaseModel", "EvalRunModel",
                "EvalMetricModel", "EvalResultModel", "EvalReportModel",
            ]
        ''')

    def _repositories_content(self) -> str:
        return dedent('''\
            """ai_evaluation repositories — SQLAlchemy 2.0 async"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.ai_evaluation.application.exceptions import AppError
            from app.modules.ai_evaluation.infrastructure.models import (
                EvalDatasetModel, EvalMetricModel, EvalReportModel,
                EvalResultModel, EvalRunModel, EvalTestCaseModel,
            )


            class EvalDatasetRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, ds: EvalDatasetModel) -> EvalDatasetModel:
                    try:
                        self._session.add(ds)
                        await self._session.flush()
                        return ds
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> EvalDatasetModel | None:
                    try:
                        result = await self._session.execute(
                            select(EvalDatasetModel).where(EvalDatasetModel.id == id)
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_name(self, ctx: object, name: str) -> EvalDatasetModel | None:
                    try:
                        result = await self._session.execute(
                            select(EvalDatasetModel).where(EvalDatasetModel.name == name)
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.find_by_name failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_all(self, ctx: object) -> list[EvalDatasetModel]:
                    try:
                        result = await self._session.execute(
                            select(EvalDatasetModel).order_by(EvalDatasetModel.name)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.list failed: {exc}")
                        raise AppError(str(exc)) from exc


            class EvalTestCaseRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create_many(self, ctx: object, cases: list) -> int:
                    try:
                        for c in cases:
                            self._session.add(c)
                        await self._session.flush()
                        return len(cases)
                    except SQLAlchemyError as exc:
                        logger.error(f"case.create_many failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_dataset(self, ctx: object, dataset_id: uuid.UUID) -> list:
                    try:
                        result = await self._session.execute(
                            select(EvalTestCaseModel).where(
                                EvalTestCaseModel.dataset_id == dataset_id
                            )
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"case.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def count_by_dataset(self, ctx: object, dataset_id: uuid.UUID) -> int:
                    try:
                        result = await self._session.execute(
                            select(func.count()).select_from(EvalTestCaseModel).where(
                                EvalTestCaseModel.dataset_id == dataset_id
                            )
                        )
                        return int(result.scalar() or 0)
                    except SQLAlchemyError as exc:
                        logger.error(f"case.count failed: {exc}")
                        raise AppError(str(exc)) from exc


            class EvalRunRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, r: EvalRunModel) -> EvalRunModel:
                    try:
                        self._session.add(r)
                        await self._session.flush()
                        return r
                    except SQLAlchemyError as exc:
                        logger.error(f"run.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_id(self, ctx: object, id: uuid.UUID) -> EvalRunModel | None:
                    try:
                        result = await self._session.execute(
                            select(EvalRunModel).where(EvalRunModel.id == id)
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"run.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def update(self, ctx: object, r: EvalRunModel) -> EvalRunModel:
                    try:
                        await self._session.flush()
                        return r
                    except SQLAlchemyError as exc:
                        logger.error(f"run.update failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def list_by_tenant(self, ctx: object, limit: int = 50) -> list:
                    try:
                        result = await self._session.execute(
                            select(EvalRunModel)
                            .order_by(EvalRunModel.created_at.desc())
                            .limit(limit)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"run.list failed: {exc}")
                        raise AppError(str(exc)) from exc


            class EvalMetricRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, m: EvalMetricModel) -> EvalMetricModel:
                    try:
                        self._session.add(m)
                        await self._session.flush()
                        return m
                    except SQLAlchemyError as exc:
                        logger.error(f"metric.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_name(self, ctx: object, name: str) -> EvalMetricModel | None:
                    try:
                        result = await self._session.execute(
                            select(EvalMetricModel).where(EvalMetricModel.name == name)
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"metric.find failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_all(self, ctx: object) -> list[EvalMetricModel]:
                    try:
                        result = await self._session.execute(
                            select(EvalMetricModel).order_by(EvalMetricModel.name)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"metric.list failed: {exc}")
                        raise AppError(str(exc)) from exc


            class EvalResultRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create_many(self, ctx: object, results: list) -> int:
                    try:
                        for r in results:
                            self._session.add(r)
                        await self._session.flush()
                        return len(results)
                    except SQLAlchemyError as exc:
                        logger.error(f"result.create_many failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_run(self, ctx: object, run_id: uuid.UUID) -> list:
                    try:
                        result = await self._session.execute(
                            select(EvalResultModel).where(EvalResultModel.run_id == run_id)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"result.find failed: {exc}")
                        raise AppError(str(exc)) from exc


            class EvalReportRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def save(self, ctx: object, r: EvalReportModel) -> EvalReportModel:
                    try:
                        self._session.add(r)
                        await self._session.flush()
                        return r
                    except SQLAlchemyError as exc:
                        logger.error(f"report.save failed: {exc}")
                        raise AppError(str(exc)) from exc

                async def find_by_run(self, ctx: object, run_id: uuid.UUID) -> EvalReportModel | None:
                    try:
                        result = await self._session.execute(
                            select(EvalReportModel).where(EvalReportModel.run_id == run_id)
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"report.find failed: {exc}")
                        raise AppError(str(exc)) from exc
        ''')

    def _services_content(self) -> str:
        return dedent('''\
            """ai_evaluation services — evaluators · judge · event bus"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Any, Optional

            from app.modules.ai_evaluation.domain.helpers.metrics import (
                exact_match, f1_score, mrr, ndcg, precision_at_k, ragas_score,
                recall_at_k, rouge_l,
            )
            from app.modules.ai_evaluation.domain.value_objects import MetricScore

            logger = logging.getLogger(__name__)


            class ExactMatchEvaluator:
                name = "exact_match"
                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    return MetricScore(name=self.name, value=exact_match(answer, case.ground_truth))


            class F1Evaluator:
                name = "f1"
                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    return MetricScore(name=self.name, value=f1_score(answer, case.ground_truth))


            class RougeEvaluator:
                name = "rouge"
                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    return MetricScore(name=self.name, value=rouge_l(answer, case.ground_truth))


            class MRREvaluator:
                name = "mrr"
                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    rank = 1 if answer and case.ground_truth and answer.strip() == case.ground_truth.strip() else 0
                    return MetricScore(name=self.name, value=mrr([rank]) if rank > 0 else 0.0)


            class NDCGEvaluator:
                name = "ndcg"
                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    rel = 1.0 if answer and case.ground_truth else 0.0
                    return MetricScore(name=self.name, value=ndcg([rel], k=10))


            class ContextPrecisionEvaluator:
                name = "context_precision"
                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    if not context:
                        return MetricScore(name=self.name, value=0.0)
                    retrieved = [str(i) for i in range(len(context))]
                    relevant = {
                        str(i) for i, c in enumerate(context)
                        if case.ground_truth and case.ground_truth.lower() in c.lower()
                    }
                    return MetricScore(
                        name=self.name,
                        value=precision_at_k(retrieved, relevant, len(retrieved)),
                    )


            class ContextRecallEvaluator:
                name = "context_recall"
                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    if not context:
                        return MetricScore(name=self.name, value=0.0)
                    retrieved = [str(i) for i in range(len(context))]
                    relevant = {
                        str(i) for i, c in enumerate(context)
                        if case.ground_truth and case.ground_truth.lower() in c.lower()
                    }
                    return MetricScore(
                        name=self.name,
                        value=recall_at_k(retrieved, relevant, len(retrieved)),
                    )


            class FaithfulnessEvaluator:
                name = "faithfulness"
                def __init__(self, judge: Any = None) -> None:
                    self._judge = judge

                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    if not context or not answer or self._judge is None:
                        return MetricScore(name=self.name, value=0.0, confidence=0.5)
                    ctx_text = "\\n".join(context)
                    prompt = (
                        "Rate 0.0-1.0 how faithful the answer is to context. "
                        "Reply with ONLY the number.\\n\\n"
                        f"Context:\\n{ctx_text}\\n\\nAnswer:\\n{answer}"
                    )
                    try:
                        out = await self._judge.judge(model="gpt-4o-mini", prompt=prompt)
                        score = float(out.get("score", 0.0) or 0.0)
                        return MetricScore(
                            name=self.name,
                            value=max(0.0, min(1.0, score)),
                            confidence=0.8,
                        )
                    except Exception as exc:
                        logger.debug("faithfulness judge failed: %s", exc)
                        return MetricScore(name=self.name, value=0.0, confidence=0.3)


            class AnswerRelevanceEvaluator:
                name = "answer_relevance"
                def __init__(self, judge: Any = None) -> None:
                    self._judge = judge

                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    if not answer or self._judge is None:
                        return MetricScore(name=self.name, value=0.0, confidence=0.5)
                    prompt = (
                        "Rate 0.0-1.0 how relevant the answer is to the question. "
                        "Reply with ONLY the number.\\n\\n"
                        f"Question:\\n{case.question}\\n\\nAnswer:\\n{answer}"
                    )
                    try:
                        out = await self._judge.judge(model="gpt-4o-mini", prompt=prompt)
                        score = float(out.get("score", 0.0) or 0.0)
                        return MetricScore(
                            name=self.name,
                            value=max(0.0, min(1.0, score)),
                            confidence=0.8,
                        )
                    except Exception as exc:
                        logger.debug("relevance judge failed: %s", exc)
                        return MetricScore(name=self.name, value=0.0, confidence=0.3)


            class HallucinationEvaluator:
                name = "hallucination"
                def __init__(self, judge: Any = None) -> None:
                    self._judge = judge

                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    if not context or not answer or self._judge is None:
                        return MetricScore(name=self.name, value=0.0, confidence=0.5)
                    ctx_text = "\\n".join(context)
                    prompt = (
                        "Rate 0.0-1.0 how much the answer is hallucinated. "
                        "Reply with ONLY the number.\\n\\n"
                        f"Context:\\n{ctx_text}\\n\\nAnswer:\\n{answer}"
                    )
                    try:
                        out = await self._judge.judge(model="gpt-4o-mini", prompt=prompt)
                        score = float(out.get("score", 0.0) or 0.0)
                        return MetricScore(
                            name=self.name,
                            value=max(0.0, min(1.0, score)),
                            higher_is_better=False, confidence=0.8,
                        )
                    except Exception as exc:
                        logger.debug("hallucination judge failed: %s", exc)
                        return MetricScore(name=self.name, value=0.0, confidence=0.3)


            class RAGASEvaluator:
                name = "ragas"
                def __init__(self, judge: Any = None) -> None:
                    self._faith = FaithfulnessEvaluator(judge)
                    self._rel = AnswerRelevanceEvaluator(judge)
                    self._prec = ContextPrecisionEvaluator()
                    self._rec = ContextRecallEvaluator()

                async def evaluate(self, *, case: Any, answer: str, context: Any = None) -> MetricScore:
                    try:
                        f = await self._faith.evaluate(case=case, answer=answer, context=context)
                        r = await self._rel.evaluate(case=case, answer=answer, context=context)
                        p = await self._prec.evaluate(case=case, answer=answer, context=context)
                        c = await self._rec.evaluate(case=case, answer=answer, context=context)
                        score = ragas_score(f.value, r.value, p.value, c.value)
                        return MetricScore(
                            name=self.name, value=score,
                            details={
                                "faithfulness": f.value,
                                "answer_relevance": r.value,
                                "context_precision": p.value,
                                "context_recall": c.value,
                            },
                        )
                    except Exception as exc:
                        logger.warning("ragas failed: %s", exc)
                        return MetricScore(name=self.name, value=0.0)


            class LLMPortJudgeAdapter:
                """TH: LLMPort as judge | EN: LLM judge adapter"""
                def __init__(self, llm_port: Any) -> None:
                    self._llm = llm_port

                async def judge(self, *, model: str, prompt: str, context: str = "") -> dict[str, Any]:
                    result = await self._llm.chat(
                        tenant_id=uuid.UUID(int=0),
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    content = getattr(result, "content", "") or ""
                    try:
                        score = float(content.strip().split()[0])
                    except Exception:
                        score = 0.0
                    return {"score": score, "raw": content}


            class RAGTargetAdapter:
                """TH: RAGUseCase as target | EN: RAG target adapter"""
                def __init__(self, rag_use_case: Any) -> None:
                    self._rag = rag_use_case

                async def invoke(
                    self, *, target: Any, question: str,
                    context: Optional[list[str]] = None,
                ) -> dict[str, Any]:
                    from app.shared.context import RequestContext as SharedCtx
                    ctx = SharedCtx(tenant_id=uuid.UUID(int=0))
                    result = await self._rag.query(
                        ctx, query=question, pipeline_id=target.pipeline_id,
                    )
                    return {
                        "answer": result.get("answer", ""),
                        "citations": result.get("citations", []),
                        "total_tokens": result.get("usage", {}).get("total_tokens", 0),
                        "cost_usd": result.get("usage", {}).get("cost_usd", 0.0),
                    }


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
            """ai_evaluation Pydantic schemas"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal
            from typing import Any, Optional
            from pydantic import BaseModel, ConfigDict, Field

            from app.modules.ai_evaluation.domain.enums import (
                TargetKind, TaskType,
            )


            class TestCaseIn(BaseModel):
                model_config = ConfigDict(extra="forbid")
                question: str = Field(min_length=1)
                ground_truth: str = ""
                context: list[str] = Field(default_factory=list)
                metadata: dict[str, Any] = Field(default_factory=dict)


            class DatasetCreateRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                name: str = Field(min_length=1, max_length=100)
                description: str = ""
                task_type: TaskType = TaskType.QA
                cases: list[TestCaseIn] = Field(default_factory=list)
                metadata: dict[str, Any] = Field(default_factory=dict)


            class DatasetOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                description: str
                task_type: str
                version: str
                case_count: int


            class RunRequest(BaseModel):
                model_config = ConfigDict(extra="forbid")
                dataset_id: uuid.UUID
                target_kind: TargetKind = TargetKind.MODEL
                target_ref: str = Field(min_length=1, max_length=200)
                pipeline_id: Optional[str] = None
                metrics: list[str] = Field(
                    default_factory=lambda: ["faithfulness", "answer_relevance"],
                )
                sample_size: int = Field(default=0, ge=0)
                temperature: float = Field(default=0.0, ge=0.0, le=2.0)
                seed: Optional[int] = None
                concurrency: int = Field(default=4, ge=1, le=32)


            class RunOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                dataset_id: uuid.UUID
                target_kind: str
                target_model: str
                status: str
                case_count: int
                completed_count: int
                failed_count: int
                duration_ms: int
                total_cost_usd: Decimal
                error_message: str
                created_at: datetime


            class ReportOut(BaseModel):
                id: uuid.UUID
                run_id: uuid.UUID
                summary: dict[str, Any]
                passed: bool
                generated_at: datetime


            class MetricOut(BaseModel):
                model_config = ConfigDict(from_attributes=True)
                id: uuid.UUID
                name: str
                kind: str
                higher_is_better: bool
                range_min: float
                range_max: float
                description: str
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """ai_evaluation DI container"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass
            from typing import Annotated, Optional

            from fastapi import Depends, Header, HTTPException, Request, status
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.ai_evaluation.application.use_case import (
                AIEvaluationUseCase,
            )
            from app.modules.ai_evaluation.infrastructure.repositories import (
                EvalDatasetRepository, EvalMetricRepository,
                EvalReportRepository, EvalResultRepository,
                EvalRunRepository, EvalTestCaseRepository,
            )
            from app.modules.ai_evaluation.infrastructure.services import (
                AnswerRelevanceEvaluator, ContextPrecisionEvaluator,
                ContextRecallEvaluator, ExactMatchEvaluator, F1Evaluator,
                FaithfulnessEvaluator, HallucinationEvaluator,
                LoggingEventBus, MRREvaluator, NDCGEvaluator, RAGASEvaluator,
                RougeEvaluator,
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
            ) -> AIEvaluationUseCase:
                judge = getattr(request.app.state, "eval_judge", None)
                target = getattr(request.app.state, "eval_target", None)
                bus = getattr(request.app.state, "eval_event_bus", None) or LoggingEventBus()

                evaluators = {
                    "exact_match": ExactMatchEvaluator(),
                    "f1": F1Evaluator(),
                    "rouge": RougeEvaluator(),
                    "mrr": MRREvaluator(),
                    "ndcg": NDCGEvaluator(),
                    "context_precision": ContextPrecisionEvaluator(),
                    "context_recall": ContextRecallEvaluator(),
                    "faithfulness": FaithfulnessEvaluator(judge),
                    "answer_relevance": AnswerRelevanceEvaluator(judge),
                    "hallucination": HallucinationEvaluator(judge),
                    "ragas": RAGASEvaluator(judge),
                }

                return AIEvaluationUseCase(
                    datasets=EvalDatasetRepository(db),
                    cases=EvalTestCaseRepository(db),
                    runs=EvalRunRepository(db),
                    metrics=EvalMetricRepository(db),
                    results=EvalResultRepository(db),
                    reports=EvalReportRepository(db),
                    evaluators=evaluators,
                    target_invoker=target,
                    llm_judge=judge,
                    event_bus=bus,
                )
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """ai_evaluation HTTP router"""
            from __future__ import annotations
            import logging
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException

            from app.modules.ai_evaluation.application.exceptions import AppError
            from app.modules.ai_evaluation.application.use_case import (
                AIEvaluationUseCase,
            )
            from app.modules.ai_evaluation.application.utils import json_loads_safe
            from app.modules.ai_evaluation.domain.exceptions import EvalError
            from app.modules.ai_evaluation.domain.value_objects import (
                EvalConfig, EvalTarget,
            )
            from app.modules.ai_evaluation.presentation.dependencies import (
                Ctx, get_ctx, get_use_case,
            )
            from app.modules.ai_evaluation.presentation.schemas import (
                DatasetCreateRequest, DatasetOut, MetricOut, ReportOut,
                RunOut, RunRequest,
            )

            logger = logging.getLogger(__name__)

            router = APIRouter(prefix="/eval", tags=["AIEvaluation"])


            def _raise(exc: Exception) -> None:
                if isinstance(exc, EvalError):
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


            @router.get("/datasets", response_model=list[DatasetOut])
            async def list_datasets(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
            ) -> list[DatasetOut]:
                try:
                    items = await uc.list_datasets(ctx)
                    return [DatasetOut.model_validate(d.model_dump()) for d in items]
                except (EvalError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/datasets", response_model=DatasetOut, status_code=201)
            async def create_dataset(
                req: DatasetCreateRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
            ) -> DatasetOut:
                try:
                    ds = await uc.create_dataset(
                        ctx, name=req.name, description=req.description,
                        task_type=str(req.task_type),
                        cases=[c.model_dump() for c in req.cases],
                        metadata=req.metadata,
                    )
                    return DatasetOut.model_validate(ds.model_dump())
                except (EvalError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.post("/run", response_model=RunOut)
            async def run_evaluation(
                req: RunRequest,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
            ) -> RunOut:
                try:
                    target = EvalTarget(
                        kind=req.target_kind, ref=req.target_ref,
                        pipeline_id=req.pipeline_id,
                    )
                    config = EvalConfig(
                        metrics=req.metrics, sample_size=req.sample_size,
                        temperature=req.temperature, seed=req.seed,
                        concurrency=req.concurrency,
                    )
                    run = await uc.run_evaluation(
                        ctx, dataset_id=req.dataset_id,
                        target=target, config=config,
                    )
                    return RunOut.model_validate(run.model_dump())
                except (EvalError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/runs/{run_id}", response_model=RunOut)
            async def get_run(
                run_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
            ) -> RunOut:
                try:
                    r = await uc.get_run(ctx, run_id)
                    return RunOut.model_validate(r.model_dump())
                except (EvalError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/runs/{run_id}/report", response_model=ReportOut)
            async def get_report(
                run_id: uuid.UUID,
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
            ) -> ReportOut:
                try:
                    r = await uc.get_report(ctx, run_id)
                    return ReportOut(
                        id=r.id, run_id=r.run_id,
                        summary=json_loads_safe(r.summary_json, {}),
                        passed=r.passed, generated_at=r.generated_at,
                    )
                except (EvalError, AppError) as exc:
                    _raise(exc)
                    raise


            @router.get("/metrics", response_model=list[MetricOut])
            async def list_metrics(
                ctx: Annotated[Ctx, Depends(get_ctx)],
                uc: Annotated[AIEvaluationUseCase, Depends(get_use_case)],
            ) -> list[MetricOut]:
                try:
                    items = await uc.list_metrics(ctx)
                    return [MetricOut.model_validate(m.model_dump()) for m in items]
                except (EvalError, AppError) as exc:
                    _raise(exc)
                    raise
        ''')

    def _swagger_content(self) -> str:
        return dedent('''\
            """ai_evaluation OpenAPI docs"""
            from __future__ import annotations
            from typing import Any


            def register_ai_evaluation_openapi(app: object) -> None:
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "AIEvaluation" for t in tags):
                        tags.append({
                            "name": "AIEvaluation",
                            "description": (
                                "โมดูล ai_evaluation — LLM/RAG Evaluation\\n\\n"
                                "• RAGAS, faithfulness, answer_relevance\\n"
                                "• MRR, NDCG, precision@k, recall@k\\n"
                                "• Hallucination detection\\n"
                                "• Dataset + Run + Report"
                            ),
                            "externalDocs": {
                                "description": "ai_evaluation Module README",
                                "url": "/docs/README_ai_evaluation.md",
                            },
                        })
                    info = schema.setdefault("info", {})
                    info.setdefault("x-module", "ai_evaluation")
                    info.setdefault("x-layer", "5-Intel")
                    info.setdefault("x-prefix", "eval")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent(f'''\
            """{self.module} module"""
            from .presentation.router import router as eval_router

            __all__ = ["eval_router"]
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
-- V001__create_ai_evaluation.sql | Module: ai_evaluation | Prefix: eval
-- Schema: public | Tables: eval_datasets, eval_test_cases, eval_runs,
--                          eval_metrics, eval_results, eval_reports
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TABLE IF EXISTS "public"."eval_datasets";
CREATE TABLE "public"."eval_datasets" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "name"           varchar(100) NOT NULL,
  "description"    text NOT NULL DEFAULT '',
  "task_type"      varchar(30) NOT NULL DEFAULT 'qa',
  "version"        varchar(20) NOT NULL DEFAULT '1.0.0',
  "case_count"     int4 NOT NULL DEFAULT 0,
  "metadata_json"  text NOT NULL DEFAULT '{}',
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "eval_datasets_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_eval_dataset_name" UNIQUE ("tenant_id", "name"),
  CONSTRAINT "ck_eval_dataset_task" CHECK (
    task_type IN ('qa','summarization','classification','rag','agent')
  )
);
CREATE INDEX "ix_eval_ds_tenant" ON "public"."eval_datasets" ("tenant_id");

DROP TABLE IF EXISTS "public"."eval_test_cases";
CREATE TABLE "public"."eval_test_cases" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "dataset_id"     uuid NOT NULL,
  "question"       text NOT NULL DEFAULT '',
  "ground_truth"   text NOT NULL DEFAULT '',
  "context_json"   text NOT NULL DEFAULT '[]',
  "metadata_json"  text NOT NULL DEFAULT '{}',
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "eval_test_cases_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_eval_case_dataset" ON "public"."eval_test_cases" ("dataset_id");
CREATE INDEX "ix_eval_case_tenant"  ON "public"."eval_test_cases" ("tenant_id");

DROP TABLE IF EXISTS "public"."eval_runs";
CREATE TABLE "public"."eval_runs" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"          uuid NOT NULL,
  "user_id"            uuid NOT NULL,
  "dataset_id"         uuid NOT NULL,
  "target_kind"        varchar(20) NOT NULL DEFAULT 'model',
  "target_model"       varchar(100) NOT NULL DEFAULT '',
  "target_pipeline"    varchar(100) NOT NULL DEFAULT '',
  "config_json"        text NOT NULL DEFAULT '{}',
  "status"             varchar(20) NOT NULL DEFAULT 'QUEUED',
  "case_count"         int4 NOT NULL DEFAULT 0,
  "completed_count"    int4 NOT NULL DEFAULT 0,
  "failed_count"       int4 NOT NULL DEFAULT 0,
  "started_at"         timestamptz(6) NULL,
  "finished_at"        timestamptz(6) NULL,
  "duration_ms"        int4 NOT NULL DEFAULT 0,
  "total_cost_usd"     numeric(12,8) NOT NULL DEFAULT 0,
  "error_message"      text NOT NULL DEFAULT '',
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"         timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "eval_runs_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_eval_run_status" CHECK (
    status IN ('QUEUED','RUNNING','DONE','FAILED','CANCELLED')
  ),
  CONSTRAINT "ck_eval_run_target_kind" CHECK (
    target_kind IN ('model','pipeline')
  )
);
CREATE INDEX "ix_eval_run_tenant_time" ON "public"."eval_runs" ("tenant_id", "created_at" DESC);
CREATE INDEX "ix_eval_run_status"      ON "public"."eval_runs" ("status");

DROP TABLE IF EXISTS "public"."eval_metrics";
CREATE TABLE "public"."eval_metrics" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "name"               varchar(50) NOT NULL,
  "kind"               varchar(30) NOT NULL,
  "higher_is_better"   bool NOT NULL DEFAULT true,
  "range_min"          float8 NOT NULL DEFAULT 0,
  "range_max"          float8 NOT NULL DEFAULT 1,
  "description"        text NOT NULL DEFAULT '',
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"         timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "eval_metrics_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_eval_metric_name" UNIQUE ("name")
);

DROP TABLE IF EXISTS "public"."eval_results";
CREATE TABLE "public"."eval_results" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "run_id"         uuid NOT NULL,
  "case_id"        uuid NOT NULL,
  "metric_name"    varchar(50) NOT NULL,
  "score"          float8 NOT NULL DEFAULT 0,
  "confidence"     float8 NOT NULL DEFAULT 1,
  "details_json"   text NOT NULL DEFAULT '{}',
  "answer_text"    text NOT NULL DEFAULT '',
  "latency_ms"     int4 NOT NULL DEFAULT 0,
  "tokens_used"    int4 NOT NULL DEFAULT 0,
  "cost_usd"       numeric(12,8) NOT NULL DEFAULT 0,
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "eval_results_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_eval_res_run_metric" ON "public"."eval_results" ("run_id", "metric_name");
CREATE INDEX "ix_eval_res_case"       ON "public"."eval_results" ("case_id");
CREATE INDEX "ix_eval_res_tenant"     ON "public"."eval_results" ("tenant_id");

DROP TABLE IF EXISTS "public"."eval_reports";
CREATE TABLE "public"."eval_reports" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "run_id"         uuid NOT NULL,
  "summary_json"   text NOT NULL DEFAULT '{}',
  "passed"         bool NOT NULL DEFAULT false,
  "generated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "eval_reports_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_eval_report_run" UNIQUE ("run_id")
);
CREATE INDEX "ix_eval_rep_tenant" ON "public"."eval_reports" ("tenant_id");

-- ═══ Trigger ═══
CREATE OR REPLACE FUNCTION public.set_updated_at_eval()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_eval_ds_updated ON "public"."eval_datasets";
CREATE TRIGGER trg_eval_ds_updated BEFORE UPDATE ON "public"."eval_datasets"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_eval();

DROP TRIGGER IF EXISTS trg_eval_case_updated ON "public"."eval_test_cases";
CREATE TRIGGER trg_eval_case_updated BEFORE UPDATE ON "public"."eval_test_cases"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_eval();

DROP TRIGGER IF EXISTS trg_eval_run_updated ON "public"."eval_runs";
CREATE TRIGGER trg_eval_run_updated BEFORE UPDATE ON "public"."eval_runs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_eval();

DROP TRIGGER IF EXISTS trg_eval_metric_updated ON "public"."eval_metrics";
CREATE TRIGGER trg_eval_metric_updated BEFORE UPDATE ON "public"."eval_metrics"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_eval();

DROP TRIGGER IF EXISTS trg_eval_res_updated ON "public"."eval_results";
CREATE TRIGGER trg_eval_res_updated BEFORE UPDATE ON "public"."eval_results"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_eval();

DROP TRIGGER IF EXISTS trg_eval_rep_updated ON "public"."eval_reports";
CREATE TRIGGER trg_eval_rep_updated BEFORE UPDATE ON "public"."eval_reports"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_eval();

-- ═══ RLS ═══
ALTER TABLE "public"."eval_datasets"    ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."eval_test_cases"  ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."eval_runs"        ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."eval_results"     ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."eval_reports"     ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_eval_ds ON "public"."eval_datasets";
CREATE POLICY p_eval_ds ON "public"."eval_datasets"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_eval_case ON "public"."eval_test_cases";
CREATE POLICY p_eval_case ON "public"."eval_test_cases"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_eval_run ON "public"."eval_runs";
CREATE POLICY p_eval_run ON "public"."eval_runs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_eval_res ON "public"."eval_results";
CREATE POLICY p_eval_res ON "public"."eval_results"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_eval_rep ON "public"."eval_reports";
CREATE POLICY p_eval_rep ON "public"."eval_reports"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_ai_evaluation.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."eval_metrics"
    (name, kind, higher_is_better, range_min, range_max, description)
VALUES
    ('exact_match', 'exact_match', TRUE, 0, 1, 'Exact string match (normalized)'),
    ('f1', 'f1', TRUE, 0, 1, 'Token-level F1'),
    ('rouge', 'rouge', TRUE, 0, 1, 'ROUGE-L F1'),
    ('faithfulness', 'faithfulness', TRUE, 0, 1, 'Faithfulness (no hallucination)'),
    ('answer_relevance', 'answer_relevance', TRUE, 0, 1, 'Answer relevance'),
    ('context_precision', 'context_precision', TRUE, 0, 1, 'Context precision'),
    ('context_recall', 'context_recall', TRUE, 0, 1, 'Context recall'),
    ('mrr', 'mrr', TRUE, 0, 1, 'Mean Reciprocal Rank'),
    ('ndcg', 'ndcg', TRUE, 0, 1, 'NDCG'),
    ('ragas', 'ragas', TRUE, 0, 1, 'RAGAS combined'),
    ('hallucination', 'hallucination', FALSE, 0, 1, 'Hallucination rate')
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_ai_evaluation.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_eval_rep_updated ON "public"."eval_reports";
DROP TRIGGER IF EXISTS trg_eval_res_updated ON "public"."eval_results";
DROP TRIGGER IF EXISTS trg_eval_metric_updated ON "public"."eval_metrics";
DROP TRIGGER IF EXISTS trg_eval_run_updated ON "public"."eval_runs";
DROP TRIGGER IF EXISTS trg_eval_case_updated ON "public"."eval_test_cases";
DROP TRIGGER IF EXISTS trg_eval_ds_updated ON "public"."eval_datasets";

DROP POLICY IF EXISTS p_eval_rep  ON "public"."eval_reports";
DROP POLICY IF EXISTS p_eval_res  ON "public"."eval_results";
DROP POLICY IF EXISTS p_eval_run  ON "public"."eval_runs";
DROP POLICY IF EXISTS p_eval_case ON "public"."eval_test_cases";
DROP POLICY IF EXISTS p_eval_ds   ON "public"."eval_datasets";

DROP TABLE IF EXISTS "public"."eval_reports"    CASCADE;
DROP TABLE IF EXISTS "public"."eval_results"    CASCADE;
DROP TABLE IF EXISTS "public"."eval_metrics"    CASCADE;
DROP TABLE IF EXISTS "public"."eval_runs"       CASCADE;
DROP TABLE IF EXISTS "public"."eval_test_cases" CASCADE;
DROP TABLE IF EXISTS "public"."eval_datasets"   CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_eval();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  3. ALEMBIC
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "eval_001"
        content = f'''"""add ai_evaluation tables

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
    """TH: สร้างตาราง ai_evaluation | EN: create tables"""
    op.create_table(
        "eval_datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("task_type", sa.String(30), nullable=False, server_default="qa"),
        sa.Column("version", sa.String(20), nullable=False, server_default="1.0.0"),
        sa.Column("case_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_eval_dataset_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "eval_test_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question", sa.Text, nullable=False, server_default=""),
        sa.Column("ground_truth", sa.Text, nullable=False, server_default=""),
        sa.Column("context_json", sa.Text, nullable=False, server_default="[]"),
        sa.Column("metadata_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "eval_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_kind", sa.String(20), nullable=False, server_default="model"),
        sa.Column("target_model", sa.String(100), nullable=False, server_default=""),
        sa.Column("target_pipeline", sa.String(100), nullable=False, server_default=""),
        sa.Column("config_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("status", sa.String(20), nullable=False, server_default="QUEUED"),
        sa.Column("case_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("completed_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_cost_usd", sa.Numeric(12, 8), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "eval_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False),
        sa.Column("higher_is_better", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("range_min", sa.Float, nullable=False, server_default="0"),
        sa.Column("range_max", sa.Float, nullable=False, server_default="1"),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("name", name="uq_eval_metric_name"),
        schema=SCHEMA,
    )
    op.create_table(
        "eval_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_name", sa.String(50), nullable=False),
        sa.Column("score", sa.Float, nullable=False, server_default="0"),
        sa.Column("confidence", sa.Float, nullable=False, server_default="1"),
        sa.Column("details_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("answer_text", sa.Text, nullable=False, server_default=""),
        sa.Column("latency_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("tokens_used", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Numeric(12, 8), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_table(
        "eval_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary_json", sa.Text, nullable=False, server_default="{{}}"),
        sa.Column("passed", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("run_id", name="uq_eval_report_run"),
        schema=SCHEMA,
    )

    op.create_index("ix_eval_ds_tenant", "eval_datasets", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_eval_case_dataset", "eval_test_cases", ["dataset_id"], schema=SCHEMA)
    op.create_index("ix_eval_case_tenant", "eval_test_cases", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_eval_run_tenant_time", "eval_runs", ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_eval_run_status", "eval_runs", ["status"], schema=SCHEMA)
    op.create_index("ix_eval_res_run_metric", "eval_results", ["run_id", "metric_name"], schema=SCHEMA)
    op.create_index("ix_eval_res_case", "eval_results", ["case_id"], schema=SCHEMA)
    op.create_index("ix_eval_res_tenant", "eval_results", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_eval_rep_tenant", "eval_reports", ["tenant_id"], schema=SCHEMA)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_eval()
        RETURNS TRIGGER AS $$
        BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
    """)

    for tbl in ("eval_datasets", "eval_test_cases", "eval_runs",
                "eval_metrics", "eval_results", "eval_reports"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f"""
            CREATE TRIGGER trg_{{tbl}}_updated
                BEFORE UPDATE ON {{SCHEMA}}.{{tbl}}
                FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_eval();
        """)
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")


def downgrade() -> None:
    """TH: ลบตาราง | EN: drop tables"""
    for tbl in ("eval_reports", "eval_results", "eval_metrics",
                "eval_runs", "eval_test_cases", "eval_datasets"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{{tbl}}_updated ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_eval();")
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
                    "name": "Create Dataset",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                            {"key": "X-User-Id", "value": "{{user_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/datasets",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "datasets"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"name":"qa_baseline","task_type":"qa","cases":[{"question":"What is 2+2?","ground_truth":"4"}]}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Run Evaluation",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/run",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "run"],
                        },
                        "body": {
                            "mode": "raw",
                            "raw": '{"dataset_id":"REPLACE","target_kind":"model","target_ref":"gpt-4o-mini","metrics":["faithfulness","answer_relevance"]}',
                            "options": {"raw": {"language": "json"}},
                        },
                    },
                },
                {
                    "name": "Get Report",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/runs/REPLACE/report",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "runs", "REPLACE", "report"],
                        },
                    },
                },
                {
                    "name": "List Metrics",
                    "request": {
                        "method": "GET",
                        "header": [
                            {"key": "X-Tenant-Id", "value": "{{tenant_id}}"},
                        ],
                        "url": {
                            "raw": f"{{{{base_url}}}}/api/v1/{self.prefix}/metrics",
                            "host": ["{{base_url}}"],
                            "path": ["api", "v1", self.prefix, "metrics"],
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
        EvalDatasetModel,
        EvalMetricModel,
        EvalReportModel,
        EvalResultModel,
        EvalRunModel,
        EvalTestCaseModel,
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
create_module_ai_evaluation.py — AI Evaluation Module Generator v{VERSION}

USAGE
    python create_module_ai_evaluation.py <action> [options]

MODULE
    name    : ai_evaluation
    layer   : 5-Intel
    prefix  : eval
    schema  : public
    tables  : eval_datasets, eval_test_cases, eval_runs,
              eval_metrics, eval_results, eval_reports

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
    python create_module_ai_evaluation.py all
    python create_module_ai_evaluation.py create --force
    python create_module_ai_evaluation.py verify
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