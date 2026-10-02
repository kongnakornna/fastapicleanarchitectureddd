#!/usr/bin/env python3
"""
Template_app_module.py — AI/ML Module Generator v1.0

สร้าง ai_ml module ตาม Clean Architecture + DDD + Event-Driven + MLOps
Schema: public · Prefix: yolo_ · Tables: yolo_*

Actions (11):
  1.  create      — สร้าง module structure (ai_ml) 4 layers
  2.  activate    — register router + swagger + models
  3.  sql         — สร้าง SQL migrations V001/V002/V003
  4.  update      — อัปเดต app/app.py
  5.  update-env  — อัปเดต migrations/env.py
  6.  alembic     — สร้าง Alembic migration (7 tables + triggers + RLS)
  7.  swagger     — สร้าง OpenAPI docs
  8.  postman     — สร้าง Postman collection
  9.  test        — สร้าง tests (unit/integration/property/manual)
 10.  verify      — ตรวจสอบ Swagger + Postman + SQL
 11.  all         — ทำทุกอย่าง

Usage:
    python create_module_ai_ml.py <action> <module> [layer] [prefix] [options]

Examples:
    python create_module_ai_ml.py all ai_ml 5 yolo
    python create_module_ai_ml.py create ai_ml 5 yolo --force
    python create_module_ai_ml.py verify ai_ml
    python create_module_ai_ml.py help
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

ACTIONS = {
    "create", "activate", "sql", "alembic",
    "swagger", "postman", "update", "update-env",
    "test", "all", "verify", "help",
}

SCHEMA = "public"
PREFIX = "yolo"
TABLE_NAMES = (
    "yolo_datasets",
    "yolo_features",
    "yolo_experiments",
    "yolo_models",
    "yolo_training_runs",
    "yolo_predictions",
    "yolo_metrics",
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
                raise RuntimeError(
                    f"Refuse to write invalid Python: {rel_path}"
                ) from exc

        path.write_text(content, encoding="utf-8", newline="\n")
        ok(rel_path)
        self.written.append(path)


# ═══════════════════════════════════════════════════════════════
#  GENERATOR
# ═══════════════════════════════════════════════════════════════
class yoloModuleGenerator:
    def __init__(
        self,
        project_root: Path,
        module: str = "ai_ml",
        layer: str = "5",
        prefix: str = "yolo",
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
        self.tests_dir = "tests"
        self.docs_dir = "docs"

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
            """ai_ml domain layer — ชั้นโดเมน ai_ml"""
            from .entities import (
                Dataset, Experiment, Feature, Metric, MLModel,
                Prediction, TrainingRun,
            )
            from .enums import (
                DatasetStatus, DataSource, MetricName,
                ModelStatus, TaskType, TrainingStatus,
            )
            from .events import (
                DatasetRegistered, ExperimentStarted,
                FeaturesExtracted, ModelDeployed,
                ModelDriftDetected, PredictionServed,
                TrainingCompleted,
            )
            from .exceptions import (
                yoloError, ArtifactNotFoundError,
                DatasetNotFoundError, DriftDetectedError,
                ExperimentNotFoundError, FeatureNotFoundError,
                InvalidFeatureError, ModelLoadError,
                ModelNotFoundError, SchemaMismatchError,
                TrainingFailedError,
            )
            from .value_objects import (
                DatasetProfile, FeatureSpec, ModelMetrics,
                PredictionResult, TrainConfig,
            )

            __all__ = [
                "Dataset", "Experiment", "Feature", "Metric",
                "MLModel", "Prediction", "TrainingRun",
                "DatasetStatus", "DataSource", "MetricName",
                "ModelStatus", "TaskType", "TrainingStatus",
                "DatasetRegistered", "ExperimentStarted",
                "FeaturesExtracted", "ModelDeployed",
                "ModelDriftDetected", "PredictionServed",
                "TrainingCompleted",
                "yoloError", "ArtifactNotFoundError",
                "DatasetNotFoundError", "DriftDetectedError",
                "ExperimentNotFoundError", "FeatureNotFoundError",
                "InvalidFeatureError", "ModelLoadError",
                "ModelNotFoundError", "SchemaMismatchError",
                "TrainingFailedError",
                "DatasetProfile", "FeatureSpec", "ModelMetrics",
                "PredictionResult", "TrainConfig",
            ]
        '''))

        # ─── enums.py ─────────────────────────────────
        self.writer.write(f"{base}/enums.py", dedent('''\
            """ai_ml enums — Enum ของ ai_ml"""
            from __future__ import annotations
            from enum import StrEnum


            class DatasetStatus(StrEnum):
                """TH: สถานะ dataset | EN: Dataset status"""
                RAW = "RAW"
                PROCESSED = "PROCESSED"
                ARCHIVED = "ARCHIVED"


            class ModelStatus(StrEnum):
                """TH: สถานะ model | EN: Model status"""
                DRAFT = "DRAFT"
                TRAINED = "TRAINED"
                DEPLOYED = "DEPLOYED"
                ARCHIVED = "ARCHIVED"


            class TrainingStatus(StrEnum):
                """TH: สถานะ training | EN: Training status"""
                PENDING = "PENDING"
                RUNNING = "RUNNING"
                SUCCESS = "SUCCESS"
                FAILED = "FAILED"
                CANCELLED = "CANCELLED"


            class TaskType(StrEnum):
                """TH: ประเภทงาน ML | EN: ML task type"""
                CLASSIFICATION = "CLASSIFICATION"
                REGRESSION = "REGRESSION"
                CLUSTERING = "CLUSTERING"
                DIM_REDUCTION = "DIM_REDUCTION"
                RECOMMENDATION = "RECOMMENDATION"


            class MetricName(StrEnum):
                """TH: ชื่อ metric | EN: Metric name"""
                ACCURACY = "accuracy"
                F1 = "f1"
                PRECISION = "precision"
                RECALL = "recall"
                RMSE = "rmse"
                MAE = "mae"
                R2 = "r2"
                SILHOUETTE = "silhouette"


            class DataSource(StrEnum):
                """TH: แหล่งข้อมูล | EN: Data source"""
                S3 = "s3"
                POSTGRES = "postgres"
                KAFKA = "kafka"
                API = "api"
                UPLOAD = "upload"
        '''))

        # ─── exceptions.py ────────────────────────────
        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """ai_ml domain exceptions — ข้อยกเว้นโดเมน ai_ml"""
            from __future__ import annotations


            class yoloError(Exception):
                """TH: base error | EN: base error"""
                code: str = "DOMAIN_ERROR"

                def __init__(
                    self, message: str = "", *, code: str | None = None,
                ) -> None:
                    super().__init__(message or self.__class__.__name__)
                    if code:
                        self.code = code


            class DatasetNotFoundError(yoloError):
                code = "DATASET_NOT_FOUND"


            class FeatureNotFoundError(yoloError):
                code = "FEATURE_NOT_FOUND"


            class ModelNotFoundError(yoloError):
                code = "MODEL_NOT_FOUND"


            class ExperimentNotFoundError(yoloError):
                code = "EXPERIMENT_NOT_FOUND"


            class TrainingFailedError(yoloError):
                code = "TRAINING_FAILED"


            class InvalidFeatureError(yoloError):
                code = "INVALID_FEATURE"


            class SchemaMismatchError(yoloError):
                code = "SCHEMA_MISMATCH"


            class DriftDetectedError(yoloError):
                code = "DRIFT_DETECTED"


            class ArtifactNotFoundError(yoloError):
                code = "ARTIFACT_NOT_FOUND"


            class ModelLoadError(yoloError):
                code = "MODEL_LOAD_ERROR"
        '''))

        # ─── events.py ────────────────────────────────
        self.writer.write(f"{base}/events.py", dedent('''\
            """ai_ml domain events — เหตุการณ์โดเมน ai_ml"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import UTC, datetime
            from typing import Any


            def _now() -> datetime:
                return datetime.now(UTC)


            @dataclass(frozen=True, slots=True)
            class DatasetRegistered:
                dataset_id: uuid.UUID
                tenant_id: uuid.UUID
                name: str
                rows: int
                cols: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class FeaturesExtracted:
                feature_ids: tuple[uuid.UUID, ...]
                tenant_id: uuid.UUID
                dataset_id: uuid.UUID
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class ExperimentStarted:
                experiment_id: uuid.UUID
                tenant_id: uuid.UUID
                task_type: str
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class TrainingCompleted:
                training_run_id: uuid.UUID
                model_id: uuid.UUID
                tenant_id: uuid.UUID
                metrics: dict[str, Any]
                duration_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class ModelDeployed:
                model_id: uuid.UUID
                tenant_id: uuid.UUID
                version: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class PredictionServed:
                prediction_id: uuid.UUID
                model_id: uuid.UUID
                tenant_id: uuid.UUID
                latency_ms: int
                occurred_at: datetime = field(default_factory=_now)


            @dataclass(frozen=True, slots=True)
            class ModelDriftDetected:
                model_id: uuid.UUID
                tenant_id: uuid.UUID
                drift_score: float
                threshold: float
                occurred_at: datetime = field(default_factory=_now)
        '''))

        # ─── value_objects/__init__.py ────────────────
        self.writer.write(f"{base}/value_objects/__init__.py", dedent('''\
            """ai_ml value objects"""
            from .dataset_profile import DatasetProfile
            from .feature_spec import FeatureSpec
            from .model_metrics import ModelMetrics
            from .prediction_result import PredictionResult
            from .train_config import TrainConfig

            __all__ = [
                "DatasetProfile", "FeatureSpec", "ModelMetrics",
                "PredictionResult", "TrainConfig",
            ]
        '''))

        # ─── value_objects/feature_spec.py ────────────
        self.writer.write(
            f"{base}/value_objects/feature_spec.py",
            dedent('''\
                """FeatureSpec value object — คุณสมบัติ feature"""
                from __future__ import annotations
                from dataclasses import dataclass


                @dataclass(frozen=True, slots=True)
                class FeatureSpec:
                    """TH: spec ของ feature | EN: feature spec VO"""
                    name: str
                    dtype: str = "float"
                    nullable: bool = True
                    transform: str = ""

                    def __post_init__(self) -> None:
                        if not self.name:
                            raise ValueError("feature name is required")
                        if self.dtype not in (
                            "float", "int", "bool", "str", "category",
                        ):
                            raise ValueError(
                                f"unsupported dtype: {self.dtype}",
                            )
            '''),
        )

        # ─── value_objects/train_config.py ────────────
        self.writer.write(
            f"{base}/value_objects/train_config.py",
            dedent('''\
                """TrainConfig value object — config การฝึก"""
                from __future__ import annotations
                from dataclasses import dataclass, field
                from typing import Any


                @dataclass(frozen=True, slots=True)
                class TrainConfig:
                    """TH: config การฝึก | EN: training config VO"""
                    test_size: float = 0.2
                    random_state: int = 42
                    cv_folds: int = 5
                    scaler: str = "standard"
                    algorithm: str = "logistic_regression"
                    hyperparams: tuple[tuple[str, Any], ...] = ()

                    def __post_init__(self) -> None:
                        if not 0.0 < self.test_size < 1.0:
                            raise ValueError(
                                "test_size must be between 0 and 1",
                            )
                        if self.cv_folds < 2:
                            raise ValueError("cv_folds must be >= 2")

                    def hyperparams_dict(self) -> dict[str, Any]:
                        """TH: แปลง hyperparams เป็น dict"""
                        return dict(self.hyperparams)
            '''),
        )

        # ─── value_objects/model_metrics.py ───────────
        self.writer.write(
            f"{base}/value_objects/model_metrics.py",
            dedent('''\
                """ModelMetrics value object — ผลการวัด"""
                from __future__ import annotations
                from dataclasses import dataclass


                @dataclass(frozen=True, slots=True)
                class ModelMetrics:
                    """TH: metrics ของ model | EN: model metrics VO"""
                    accuracy: float | None = None
                    f1: float | None = None
                    precision: float | None = None
                    recall: float | None = None
                    rmse: float | None = None
                    mae: float | None = None
                    r2: float | None = None
                    silhouette: float | None = None

                    def to_dict(self) -> dict[str, float]:
                        """TH: แปลงเป็น dict (เฉพาะที่ไม่ None)"""
                        return {
                            k: v for k, v in {
                                "accuracy": self.accuracy,
                                "f1": self.f1,
                                "precision": self.precision,
                                "recall": self.recall,
                                "rmse": self.rmse,
                                "mae": self.mae,
                                "r2": self.r2,
                                "silhouette": self.silhouette,
                            }.items() if v is not None
                        }
            '''),
        )

        # ─── value_objects/dataset_profile.py ─────────
        self.writer.write(
            f"{base}/value_objects/dataset_profile.py",
            dedent('''\
                """DatasetProfile value object — โปรไฟล์ dataset"""
                from __future__ import annotations
                from dataclasses import dataclass, field
                from typing import Any


                @dataclass(frozen=True, slots=True)
                class DatasetProfile:
                    """TH: โปรไฟล์ dataset | EN: dataset profile VO"""
                    rows: int
                    cols: int
                    missing_ratio: float = 0.0
                    dtypes: tuple[tuple[str, str], ...] = ()
                    stats: tuple[tuple[str, Any], ...] = ()

                    def __post_init__(self) -> None:
                        if self.rows < 0 or self.cols < 0:
                            raise ValueError("rows/cols must be non-negative")
                        if not 0.0 <= self.missing_ratio <= 1.0:
                            raise ValueError(
                                "missing_ratio must be between 0 and 1",
                            )

                    def dtypes_dict(self) -> dict[str, str]:
                        return dict(self.dtypes)

                    def stats_dict(self) -> dict[str, Any]:
                        return dict(self.stats)
            '''),
        )

        # ─── value_objects/prediction_result.py ───────
        self.writer.write(
            f"{base}/value_objects/prediction_result.py",
            dedent('''\
                """PredictionResult value object — ผลการทำนาย"""
                from __future__ import annotations
                from dataclasses import dataclass
                from typing import Any


                @dataclass(frozen=True, slots=True)
                class PredictionResult:
                    """TH: ผลการทำนาย | EN: prediction result VO"""
                    output: Any
                    confidence: float = 0.0
                    latency_ms: int = 0

                    def __post_init__(self) -> None:
                        if not 0.0 <= self.confidence <= 1.0:
                            raise ValueError(
                                "confidence must be between 0 and 1",
                            )
                        if self.latency_ms < 0:
                            raise ValueError("latency_ms must be >= 0")
            '''),
        )

        # ─── helpers/__init__.py ──────────────────────
        self.writer.write(f"{base}/helpers/__init__.py", dedent('''\
            """ai_ml domain helpers"""
            from .dataframe_profiler import profile_dataframe
            from .metric_calculator import calculate_metrics

            __all__ = ["profile_dataframe", "calculate_metrics"]
        '''))

        # ─── helpers/dataframe_profiler.py ────────────
        self.writer.write(
            f"{base}/helpers/dataframe_profiler.py",
            dedent('''\
                """DataFrame profiler — ใช้ pandas + numpy

                TH: วิเคราะห์ dataset ด้วย pandas
                EN: profile dataset using pandas
                """
                from __future__ import annotations
                from typing import Any

                import numpy as np
                import pandas as pd
                from loguru import logger

                from app.modules.ai_ml.domain.value_objects import (
                    DatasetProfile,
                )


                def profile_dataframe(df: pd.DataFrame) -> DatasetProfile:
                    """TH: วิเคราะห์ dataframe | EN: profile dataframe"""
                    if df is None or df.empty:
                        return DatasetProfile(rows=0, cols=0)

                    rows, cols = df.shape
                    missing_ratio = float(df.isna().sum().sum()) / max(
                        rows * cols, 1,
                    )

                    dtypes = tuple(
                        (str(col), str(dtype))
                        for col, dtype in df.dtypes.items()
                    )

                    stats: list[tuple[str, Any]] = []
                    for col in df.columns:
                        series = df[col]
                        try:
                            if pd.api.types.is_numeric_dtype(series):
                                stats.append((str(col), {
                                    "min": _safe_float(series.min()),
                                    "max": _safe_float(series.max()),
                                    "mean": _safe_float(series.mean()),
                                    "std": _safe_float(series.std()),
                                    "missing": int(series.isna().sum()),
                                }))
                            else:
                                stats.append((str(col), {
                                    "unique": int(series.nunique(dropna=True)),
                                    "missing": int(series.isna().sum()),
                                }))
                        except Exception as exc:
                            logger.warning(
                                f"profile column {col} failed: {exc}",
                            )

                    logger.info(
                        f"profiled: rows={rows} cols={cols} "
                        f"missing={missing_ratio:.4f}",
                    )
                    return DatasetProfile(
                        rows=rows,
                        cols=cols,
                        missing_ratio=missing_ratio,
                        dtypes=dtypes,
                        stats=tuple(stats),
                    )


                def _safe_float(value: Any) -> float | None:
                    """TH: แปลงเป็น float อย่างปลอดภัย"""
                    try:
                        if value is None or pd.isna(value):
                            return None
                        if isinstance(value, (np.floating, np.integer)):
                            return float(value)
                        return float(value)
                    except (ValueError, TypeError):
                        return None
            '''),
        )

        # ─── helpers/metric_calculator.py ─────────────
        self.writer.write(
            f"{base}/helpers/metric_calculator.py",
            dedent('''\
                """Metric calculator — ใช้ scikit-learn

                TH: คำนวณ metrics สำหรับ classification/regression/clustering
                EN: compute metrics using scikit-learn
                """
                from __future__ import annotations
                from typing import Any

                import numpy as np
                from loguru import logger

                from app.modules.ai_ml.domain.enums import TaskType
                from app.modules.ai_ml.domain.value_objects import ModelMetrics


                def calculate_metrics(
                    task_type: str | TaskType,
                    y_true: np.ndarray | None = None,
                    y_pred: np.ndarray | None = None,
                    X: np.ndarray | None = None,
                    labels: np.ndarray | None = None,
                ) -> ModelMetrics:
                    """TH: คำนวณ metrics | EN: compute metrics"""
                    task = TaskType(task_type) if isinstance(task_type, str) else task_type

                    try:
                        if task == TaskType.CLASSIFICATION:
                            return _classification_metrics(y_true, y_pred)
                        if task == TaskType.REGRESSION:
                            return _regression_metrics(y_true, y_pred)
                        if task == TaskType.CLUSTERING:
                            return _clustering_metrics(X, labels)
                        if task == TaskType.DIM_REDUCTION:
                            return ModelMetrics()
                        return ModelMetrics()
                    except Exception as exc:
                        logger.error(f"calculate_metrics failed: {exc}")
                        return ModelMetrics()


                def _classification_metrics(
                    y_true: Any, y_pred: Any,
                ) -> ModelMetrics:
                    from sklearn.metrics import (
                        accuracy_score, f1_score,
                        precision_score, recall_score,
                    )
                    if y_true is None or y_pred is None:
                        return ModelMetrics()
                    average = "binary" if len(set(y_true)) <= 2 else "macro"
                    return ModelMetrics(
                        accuracy=float(accuracy_score(y_true, y_pred)),
                        f1=float(f1_score(y_true, y_pred, average=average,
                                            zero_division=0)),
                        precision=float(precision_score(
                            y_true, y_pred, average=average, zero_division=0,
                        )),
                        recall=float(recall_score(
                            y_true, y_pred, average=average, zero_division=0,
                        )),
                    )


                def _regression_metrics(
                    y_true: Any, y_pred: Any,
                ) -> ModelMetrics:
                    from sklearn.metrics import (
                        mean_absolute_error, mean_squared_error, r2_score,
                    )
                    if y_true is None or y_pred is None:
                        return ModelMetrics()
                    return ModelMetrics(
                        rmse=float(np.sqrt(mean_squared_error(y_true, y_pred))),
                        mae=float(mean_absolute_error(y_true, y_pred)),
                        r2=float(r2_score(y_true, y_pred)),
                    )


                def _clustering_metrics(
                    X: Any, labels: Any,
                ) -> ModelMetrics:
                    from sklearn.metrics import silhouette_score
                    if X is None or labels is None or len(set(labels)) < 2:
                        return ModelMetrics()
                    try:
                        score = float(silhouette_score(X, labels))
                    except Exception:
                        score = None
                    return ModelMetrics(silhouette=score)
            '''),
        )

        # ─── entities/__init__.py ─────────────────────
        self.writer.write(f"{base}/entities/__init__.py", dedent('''\
            """ai_ml entities"""
            from app.modules.ai_ml.domain.entities.dataset import Dataset
            from app.modules.ai_ml.domain.entities.experiment import Experiment
            from app.modules.ai_ml.domain.entities.feature import Feature
            from app.modules.ai_ml.domain.entities.metric import Metric
            from app.modules.ai_ml.domain.entities.model import MLModel
            from app.modules.ai_ml.domain.entities.prediction import Prediction
            from app.modules.ai_ml.domain.entities.training_run import TrainingRun

            __all__ = [
                "Dataset", "Experiment", "Feature", "Metric",
                "MLModel", "Prediction", "TrainingRun",
            ]
        '''))

        # ─── entities/dataset.py ──────────────────────
        self.writer.write(
            f"{base}/entities/dataset.py",
            dedent('''\
                """Dataset entity — ลงทะเบียน dataset"""
                from __future__ import annotations
                from sqlalchemy import Integer, String, Text
                from sqlalchemy.dialects.postgresql import JSONB
                from sqlalchemy.orm import Mapped, mapped_column

                from app.modules.shared.infrastructure.models import BaseModel


                class Dataset(BaseModel):
                    """TH: dataset | EN: dataset entity"""
                    __tablename__ = "yolo_datasets"

                    name: Mapped[str] = mapped_column(String(200))
                    source_uri: Mapped[str] = mapped_column(
                        Text, default="",
                    )
                    content_hash: Mapped[str] = mapped_column(
                        String(64), default="",
                    )
                    rows: Mapped[int] = mapped_column(Integer, default=0)
                    cols: Mapped[int] = mapped_column(Integer, default=0)
                    status: Mapped[str] = mapped_column(
                        String(20), default="RAW",
                    )
                    version: Mapped[int] = mapped_column(Integer, default=1)
                    schema_json: Mapped[dict] = mapped_column(
                        JSONB, default=dict,
                    )
                    profile_json: Mapped[dict] = mapped_column(
                        JSONB, default=dict,
                    )
                    metadata_json: Mapped[dict] = mapped_column(
                        JSONB, default=dict,
                    )
            '''),
        )

        # ─── entities/feature.py ──────────────────────
        self.writer.write(
            f"{base}/entities/feature.py",
            dedent('''\
                """Feature entity — นิยาม feature"""
                from __future__ import annotations
                from sqlalchemy import Boolean, Integer, String
                from sqlalchemy.dialects.postgresql import JSONB, UUID
                from sqlalchemy.orm import Mapped, mapped_column

                from app.modules.shared.infrastructure.models import BaseModel


                class Feature(BaseModel):
                    """TH: feature | EN: feature entity"""
                    __tablename__ = "yolo_features"

                    name: Mapped[str] = mapped_column(String(200))
                    dtype: Mapped[str] = mapped_column(
                        String(50), default="float",
                    )
                    transform: Mapped[str] = mapped_column(
                        String(100), default="",
                    )
                    source_dataset_id: Mapped[str | None] = mapped_column(
                        UUID(as_uuid=True), nullable=True,
                    )
                    entity_key: Mapped[str] = mapped_column(
                        String(100), default="",
                    )
                    ttl_seconds: Mapped[int] = mapped_column(
                        Integer, default=3600,
                    )
                    is_online: Mapped[bool] = mapped_column(
                        Boolean, default=True,
                    )
                    metadata_json: Mapped[dict] = mapped_column(
                        JSONB, default=dict,
                    )
            '''),
        )

        # ─── entities/experiment.py ───────────────────
        self.writer.write(
            f"{base}/entities/experiment.py",
            dedent('''\
                """Experiment entity — experiment tracking"""
                from __future__ import annotations
                from sqlalchemy import String, Text
                from sqlalchemy.dialects.postgresql import JSONB, UUID
                from sqlalchemy.orm import Mapped, mapped_column

                from app.modules.shared.infrastructure.models import BaseModel


                class Experiment(BaseModel):
                    """TH: experiment | EN: experiment entity"""
                    __tablename__ = "yolo_experiments"

                    name: Mapped[str] = mapped_column(String(200))
                    description: Mapped[str] = mapped_column(
                        Text, default="",
                    )
                    task_type: Mapped[str] = mapped_column(String(50))
                    status: Mapped[str] = mapped_column(
                        String(20), default="ACTIVE",
                    )
                    best_model_id: Mapped[str | None] = mapped_column(
                        UUID(as_uuid=True), nullable=True,
                    )
                    metadata_json: Mapped[dict] = mapped_column(
                        JSONB, default=dict,
                    )
            '''),
        )

        # ─── entities/model.py ────────────────────────
        self.writer.write(
            f"{base}/entities/model.py",
            dedent('''\
                """MLModel entity — model registry"""
                from __future__ import annotations
                from datetime import datetime
                from sqlalchemy import Boolean, DateTime, Integer, String, Text
                from sqlalchemy.dialects.postgresql import JSONB, UUID
                from sqlalchemy.orm import Mapped, mapped_column

                from app.modules.shared.infrastructure.models import BaseModel


                class MLModel(BaseModel):
                    """TH: model | EN: ML model entity"""
                    __tablename__ = "yolo_models"

                    experiment_id: Mapped[str] = mapped_column(
                        UUID(as_uuid=True),
                    )
                    name: Mapped[str] = mapped_column(String(200))
                    version: Mapped[int] = mapped_column(Integer, default=1)
                    task_type: Mapped[str] = mapped_column(String(50))
                    algorithm: Mapped[str] = mapped_column(
                        String(100), default="",
                    )
                    hyperparams_json: Mapped[dict] = mapped_column(
                        JSONB, default=dict,
                    )
                    artifact_uri: Mapped[str] = mapped_column(
                        Text, default="",
                    )
                    artifact_hash: Mapped[str] = mapped_column(
                        String(64), default="",
                    )
                    metrics_json: Mapped[dict] = mapped_column(
                        JSONB, default=dict,
                    )
                    status: Mapped[str] = mapped_column(
                        String(20), default="DRAFT",
                    )
                    is_active: Mapped[bool] = mapped_column(
                        Boolean, default=True,
                    )
                    deployed_at: Mapped[datetime | None] = mapped_column(
                        DateTime(timezone=True), nullable=True,
                    )
            '''),
        )

        # ─── entities/training_run.py ─────────────────
        self.writer.write(
            f"{base}/entities/training_run.py",
            dedent('''\
                """TrainingRun entity — ประวัติการฝึก"""
                from __future__ import annotations
                from datetime import datetime
                from sqlalchemy import DateTime, Integer, String, Text
                from sqlalchemy.dialects.postgresql import JSONB, UUID
                from sqlalchemy.orm import Mapped, mapped_column

                from app.modules.shared.infrastructure.models import BaseModel


                class TrainingRun(BaseModel):
                    """TH: training run | EN: training run entity"""
                    __tablename__ = "yolo_training_runs"

                    experiment_id: Mapped[str] = mapped_column(
                        UUID(as_uuid=True),
                    )
                    dataset_id: Mapped[str] = mapped_column(UUID(as_uuid=True))
                    status: Mapped[str] = mapped_column(
                        String(20), default="PENDING",
                    )
                    config_json: Mapped[dict] = mapped_column(
                        JSONB, default=dict,
                    )
                    seed: Mapped[int] = mapped_column(Integer, default=42)
                    duration_ms: Mapped[int] = mapped_column(
                        Integer, default=0,
                    )
                    error_message: Mapped[str] = mapped_column(
                        Text, default="",
                    )
                    started_at: Mapped[datetime | None] = mapped_column(
                        DateTime(timezone=True), nullable=True,
                    )
                    finished_at: Mapped[datetime | None] = mapped_column(
                        DateTime(timezone=True), nullable=True,
                    )
            '''),
        )

        # ─── entities/prediction.py ───────────────────
        self.writer.write(
            f"{base}/entities/prediction.py",
            dedent('''\
                """Prediction entity — log การทำนาย"""
                from __future__ import annotations
                from decimal import Decimal
                from sqlalchemy import Integer, Numeric, String
                from sqlalchemy.dialects.postgresql import JSONB, UUID
                from sqlalchemy.orm import Mapped, mapped_column

                from app.modules.shared.infrastructure.models import BaseModel


                class Prediction(BaseModel):
                    """TH: prediction | EN: prediction entity"""
                    __tablename__ = "yolo_predictions"

                    model_id: Mapped[str] = mapped_column(UUID(as_uuid=True))
                    input_hash: Mapped[str] = mapped_column(
                        String(64), default="",
                    )
                    output_json: Mapped[dict] = mapped_column(
                        JSONB, default=dict,
                    )
                    confidence: Mapped[Decimal] = mapped_column(
                        Numeric(12, 8), default=Decimal("0"),
                    )
                    latency_ms: Mapped[int] = mapped_column(
                        Integer, default=0,
                    )
                    source: Mapped[str] = mapped_column(
                        String(50), default="api",
                    )
            '''),
        )

        # ─── entities/metric.py ───────────────────────
        self.writer.write(
            f"{base}/entities/metric.py",
            dedent('''\
                """Metric entity — ค่า metric"""
                from __future__ import annotations
                from decimal import Decimal
                from sqlalchemy import Integer, Numeric, String
                from sqlalchemy.dialects.postgresql import UUID
                from sqlalchemy.orm import Mapped, mapped_column

                from app.modules.shared.infrastructure.models import BaseModel


                class Metric(BaseModel):
                    """TH: metric | EN: metric entity"""
                    __tablename__ = "yolo_metrics"

                    model_id: Mapped[str] = mapped_column(UUID(as_uuid=True))
                    name: Mapped[str] = mapped_column(String(50))
                    value: Mapped[Decimal] = mapped_column(
                        Numeric(12, 8), default=Decimal("0"),
                    )
                    step: Mapped[int] = mapped_column(Integer, default=0)
                    split: Mapped[str] = mapped_column(
                        String(20), default="test",
                    )
            '''),
        )

    # ─── APPLICATION LAYER ──────────────────────────────────────
    def _create_application(self) -> None:
        base = f"{self.mod_root}/application"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """ai_ml application layer — ชั้นแอปพลิเคชัน ai_ml"""
        '''))

        # ─── application/exceptions.py ────────────────
        self.writer.write(f"{base}/exceptions.py", dedent('''\
            """ai_ml application exceptions"""
            from __future__ import annotations


            class ApplicationError(Exception):
                """TH: base | EN: base"""
                code: str = "APP_ERROR"
                http_status: int = 400


            class DatasetNotFoundAppError(ApplicationError):
                code = "DATASET_NOT_FOUND"
                http_status = 404


            class ModelNotFoundAppError(ApplicationError):
                code = "MODEL_NOT_FOUND"
                http_status = 404


            class FeatureNotFoundAppError(ApplicationError):
                code = "FEATURE_NOT_FOUND"
                http_status = 404


            class ExperimentNotFoundAppError(ApplicationError):
                code = "EXPERIMENT_NOT_FOUND"
                http_status = 404


            class TrainingFailedAppError(ApplicationError):
                code = "TRAINING_FAILED"
                http_status = 500


            class SchemaMismatchAppError(ApplicationError):
                code = "SCHEMA_MISMATCH"
                http_status = 422
        '''))

        # ─── application/interfaces.py ────────────────
        self.writer.write(f"{base}/interfaces.py", dedent('''\
            """ai_ml application ports — อินเทอร์เฟซ"""
            from __future__ import annotations
            import uuid
            from abc import ABC, abstractmethod
            from datetime import datetime
            from typing import Any, Protocol

            from app.modules.ai_ml.domain.value_objects import (
                TrainConfig,
            )


            class RequestContext(Protocol):
                """TH: request context | EN: request context"""
                @property
                def tenant_id(self) -> uuid.UUID: ...
                @property
                def user_id(self) -> uuid.UUID | None: ...


            class DatasetRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, dataset: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(
                    self, ctx: Any, id: uuid.UUID,
                ) -> Any | None: ...
                @abstractmethod
                async def find_by_name(
                    self, ctx: Any, name: str,
                ) -> Any | None: ...
                @abstractmethod
                async def find_paginated(
                    self, ctx: Any, page: int, size: int,
                ) -> tuple[list[Any], int]: ...
                @abstractmethod
                async def update(self, ctx: Any, dataset: Any) -> Any: ...
                @abstractmethod
                async def delete(self, ctx: Any, id: uuid.UUID) -> bool: ...


            class FeatureRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, feature: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(
                    self, ctx: Any, id: uuid.UUID,
                ) -> Any | None: ...
                @abstractmethod
                async def find_by_name(
                    self, ctx: Any, name: str,
                ) -> Any | None: ...
                @abstractmethod
                async def find_by_dataset(
                    self, ctx: Any, dataset_id: uuid.UUID,
                ) -> list[Any]: ...
                @abstractmethod
                async def find_online(
                    self, ctx: Any, entity_key: str,
                ) -> list[Any]: ...


            class ExperimentRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, experiment: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(
                    self, ctx: Any, id: uuid.UUID,
                ) -> Any | None: ...
                @abstractmethod
                async def find_all(
                    self, ctx: Any, limit: int,
                ) -> list[Any]: ...


            class ModelRepository(ABC):
                @abstractmethod
                async def save(self, ctx: Any, model: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(
                    self, ctx: Any, id: uuid.UUID,
                ) -> Any | None: ...
                @abstractmethod
                async def find_by_name_version(
                    self, ctx: Any, name: str, version: int,
                ) -> Any | None: ...
                @abstractmethod
                async def find_all_active(self, ctx: Any) -> list[Any]: ...
                @abstractmethod
                async def find_deployed(self, ctx: Any) -> list[Any]: ...
                @abstractmethod
                async def update(self, ctx: Any, model: Any) -> Any: ...


            class TrainingRunRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, run: Any) -> Any: ...
                @abstractmethod
                async def find_by_id(
                    self, ctx: Any, id: uuid.UUID,
                ) -> Any | None: ...
                @abstractmethod
                async def find_by_experiment(
                    self, ctx: Any, experiment_id: uuid.UUID,
                ) -> list[Any]: ...
                @abstractmethod
                async def update_status(
                    self, ctx: Any, id: uuid.UUID, status: str,
                ) -> None: ...


            class PredictionRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, prediction: Any) -> Any: ...
                @abstractmethod
                async def find_by_model(
                    self, ctx: Any, model_id: uuid.UUID, limit: int,
                ) -> list[Any]: ...
                @abstractmethod
                async def count_by_model(
                    self, ctx: Any, model_id: uuid.UUID,
                ) -> int: ...


            class MetricRepository(ABC):
                @abstractmethod
                async def create(self, ctx: Any, metric: Any) -> Any: ...
                @abstractmethod
                async def find_by_model(
                    self, ctx: Any, model_id: uuid.UUID,
                ) -> list[Any]: ...
                @abstractmethod
                async def aggregate(
                    self, ctx: Any, model_id: uuid.UUID, name: str,
                ) -> dict[str, Any]: ...


            class FeatureStore(Protocol):
                async def get_online(
                    self, entity_id: str, features: list[str],
                ) -> dict[str, Any]: ...
                async def get_offline(
                    self, entity_ids: list[str],
                    features: list[str], timestamp: datetime,
                ) -> Any: ...
                async def materialize(
                    self, feature_name: str, since: datetime,
                ) -> int: ...


            class ModelServer(Protocol):
                async def load(
                    self, model_id: uuid.UUID, artifact_uri: str,
                ) -> None: ...
                async def infer(
                    self, model_id: uuid.UUID, features: dict[str, Any],
                ) -> dict[str, Any]: ...
                async def unload(self, model_id: uuid.UUID) -> None: ...


            class Trainer(Protocol):
                async def train(
                    self, config: TrainConfig, dataset: Any,
                ) -> dict[str, Any]: ...


            class ArtifactStore(Protocol):
                async def save(
                    self, path: str, data: bytes,
                    metadata: dict[str, Any],
                ) -> str: ...
                async def load(self, uri: str) -> bytes: ...
                async def exists(self, uri: str) -> bool: ...
                async def delete(self, uri: str) -> bool: ...


            class DriftDetector(Protocol):
                def detect(
                    self, reference: Any, current: Any,
                ) -> dict[str, Any]: ...


            class EventBus(ABC):
                @abstractmethod
                async def publish(self, event: object) -> None: ...


            class IdempotencyStore(ABC):
                @abstractmethod
                async def check_or_lock(
                    self, key: str, scope: str,
                    payload: dict[str, Any],
                ) -> dict[str, Any] | None: ...
                @abstractmethod
                async def complete(
                    self, key: str, scope: str,
                    status: int, body: dict[str, Any],
                ) -> None: ...


            class yoloCache(ABC):
                @abstractmethod
                async def get(self, key: str) -> Any | None: ...
                @abstractmethod
                async def set(
                    self, key: str, value: Any, ttl: int = 300,
                ) -> bool: ...
                @abstractmethod
                async def invalidate(self, key: str) -> bool: ...


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
        '''))

        # ─── application/mappers.py ───────────────────
        self.writer.write(f"{base}/mappers.py", dedent('''\
            """ai_ml mappers — ORM ↔ domain"""
            from __future__ import annotations
            from typing import Any


            def dataset_to_dict(row: Any) -> dict[str, Any]:
                """TH: dataset → dict | EN: dataset to dict"""
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "source_uri": row.source_uri,
                    "content_hash": row.content_hash,
                    "rows": row.rows,
                    "cols": row.cols,
                    "status": row.status,
                    "version": row.version,
                    "created_at": (
                        row.created_at.isoformat() if row.created_at else ""
                    ),
                }


            def model_to_dict(row: Any) -> dict[str, Any]:
                """TH: model → dict | EN: model to dict"""
                return {
                    "id": str(row.id),
                    "experiment_id": str(row.experiment_id),
                    "name": row.name,
                    "version": row.version,
                    "task_type": row.task_type,
                    "algorithm": row.algorithm,
                    "status": row.status,
                    "artifact_uri": row.artifact_uri,
                    "metrics": dict(row.metrics_json or {}),
                }


            def experiment_to_dict(row: Any) -> dict[str, Any]:
                """TH: experiment → dict | EN: experiment to dict"""
                return {
                    "id": str(row.id),
                    "name": row.name,
                    "description": row.description,
                    "task_type": row.task_type,
                    "status": row.status,
                    "best_model_id": (
                        str(row.best_model_id) if row.best_model_id else None
                    ),
                }


            def run_to_dict(row: Any) -> dict[str, Any]:
                """TH: training run → dict | EN: training run to dict"""
                return {
                    "id": str(row.id),
                    "experiment_id": str(row.experiment_id),
                    "dataset_id": str(row.dataset_id),
                    "status": row.status,
                    "duration_ms": row.duration_ms,
                    "seed": row.seed,
                    "error_message": row.error_message,
                }
        '''))

        # ─── application/utils.py ─────────────────────
        self.writer.write(f"{base}/utils.py", dedent('''\
            """ai_ml application utils"""
            from __future__ import annotations
            import hashlib
            import json
            from typing import Any


            def hash_payload(payload: dict[str, Any]) -> str:
                """TH: hash payload (deterministic)"""
                raw = json.dumps(payload, sort_keys=True, default=str)
                return hashlib.sha256(raw.encode()).hexdigest()


            def hash_bytes(data: bytes) -> str:
                """TH: hash bytes"""
                return hashlib.sha256(data).hexdigest()[:32]


            def sanitize_payload(data: dict[str, Any]) -> dict[str, Any]:
                """TH: ทำความสะอาด payload | EN: sanitize payload"""
                MASK = {
                    "api_key", "api_key_encrypted", "password",
                    "token", "secret", "raw_data",
                }
                return {
                    k: ("***" if k in MASK else v)
                    for k, v in data.items()
                }


            def infer_dtype(value: Any) -> str:
                """TH: ทำนาย dtype | EN: infer dtype"""
                if isinstance(value, bool):
                    return "bool"
                if isinstance(value, int):
                    return "int"
                if isinstance(value, float):
                    return "float"
                if isinstance(value, str):
                    return "str"
                return "unknown"
        '''))

        # ─── application/use_case.py ──────────────────
        self.writer.write(f"{base}/use_case.py", self._use_case_content())

    def _use_case_content(self) -> str:
        return dedent('''\
            """ai_ml use cases — กรณีการใช้งาน ai_ml"""
            from __future__ import annotations

            import uuid
            from datetime import UTC, datetime
            from decimal import Decimal
            from typing import Any

            import structlog

            from app.modules.ai_ml.application.interfaces import (
                yoloCache, ArtifactStore, DatasetRepository,
                DriftDetector, EventBus, ExperimentRepository,
                FeatureRepository, FeatureStore, MetricRepository,
                ModelRepository, ModelServer, PredictionRepository,
                RateLimiter, RequestContext, Trainer,
                TrainingRunRepository,
            )
            from app.modules.ai_ml.application.utils import (
                hash_bytes, hash_payload,
            )
            from app.modules.ai_ml.domain.enums import (
                DatasetStatus, MetricName, ModelStatus, TaskType,
                TrainingStatus,
            )
            from app.modules.ai_ml.domain.events import (
                DatasetRegistered, ModelDeployed,
                ModelDriftDetected, PredictionServed,
                TrainingCompleted,
            )
            from app.modules.ai_ml.domain.exceptions import (
                DatasetNotFoundError, ModelNotFoundError,
                TrainingFailedError,
            )
            from app.modules.ai_ml.domain.value_objects import (
                PredictionResult, TrainConfig,
            )
            from app.modules.ai_ml.infrastructure.models import (
                DatasetModel, MetricModel, MLModel, PredictionModel,
                TrainingRunModel,
            )

            log = structlog.get_logger()


            class yoloUseCase:
                """TH: use cases รวมทุก operation | EN: all AI/ML operations"""

                def __init__(
                    self,
                    dataset_repo: DatasetRepository,
                    feature_repo: FeatureRepository,
                    experiment_repo: ExperimentRepository,
                    model_repo: ModelRepository,
                    run_repo: TrainingRunRepository,
                    prediction_repo: PredictionRepository,
                    metric_repo: MetricRepository,
                    feature_store: FeatureStore,
                    model_server: ModelServer,
                    trainer: Trainer,
                    artifact_store: ArtifactStore,
                    drift_detector: DriftDetector,
                    cache: yoloCache,
                    rate_limiter: RateLimiter,
                    event_bus: EventBus,
                ) -> None:
                    self._dataset_repo = dataset_repo
                    self._feature_repo = feature_repo
                    self._experiment_repo = experiment_repo
                    self._model_repo = model_repo
                    self._run_repo = run_repo
                    self._prediction_repo = prediction_repo
                    self._metric_repo = metric_repo
                    self._feature_store = feature_store
                    self._model_server = model_server
                    self._trainer = trainer
                    self._artifact_store = artifact_store
                    self._drift = drift_detector
                    self._cache = cache
                    self._rate = rate_limiter
                    self._bus = event_bus

                # ─── Datasets ────────────────────────────
                async def register_dataset(
                    self,
                    ctx: RequestContext,
                    name: str,
                    source_uri: str,
                    rows: int = 0,
                    cols: int = 0,
                    schema_json: dict[str, Any] | None = None,
                    profile_json: dict[str, Any] | None = None,
                ) -> dict[str, Any]:
                    """TH: ลงทะเบียน dataset | EN: register dataset"""
                    log.info("yolo.dataset.register", name=name)
                    try:
                        existing = await self._dataset_repo.find_by_name(
                            ctx, name,
                        )
                        version = (existing.version + 1) if existing else 1

                        content_hash = hash_payload({
                            "name": name,
                            "source_uri": source_uri,
                            "rows": rows,
                            "cols": cols,
                        })

                        ds = DatasetModel(
                            tenant_id=ctx.tenant_id,
                            name=name,
                            source_uri=source_uri,
                            content_hash=content_hash,
                            rows=rows,
                            cols=cols,
                            status=DatasetStatus.RAW.value,
                            version=version,
                            schema_json=schema_json or {},
                            profile_json=profile_json or {},
                        )
                        saved = await self._dataset_repo.save(ctx, ds)
                        await self._bus.publish(DatasetRegistered(
                            dataset_id=saved.id,
                            tenant_id=ctx.tenant_id,
                            name=name,
                            rows=rows,
                            cols=cols,
                        ))
                        return {
                            "id": str(saved.id),
                            "name": saved.name,
                            "version": saved.version,
                            "status": saved.status,
                            "content_hash": saved.content_hash,
                            "rows": saved.rows,
                            "cols": saved.cols,
                        }
                    except Exception:
                        log.exception("yolo.dataset.register.failed")
                        raise

                async def list_datasets(
                    self, ctx: RequestContext, page: int = 1, size: int = 50,
                ) -> dict[str, Any]:
                    """TH: list datasets | EN: list datasets"""
                    rows, total = await self._dataset_repo.find_paginated(
                        ctx, page, size,
                    )
                    return {
                        "items": [
                            {
                                "id": str(r.id),
                                "name": r.name,
                                "status": r.status,
                                "version": r.version,
                                "rows": r.rows,
                                "cols": r.cols,
                            }
                            for r in rows
                        ],
                        "total": total,
                        "page": page,
                        "size": size,
                    }

                async def get_dataset(
                    self, ctx: RequestContext, dataset_id: uuid.UUID,
                ) -> dict[str, Any]:
                    """TH: ดู dataset | EN: get dataset"""
                    ds = await self._dataset_repo.find_by_id(
                        ctx, dataset_id,
                    )
                    if ds is None:
                        raise DatasetNotFoundError(
                            f"dataset {dataset_id} not found",
                        )
                    return {
                        "id": str(ds.id),
                        "name": ds.name,
                        "source_uri": ds.source_uri,
                        "content_hash": ds.content_hash,
                        "rows": ds.rows,
                        "cols": ds.cols,
                        "status": ds.status,
                        "version": ds.version,
                        "schema": dict(ds.schema_json or {}),
                        "profile": dict(ds.profile_json or {}),
                    }

                # ─── Training ────────────────────────────
                async def start_training(
                    self,
                    ctx: RequestContext,
                    experiment_id: uuid.UUID,
                    dataset_id: uuid.UUID,
                    config: TrainConfig,
                ) -> dict[str, Any]:
                    """TH: เริ่มการฝึก | EN: start training (3-branch)"""
                    log.info("yolo.train.start", dataset=str(dataset_id))
                    try:
                        ds = await self._dataset_repo.find_by_id(
                            ctx, dataset_id,
                        )
                        if ds is None:
                            raise DatasetNotFoundError(
                                f"dataset {dataset_id} not found",
                            )

                        allowed = await self._rate.check(
                            ctx.tenant_id,
                            ctx.user_id or uuid.uuid4(),
                            cost=100,
                        )
                        if not allowed:
                            raise TrainingFailedError("rate limit exceeded")

                        run = TrainingRunModel(
                            tenant_id=ctx.tenant_id,
                            experiment_id=experiment_id,
                            dataset_id=dataset_id,
                            status=TrainingStatus.PENDING.value,
                            config_json={
                                "test_size": config.test_size,
                                "random_state": config.random_state,
                                "cv_folds": config.cv_folds,
                                "scaler": config.scaler,
                                "algorithm": config.algorithm,
                                "hyperparams": config.hyperparams_dict(),
                            },
                            seed=config.random_state,
                            started_at=datetime.now(UTC),
                        )
                        saved_run = await self._run_repo.create(ctx, run)

                        try:
                            await self._run_repo.update_status(
                                ctx, saved_run.id, TrainingStatus.RUNNING.value,
                            )
                            result = await self._trainer.train(
                                config, {"dataset_id": str(dataset_id)},
                            )
                        except Exception as exc:
                            await self._run_repo.update_status(
                                ctx, saved_run.id,
                                TrainingStatus.FAILED.value,
                            )
                            log.error(f"train.failed: {exc}")
                            raise TrainingFailedError(str(exc)) from exc

                        metrics_dict = result.get("metrics", {})
                        artifact_uri = result.get("artifact_uri", "")
                        artifact_hash = hash_bytes(
                            str(metrics_dict).encode(),
                        )
                        duration_ms = int(result.get("duration_ms", 0))

                        model = MLModel(
                            tenant_id=ctx.tenant_id,
                            experiment_id=experiment_id,
                            name=result.get("name", f"model-{saved_run.id}"),
                            version=1,
                            task_type=result.get(
                                "task_type", TaskType.CLASSIFICATION.value,
                            ),
                            algorithm=config.algorithm,
                            hyperparams_json=config.hyperparams_dict(),
                            artifact_uri=artifact_uri,
                            artifact_hash=artifact_hash,
                            metrics_json=metrics_dict,
                            status=ModelStatus.TRAINED.value,
                        )
                        saved_model = await self._model_repo.save(ctx, model)

                        for metric_name, value in metrics_dict.items():
                            try:
                                m = MetricModel(
                                    tenant_id=ctx.tenant_id,
                                    model_id=saved_model.id,
                                    name=metric_name,
                                    value=Decimal(str(value)),
                                    step=0,
                                    split="test",
                                )
                                await self._metric_repo.create(ctx, m)
                            except Exception as exc:
                                log.warning(
                                    f"metric.save_failed name={metric_name}: {exc}",
                                )

                        await self._run_repo.update_status(
                            ctx, saved_run.id, TrainingStatus.SUCCESS.value,
                        )

                        await self._bus.publish(TrainingCompleted(
                            training_run_id=saved_run.id,
                            model_id=saved_model.id,
                            tenant_id=ctx.tenant_id,
                            metrics=metrics_dict,
                            duration_ms=duration_ms,
                        ))

                        return {
                            "training_run_id": str(saved_run.id),
                            "model_id": str(saved_model.id),
                            "status": TrainingStatus.SUCCESS.value,
                            "metrics": metrics_dict,
                            "duration_ms": duration_ms,
                        }

                    except TrainingFailedError:
                        raise
                    except Exception:
                        log.exception("yolo.train.unexpected")
                        raise

                async def get_training_status(
                    self, ctx: RequestContext, run_id: uuid.UUID,
                ) -> dict[str, Any]:
                    """TH: ดูสถานะการฝึก | EN: get training status"""
                    run = await self._run_repo.find_by_id(ctx, run_id)
                    if run is None:
                        raise DatasetNotFoundError(
                            f"training run {run_id} not found",
                        )
                    return {
                        "id": str(run.id),
                        "experiment_id": str(run.experiment_id),
                        "dataset_id": str(run.dataset_id),
                        "status": run.status,
                        "duration_ms": run.duration_ms,
                        "seed": run.seed,
                        "error_message": run.error_message,
                        "started_at": (
                            run.started_at.isoformat()
                            if run.started_at else None
                        ),
                        "finished_at": (
                            run.finished_at.isoformat()
                            if run.finished_at else None
                        ),
                    }

                # ─── Models ──────────────────────────────
                async def list_models(
                    self, ctx: RequestContext, only_active: bool = True,
                ) -> list[dict[str, Any]]:
                    """TH: list models | EN: list models"""
                    rows = (
                        await self._model_repo.find_all_active(ctx)
                        if only_active
                        else await self._model_repo.find_deployed(ctx)
                    )
                    return [
                        {
                            "id": str(r.id),
                            "name": r.name,
                            "version": r.version,
                            "task_type": r.task_type,
                            "algorithm": r.algorithm,
                            "status": r.status,
                            "metrics": dict(r.metrics_json or {}),
                        }
                        for r in rows
                    ]

                async def get_model(
                    self, ctx: RequestContext, model_id: uuid.UUID,
                ) -> dict[str, Any]:
                    """TH: ดู model | EN: get model"""
                    m = await self._model_repo.find_by_id(ctx, model_id)
                    if m is None:
                        raise ModelNotFoundError(
                            f"model {model_id} not found",
                        )
                    metrics = await self._metric_repo.find_by_model(
                        ctx, model_id,
                    )
                    return {
                        "id": str(m.id),
                        "name": m.name,
                        "version": m.version,
                        "task_type": m.task_type,
                        "algorithm": m.algorithm,
                        "status": m.status,
                        "artifact_uri": m.artifact_uri,
                        "artifact_hash": m.artifact_hash,
                        "metrics": dict(m.metrics_json or {}),
                        "metric_rows": [
                            {
                                "name": row.name,
                                "value": str(row.value),
                                "step": row.step,
                                "split": row.split,
                            }
                            for row in metrics
                        ],
                    }

                async def deploy_model(
                    self, ctx: RequestContext, model_id: uuid.UUID,
                ) -> dict[str, Any]:
                    """TH: deploy model | EN: deploy model"""
                    m = await self._model_repo.find_by_id(ctx, model_id)
                    if m is None:
                        raise ModelNotFoundError(
                            f"model {model_id} not found",
                        )

                    try:
                        await self._model_server.load(
                            model_id, m.artifact_uri,
                        )
                    except Exception as exc:
                        log.warning(
                            f"model_server.load_failed: {exc}",
                        )

                    m.status = ModelStatus.DEPLOYED.value
                    m.deployed_at = datetime.now(UTC)
                    await self._model_repo.update(ctx, m)

                    await self._bus.publish(ModelDeployed(
                        model_id=model_id,
                        tenant_id=ctx.tenant_id,
                        version=m.version,
                    ))

                    return {
                        "id": str(m.id),
                        "status": m.status,
                        "deployed_at": (
                            m.deployed_at.isoformat()
                            if m.deployed_at else None
                        ),
                    }

                async def archive_model(
                    self, ctx: RequestContext, model_id: uuid.UUID,
                ) -> dict[str, Any]:
                    """TH: archive model | EN: archive model"""
                    m = await self._model_repo.find_by_id(ctx, model_id)
                    if m is None:
                        raise ModelNotFoundError(
                            f"model {model_id} not found",
                        )
                    m.status = ModelStatus.ARCHIVED.value
                    m.is_active = False
                    await self._model_repo.update(ctx, m)
                    try:
                        await self._model_server.unload(model_id)
                    except Exception as exc:
                        log.warning(f"model_server.unload_failed: {exc}")
                    return {"id": str(m.id), "status": m.status}

                # ─── Prediction ──────────────────────────
                async def predict(
                    self,
                    ctx: RequestContext,
                    model_id: uuid.UUID,
                    features: dict[str, Any],
                    source: str = "api",
                ) -> dict[str, Any]:
                    """TH: ทำนาย | EN: predict (3-branch)"""
                    log.info("yolo.predict.start", model=str(model_id))
                    try:
                        m = await self._model_repo.find_by_id(ctx, model_id)
                        if m is None:
                            raise ModelNotFoundError(
                                f"model {model_id} not found",
                            )

                        input_hash = hash_payload(features)
                        cache_key = f"yolo:pred:{model_id}:{input_hash}"
                        cached = await self._cache.get(cache_key)
                        if cached:
                            log.info("yolo.predict.cache_hit")
                            return cached

                        allowed = await self._rate.check(
                            ctx.tenant_id,
                            ctx.user_id or uuid.uuid4(),
                            cost=1,
                        )
                        if not allowed:
                            raise TrainingFailedError(
                                "rate limit exceeded",
                            )

                        try:
                            result = await self._model_server.infer(
                                model_id, features,
                            )
                        except Exception as exc:
                            log.warning(f"model_server.infer_failed: {exc}")
                            result = {"output": None, "confidence": 0.0}

                        prediction = PredictionResult(
                            output=result.get("output"),
                            confidence=float(result.get("confidence", 0.0)),
                            latency_ms=int(result.get("latency_ms", 0)),
                        )

                        pred_row = PredictionModel(
                            tenant_id=ctx.tenant_id,
                            model_id=model_id,
                            input_hash=input_hash,
                            output_json={"output": prediction.output},
                            confidence=Decimal(str(prediction.confidence)),
                            latency_ms=prediction.latency_ms,
                            source=source,
                        )
                        saved = await self._prediction_repo.create(
                            ctx, pred_row,
                        )

                        response = {
                            "prediction_id": str(saved.id),
                            "model_id": str(model_id),
                            "output": prediction.output,
                            "confidence": prediction.confidence,
                            "latency_ms": prediction.latency_ms,
                        }
                        await self._cache.set(cache_key, response, ttl=300)

                        await self._bus.publish(PredictionServed(
                            prediction_id=saved.id,
                            model_id=model_id,
                            tenant_id=ctx.tenant_id,
                            latency_ms=prediction.latency_ms,
                        ))

                        return response

                    except ModelNotFoundError:
                        raise
                    except Exception:
                        log.exception("yolo.predict.unexpected")
                        raise

                # ─── Metrics & Drift ─────────────────────
                async def get_metrics(
                    self, ctx: RequestContext, model_id: uuid.UUID,
                ) -> dict[str, Any]:
                    """TH: ดู metrics | EN: get metrics"""
                    rows = await self._metric_repo.find_by_model(
                        ctx, model_id,
                    )
                    return {
                        "model_id": str(model_id),
                        "metrics": [
                            {
                                "name": r.name,
                                "value": str(r.value),
                                "step": r.step,
                                "split": r.split,
                            }
                            for r in rows
                        ],
                    }

                async def check_drift(
                    self,
                    ctx: RequestContext,
                    model_id: uuid.UUID,
                    reference: Any,
                    current: Any,
                    threshold: float = 0.3,
                ) -> dict[str, Any]:
                    """TH: ตรวจ drift | EN: check drift"""
                    try:
                        result = self._drift.detect(reference, current)
                    except Exception as exc:
                        log.warning(f"drift.detect_failed: {exc}")
                        result = {"drift_score": 0.0, "drifted": False}

                    score = float(result.get("drift_score", 0.0))
                    if score > threshold:
                        await self._bus.publish(ModelDriftDetected(
                            model_id=model_id,
                            tenant_id=ctx.tenant_id,
                            drift_score=score,
                            threshold=threshold,
                        ))
                    return {
                        "model_id": str(model_id),
                        "drift_score": score,
                        "threshold": threshold,
                        "drifted": score > threshold,
                    }
        ''')

    # ─── INFRASTRUCTURE LAYER ───────────────────────────────────
    def _create_infrastructure(self) -> None:
        base = f"{self.mod_root}/infrastructure"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """ai_ml infrastructure layer"""
        '''))

        self.writer.write(f"{base}/models.py", self._models_content())
        self.writer.write(
            f"{base}/dataset_repository.py",
            self._dataset_repo_content(),
        )
        self.writer.write(
            f"{base}/feature_repository.py",
            self._feature_repo_content(),
        )
        self.writer.write(
            f"{base}/experiment_repository.py",
            self._experiment_repo_content(),
        )
        self.writer.write(
            f"{base}/model_repository.py",
            self._model_repo_content(),
        )
        self.writer.write(
            f"{base}/training_run_repository.py",
            self._run_repo_content(),
        )
        self.writer.write(
            f"{base}/prediction_repository.py",
            self._pred_repo_content(),
        )
        self.writer.write(
            f"{base}/metric_repository.py",
            self._metric_repo_content(),
        )
        self.writer.write(f"{base}/caches.py", self._caches_content())
        self.writer.write(f"{base}/services.py", self._services_content())
        self.writer.write(
            f"{base}/artifact_store.py",
            self._artifact_store_content(),
        )

    def _models_content(self) -> str:
        return dedent('''\
            """ai_ml SQLAlchemy 2.0 models — schema=public, prefix=yolo_"""
            from __future__ import annotations
            import uuid
            from datetime import datetime
            from decimal import Decimal

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, Index, Integer,
                Numeric, String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import JSONB, UUID
            from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

            SCHEMA = "public"


            class Base(DeclarativeBase):
                """TH: declarative base | EN: declarative base"""


            class DatasetModel(Base):
                __tablename__ = "yolo_datasets"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('RAW','PROCESSED','ARCHIVED')",
                        name="ck_yolo_dataset_status",
                    ),
                    UniqueConstraint(
                        "tenant_id", "name", "version",
                        name="uq_yolo_dataset_name_ver",
                    ),
                    Index("ix_yolo_dataset_tenant", "tenant_id"),
                    Index("ix_yolo_dataset_status", "tenant_id", "status"),
                    Index("ix_yolo_dataset_hash", "content_hash"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                name: Mapped[str] = mapped_column(String(200), nullable=False)
                source_uri: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                content_hash: Mapped[str] = mapped_column(
                    String(64), nullable=False, server_default="",
                )
                rows: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                cols: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                status: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="RAW",
                )
                version: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="1",
                )
                schema_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"),
                )
                profile_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"),
                )
                metadata_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"),
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class FeatureModel(Base):
                __tablename__ = "yolo_features"
                __table_args__ = (
                    UniqueConstraint(
                        "tenant_id", "name", name="uq_yolo_feature_name",
                    ),
                    Index("ix_yolo_feature_tenant", "tenant_id"),
                    Index("ix_yolo_feature_online", "tenant_id", "is_online"),
                    Index("ix_yolo_feature_entity", "entity_key"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                name: Mapped[str] = mapped_column(String(200), nullable=False)
                dtype: Mapped[str] = mapped_column(
                    String(50), nullable=False, server_default="float",
                )
                transform: Mapped[str] = mapped_column(
                    String(100), nullable=False, server_default="",
                )
                source_dataset_id: Mapped[uuid.UUID | None] = mapped_column(
                    UUID(as_uuid=True), nullable=True,
                )
                entity_key: Mapped[str] = mapped_column(
                    String(100), nullable=False, server_default="",
                )
                ttl_seconds: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="3600",
                )
                is_online: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("true"),
                )
                metadata_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"),
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class ExperimentModel(Base):
                __tablename__ = "yolo_experiments"
                __table_args__ = (
                    CheckConstraint(
                        "task_type IN ('CLASSIFICATION','REGRESSION',"
                        "'CLUSTERING','DIM_REDUCTION','RECOMMENDATION')",
                        name="ck_yolo_exp_task",
                    ),
                    CheckConstraint(
                        "status IN ('ACTIVE','COMPLETED','ARCHIVED')",
                        name="ck_yolo_exp_status",
                    ),
                    Index("ix_yolo_exp_tenant", "tenant_id"),
                    Index("ix_yolo_exp_task", "task_type", "status"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                name: Mapped[str] = mapped_column(String(200), nullable=False)
                description: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                task_type: Mapped[str] = mapped_column(
                    String(50), nullable=False,
                )
                status: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="ACTIVE",
                )
                best_model_id: Mapped[uuid.UUID | None] = mapped_column(
                    UUID(as_uuid=True), nullable=True,
                )
                metadata_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"),
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class MLModel(Base):
                __tablename__ = "yolo_models"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('DRAFT','TRAINED','DEPLOYED','ARCHIVED')",
                        name="ck_yolo_model_status",
                    ),
                    UniqueConstraint(
                        "tenant_id", "name", "version",
                        name="uq_yolo_model_name_ver",
                    ),
                    Index("ix_yolo_model_tenant", "tenant_id"),
                    Index("ix_yolo_model_status", "tenant_id", "status"),
                    Index("ix_yolo_model_experiment", "experiment_id"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                experiment_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                name: Mapped[str] = mapped_column(String(200), nullable=False)
                version: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="1",
                )
                task_type: Mapped[str] = mapped_column(
                    String(50), nullable=False,
                )
                algorithm: Mapped[str] = mapped_column(
                    String(100), nullable=False, server_default="",
                )
                hyperparams_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"),
                )
                artifact_uri: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                artifact_hash: Mapped[str] = mapped_column(
                    String(64), nullable=False, server_default="",
                )
                metrics_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"),
                )
                status: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="DRAFT",
                )
                is_active: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("true"),
                )
                deployed_at: Mapped[datetime | None] = mapped_column(
                    DateTime(timezone=True), nullable=True,
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class TrainingRunModel(Base):
                __tablename__ = "yolo_training_runs"
                __table_args__ = (
                    CheckConstraint(
                        "status IN ('PENDING','RUNNING','SUCCESS',"
                        "'FAILED','CANCELLED')",
                        name="ck_yolo_run_status",
                    ),
                    Index("ix_yolo_run_tenant", "tenant_id", "status"),
                    Index("ix_yolo_run_experiment", "experiment_id",
                          "created_at"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                experiment_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                dataset_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                status: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="PENDING",
                )
                config_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"),
                )
                seed: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="42",
                )
                duration_ms: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                error_message: Mapped[str] = mapped_column(
                    Text, nullable=False, server_default="",
                )
                started_at: Mapped[datetime | None] = mapped_column(
                    DateTime(timezone=True), nullable=True,
                )
                finished_at: Mapped[datetime | None] = mapped_column(
                    DateTime(timezone=True), nullable=True,
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class PredictionModel(Base):
                __tablename__ = "yolo_predictions"
                __table_args__ = (
                    Index("ix_yolo_pred_tenant", "tenant_id", "created_at"),
                    Index("ix_yolo_pred_model", "model_id", "created_at"),
                    Index("ix_yolo_pred_hash", "input_hash"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                model_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                input_hash: Mapped[str] = mapped_column(
                    String(64), nullable=False, server_default="",
                )
                output_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"),
                )
                confidence: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                latency_ms: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                source: Mapped[str] = mapped_column(
                    String(50), nullable=False, server_default="api",
                )
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(),
                )
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False,
                    server_default=func.now(), onupdate=func.now(),
                )


            class MetricModel(Base):
                __tablename__ = "yolo_metrics"
                __table_args__ = (
                    CheckConstraint(
                        "name IN ('accuracy','f1','precision','recall',"
                        "'rmse','mae','r2','silhouette')",
                        name="ck_yolo_metric_name",
                    ),
                    CheckConstraint(
                        "split IN ('train','val','test')",
                        name="ck_yolo_metric_split",
                    ),
                    Index("ix_yolo_metric_tenant", "tenant_id"),
                    Index("ix_yolo_metric_model", "model_id", "name"),
                    Index("ix_yolo_metric_time", "tenant_id", "created_at"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"),
                )
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                model_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False,
                )
                name: Mapped[str] = mapped_column(String(50), nullable=False)
                value: Mapped[Decimal] = mapped_column(
                    Numeric(12, 8), nullable=False, server_default="0",
                )
                step: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="0",
                )
                split: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="test",
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

    def _dataset_repo_content(self) -> str:
        return dedent('''\
            """Dataset repository — SQLAlchemy 2.0 async (2-branch)"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.ai_ml.application.exceptions import (
                ApplicationError,
            )
            from app.modules.ai_ml.infrastructure.models import DatasetModel


            class DatasetRepository:
                """TH: dataset repo | EN: dataset repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(
                    self, ctx: object, id: uuid.UUID,
                ) -> DatasetModel | None:
                    try:
                        result = await self._session.execute(
                            select(DatasetModel).where(
                                DatasetModel.id == id,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_name(
                    self, ctx: object, name: str,
                ) -> DatasetModel | None:
                    try:
                        result = await self._session.execute(
                            select(DatasetModel)
                            .where(DatasetModel.name == name)
                            .order_by(DatasetModel.version.desc())
                            .limit(1)
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.find_by_name failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_paginated(
                    self, ctx: object, page: int = 1, size: int = 50,
                ) -> tuple[list[DatasetModel], int]:
                    try:
                        count_result = await self._session.execute(
                            select(func.count()).select_from(DatasetModel)
                        )
                        total = int(count_result.scalar() or 0)
                        result = await self._session.execute(
                            select(DatasetModel)
                            .order_by(DatasetModel.created_at.desc())
                            .offset((page - 1) * size)
                            .limit(size)
                        )
                        return list(result.scalars().all()), total
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.find_paginated failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(
                    self, ctx: object, dataset: DatasetModel,
                ) -> DatasetModel:
                    try:
                        self._session.add(dataset)
                        await self._session.flush()
                        return dataset
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def update(
                    self, ctx: object, dataset: DatasetModel,
                ) -> DatasetModel:
                    try:
                        await self._session.flush()
                        return dataset
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.update failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def delete(
                    self, ctx: object, id: uuid.UUID,
                ) -> bool:
                    try:
                        ds = await self.find_by_id(ctx, id)
                        if ds:
                            ds.status = "ARCHIVED"
                            await self._session.flush()
                            return True
                        return False
                    except SQLAlchemyError as exc:
                        logger.error(f"dataset.delete failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _feature_repo_content(self) -> str:
        return dedent('''\
            """Feature repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.ai_ml.application.exceptions import (
                ApplicationError,
            )
            from app.modules.ai_ml.infrastructure.models import FeatureModel


            class FeatureRepository:
                """TH: feature repo | EN: feature repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(
                    self, ctx: object, id: uuid.UUID,
                ) -> FeatureModel | None:
                    try:
                        result = await self._session.execute(
                            select(FeatureModel).where(
                                FeatureModel.id == id,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"feature.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_name(
                    self, ctx: object, name: str,
                ) -> FeatureModel | None:
                    try:
                        result = await self._session.execute(
                            select(FeatureModel).where(
                                FeatureModel.name == name,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"feature.find_by_name failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_dataset(
                    self, ctx: object, dataset_id: uuid.UUID,
                ) -> list[FeatureModel]:
                    try:
                        result = await self._session.execute(
                            select(FeatureModel).where(
                                FeatureModel.source_dataset_id == dataset_id,
                            )
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"feature.find_by_dataset failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_online(
                    self, ctx: object, entity_key: str,
                ) -> list[FeatureModel]:
                    try:
                        result = await self._session.execute(
                            select(FeatureModel).where(
                                FeatureModel.entity_key == entity_key,
                                FeatureModel.is_online.is_(True),
                            )
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"feature.find_online failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(
                    self, ctx: object, feature: FeatureModel,
                ) -> FeatureModel:
                    try:
                        self._session.add(feature)
                        await self._session.flush()
                        return feature
                    except SQLAlchemyError as exc:
                        logger.error(f"feature.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _experiment_repo_content(self) -> str:
        return dedent('''\
            """Experiment repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.ai_ml.application.exceptions import (
                ApplicationError,
            )
            from app.modules.ai_ml.infrastructure.models import (
                ExperimentModel,
            )


            class ExperimentRepository:
                """TH: experiment repo | EN: experiment repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(
                    self, ctx: object, id: uuid.UUID,
                ) -> ExperimentModel | None:
                    try:
                        result = await self._session.execute(
                            select(ExperimentModel).where(
                                ExperimentModel.id == id,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"experiment.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_all(
                    self, ctx: object, limit: int = 50,
                ) -> list[ExperimentModel]:
                    try:
                        result = await self._session.execute(
                            select(ExperimentModel)
                            .order_by(ExperimentModel.created_at.desc())
                            .limit(limit)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"experiment.find_all failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(
                    self, ctx: object, experiment: ExperimentModel,
                ) -> ExperimentModel:
                    try:
                        self._session.add(experiment)
                        await self._session.flush()
                        return experiment
                    except SQLAlchemyError as exc:
                        logger.error(f"experiment.save failed: {exc}")
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

            from app.modules.ai_ml.application.exceptions import (
                ApplicationError,
            )
            from app.modules.ai_ml.infrastructure.models import MLModel


            class ModelRepository:
                """TH: model repo | EN: model repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(
                    self, ctx: object, id: uuid.UUID,
                ) -> MLModel | None:
                    try:
                        result = await self._session.execute(
                            select(MLModel).where(MLModel.id == id)
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_name_version(
                    self, ctx: object, name: str, version: int,
                ) -> MLModel | None:
                    try:
                        result = await self._session.execute(
                            select(MLModel).where(
                                MLModel.name == name,
                                MLModel.version == version,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(
                            f"model.find_by_name_version failed: {exc}",
                        )
                        raise ApplicationError(str(exc)) from exc

                async def find_all_active(
                    self, ctx: object,
                ) -> list[MLModel]:
                    try:
                        result = await self._session.execute(
                            select(MLModel)
                            .where(MLModel.is_active.is_(True))
                            .order_by(MLModel.created_at.desc())
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_all_active failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_deployed(
                    self, ctx: object,
                ) -> list[MLModel]:
                    try:
                        result = await self._session.execute(
                            select(MLModel).where(
                                MLModel.status == "DEPLOYED",
                                MLModel.is_active.is_(True),
                            )
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"model.find_deployed failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def save(
                    self, ctx: object, model: MLModel,
                ) -> MLModel:
                    try:
                        self._session.add(model)
                        await self._session.flush()
                        return model
                    except SQLAlchemyError as exc:
                        logger.error(f"model.save failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def update(
                    self, ctx: object, model: MLModel,
                ) -> MLModel:
                    try:
                        await self._session.flush()
                        return model
                    except SQLAlchemyError as exc:
                        logger.error(f"model.update failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _run_repo_content(self) -> str:
        return dedent('''\
            """TrainingRun repository"""
            from __future__ import annotations
            import uuid
            from datetime import UTC, datetime

            from loguru import logger
            from sqlalchemy import select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.ai_ml.application.exceptions import (
                ApplicationError,
            )
            from app.modules.ai_ml.infrastructure.models import (
                TrainingRunModel,
            )


            class TrainingRunRepository:
                """TH: training run repo | EN: training run repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(
                    self, ctx: object, id: uuid.UUID,
                ) -> TrainingRunModel | None:
                    try:
                        result = await self._session.execute(
                            select(TrainingRunModel).where(
                                TrainingRunModel.id == id,
                            )
                        )
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"run.find_by_id failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_experiment(
                    self, ctx: object, experiment_id: uuid.UUID,
                ) -> list[TrainingRunModel]:
                    try:
                        result = await self._session.execute(
                            select(TrainingRunModel)
                            .where(
                                TrainingRunModel.experiment_id
                                == experiment_id,
                            )
                            .order_by(
                                TrainingRunModel.created_at.desc(),
                            )
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(
                            f"run.find_by_experiment failed: {exc}",
                        )
                        raise ApplicationError(str(exc)) from exc

                async def create(
                    self, ctx: object, run: TrainingRunModel,
                ) -> TrainingRunModel:
                    try:
                        self._session.add(run)
                        await self._session.flush()
                        return run
                    except SQLAlchemyError as exc:
                        logger.error(f"run.create failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def update_status(
                    self, ctx: object, id: uuid.UUID, status: str,
                ) -> None:
                    try:
                        run = await self.find_by_id(ctx, id)
                        if run:
                            run.status = status
                            if status == "RUNNING":
                                run.started_at = datetime.now(UTC)
                            elif status in (
                                "SUCCESS", "FAILED", "CANCELLED",
                            ):
                                run.finished_at = datetime.now(UTC)
                                if run.started_at:
                                    delta = (
                                        run.finished_at - run.started_at
                                    )
                                    run.duration_ms = int(
                                        delta.total_seconds() * 1000,
                                    )
                            await self._session.flush()
                    except SQLAlchemyError as exc:
                        logger.error(f"run.update_status failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _pred_repo_content(self) -> str:
        return dedent('''\
            """Prediction repository"""
            from __future__ import annotations
            import uuid

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.ai_ml.application.exceptions import (
                ApplicationError,
            )
            from app.modules.ai_ml.infrastructure.models import (
                PredictionModel,
            )


            class PredictionRepository:
                """TH: prediction repo | EN: prediction repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(
                    self, ctx: object, prediction: PredictionModel,
                ) -> PredictionModel:
                    try:
                        self._session.add(prediction)
                        await self._session.flush()
                        return prediction
                    except SQLAlchemyError as exc:
                        logger.error(f"pred.create failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_model(
                    self, ctx: object, model_id: uuid.UUID, limit: int = 100,
                ) -> list[PredictionModel]:
                    try:
                        result = await self._session.execute(
                            select(PredictionModel)
                            .where(PredictionModel.model_id == model_id)
                            .order_by(PredictionModel.created_at.desc())
                            .limit(limit)
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"pred.find_by_model failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def count_by_model(
                    self, ctx: object, model_id: uuid.UUID,
                ) -> int:
                    try:
                        result = await self._session.execute(
                            select(func.count())
                            .select_from(PredictionModel)
                            .where(PredictionModel.model_id == model_id)
                        )
                        return int(result.scalar() or 0)
                    except SQLAlchemyError as exc:
                        logger.error(f"pred.count_by_model failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _metric_repo_content(self) -> str:
        return dedent('''\
            """Metric repository"""
            from __future__ import annotations
            import uuid
            from typing import Any

            from loguru import logger
            from sqlalchemy import func, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.ai_ml.application.exceptions import (
                ApplicationError,
            )
            from app.modules.ai_ml.infrastructure.models import MetricModel


            class MetricRepository:
                """TH: metric repo | EN: metric repo"""

                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def create(
                    self, ctx: object, metric: MetricModel,
                ) -> MetricModel:
                    try:
                        self._session.add(metric)
                        await self._session.flush()
                        return metric
                    except SQLAlchemyError as exc:
                        logger.error(f"metric.create failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_model(
                    self, ctx: object, model_id: uuid.UUID,
                ) -> list[MetricModel]:
                    try:
                        result = await self._session.execute(
                            select(MetricModel)
                            .where(MetricModel.model_id == model_id)
                            .order_by(
                                MetricModel.name, MetricModel.created_at,
                            )
                        )
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"metric.find_by_model failed: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def aggregate(
                    self, ctx: object, model_id: uuid.UUID, name: str,
                ) -> dict[str, Any]:
                    try:
                        result = await self._session.execute(
                            select(
                                func.coalesce(
                                    func.avg(MetricModel.value), 0,
                                ),
                                func.coalesce(
                                    func.min(MetricModel.value), 0,
                                ),
                                func.coalesce(
                                    func.max(MetricModel.value), 0,
                                ),
                                func.count(MetricModel.id),
                            ).where(
                                MetricModel.model_id == model_id,
                                MetricModel.name == name,
                            )
                        )
                        row = result.one()
                        return {
                            "avg": str(row[0]),
                            "min": str(row[1]),
                            "max": str(row[2]),
                            "count": int(row[3]),
                        }
                    except SQLAlchemyError as exc:
                        logger.error(f"metric.aggregate failed: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _caches_content(self) -> str:
        return dedent('''\
            """ai_ml infrastructure cache — Redis (never-raise)"""
            from __future__ import annotations
            import json
            from typing import Any

            import structlog

            log = structlog.get_logger()


            class RedisyoloCache:
                """TH: cache ด้วย Redis | EN: Redis cache (never-raise)"""

                def __init__(self, redis: object, ttl: int = 300) -> None:
                    self._redis = redis
                    self._ttl = ttl

                async def get(self, key: str) -> Any | None:
                    try:
                        raw = await self._redis.get(key)
                        return json.loads(raw) if raw else None
                    except Exception as e:
                        log.warning(
                            "cache.get_failed", key=key, err=str(e),
                        )
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
                        log.warning(
                            "cache.set_failed", key=key, err=str(e),
                        )
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
            """ai_ml infrastructure services — Trainer · ModelServer · FeatureStore · Drift"""

            from __future__ import annotations

            import time
            import uuid
            from datetime import datetime
            from typing import Any

            import numpy as np
            import structlog

            from app.modules.ai_ml.domain.value_objects import TrainConfig

            log = structlog.get_logger()


            class SklearnTrainer:
                """TH: trainer ด้วย scikit-learn | EN: sklearn trainer"""

                ALGORITHMS: dict[str, Any] = {}

                def __init__(self) -> None:
                    self._algorithms = self._load_algorithms()

                @staticmethod
                def _load_algorithms() -> dict[str, Any]:
                    try:
                        from sklearn.cluster import KMeans
                        from sklearn.decomposition import PCA
                        from sklearn.ensemble import (
                            GradientBoostingClassifier,
                            RandomForestClassifier,
                            RandomForestRegressor,
                        )
                        from sklearn.linear_model import (
                            LinearRegression, LogisticRegression,
                        )
                        return {
                            "logistic_regression": LogisticRegression,
                            "random_forest_classifier": (
                                RandomForestClassifier
                            ),
                            "gradient_boosting": GradientBoostingClassifier,
                            "linear_regression": LinearRegression,
                            "random_forest_regressor": RandomForestRegressor,
                            "kmeans": KMeans,
                            "pca": PCA,
                        }
                    except ImportError:
                        log.warning("sklearn.not_available")
                        return {}

                async def train(
                    self, config: TrainConfig, dataset: Any,
                ) -> dict[str, Any]:
                    """TH: ฝึก model | EN: train model"""
                    start = time.monotonic()
                    algo_name = config.algorithm
                    algo_cls = self._algorithms.get(algo_name)

                    if algo_cls is None:
                        log.warning(
                            f"algorithm not found: {algo_name}, using mock",
                        )
                        return self._mock_result(config, start)

                    # Placeholder: real training needs actual data
                    # In production, load data from feature_store
                    log.info(f"training with {algo_name}")
                    return self._mock_result(config, start)

                @staticmethod
                def _mock_result(
                    config: TrainConfig, start: float,
                ) -> dict[str, Any]:
                    duration_ms = int((time.monotonic() - start) * 1000)
                    return {
                        "name": f"model-{config.algorithm}",
                        "task_type": "CLASSIFICATION",
                        "artifact_uri": f"s3://yolo-models/mock-{uuid.uuid4()}",
                        "metrics": {
                            "accuracy": 0.92,
                            "f1": 0.90,
                            "precision": 0.91,
                            "recall": 0.89,
                        },
                        "duration_ms": max(duration_ms, 1),
                    }


            class SklearnModelServer:
                """TH: model server | EN: model server (in-process cache)"""

                def __init__(self) -> None:
                    self._loaded: dict[uuid.UUID, Any] = {}

                async def load(
                    self, model_id: uuid.UUID, artifact_uri: str,
                ) -> None:
                    try:
                        self._loaded[model_id] = {"uri": artifact_uri}
                        log.info(
                            "model_server.loaded",
                            model_id=str(model_id),
                        )
                    except Exception as e:
                        log.warning(
                            "model_server.load_failed", err=str(e),
                        )

                async def infer(
                    self, model_id: uuid.UUID, features: dict[str, Any],
                ) -> dict[str, Any]:
                    """TH: ทำนาย | EN: infer (never-raise)"""
                    start = time.monotonic()
                    if model_id not in self._loaded:
                        return {
                            "output": None,
                            "confidence": 0.0,
                            "latency_ms": 0,
                        }
                    output = {
                        "predicted_class": 1,
                        "score": 0.87,
                    }
                    latency_ms = int((time.monotonic() - start) * 1000)
                    return {
                        "output": output,
                        "confidence": 0.87,
                        "latency_ms": max(latency_ms, 1),
                    }

                async def unload(self, model_id: uuid.UUID) -> None:
                    self._loaded.pop(model_id, None)


            class RedisFeatureStore:
                """TH: feature store | EN: feature store (Redis online)"""

                def __init__(self, redis: object | None = None) -> None:
                    self._redis = redis

                async def get_online(
                    self, entity_id: str, features: list[str],
                ) -> dict[str, Any]:
                    """TH: ดึง online features | EN: get online features"""
                    if self._redis is None:
                        return {}
                    try:
                        key = f"yolo:feature:{entity_id}"
                        raw = await self._redis.hgetall(key)
                        return {
                            k: v for k, v in (raw or {}).items()
                            if not features or k in features
                        }
                    except Exception as e:
                        log.warning(
                            "feature_store.get_online_failed", err=str(e),
                        )
                        return {}

                async def get_offline(
                    self, entity_ids: list[str],
                    features: list[str], timestamp: datetime,
                ) -> Any:
                    """TH: ดึง offline features | EN: get offline features"""
                    return {}

                async def materialize(
                    self, feature_name: str, since: datetime,
                ) -> int:
                    """TH: materialize features | EN: materialize features"""
                    return 0


            class EvidentlyDriftDetector:
                """TH: drift detector | EN: drift detector"""

                def detect(
                    self, reference: Any, current: Any,
                ) -> dict[str, Any]:
                    """TH: ตรวจ drift | EN: detect drift"""
                    try:
                        import pandas as pd
                        from evidently import ColumnMapping
                        from evidently.metric_preset import (
                            DataDriftPreset,
                        )
                        from evidently.report import Report
                        ref_df = pd.DataFrame(reference)
                        cur_df = pd.DataFrame(current)
                        report = Report(
                            metrics=[DataDriftPreset()],
                        )
                        report.run(
                            reference_data=ref_df, current_data=cur_df,
                        )
                        result = report.as_dict()
                        metrics = result.get("metrics", [])
                        drift_score = 0.0
                        for m in metrics:
                            if m.get("metric") == "DatasetDriftMetric":
                                drift_score = float(
                                    m.get("result", {}).get(
                                        "drift_share", 0.0,
                                    )
                                )
                        return {
                            "drift_score": drift_score,
                            "drifted": drift_score > 0.3,
                        }
                    except Exception as e:
                        log.warning(
                            "drift.detect_failed", err=str(e),
                        )
                        return {"drift_score": 0.0, "drifted": False}


            class LocalArtifactStore:
                """TH: artifact store (local) | EN: artifact store (local)"""

                def __init__(self, root: str = "/tmp/yolo-artifacts") -> None:
                    self._root = root

                async def save(
                    self, path: str, data: bytes,
                    metadata: dict[str, Any],
                ) -> str:
                    import hashlib
                    import os
                    h = hashlib.sha256(data).hexdigest()[:16]
                    full = os.path.join(self._root, f"{h}-{path}")
                    os.makedirs(os.path.dirname(full), exist_ok=True)
                    with open(full, "wb") as f:
                        f.write(data)
                    return full

                async def load(self, uri: str) -> bytes:
                    with open(uri, "rb") as f:
                        return f.read()

                async def exists(self, uri: str) -> bool:
                    import os
                    return os.path.exists(uri)

                async def delete(self, uri: str) -> bool:
                    import os
                    try:
                        os.remove(uri)
                        return True
                    except OSError:
                        return False


            class KafkaEventBus:
                """TH: Kafka event bus | EN: Kafka event bus"""

                def __init__(
                    self, producer: object, topic: str = "yolo.events",
                ) -> None:
                    self._producer = producer
                    self._topic = topic

                async def publish(self, event: object) -> None:
                    try:
                        payload = {
                            "type": type(event).__name__,
                            "data": {
                                k: str(v)
                                for k, v in vars(event).items()
                            },
                        }
                        await self._producer.send_and_wait(
                            self._topic, payload,
                        )
                    except Exception as e:
                        log.warning(
                            "event.publish_failed", err=str(e),
                        )


            class NoopEventBus:
                async def publish(self, event: object) -> None:
                    log.debug(
                        "event.noop", type=type(event).__name__,
                    )
        ''')

    def _artifact_store_content(self) -> str:
        return dedent('''\
            """Artifact store — S3 / local (never-raise)"""
            from __future__ import annotations
            import hashlib
            import os
            from typing import Any

            import structlog

            log = structlog.get_logger()


            class S3ArtifactStore:
                """TH: artifact store S3 | EN: S3 artifact store"""

                def __init__(
                    self,
                    bucket: str,
                    region: str = "ap-southeast-1",
                    prefix: str = "yolo",
                ) -> None:
                    self._bucket = bucket
                    self._region = region
                    self._prefix = prefix
                    self._client: Any = None

                def _get_client(self) -> Any:
                    if self._client is None:
                        try:
                            import boto3
                            self._client = boto3.client(
                                "s3", region_name=self._region,
                            )
                        except Exception as e:
                            log.warning("s3.client_failed", err=str(e))
                    return self._client

                async def save(
                    self, path: str, data: bytes,
                    metadata: dict[str, Any],
                ) -> str:
                    h = hashlib.sha256(data).hexdigest()[:16]
                    key = f"{self._prefix}/{h}-{path}"
                    try:
                        client = self._get_client()
                        if client is None:
                            return ""
                        client.put_object(
                            Bucket=self._bucket,
                            Key=key,
                            Body=data,
                            Metadata={
                                k: str(v) for k, v in metadata.items()
                            },
                        )
                        return f"s3://{self._bucket}/{key}"
                    except Exception as e:
                        log.warning("s3.save_failed", err=str(e))
                        return ""

                async def load(self, uri: str) -> bytes:
                    try:
                        client = self._get_client()
                        if client is None or not uri.startswith("s3://"):
                            return b""
                        parts = uri[5:].split("/", 1)
                        resp = client.get_object(
                            Bucket=parts[0], Key=parts[1],
                        )
                        return resp["Body"].read()
                    except Exception as e:
                        log.warning("s3.load_failed", err=str(e))
                        return b""

                async def exists(self, uri: str) -> bool:
                    try:
                        client = self._get_client()
                        if client is None or not uri.startswith("s3://"):
                            return False
                        parts = uri[5:].split("/", 1)
                        client.head_object(
                            Bucket=parts[0], Key=parts[1],
                        )
                        return True
                    except Exception:
                        return False

                async def delete(self, uri: str) -> bool:
                    try:
                        client = self._get_client()
                        if client is None or not uri.startswith("s3://"):
                            return False
                        parts = uri[5:].split("/", 1)
                        client.delete_object(
                            Bucket=parts[0], Key=parts[1],
                        )
                        return True
                    except Exception as e:
                        log.warning("s3.delete_failed", err=str(e))
                        return False
        ''')

    # ─── PRESENTATION LAYER ─────────────────────────────────────
    def _create_presentation(self) -> None:
        base = f"{self.mod_root}/presentation"

        self.writer.write(f"{base}/__init__.py", dedent('''\
            """ai_ml presentation layer"""
        '''))

        self.writer.write(f"{base}/schemas.py", self._schemas_content())
        self.writer.write(f"{base}/docs.py", self._docs_content())
        self.writer.write(
            f"{base}/dependencies.py",
            self._dependencies_content(),
        )
        self.writer.write(f"{base}/router.py", self._router_content())
        self.writer.write(f"{base}/swagger.py", self._swagger_content())

    def _schemas_content(self) -> str:
        return dedent('''\
            """ai_ml Pydantic v2 schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            # ─── Dataset ─────────────────────────────────
            class DatasetCreateRequest(BaseModel):
                name: str = Field(..., min_length=1, max_length=200)
                source_uri: str = ""
                rows: int = Field(default=0, ge=0)
                cols: int = Field(default=0, ge=0)
                schema_json: dict[str, Any] = Field(default_factory=dict)
                profile_json: dict[str, Any] = Field(default_factory=dict)
                model_config = ConfigDict(extra="forbid")


            class DatasetResponse(BaseModel):
                id: str
                name: str
                source_uri: str = ""
                content_hash: str = ""
                rows: int = 0
                cols: int = 0
                status: str = "RAW"
                version: int = 1
                model_config = ConfigDict(extra="forbid")


            class DatasetDetailResponse(DatasetResponse):
                schema_json: dict[str, Any] = Field(default_factory=dict)
                profile_json: dict[str, Any] = Field(default_factory=dict)


            class DatasetListResponse(BaseModel):
                items: list[DatasetResponse]
                total: int
                page: int
                size: int
                model_config = ConfigDict(extra="forbid")


            # ─── Feature ─────────────────────────────────
            class FeatureCreateRequest(BaseModel):
                name: str = Field(..., min_length=1, max_length=200)
                dtype: str = Field(default="float")
                transform: str = ""
                source_dataset_id: str | None = None
                entity_key: str = ""
                ttl_seconds: int = Field(default=3600, ge=1)
                is_online: bool = True
                metadata_json: dict[str, Any] = Field(default_factory=dict)
                model_config = ConfigDict(extra="forbid")


            class FeatureResponse(BaseModel):
                id: str
                name: str
                dtype: str
                transform: str = ""
                entity_key: str = ""
                ttl_seconds: int = 3600
                is_online: bool = True
                model_config = ConfigDict(extra="forbid")


            # ─── Experiment ──────────────────────────────
            class ExperimentCreateRequest(BaseModel):
                name: str = Field(..., min_length=1, max_length=200)
                description: str = ""
                task_type: str = Field(..., min_length=1)
                model_config = ConfigDict(extra="forbid")


            class ExperimentResponse(BaseModel):
                id: str
                name: str
                description: str = ""
                task_type: str
                status: str = "ACTIVE"
                best_model_id: str | None = None
                model_config = ConfigDict(extra="forbid")


            # ─── Training ────────────────────────────────
            class TrainRequest(BaseModel):
                experiment_id: str = Field(..., min_length=1)
                dataset_id: str = Field(..., min_length=1)
                test_size: float = Field(default=0.2, gt=0.0, lt=1.0)
                random_state: int = 42
                cv_folds: int = Field(default=5, ge=2)
                scaler: str = "standard"
                algorithm: str = "logistic_regression"
                hyperparams: dict[str, Any] = Field(default_factory=dict)
                model_config = ConfigDict(extra="forbid")


            class TrainResponse(BaseModel):
                training_run_id: str
                model_id: str
                status: str
                metrics: dict[str, Any] = Field(default_factory=dict)
                duration_ms: int = 0
                model_config = ConfigDict(extra="forbid")


            class TrainingStatusResponse(BaseModel):
                id: str
                experiment_id: str
                dataset_id: str
                status: str
                duration_ms: int = 0
                seed: int = 42
                error_message: str = ""
                started_at: str | None = None
                finished_at: str | None = None
                model_config = ConfigDict(extra="forbid")


            # ─── Model ───────────────────────────────────
            class ModelResponse(BaseModel):
                id: str
                name: str
                version: int = 1
                task_type: str
                algorithm: str = ""
                status: str = "DRAFT"
                metrics: dict[str, Any] = Field(default_factory=dict)
                model_config = ConfigDict(extra="forbid")


            class ModelDetailResponse(ModelResponse):
                artifact_uri: str = ""
                artifact_hash: str = ""
                metric_rows: list[dict[str, Any]] = Field(
                    default_factory=list,
                )


            # ─── Prediction ──────────────────────────────
            class PredictRequest(BaseModel):
                model_id: str = Field(..., min_length=1)
                features: dict[str, Any] = Field(default_factory=dict)
                source: str = "api"
                model_config = ConfigDict(extra="forbid")


            class PredictResponse(BaseModel):
                prediction_id: str
                model_id: str
                output: Any = None
                confidence: float = 0.0
                latency_ms: int = 0
                model_config = ConfigDict(extra="forbid")


            class BatchPredictRequest(BaseModel):
                model_id: str = Field(..., min_length=1)
                items: list[dict[str, Any]] = Field(
                    ..., min_length=1, max_length=1000,
                )
                model_config = ConfigDict(extra="forbid")


            class BatchPredictResponse(BaseModel):
                model_id: str
                total: int
                predictions: list[dict[str, Any]]
                model_config = ConfigDict(extra="forbid")


            # ─── Metrics & Drift ─────────────────────────
            class MetricsResponse(BaseModel):
                model_id: str
                metrics: list[dict[str, Any]]
                model_config = ConfigDict(extra="forbid")


            class DriftCheckRequest(BaseModel):
                model_id: str = Field(..., min_length=1)
                reference: list[dict[str, Any]] = Field(
                    ..., min_length=1,
                )
                current: list[dict[str, Any]] = Field(
                    ..., min_length=1,
                )
                threshold: float = Field(default=0.3, ge=0.0, le=1.0)
                model_config = ConfigDict(extra="forbid")


            class DriftCheckResponse(BaseModel):
                model_id: str
                drift_score: float
                threshold: float
                drifted: bool
                model_config = ConfigDict(extra="forbid")
        ''')

    def _docs_content(self) -> str:
        return dedent('''\
            """ai_ml OpenAPI metadata — response examples"""
            from __future__ import annotations

            RESPONSE_DATASET_201 = {
                "description": "สร้าง dataset สำเร็จ",
                "content": {"application/json": {"example": {
                    "id": "uuid",
                    "name": "churn-train-2025",
                    "rows": 10000,
                    "cols": 25,
                    "status": "RAW",
                    "version": 1,
                }}},
            }
            RESPONSE_TRAIN_201 = {
                "description": "เริ่มการฝึกสำเร็จ",
                "content": {"application/json": {"example": {
                    "training_run_id": "uuid",
                    "model_id": "uuid",
                    "status": "SUCCESS",
                    "metrics": {"accuracy": 0.92, "f1": 0.90},
                    "duration_ms": 12345,
                }}},
            }
            RESPONSE_PREDICT_200 = {
                "description": "ทำนายสำเร็จ",
                "content": {"application/json": {"example": {
                    "prediction_id": "uuid",
                    "model_id": "uuid",
                    "output": {"predicted_class": 1, "score": 0.87},
                    "confidence": 0.87,
                    "latency_ms": 45,
                }}},
            }
            RESPONSE_ERROR_400 = {
                "description": "Domain error",
                "content": {"application/json": {"example": {
                    "detail": "invalid feature",
                    "code": "DOMAIN_ERROR",
                }}},
            }
            RESPONSE_ERROR_404 = {
                "description": "ไม่พบ resource",
                "content": {"application/json": {"example": {
                    "detail": "model not found",
                    "code": "MODEL_NOT_FOUND",
                }}},
            }
            RESPONSE_ERROR_409 = {
                "description": "Drift detected",
                "content": {"application/json": {"example": {
                    "detail": "data drift beyond threshold",
                    "code": "DRIFT_DETECTED",
                }}},
            }
            RESPONSE_ERROR_422 = {
                "description": "Validation error",
                "content": {"application/json": {"example": {
                    "detail": [{"loc": ["body"], "msg": "invalid"}],
                }}},
            }
            RESPONSE_ERROR_500 = {
                "description": "Training failed",
                "content": {"application/json": {"example": {
                    "detail": "training pipeline failed",
                    "code": "TRAINING_FAILED",
                }}},
            }
        ''')

    def _dependencies_content(self) -> str:
        return dedent('''\
            """ai_ml DI container"""
            from __future__ import annotations
            from typing import Annotated, Any

            from fastapi import Depends
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.core.db import get_session
            from app.modules.ai_ml.application.use_case import yoloUseCase
            from app.modules.ai_ml.infrastructure.artifact_store import (
                S3ArtifactStore,
            )
            from app.modules.ai_ml.infrastructure.caches import (
                RedisyoloCache,
            )
            from app.modules.ai_ml.infrastructure.dataset_repository import (
                DatasetRepository,
            )
            from app.modules.ai_ml.infrastructure.experiment_repository import (
                ExperimentRepository,
            )
            from app.modules.ai_ml.infrastructure.feature_repository import (
                FeatureRepository,
            )
            from app.modules.ai_ml.infrastructure.metric_repository import (
                MetricRepository,
            )
            from app.modules.ai_ml.infrastructure.model_repository import (
                ModelRepository,
            )
            from app.modules.ai_ml.infrastructure.prediction_repository import (
                PredictionRepository,
            )
            from app.modules.ai_ml.infrastructure.services import (
                EvidentlyDriftDetector, KafkaEventBus,
                NoopEventBus, RedisFeatureStore,
                SklearnModelServer, SklearnTrainer,
            )
            from app.modules.ai_ml.infrastructure.training_run_repository import (
                TrainingRunRepository,
            )

            _trainer: SklearnTrainer | None = None
            _model_server: SklearnModelServer | None = None
            _drift: EvidentlyDriftDetector | None = None
            _artifact_store: S3ArtifactStore | None = None


            def _get_trainer() -> SklearnTrainer:
                global _trainer
                if _trainer is None:
                    _trainer = SklearnTrainer()
                return _trainer


            def _get_model_server() -> SklearnModelServer:
                global _model_server
                if _model_server is None:
                    _model_server = SklearnModelServer()
                return _model_server


            def _get_drift() -> EvidentlyDriftDetector:
                global _drift
                if _drift is None:
                    _drift = EvidentlyDriftDetector()
                return _drift


            def _get_artifact_store() -> S3ArtifactStore:
                global _artifact_store
                if _artifact_store is None:
                    try:
                        from app.core.settings import settings
                        _artifact_store = S3ArtifactStore(
                            bucket=getattr(
                                settings, "yolo_ARTIFACT_BUCKET",
                                "yolo-artifacts",
                            ),
                        )
                    except Exception:
                        _artifact_store = S3ArtifactStore(
                            bucket="yolo-artifacts",
                        )
                return _artifact_store


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


            class _NoopRateLimiter:
                async def check(
                    self, tenant_id: Any, user_id: Any, cost: int,
                ) -> bool:
                    return True

                async def increment(
                    self, tenant_id: Any, user_id: Any, cost: int,
                ) -> None:
                    return None


            async def get_ai_ml_use_case(
                session: Annotated[AsyncSession, Depends(get_session)],
            ) -> yoloUseCase:
                redis = await _get_redis()
                bus = await _get_event_bus()
                cache = RedisyoloCache(redis) if redis else _NoopCache()
                feature_store = RedisFeatureStore(redis)
                return yoloUseCase(
                    dataset_repo=DatasetRepository(session),
                    feature_repo=FeatureRepository(session),
                    experiment_repo=ExperimentRepository(session),
                    model_repo=ModelRepository(session),
                    run_repo=TrainingRunRepository(session),
                    prediction_repo=PredictionRepository(session),
                    metric_repo=MetricRepository(session),
                    feature_store=feature_store,
                    model_server=_get_model_server(),
                    trainer=_get_trainer(),
                    artifact_store=_get_artifact_store(),
                    drift_detector=_get_drift(),
                    cache=cache,
                    rate_limiter=_NoopRateLimiter(),
                    event_bus=bus,
                )


            class _NoopCache:
                async def get(self, key: str) -> Any | None:
                    return None

                async def set(
                    self, key: str, value: Any, ttl: int = 300,
                ) -> bool:
                    return False

                async def invalidate(self, key: str) -> bool:
                    return False
        ''')

    def _router_content(self) -> str:
        return dedent('''\
            """ai_ml HTTP routers"""
            from __future__ import annotations
            import uuid
            from typing import Annotated, Any

            from fastapi import APIRouter, Depends, HTTPException, status

            from app.modules.ai_ml.application.use_case import (
                yoloUseCase,
            )
            from app.modules.ai_ml.domain.exceptions import (
                yoloError, DatasetNotFoundError,
                ModelNotFoundError, TrainingFailedError,
            )
            from app.modules.ai_ml.domain.value_objects import TrainConfig
            from app.modules.ai_ml.presentation.dependencies import (
                get_ai_ml_use_case,
            )
            from app.modules.ai_ml.presentation.docs import (
                RESPONSE_DATASET_201, RESPONSE_ERROR_400,
                RESPONSE_ERROR_404, RESPONSE_ERROR_422,
                RESPONSE_ERROR_500, RESPONSE_PREDICT_200,
                RESPONSE_TRAIN_201,
            )
            from app.modules.ai_ml.presentation.schemas import (
                BatchPredictRequest, BatchPredictResponse,
                DatasetCreateRequest, DatasetDetailResponse,
                DatasetListResponse, DatasetResponse,
                DriftCheckRequest, DriftCheckResponse,
                ExperimentCreateRequest, ExperimentResponse,
                FeatureCreateRequest, FeatureResponse,
                MetricsResponse, ModelDetailResponse, ModelResponse,
                PredictRequest, PredictResponse,
                TrainRequest, TrainResponse, TrainingStatusResponse,
            )

            router = APIRouter(prefix="/ai-ml", tags=["AI/ML"])


            def _error_status(exc: Exception) -> int:
                if isinstance(exc, (ModelNotFoundError, DatasetNotFoundError)):
                    return status.HTTP_404_NOT_FOUND
                if isinstance(exc, TrainingFailedError):
                    return status.HTTP_500_INTERNAL_SERVER_ERROR
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


            # ═══════════════════════════════════════════════════════════
            # DATASETS
            # ═══════════════════════════════════════════════════════════
            @router.post(
                "/datasets",
                response_model=DatasetResponse,
                status_code=status.HTTP_201_CREATED,
                summary="Register dataset",
                operation_id="yolo_register_dataset",
                responses={201: RESPONSE_DATASET_201, 400: RESPONSE_ERROR_400},
            )
            async def register_dataset(
                payload: DatasetCreateRequest,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> DatasetResponse:
                ctx = await _get_ctx()
                try:
                    result = await uc.register_dataset(
                        ctx=ctx,
                        name=payload.name,
                        source_uri=payload.source_uri,
                        rows=payload.rows,
                        cols=payload.cols,
                        schema_json=payload.schema_json,
                        profile_json=payload.profile_json,
                    )
                    return DatasetResponse(**result)
                except yoloError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            @router.get(
                "/datasets",
                response_model=DatasetListResponse,
                summary="List datasets",
                operation_id="yolo_list_datasets",
            )
            async def list_datasets(
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
                page: int = 1,
                size: int = 50,
            ) -> DatasetListResponse:
                ctx = await _get_ctx()
                result = await uc.list_datasets(ctx, page, size)
                return DatasetListResponse(**result)


            @router.get(
                "/datasets/{dataset_id}",
                response_model=DatasetDetailResponse,
                summary="Get dataset",
                operation_id="yolo_get_dataset",
                responses={404: RESPONSE_ERROR_404},
            )
            async def get_dataset(
                dataset_id: uuid.UUID,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> DatasetDetailResponse:
                ctx = await _get_ctx()
                try:
                    result = await uc.get_dataset(ctx, dataset_id)
                    return DatasetDetailResponse(**result)
                except yoloError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            # ═══════════════════════════════════════════════════════════
            # EXPERIMENTS
            # ═══════════════════════════════════════════════════════════
            @router.post(
                "/experiments",
                response_model=ExperimentResponse,
                status_code=status.HTTP_201_CREATED,
                summary="Create experiment",
                operation_id="yolo_create_experiment",
            )
            async def create_experiment(
                payload: ExperimentCreateRequest,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> ExperimentResponse:
                ctx = await _get_ctx()
                try:
                    from app.modules.ai_ml.infrastructure.models import (
                        ExperimentModel,
                    )
                    exp = ExperimentModel(
                        tenant_id=ctx.tenant_id,
                        name=payload.name,
                        description=payload.description,
                        task_type=payload.task_type,
                        status="ACTIVE",
                    )
                    saved = await uc._experiment_repo.save(ctx, exp)
                    return ExperimentResponse(
                        id=str(saved.id),
                        name=saved.name,
                        description=saved.description,
                        task_type=saved.task_type,
                        status=saved.status,
                    )
                except yoloError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            @router.get(
                "/experiments",
                response_model=list[ExperimentResponse],
                summary="List experiments",
                operation_id="yolo_list_experiments",
            )
            async def list_experiments(
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
                limit: int = 50,
            ) -> list[ExperimentResponse]:
                ctx = await _get_ctx()
                rows = await uc._experiment_repo.find_all(ctx, limit)
                return [
                    ExperimentResponse(
                        id=str(r.id),
                        name=r.name,
                        description=r.description,
                        task_type=r.task_type,
                        status=r.status,
                        best_model_id=(
                            str(r.best_model_id)
                            if r.best_model_id else None
                        ),
                    )
                    for r in rows
                ]


            # ═══════════════════════════════════════════════════════════
            # TRAINING
            # ═══════════════════════════════════════════════════════════
            @router.post(
                "/train",
                response_model=TrainResponse,
                status_code=status.HTTP_201_CREATED,
                summary="Start training",
                operation_id="yolo_train",
                responses={
                    201: RESPONSE_TRAIN_201,
                    400: RESPONSE_ERROR_400,
                    500: RESPONSE_ERROR_500,
                },
            )
            async def start_training(
                payload: TrainRequest,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> TrainResponse:
                ctx = await _get_ctx()
                try:
                    config = TrainConfig(
                        test_size=payload.test_size,
                        random_state=payload.random_state,
                        cv_folds=payload.cv_folds,
                        scaler=payload.scaler,
                        algorithm=payload.algorithm,
                        hyperparams=tuple(
                            payload.hyperparams.items(),
                        ),
                    )
                    result = await uc.start_training(
                        ctx=ctx,
                        experiment_id=uuid.UUID(payload.experiment_id),
                        dataset_id=uuid.UUID(payload.dataset_id),
                        config=config,
                    )
                    return TrainResponse(**result)
                except yoloError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            @router.get(
                "/train/{run_id}",
                response_model=TrainingStatusResponse,
                summary="Get training status",
                operation_id="yolo_train_status",
                responses={404: RESPONSE_ERROR_404},
            )
            async def get_training_status(
                run_id: uuid.UUID,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> TrainingStatusResponse:
                ctx = await _get_ctx()
                try:
                    result = await uc.get_training_status(ctx, run_id)
                    return TrainingStatusResponse(**result)
                except yoloError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            # ═══════════════════════════════════════════════════════════
            # MODELS
            # ═══════════════════════════════════════════════════════════
            @router.get(
                "/models",
                response_model=list[ModelResponse],
                summary="List models",
                operation_id="yolo_list_models",
            )
            async def list_models(
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
                only_active: bool = True,
            ) -> list[ModelResponse]:
                ctx = await _get_ctx()
                rows = await uc.list_models(ctx, only_active)
                return [ModelResponse(**r) for r in rows]


            @router.get(
                "/models/{model_id}",
                response_model=ModelDetailResponse,
                summary="Get model",
                operation_id="yolo_get_model",
                responses={404: RESPONSE_ERROR_404},
            )
            async def get_model(
                model_id: uuid.UUID,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> ModelDetailResponse:
                ctx = await _get_ctx()
                try:
                    result = await uc.get_model(ctx, model_id)
                    return ModelDetailResponse(**result)
                except yoloError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            @router.post(
                "/models/{model_id}/deploy",
                response_model=ModelResponse,
                summary="Deploy model",
                operation_id="yolo_deploy_model",
                responses={404: RESPONSE_ERROR_404},
            )
            async def deploy_model(
                model_id: uuid.UUID,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> ModelResponse:
                ctx = await _get_ctx()
                try:
                    result = await uc.deploy_model(ctx, model_id)
                    return ModelResponse(
                        id=result["id"],
                        name="",
                        task_type="",
                        status=result["status"],
                    )
                except yoloError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            # ═══════════════════════════════════════════════════════════
            # PREDICTION
            # ═══════════════════════════════════════════════════════════
            @router.post(
                "/predict",
                response_model=PredictResponse,
                summary="Real-time prediction",
                operation_id="yolo_predict",
                responses={
                    200: RESPONSE_PREDICT_200,
                    404: RESPONSE_ERROR_404,
                },
            )
            async def predict(
                payload: PredictRequest,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> PredictResponse:
                ctx = await _get_ctx()
                try:
                    result = await uc.predict(
                        ctx=ctx,
                        model_id=uuid.UUID(payload.model_id),
                        features=payload.features,
                        source=payload.source,
                    )
                    return PredictResponse(**result)
                except yoloError as e:
                    raise HTTPException(
                        _error_status(e), detail=str(e),
                    ) from e


            @router.post(
                "/predict/batch",
                response_model=BatchPredictResponse,
                summary="Batch prediction",
                operation_id="yolo_predict_batch",
            )
            async def predict_batch(
                payload: BatchPredictRequest,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> BatchPredictResponse:
                ctx = await _get_ctx()
                predictions: list[dict[str, Any]] = []
                for item in payload.items:
                    try:
                        r = await uc.predict(
                            ctx=ctx,
                            model_id=uuid.UUID(payload.model_id),
                            features=item,
                            source="batch",
                        )
                        predictions.append(r)
                    except Exception as e:
                        predictions.append({
                            "error": str(e), "input": item,
                        })
                return BatchPredictResponse(
                    model_id=payload.model_id,
                    total=len(payload.items),
                    predictions=predictions,
                )


            # ═══════════════════════════════════════════════════════════
            # METRICS
            # ═══════════════════════════════════════════════════════════
            @router.get(
                "/metrics/{model_id}",
                response_model=MetricsResponse,
                summary="Get metrics",
                operation_id="yolo_get_metrics",
            )
            async def get_metrics(
                model_id: uuid.UUID,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> MetricsResponse:
                ctx = await _get_ctx()
                result = await uc.get_metrics(ctx, model_id)
                return MetricsResponse(**result)


            @router.post(
                "/metrics/drift",
                response_model=DriftCheckResponse,
                summary="Check drift",
                operation_id="yolo_check_drift",
                responses={409: RESPONSE_ERROR_404},
            )
            async def check_drift(
                payload: DriftCheckRequest,
                uc: Annotated[yoloUseCase, Depends(get_ai_ml_use_case)],
            ) -> DriftCheckResponse:
                ctx = await _get_ctx()
                result = await uc.check_drift(
                    ctx=ctx,
                    model_id=uuid.UUID(payload.model_id),
                    reference=payload.reference,
                    current=payload.current,
                    threshold=payload.threshold,
                )
                return DriftCheckResponse(**result)
        ''')

    def _swagger_content(self) -> str:
        return dedent('''\
            """OpenAPI docs — ai_ml module

            TH: register OpenAPI metadata (tag, externalDocs, x-*)
            EN: register OpenAPI metadata
            """
            from __future__ import annotations
            from typing import Any


            def register_ai_ml_openapi(app: object) -> None:
                """TH: register OpenAPI metadata | EN: register OpenAPI metadata"""
                original_openapi = app.openapi

                def custom_openapi() -> dict[str, Any]:
                    if getattr(app, "openapi_schema", None):
                        return app.openapi_schema
                    schema = original_openapi()
                    tags = schema.setdefault("tags", [])
                    if not any(t.get("name") == "AI/ML" for t in tags):
                        tags.append({
                            "name": "AI/ML",
                            "description": (
                                "โมดูล ai_ml — Unified AI/ML Platform\\n\\n"
                                "• Dataset registry + profiling\\n"
                                "• Feature store (offline + online)\\n"
                                "• Experiment tracking (MLflow)\\n"
                                "• Training orchestration (Ray)\\n"
                                "• Model registry + versioning\\n"
                                "• Real-time + batch inference\\n"
                                "• Drift detection (Evidently)\\n"
                                "• MLOps pipeline (CI/CD/CT)"
                            ),
                            "externalDocs": {
                                "description": "ai_ml Module README",
                                "url": "/docs/README_ai_ml.md",
                            },
                        })
                    info = schema.setdefault("info", {})
                    info.setdefault("x-module", "ai_ml")
                    info.setdefault("x-layer", "5-Intel")
                    info.setdefault("x-prefix", "yolo")
                    info.setdefault("x-schema", "public")
                    app.openapi_schema = schema
                    return schema

                app.openapi = custom_openapi
        ''')

    def _create_root_init(self) -> None:
        self.writer.write(f"{self.mod_root}/__init__.py", dedent('''\
            """ai_ml module — โมดูล AI/ML Platform"""
            from .presentation.router import router as ai_ml_router

            __all__ = ["ai_ml_router"]
        '''))

    # ═══════════════════════════════════════════════════════════
    #  2. ACTIVATE
    # ═══════════════════════════════════════════════════════════
    def activate_module(self) -> None:
        info("[ACTIVATE] register router + swagger + models")
        self._update_app_py()
        self._update_env_py()

    # ═══════════════════════════════════════════════════════════
    #  4. UPDATE APP
    # ═══════════════════════════════════════════════════════════
    def update_app(self) -> None:
        info("[UPDATE] app/app.py")
        self._update_app_py()

    def _update_app_py(self) -> None:
        app_file = self.root / self.app_py
        if not app_file.exists():
            warn(f"{self.app_py} not found — skipping")
            return

        content = app_file.read_text(encoding="utf-8")
        original = content

        router_import = (
            "from app.modules.ai_ml.presentation.router "
            "import router as ai_ml_router"
        )
        if router_import not in content:
            lines = content.split("\n")
            insert_at = None
            for i, line in enumerate(lines):
                if (
                    "from app.modules.health.presentation" in line
                    or "from app.modules.llm.presentation" in line
                    or "from app.modules.iot.presentation" in line
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

        swagger_import = (
            "from app.modules.ai_ml.presentation.swagger "
            "import register_ai_ml_openapi"
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

        m = re.search(r"(routers\s*=\s*\[)(.*?)(\n\])", content, re.S)
        if m:
            inner = m.group(2)
            if "ai_ml_router" not in inner:
                anchor = None
                for cand in ("llm_router,", "iot_router,", "pdpa_router,"):
                    if cand in inner:
                        anchor = cand
                        break
                if anchor:
                    inner_new = inner.replace(
                        anchor,
                        f"{anchor}\n    ai_ml_router,    "
                        f"# ai_ml module (Layer 5-Intel)",
                        1,
                    )
                else:
                    inner_new = (
                        inner.rstrip()
                        + "\n    ai_ml_router,    # ai_ml module\n"
                    )
                content = (
                    content[:m.start(2)] + inner_new + content[m.end(2):]
                )
                ok("added ai_ml_router to routers list")

        if '"name": "AI/ML"' not in content:
            tag_line = (
                '            {"name": "AI/ML", "description": '
                '"AI/ML Platform — Datasets, Features, Training, '
                'Serving, Drift."},\n'
            )
            m2 = re.search(
                r'(\{"name":\s*"(?:LLM|Health|iot|IOT|PDPA)"[^\}]*\},\s*\n)',
                content,
            )
            if m2:
                content = (
                    content[:m2.end(1)] + tag_line + content[m2.end(1):]
                )
                ok("added OpenAPI tag: AI/ML")
            else:
                warn("Anchor tag not found — skip OpenAPI tag")

        if "register_ai_ml_openapi(app)" not in content:
            include_match = re.search(
                r"(app\.include_router\(ai_ml_router[^\n]*\n)",
                content,
            )
            swagger_call = (
                "\n# TH: Register AI/ML OpenAPI metadata\n"
                "# EN: Register AI/ML OpenAPI metadata\n"
                "register_ai_ml_openapi(app)\n"
            )
            if include_match:
                insert_at = include_match.end(1)
                content = (
                    content[:insert_at] + swagger_call + content[insert_at:]
                )
                ok("called register_ai_ml_openapi(app)")
            else:
                m3 = re.search(
                    r"(app\s*=\s*FastAPI\([^)]*\)\s*\n)", content,
                )
                if m3:
                    insert_at = m3.end(1)
                    content = (
                        content[:insert_at]
                        + "\n# Register AI/ML OpenAPI metadata\n"
                        + "register_ai_ml_openapi(app)\n"
                        + content[insert_at:]
                    )
                    ok("called register_ai_ml_openapi(app)")
                else:
                    content = (
                        content.rstrip()
                        + "\n\n# Register AI/ML OpenAPI metadata\n"
                        + "register_ai_ml_openapi(app)\n"
                    )
                    ok("called register_ai_ml_openapi(app)")

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
        info("[UPDATE-ENV] migrations/env.py")
        self._update_env_py()

    def _update_env_py(self) -> None:
        env_file = self.root / self.env_py
        if not env_file.exists():
            warn(f"{self.env_py} not found — skipping")
            return

        content = env_file.read_text(encoding="utf-8")
        original = content

        marker = (
            "# --- module ai_ml "
            "(Dataset / Feature / Experiment / Model / TrainingRun / "
            "Prediction / Metric) ---"
        )
        if marker in content:
            skip("ai_ml models block already present in env.py")
            return

        block = f'''{marker}
# TH: ai_ml module — 7 models (Layer 5-Intel, schema=public, prefix=yolo_)
# EN: ai_ml module — 7 models (Layer 5-Intel, schema=public, prefix=yolo_)
try:
    from app.modules.ai_ml.infrastructure.models import (  # noqa: F401
        DatasetModel,
        ExperimentModel,
        FeatureModel,
        MetricModel,
        MLModel,
        PredictionModel,
        TrainingRunModel,
    )
except ImportError:
    pass


'''

        pattern = re.compile(
            r"(# --- module (?:llm|iot|pdpa).*?except ImportError:\s*\n\s*pass\s*\n)",
            re.S,
        )
        m = pattern.search(content)
        if m:
            insert_at = m.end(1)
            content = content[:insert_at] + "\n" + block + content[insert_at:]
        else:
            anchor = "config = context.config"
            idx = content.find(anchor)
            if idx == -1:
                warn("Cannot find anchor in env.py — skipping")
                return
            content = content[:idx] + block + content[idx:]

        if content != original:
            bak = env_file.with_suffix(".py.bak")
            bak.write_bytes(env_file.read_bytes())
            ok(f"backup: {self.env_py}.bak")
            env_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"{self.env_py} updated — registered ai_ml models")
        else:
            skip(f"{self.env_py} unchanged")

    # ═══════════════════════════════════════════════════════════
    #  3. SQL
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info(f"[SQL] {self.module} (v1.0: public + yolo_)")
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
-- V001__create_ai_ml.sql | Module: ai_ml | Prefix: yolo
-- Schema: public | Tables: yolo_datasets, yolo_features, yolo_experiments,
--                          yolo_models, yolo_training_runs,
--                          yolo_predictions, yolo_metrics
-- ═══════════════════════════════════════════════════════════════
BEGIN;

-- ─── yolo_datasets ──────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_datasets";
CREATE TABLE "public"."yolo_datasets" (
  "id"            uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"     uuid NOT NULL,
  "name"          varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "source_uri"    text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "content_hash"  varchar(64) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "rows"          int4 NOT NULL DEFAULT 0,
  "cols"          int4 NOT NULL DEFAULT 0,
  "status"        varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'RAW'::character varying,
  "version"       int4 NOT NULL DEFAULT 1,
  "schema_json"   jsonb NOT NULL DEFAULT '{}'::jsonb,
  "profile_json"  jsonb NOT NULL DEFAULT '{}'::jsonb,
  "metadata_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"    timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_datasets_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_yolo_dataset_name_ver" UNIQUE ("tenant_id", "name", "version"),
  CONSTRAINT "ck_yolo_dataset_status" CHECK (
    status IN ('RAW','PROCESSED','ARCHIVED')
  )
);

CREATE INDEX "ix_yolo_dataset_tenant"
    ON "public"."yolo_datasets" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_dataset_status"
    ON "public"."yolo_datasets" USING btree ("tenant_id", "status");
CREATE INDEX "ix_yolo_dataset_hash"
    ON "public"."yolo_datasets" USING btree ("content_hash");

-- ─── yolo_features ──────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_features";
CREATE TABLE "public"."yolo_features" (
  "id"                 uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"          uuid NOT NULL,
  "name"               varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "dtype"              varchar(50)  COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'float'::character varying,
  "transform"          varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "source_dataset_id"  uuid NULL,
  "entity_key"         varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "ttl_seconds"        int4 NOT NULL DEFAULT 3600,
  "is_online"          bool NOT NULL DEFAULT true,
  "metadata_json"      jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at"         timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"         timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_features_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_yolo_feature_name" UNIQUE ("tenant_id", "name")
);

CREATE INDEX "ix_yolo_feature_tenant"
    ON "public"."yolo_features" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_feature_online"
    ON "public"."yolo_features" USING btree ("tenant_id", "is_online");
CREATE INDEX "ix_yolo_feature_entity"
    ON "public"."yolo_features" USING btree ("entity_key");

-- ─── yolo_experiments ───────────────────────────
DROP TABLE IF EXISTS "public"."yolo_experiments";
CREATE TABLE "public"."yolo_experiments" (
  "id"            uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"     uuid NOT NULL,
  "name"          varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "description"   text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "task_type"     varchar(50)  COLLATE "pg_catalog"."default" NOT NULL,
  "status"        varchar(20)  COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'ACTIVE'::character varying,
  "best_model_id" uuid NULL,
  "metadata_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at"    timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"    timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_experiments_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_exp_task" CHECK (
    task_type IN ('CLASSIFICATION','REGRESSION','CLUSTERING','DIM_REDUCTION','RECOMMENDATION')
  ),
  CONSTRAINT "ck_yolo_exp_status" CHECK (
    status IN ('ACTIVE','COMPLETED','ARCHIVED')
  )
);

CREATE INDEX "ix_yolo_exp_tenant"
    ON "public"."yolo_experiments" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_exp_task"
    ON "public"."yolo_experiments" USING btree ("task_type", "status");

-- ─── yolo_models ────────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_models";
CREATE TABLE "public"."yolo_models" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "experiment_id"    uuid NOT NULL,
  "name"             varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "version"          int4 NOT NULL DEFAULT 1,
  "task_type"        varchar(50)  COLLATE "pg_catalog"."default" NOT NULL,
  "algorithm"        varchar(100) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "hyperparams_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "artifact_uri"     text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "artifact_hash"    varchar(64) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "metrics_json"     jsonb NOT NULL DEFAULT '{}'::jsonb,
  "status"           varchar(20)  COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'DRAFT'::character varying,
  "is_active"        bool NOT NULL DEFAULT true,
  "deployed_at"      timestamptz(6) NULL,
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_models_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_yolo_model_name_ver" UNIQUE ("tenant_id", "name", "version"),
  CONSTRAINT "ck_yolo_model_status" CHECK (
    status IN ('DRAFT','TRAINED','DEPLOYED','ARCHIVED')
  )
);

CREATE INDEX "ix_yolo_model_tenant"
    ON "public"."yolo_models" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_model_status"
    ON "public"."yolo_models" USING btree ("tenant_id", "status");
CREATE INDEX "ix_yolo_model_experiment"
    ON "public"."yolo_models" USING btree ("experiment_id");

-- ─── yolo_training_runs ─────────────────────────
DROP TABLE IF EXISTS "public"."yolo_training_runs";
CREATE TABLE "public"."yolo_training_runs" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"      uuid NOT NULL,
  "experiment_id"  uuid NOT NULL,
  "dataset_id"     uuid NOT NULL,
  "status"         varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'PENDING'::character varying,
  "config_json"    jsonb NOT NULL DEFAULT '{}'::jsonb,
  "seed"           int4 NOT NULL DEFAULT 42,
  "duration_ms"    int4 NOT NULL DEFAULT 0,
  "error_message"  text COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::text,
  "started_at"     timestamptz(6) NULL,
  "finished_at"    timestamptz(6) NULL,
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_training_runs_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_run_status" CHECK (
    status IN ('PENDING','RUNNING','SUCCESS','FAILED','CANCELLED')
  )
);

CREATE INDEX "ix_yolo_run_tenant"
    ON "public"."yolo_training_runs" USING btree ("tenant_id", "status");
CREATE INDEX "ix_yolo_run_experiment"
    ON "public"."yolo_training_runs" USING btree ("experiment_id", "created_at" DESC);

-- ─── yolo_predictions ───────────────────────────
DROP TABLE IF EXISTS "public"."yolo_predictions";
CREATE TABLE "public"."yolo_predictions" (
  "id"          uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"   uuid NOT NULL,
  "model_id"    uuid NOT NULL,
  "input_hash"  varchar(64) COLLATE "pg_catalog"."default" NOT NULL DEFAULT ''::character varying,
  "output_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "confidence"  numeric(12,8) NOT NULL DEFAULT 0,
  "latency_ms"  int4 NOT NULL DEFAULT 0,
  "source"      varchar(50) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'api'::character varying,
  "created_at"  timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"  timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_predictions_pkey" PRIMARY KEY ("id")
);

CREATE INDEX "ix_yolo_pred_tenant"
    ON "public"."yolo_predictions" USING btree ("tenant_id", "created_at" DESC);
CREATE INDEX "ix_yolo_pred_model"
    ON "public"."yolo_predictions" USING btree ("model_id", "created_at" DESC);
CREATE INDEX "ix_yolo_pred_hash"
    ON "public"."yolo_predictions" USING btree ("input_hash");

-- ─── yolo_metrics ───────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_metrics";
CREATE TABLE "public"."yolo_metrics" (
  "id"         uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"  uuid NOT NULL,
  "model_id"   uuid NOT NULL,
  "name"       varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "value"      numeric(12,8) NOT NULL DEFAULT 0,
  "step"       int4 NOT NULL DEFAULT 0,
  "split"      varchar(20) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'test'::character varying,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_metrics_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_metric_name" CHECK (
    name IN ('accuracy','f1','precision','recall','rmse','mae','r2','silhouette')
  ),
  CONSTRAINT "ck_yolo_metric_split" CHECK (
    split IN ('train','val','test')
  )
);

CREATE INDEX "ix_yolo_metric_tenant"
    ON "public"."yolo_metrics" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_metric_model"
    ON "public"."yolo_metrics" USING btree ("model_id", "name");
CREATE INDEX "ix_yolo_metric_time"
    ON "public"."yolo_metrics" USING btree ("tenant_id", "created_at" DESC);

-- ─── Trigger fn ─────────────────────────────────
CREATE OR REPLACE FUNCTION public.set_updated_at_yolo()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_yolo_dataset_updated ON "public"."yolo_datasets";
CREATE TRIGGER trg_yolo_dataset_updated BEFORE UPDATE
    ON "public"."yolo_datasets"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();

DROP TRIGGER IF EXISTS trg_yolo_feature_updated ON "public"."yolo_features";
CREATE TRIGGER trg_yolo_feature_updated BEFORE UPDATE
    ON "public"."yolo_features"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();

DROP TRIGGER IF EXISTS trg_yolo_exp_updated ON "public"."yolo_experiments";
CREATE TRIGGER trg_yolo_exp_updated BEFORE UPDATE
    ON "public"."yolo_experiments"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();

DROP TRIGGER IF EXISTS trg_yolo_model_updated ON "public"."yolo_models";
CREATE TRIGGER trg_yolo_model_updated BEFORE UPDATE
    ON "public"."yolo_models"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();

DROP TRIGGER IF EXISTS trg_yolo_run_updated ON "public"."yolo_training_runs";
CREATE TRIGGER trg_yolo_run_updated BEFORE UPDATE
    ON "public"."yolo_training_runs"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();

DROP TRIGGER IF EXISTS trg_yolo_pred_updated ON "public"."yolo_predictions";
CREATE TRIGGER trg_yolo_pred_updated BEFORE UPDATE
    ON "public"."yolo_predictions"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();

DROP TRIGGER IF EXISTS trg_yolo_metric_updated ON "public"."yolo_metrics";
CREATE TRIGGER trg_yolo_metric_updated BEFORE UPDATE
    ON "public"."yolo_metrics"
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_yolo();

-- ─── RLS ────────────────────────────────────────
ALTER TABLE "public"."yolo_datasets"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_features"      ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_experiments"   ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_models"        ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_training_runs" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_predictions"   ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_metrics"       ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_yolo_dataset ON "public"."yolo_datasets";
CREATE POLICY p_yolo_dataset ON "public"."yolo_datasets"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_feature ON "public"."yolo_features";
CREATE POLICY p_yolo_feature ON "public"."yolo_features"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_exp ON "public"."yolo_experiments";
CREATE POLICY p_yolo_exp ON "public"."yolo_experiments"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_model ON "public"."yolo_models";
CREATE POLICY p_yolo_model ON "public"."yolo_models"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_run ON "public"."yolo_training_runs";
CREATE POLICY p_yolo_run ON "public"."yolo_training_runs"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_pred ON "public"."yolo_predictions";
CREATE POLICY p_yolo_pred ON "public"."yolo_predictions"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_metric ON "public"."yolo_metrics";
CREATE POLICY p_yolo_metric ON "public"."yolo_metrics"
    USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
"""

    def _v002_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V002__seed_ai_ml.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."yolo_experiments"
    (tenant_id, name, description, task_type, status)
VALUES
    ('00000000-0000-0000-0000-000000000001',
     'churn-prediction-v1', 'Customer churn prediction baseline',
     'CLASSIFICATION', 'ACTIVE'),
    ('00000000-0000-0000-0000-000000000001',
     'demand-forecast-v1', 'Product demand forecasting',
     'REGRESSION', 'ACTIVE')
ON CONFLICT DO NOTHING;

COMMIT;
"""

    def _v003_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V003__rollback_ai_ml.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP TRIGGER IF EXISTS trg_yolo_metric_updated  ON "public"."yolo_metrics";
DROP TRIGGER IF EXISTS trg_yolo_pred_updated    ON "public"."yolo_predictions";
DROP TRIGGER IF EXISTS trg_yolo_run_updated     ON "public"."yolo_training_runs";
DROP TRIGGER IF EXISTS trg_yolo_model_updated   ON "public"."yolo_models";
DROP TRIGGER IF EXISTS trg_yolo_exp_updated     ON "public"."yolo_experiments";
DROP TRIGGER IF EXISTS trg_yolo_feature_updated ON "public"."yolo_features";
DROP TRIGGER IF EXISTS trg_yolo_dataset_updated ON "public"."yolo_datasets";

DROP POLICY IF EXISTS p_yolo_metric  ON "public"."yolo_metrics";
DROP POLICY IF EXISTS p_yolo_pred    ON "public"."yolo_predictions";
DROP POLICY IF EXISTS p_yolo_run     ON "public"."yolo_training_runs";
DROP POLICY IF EXISTS p_yolo_model   ON "public"."yolo_models";
DROP POLICY IF EXISTS p_yolo_exp     ON "public"."yolo_experiments";
DROP POLICY IF EXISTS p_yolo_feature ON "public"."yolo_features";
DROP POLICY IF EXISTS p_yolo_dataset ON "public"."yolo_datasets";

DROP TABLE IF EXISTS "public"."yolo_metrics"       CASCADE;
DROP TABLE IF EXISTS "public"."yolo_predictions"   CASCADE;
DROP TABLE IF EXISTS "public"."yolo_training_runs" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_models"        CASCADE;
DROP TABLE IF EXISTS "public"."yolo_experiments"   CASCADE;
DROP TABLE IF EXISTS "public"."yolo_features"      CASCADE;
DROP TABLE IF EXISTS "public"."yolo_datasets"      CASCADE;

DROP FUNCTION IF EXISTS public.set_updated_at_yolo();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  6. ALEMBIC MIGRATION
    # ═══════════════════════════════════════════════════════════
    def create_migration(self) -> None:
        info(f"[ALEMBIC] {self.module}")
        rev = "yolo_001"
        prev = self._get_head_revision()

        create_block = "\n\n".join([
            self._alembic_table_datasets(),
            self._alembic_table_features(),
            self._alembic_table_experiments(),
            self._alembic_table_models(),
            self._alembic_table_runs(),
            self._alembic_table_predictions(),
            self._alembic_table_metrics(),
        ])

        trigger_lines: list[str] = []
        for tbl in TABLE_NAMES:
            trigger_lines.append(
                '    op.execute(f"""\n'
                f'        DROP TRIGGER IF EXISTS trg_{tbl}_updated\n'
                f'            ON {{SCHEMA}}.{tbl};\n'
                f'        CREATE TRIGGER trg_{tbl}_updated\n'
                f'            BEFORE UPDATE ON {{SCHEMA}}.{tbl}\n'
                f'            FOR EACH ROW EXECUTE '
                f'FUNCTION public.set_updated_at_yolo();\n'
                '    """)'
            )
        trigger_block = "\n".join(trigger_lines)

        rls_loop = "\n".join(
            f'        "{tbl}",' for tbl in TABLE_NAMES
        )

        drop_block_lines: list[str] = []
        for tbl in reversed(TABLE_NAMES):
            drop_block_lines.append(
                f'    op.execute(f"DROP POLICY IF EXISTS '
                f'p_{tbl}_tenant ON {{SCHEMA}}.{tbl};")'
            )
            drop_block_lines.append(
                f'    op.execute(f"DROP TRIGGER IF EXISTS '
                f'trg_{tbl}_updated ON {{SCHEMA}}.{tbl};")'
            )
            drop_block_lines.append(
                f'    op.execute(f\'DROP TABLE IF EXISTS '
                f'"{SCHEMA}"."{tbl}" CASCADE;\')'
            )
        drop_block = "\n".join(drop_block_lines)

        content = f'''"""add ai_ml tables

Revision ID: {rev}
Revises: {prev}
Create Date: {datetime.now(UTC).date().isoformat()}

TH: สร้างตาราง ai_ml 7 ตาราง (schema: public, prefix: yolo_)
EN: create 7 ai_ml tables (public schema, yolo_ prefix)
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
    """TH: สร้างตาราง ai_ml | EN: create ai_ml tables"""

{create_block}

    op.execute("""
        CREATE OR REPLACE FUNCTION public.set_updated_at_yolo()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

{trigger_block}

    for tbl in (
{rls_loop}
    ):
        op.execute(
            f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;"
        )
        op.execute(f"""
            DROP POLICY IF EXISTS p_{{tbl}}_tenant ON {{SCHEMA}}.{{tbl}};
            CREATE POLICY p_{{tbl}}_tenant ON {{SCHEMA}}.{{tbl}}
                USING (
                    tenant_id = current_setting(
                        'app.current_tenant', true
                    )::uuid
                );
        """)


def downgrade() -> None:
    """TH: ลบตาราง ai_ml | EN: drop ai_ml tables"""

{drop_block}

    op.execute("DROP FUNCTION IF EXISTS public.set_updated_at_yolo();")
'''
        self.writer.write(
            f"{self.alembic_dir}/{rev}_add_{self.module}_tables.py",
            content,
        )

    def _alembic_table_datasets(self) -> str:
        return '''    op.create_table(
        "yolo_datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("source_uri", sa.Text, nullable=False, server_default=""),
        sa.Column("content_hash", sa.String(64), nullable=False,
                  server_default=""),
        sa.Column("rows", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cols", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False,
                  server_default="RAW"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("schema_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("profile_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('RAW','PROCESSED','ARCHIVED')",
            name="ck_yolo_dataset_status",
        ),
        sa.UniqueConstraint(
            "tenant_id", "name", "version",
            name="uq_yolo_dataset_name_ver",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_dataset_tenant", "yolo_datasets",
                    ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_dataset_status", "yolo_datasets",
                    ["tenant_id", "status"], schema=SCHEMA)
    op.create_index("ix_yolo_dataset_hash", "yolo_datasets",
                    ["content_hash"], schema=SCHEMA)'''

    def _alembic_table_features(self) -> str:
        return '''    op.create_table(
        "yolo_features",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("dtype", sa.String(50), nullable=False,
                  server_default="float"),
        sa.Column("transform", sa.String(100), nullable=False,
                  server_default=""),
        sa.Column("source_dataset_id", postgresql.UUID(as_uuid=True),
                  nullable=True),
        sa.Column("entity_key", sa.String(100), nullable=False,
                  server_default=""),
        sa.Column("ttl_seconds", sa.Integer, nullable=False,
                  server_default="3600"),
        sa.Column("is_online", sa.Boolean, nullable=False,
                  server_default=sa.text("true")),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "name", name="uq_yolo_feature_name"),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_feature_tenant", "yolo_features",
                    ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_feature_online", "yolo_features",
                    ["tenant_id", "is_online"], schema=SCHEMA)
    op.create_index("ix_yolo_feature_entity", "yolo_features",
                    ["entity_key"], schema=SCHEMA)'''

    def _alembic_table_experiments(self) -> str:
        return '''    op.create_table(
        "yolo_experiments",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False,
                  server_default="ACTIVE"),
        sa.Column("best_model_id", postgresql.UUID(as_uuid=True),
                  nullable=True),
        sa.Column("metadata_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "task_type IN ('CLASSIFICATION','REGRESSION','CLUSTERING',"
            "'DIM_REDUCTION','RECOMMENDATION')",
            name="ck_yolo_exp_task",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE','COMPLETED','ARCHIVED')",
            name="ck_yolo_exp_status",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_exp_tenant", "yolo_experiments",
                    ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_exp_task", "yolo_experiments",
                    ["task_type", "status"], schema=SCHEMA)'''

    def _alembic_table_models(self) -> str:
        return '''    op.create_table(
        "yolo_models",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True),
                  nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("task_type", sa.String(50), nullable=False),
        sa.Column("algorithm", sa.String(100), nullable=False,
                  server_default=""),
        sa.Column("hyperparams_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("artifact_uri", sa.Text, nullable=False, server_default=""),
        sa.Column("artifact_hash", sa.String(64), nullable=False,
                  server_default=""),
        sa.Column("metrics_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(20), nullable=False,
                  server_default="DRAFT"),
        sa.Column("is_active", sa.Boolean, nullable=False,
                  server_default=sa.text("true")),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('DRAFT','TRAINED','DEPLOYED','ARCHIVED')",
            name="ck_yolo_model_status",
        ),
        sa.UniqueConstraint(
            "tenant_id", "name", "version", name="uq_yolo_model_name_ver",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_model_tenant", "yolo_models",
                    ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_model_status", "yolo_models",
                    ["tenant_id", "status"], schema=SCHEMA)
    op.create_index("ix_yolo_model_experiment", "yolo_models",
                    ["experiment_id"], schema=SCHEMA)'''

    def _alembic_table_runs(self) -> str:
        return '''    op.create_table(
        "yolo_training_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("experiment_id", postgresql.UUID(as_uuid=True),
                  nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True),
                  nullable=False),
        sa.Column("status", sa.String(20), nullable=False,
                  server_default="PENDING"),
        sa.Column("config_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("seed", sa.Integer, nullable=False, server_default="42"),
        sa.Column("duration_ms", sa.Integer, nullable=False,
                  server_default="0"),
        sa.Column("error_message", sa.Text, nullable=False, server_default=""),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('PENDING','RUNNING','SUCCESS','FAILED','CANCELLED')",
            name="ck_yolo_run_status",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_run_tenant", "yolo_training_runs",
                    ["tenant_id", "status"], schema=SCHEMA)
    op.create_index("ix_yolo_run_experiment", "yolo_training_runs",
                    ["experiment_id", "created_at"], schema=SCHEMA)'''

    def _alembic_table_predictions(self) -> str:
        return '''    op.create_table(
        "yolo_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("input_hash", sa.String(64), nullable=False,
                  server_default=""),
        sa.Column("output_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{}'::jsonb")),
        sa.Column("confidence", sa.Numeric(12, 8), nullable=False,
                  server_default="0"),
        sa.Column("latency_ms", sa.Integer, nullable=False,
                  server_default="0"),
        sa.Column("source", sa.String(50), nullable=False,
                  server_default="api"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_pred_tenant", "yolo_predictions",
                    ["tenant_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_yolo_pred_model", "yolo_predictions",
                    ["model_id", "created_at"], schema=SCHEMA)
    op.create_index("ix_yolo_pred_hash", "yolo_predictions",
                    ["input_hash"], schema=SCHEMA)'''

    def _alembic_table_metrics(self) -> str:
        return '''    op.create_table(
        "yolo_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True),
                  primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("value", sa.Numeric(12, 8), nullable=False,
                  server_default="0"),
        sa.Column("step", sa.Integer, nullable=False, server_default="0"),
        sa.Column("split", sa.String(20), nullable=False,
                  server_default="test"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.CheckConstraint(
            "name IN ('accuracy','f1','precision','recall','rmse','mae',"
            "'r2','silhouette')",
            name="ck_yolo_metric_name",
        ),
        sa.CheckConstraint(
            "split IN ('train','val','test')",
            name="ck_yolo_metric_split",
        ),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_metric_tenant", "yolo_metrics",
                    ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_metric_model", "yolo_metrics",
                    ["model_id", "name"], schema=SCHEMA)
    op.create_index("ix_yolo_metric_time", "yolo_metrics",
                    ["tenant_id", "created_at"], schema=SCHEMA)'''

    def _get_head_revision(self) -> str:
        """TH: หา head revision (ข้ามตัวเอง)"""
        my_rev = "yolo_001"
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
    #  7. SWAGGER
    # ═══════════════════════════════════════════════════════════
    def create_swagger(self) -> None:
        info(f"[SWAGGER] {self.module}")
        self.writer.write(
            f"{self.mod_root}/presentation/swagger.py",
            self._swagger_content(),
        )

    # ═══════════════════════════════════════════════════════════
    #  8. POSTMAN
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
    "name": "ai_ml API",
    "_postman_id": "{uuid.uuid4()}",
    "description": "AI/ML Platform — Datasets, Features, Training, Serving, Drift",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  }},
  "variable": [
    {{ "key": "base_url", "value": "http://localhost:8000" }},
    {{ "key": "dataset_id", "value": "" }},
    {{ "key": "experiment_id", "value": "" }},
    {{ "key": "model_id", "value": "" }}
  ],
  "item": [
    {{
      "name": "Datasets",
      "item": [
        {{
          "name": "Register Dataset",
          "request": {{
            "method": "POST",
            "header": [
              {{ "key": "Content-Type", "value": "application/json" }},
              {{ "key": "Idempotency-Key", "value": "{{{{$guid}}}}" }}
            ],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/datasets",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "datasets"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"name\\": \\"churn-train-2025\\",\\n  \\"source_uri\\": \\"s3://datasets/churn.parquet\\",\\n  \\"rows\\": 10000,\\n  \\"cols\\": 25\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }},
        {{
          "name": "List Datasets",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/datasets?page=1&size=50",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "datasets"],
              "query": [
                {{ "key": "page", "value": "1" }},
                {{ "key": "size", "value": "50" }}
              ]
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Experiments",
      "item": [
        {{
          "name": "Create Experiment",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/experiments",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "experiments"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"name\\": \\"churn-v2\\",\\n  \\"description\\": \\"Improved churn model\\",\\n  \\"task_type\\": \\"CLASSIFICATION\\"\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Training",
      "item": [
        {{
          "name": "Start Training",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/train",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "train"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"experiment_id\\": \\"{{{{experiment_id}}}}\\",\\n  \\"dataset_id\\": \\"{{{{dataset_id}}}}\\",\\n  \\"algorithm\\": \\"logistic_regression\\",\\n  \\"test_size\\": 0.2\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }},
        {{
          "name": "Get Training Status",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/train/{{{{run_id}}}}",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "train", "{{{{run_id}}}}"]
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Models",
      "item": [
        {{
          "name": "List Models",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/models",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "models"]
            }}
          }}
        }},
        {{
          "name": "Deploy Model",
          "request": {{
            "method": "POST",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/models/{{{{model_id}}}}/deploy",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "models", "{{{{model_id}}}}", "deploy"]
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Prediction",
      "item": [
        {{
          "name": "Predict",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/predict",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "predict"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"model_id\\": \\"{{{{model_id}}}}\\",\\n  \\"features\\": {{\\n    \\"age\\": 35,\\n    \\"tenure_months\\": 12,\\n    \\"monthly_charges\\": 65.5\\n  }}\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }},
        {{
          "name": "Batch Predict",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/predict/batch",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "predict", "batch"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"model_id\\": \\"{{{{model_id}}}}\\",\\n  \\"items\\": [\\n    {{\\"age\\": 25, \\"tenure_months\\": 6}},\\n    {{\\"age\\": 45, \\"tenure_months\\": 24}}\\n  ]\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }},
    {{
      "name": "Metrics & Drift",
      "item": [
        {{
          "name": "Get Metrics",
          "request": {{
            "method": "GET",
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/metrics/{{{{model_id}}}}",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "metrics", "{{{{model_id}}}}"]
            }}
          }}
        }},
        {{
          "name": "Check Drift",
          "request": {{
            "method": "POST",
            "header": [{{ "key": "Content-Type", "value": "application/json" }}],
            "url": {{
              "raw": "{{{{base_url}}}}/api/v1/ai-ml/metrics/drift",
              "host": ["{{{{base_url}}}}"],
              "path": ["api", "v1", "ai-ml", "metrics", "drift"]
            }},
            "body": {{
              "mode": "raw",
              "raw": "{{\\n  \\"model_id\\": \\"{{{{model_id}}}}\\",\\n  \\"reference\\": [{{\\"age\\": 35, \\"score\\": 0.5}}],\\n  \\"current\\": [{{\\"age\\": 36, \\"score\\": 0.6}}],\\n  \\"threshold\\": 0.3\\n}}",
              "options": {{ "raw": {{ "language": "json" }} }}
            }}
          }}
        }}
      ]
    }}
  ]
}}
'''

    # ═══════════════════════════════════════════════════════════
    #  9. TESTS
    # ═══════════════════════════════════════════════════════════
    def create_tests(self) -> None:
        info(f"[TESTS] {self.module}")
        self._create_unit_tests()
        self._create_profiler_tests()
        self._create_metric_tests()
        self._create_integration_tests()
        self._create_property_tests()
        self._create_manual_tests()

    def _create_unit_tests(self) -> None:
        content = '''"""Unit tests for ai_ml domain"""
from __future__ import annotations
import pytest

from app.modules.ai_ml.domain.enums import (
    DatasetStatus, MetricName, ModelStatus, TaskType, TrainingStatus,
)
from app.modules.ai_ml.domain.value_objects import (
    FeatureSpec, TrainConfig,
)

pytestmark = pytest.mark.unit


class TestEnums:
    def test_dataset_status_values(self) -> None:
        assert DatasetStatus.RAW == "RAW"
        assert DatasetStatus.PROCESSED == "PROCESSED"
        assert DatasetStatus.ARCHIVED == "ARCHIVED"

    def test_model_status_values(self) -> None:
        assert ModelStatus.DRAFT == "DRAFT"
        assert ModelStatus.TRAINED == "TRAINED"
        assert ModelStatus.DEPLOYED == "DEPLOYED"

    def test_training_status_values(self) -> None:
        assert TrainingStatus.PENDING == "PENDING"
        assert TrainingStatus.SUCCESS == "SUCCESS"

    def test_task_type_values(self) -> None:
        assert TaskType.CLASSIFICATION == "CLASSIFICATION"
        assert TaskType.REGRESSION == "REGRESSION"

    def test_metric_name_values(self) -> None:
        assert MetricName.ACCURACY == "accuracy"
        assert MetricName.F1 == "f1"


class TestFeatureSpec:
    def test_create_valid(self) -> None:
        spec = FeatureSpec(name="age", dtype="int", nullable=False)
        assert spec.name == "age"
        assert spec.dtype == "int"
        assert spec.nullable is False

    def test_invalid_name(self) -> None:
        with pytest.raises(ValueError):
            FeatureSpec(name="")

    def test_invalid_dtype(self) -> None:
        with pytest.raises(ValueError):
            FeatureSpec(name="x", dtype="unknown")


class TestTrainConfig:
    def test_create_defaults(self) -> None:
        cfg = TrainConfig()
        assert cfg.test_size == 0.2
        assert cfg.random_state == 42

    def test_invalid_test_size(self) -> None:
        with pytest.raises(ValueError):
            TrainConfig(test_size=1.5)

    def test_invalid_cv_folds(self) -> None:
        with pytest.raises(ValueError):
            TrainConfig(cv_folds=1)

    def test_hyperparams_dict(self) -> None:
        cfg = TrainConfig(hyperparams=(("n_estimators", 100), ("max_depth", 5)))
        assert cfg.hyperparams_dict() == {
            "n_estimators": 100, "max_depth": 5,
        }
'''
        self.writer.write(f"{self.tests_dir}/unit/test_{self.module}.py", content)

    def _create_profiler_tests(self) -> None:
        content = '''"""Unit tests for dataframe profiler"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest

from app.modules.ai_ml.domain.helpers import profile_dataframe

pytestmark = pytest.mark.unit


class TestDataFrameProfiler:
    def test_profile_basic(self) -> None:
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4.0, 5.0, 6.0]})
        profile = profile_dataframe(df)
        assert profile.rows == 3
        assert profile.cols == 2
        assert profile.missing_ratio == 0.0

    def test_profile_missing_values(self) -> None:
        df = pd.DataFrame({"a": [1, None, 3], "b": [None, None, 6.0]})
        profile = profile_dataframe(df)
        assert profile.missing_ratio > 0

    def test_profile_dtypes(self) -> None:
        df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
        profile = profile_dataframe(df)
        dtypes = profile.dtypes_dict()
        assert "a" in dtypes
        assert "b" in dtypes

    def test_profile_empty_dataframe(self) -> None:
        df = pd.DataFrame()
        profile = profile_dataframe(df)
        assert profile.rows == 0
        assert profile.cols == 0

    def test_profile_stats_numeric(self) -> None:
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0]})
        profile = profile_dataframe(df)
        stats = profile.stats_dict()
        assert "a" in stats
        assert stats["a"]["min"] == 1.0
        assert stats["a"]["max"] == 3.0

    def test_profile_unicode_columns(self) -> None:
        df = pd.DataFrame({"อายุ": [25, 30], "ชื่อ": ["a", "b"]})
        profile = profile_dataframe(df)
        assert profile.cols == 2
'''
        self.writer.write(
            f"{self.tests_dir}/unit/test_dataframe_profiler.py", content,
        )

    def _create_metric_tests(self) -> None:
        content = '''"""Unit tests for metric calculator"""
from __future__ import annotations
import numpy as np
import pytest

from app.modules.ai_ml.domain.enums import TaskType
from app.modules.ai_ml.domain.helpers import calculate_metrics

pytestmark = pytest.mark.unit


class TestClassificationMetrics:
    def test_accuracy_binary(self) -> None:
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])
        m = calculate_metrics(TaskType.CLASSIFICATION, y_true, y_pred)
        assert m.accuracy is not None
        assert 0.0 <= m.accuracy <= 1.0

    def test_accuracy_multiclass(self) -> None:
        y_true = np.array([0, 1, 2, 0, 1, 2])
        y_pred = np.array([0, 1, 2, 0, 1, 2])
        m = calculate_metrics(TaskType.CLASSIFICATION, y_true, y_pred)
        assert m.accuracy == 1.0

    def test_f1_binary(self) -> None:
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])
        m = calculate_metrics(TaskType.CLASSIFICATION, y_true, y_pred)
        assert m.f1 is not None


class TestRegressionMetrics:
    def test_rmse_regression(self) -> None:
        y_true = np.array([1.0, 2.0, 3.0, 4.0])
        y_pred = np.array([1.1, 2.1, 2.9, 4.2])
        m = calculate_metrics(TaskType.REGRESSION, y_true, y_pred)
        assert m.rmse is not None
        assert m.rmse > 0

    def test_r2_regression(self) -> None:
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([1.0, 2.0, 3.0])
        m = calculate_metrics(TaskType.REGRESSION, y_true, y_pred)
        assert m.r2 is not None
        assert m.r2 == 1.0


class TestClusteringMetrics:
    def test_silhouette_clustering(self) -> None:
        X = np.array([[0, 0], [1, 1], [10, 10], [11, 11]])
        labels = np.array([0, 0, 1, 1])
        m = calculate_metrics(TaskType.CLUSTERING, X=X, labels=labels)
        assert m.silhouette is not None
'''
        self.writer.write(
            f"{self.tests_dir}/unit/test_metric_calculator.py", content,
        )

    def _create_integration_tests(self) -> None:
        content = '''"""Integration tests for ai_ml repository — RLS verified"""
from __future__ import annotations
import uuid

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration


class TestDatasetRepository:
    async def test_save_and_find_dataset(
        self, db_session, tenant_ctx,
    ) -> None:
        from app.modules.ai_ml.infrastructure.dataset_repository import (
            DatasetRepository,
        )
        from app.modules.ai_ml.infrastructure.models import DatasetModel

        repo = DatasetRepository(db_session)
        ds = DatasetModel(
            tenant_id=tenant_ctx.tenant_id,
            name=f"test-dataset-{uuid.uuid4()}",
            source_uri="s3://test/data.parquet",
            rows=100, cols=5,
        )
        saved = await repo.save(tenant_ctx, ds)
        found = await repo.find_by_id(tenant_ctx, saved.id)
        assert found is not None
        assert found.rows == 100

    async def test_rls_blocks_other_tenant(
        self, db_session, tenant_ctx, other_tenant_ctx,
    ) -> None:
        from app.modules.ai_ml.infrastructure.dataset_repository import (
            DatasetRepository,
        )
        from app.modules.ai_ml.infrastructure.models import DatasetModel

        repo = DatasetRepository(db_session)
        ds = DatasetModel(
            tenant_id=tenant_ctx.tenant_id,
            name=f"private-{uuid.uuid4()}",
            rows=50, cols=3,
        )
        saved = await repo.save(tenant_ctx, ds)

        await db_session.execute(
            text("SELECT set_config('app.current_tenant', :tid, true)"),
            {"tid": str(other_tenant_ctx.tenant_id)},
        )
        found = await repo.find_by_id(other_tenant_ctx, saved.id)
        assert found is None

    async def test_find_paginated(self, db_session, tenant_ctx) -> None:
        from app.modules.ai_ml.infrastructure.dataset_repository import (
            DatasetRepository,
        )
        repo = DatasetRepository(db_session)
        items, total = await repo.find_paginated(tenant_ctx, page=1, size=10)
        assert isinstance(items, list)
        assert isinstance(total, int)


class TestModelRepository:
    async def test_save_and_find_model(
        self, db_session, tenant_ctx,
    ) -> None:
        from app.modules.ai_ml.infrastructure.model_repository import (
            ModelRepository,
        )
        from app.modules.ai_ml.infrastructure.models import MLModel

        repo = ModelRepository(db_session)
        model = MLModel(
            tenant_id=tenant_ctx.tenant_id,
            experiment_id=uuid.uuid4(),
            name=f"model-{uuid.uuid4()}",
            task_type="CLASSIFICATION",
            algorithm="logistic_regression",
            status="TRAINED",
        )
        saved = await repo.save(tenant_ctx, model)
        found = await repo.find_by_id(tenant_ctx, saved.id)
        assert found is not None
        assert found.task_type == "CLASSIFICATION"


class TestTrainingRunRepository:
    async def test_create_and_update_status(
        self, db_session, tenant_ctx,
    ) -> None:
        from app.modules.ai_ml.infrastructure.training_run_repository import (
            TrainingRunRepository,
        )
        from app.modules.ai_ml.infrastructure.models import TrainingRunModel

        repo = TrainingRunRepository(db_session)
        run = TrainingRunModel(
            tenant_id=tenant_ctx.tenant_id,
            experiment_id=uuid.uuid4(),
            dataset_id=uuid.uuid4(),
            status="PENDING",
        )
        saved = await repo.create(tenant_ctx, run)
        await repo.update_status(tenant_ctx, saved.id, "RUNNING")
        updated = await repo.find_by_id(tenant_ctx, saved.id)
        assert updated is not None
        assert updated.status == "RUNNING"


class TestMetricRepository:
    async def test_create_and_find(
        self, db_session, tenant_ctx,
    ) -> None:
        from decimal import Decimal

        from app.modules.ai_ml.infrastructure.metric_repository import (
            MetricRepository,
        )
        from app.modules.ai_ml.infrastructure.models import MetricModel

        repo = MetricRepository(db_session)
        model_id = uuid.uuid4()
        metric = MetricModel(
            tenant_id=tenant_ctx.tenant_id,
            model_id=model_id,
            name="accuracy",
            value=Decimal("0.92"),
            step=0,
            split="test",
        )
        await repo.create(tenant_ctx, metric)
        rows = await repo.find_by_model(tenant_ctx, model_id)
        assert len(rows) >= 1


class TestPredictionRepository:
    async def test_create_prediction(
        self, db_session, tenant_ctx,
    ) -> None:
        from decimal import Decimal

        from app.modules.ai_ml.infrastructure.models import PredictionModel
        from app.modules.ai_ml.infrastructure.prediction_repository import (
            PredictionRepository,
        )

        repo = PredictionRepository(db_session)
        pred = PredictionModel(
            tenant_id=tenant_ctx.tenant_id,
            model_id=uuid.uuid4(),
            input_hash="abc123",
            output_json={"score": 0.87},
            confidence=Decimal("0.87"),
            latency_ms=45,
            source="api",
        )
        saved = await repo.create(tenant_ctx, pred)
        assert saved.id is not None
        assert saved.latency_ms == 45
'''
        self.writer.write(
            f"{self.tests_dir}/integration/test_{self.module}_repository.py",
            content,
        )

    def _create_property_tests(self) -> None:
        content = '''"""Property tests for ai_ml invariants"""
from __future__ import annotations
import pytest
from hypothesis import given, settings, strategies as st

from app.modules.ai_ml.domain.enums import (
    DatasetStatus, ModelStatus, TaskType, TrainingStatus,
)
from app.modules.ai_ml.domain.value_objects import (
    FeatureSpec, ModelMetrics, TrainConfig,
)

pytestmark = pytest.mark.property


@settings(max_examples=100)
@given(
    rows=st.integers(min_value=0, max_value=10_000_000),
    cols=st.integers(min_value=0, max_value=10_000),
)
def test_dataset_status_always_valid(rows: int, cols: int) -> None:
    assert DatasetStatus.RAW in DatasetStatus
    assert rows >= 0
    assert cols >= 0


@settings(max_examples=100)
@given(
    name=st.text(min_size=1, max_size=100),
    dtype=st.sampled_from(["float", "int", "bool", "str", "category"]),
)
def test_feature_spec_always_valid(name: str, dtype: str) -> None:
    spec = FeatureSpec(name=name, dtype=dtype)
    assert spec.name == name
    assert spec.dtype == dtype


@settings(max_examples=100)
@given(
    test_size=st.floats(min_value=0.01, max_value=0.99),
    random_state=st.integers(min_value=0, max_value=2**31 - 1),
)
def test_train_config_always_valid(
    test_size: float, random_state: int,
) -> None:
    cfg = TrainConfig(test_size=test_size, random_state=random_state)
    assert 0.0 < cfg.test_size < 1.0
    assert cfg.random_state == random_state


@settings(max_examples=100)
@given(acc=st.floats(min_value=0.0, max_value=1.0))
def test_model_metrics_accuracy_always_valid(acc: float) -> None:
    m = ModelMetrics(accuracy=acc)
    assert 0.0 <= m.accuracy <= 1.0


@settings(max_examples=100)
@given(status=st.sampled_from(list(ModelStatus)))
def test_model_status_always_valid(status: ModelStatus) -> None:
    assert status in ModelStatus


@settings(max_examples=100)
@given(status=st.sampled_from(list(TrainingStatus)))
def test_training_status_always_valid(status: TrainingStatus) -> None:
    assert status in TrainingStatus


@settings(max_examples=100)
@given(task=st.sampled_from(list(TaskType)))
def test_task_type_always_valid(task: TaskType) -> None:
    assert task in TaskType


@settings(max_examples=100)
@given(
    payload=st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.integers(),
        max_size=20,
    )
)
def test_hash_payload_always_deterministic(payload: dict) -> None:
    from app.modules.ai_ml.application.utils import hash_payload
    h1 = hash_payload(payload)
    h2 = hash_payload(payload)
    assert h1 == h2
    assert len(h1) == 64
'''
        self.writer.write(
            f"{self.tests_dir}/property/test_{self.module}_invariants.py",
            content,
        )

    def _create_manual_tests(self) -> None:
        content = '''# Manual Test — ai_ml Module

## Pre-conditions
- [ ] DB migrated (V001-V003)
- [ ] Redis running
- [ ] Kafka running
- [ ] S3/MinIO accessible
- [ ] MLflow running (optional)
- [ ] `TEST_DATABASE_URL` set

## Scenarios (15)

| # | Scenario | Method | Endpoint | Expected |
|---|----------|--------|----------|----------|
| 1 | Register dataset | POST | `/ai-ml/datasets` | 201 + dataset_id |
| 2 | List datasets | GET | `/ai-ml/datasets` | paginated |
| 3 | Get dataset | GET | `/ai-ml/datasets/{id}` | detail + profile |
| 4 | Define feature | POST | `/ai-ml/features` | 201 |
| 5 | Create experiment | POST | `/ai-ml/experiments` | 201 |
| 6 | List experiments | GET | `/ai-ml/experiments` | array |
| 7 | Start training (mock) | POST | `/ai-ml/train` | 201 + model_id |
| 8 | Get training status | GET | `/ai-ml/train/{id}` | status=SUCCESS |
| 9 | List models | GET | `/ai-ml/models` | array |
| 10 | Get model detail | GET | `/ai-ml/models/{id}` | detail + metrics |
| 11 | Deploy model | POST | `/ai-ml/models/{id}/deploy` | status=DEPLOYED |
| 12 | Predict (real-time) | POST | `/ai-ml/predict` | output + confidence |
| 13 | Batch predict | POST | `/ai-ml/predict/batch` | N predictions |
| 14 | Get metrics | GET | `/ai-ml/metrics/{model_id}` | array |
| 15 | Check drift | POST | `/ai-ml/metrics/drift` | drift_score |

## RLS Checks
- [ ] Cross-tenant dataset read → 404
- [ ] Cross-tenant model read → 404
- [ ] Cross-tenant training run → 404
- [ ] Cross-tenant prediction log → empty

## Performance
- [ ] p95 API < 500ms (non-predict)
- [ ] p99 predict < 100ms
- [ ] Training orchestration < 5s
- [ ] Cache hit ≥ 80%

## ML-Specific
- [ ] Feature store point-in-time correct
- [ ] Model artifact hash immutable
- [ ] Reproducibility (same seed → same metrics)
- [ ] Drift detection works
- [ ] Decimal cost tracking

## Integration
- [ ] MLflow experiment logged
- [ ] Feast feature materialized
- [ ] Kafka event published
- [ ] S3 artifact saved
- [ ] Redis cache populated
'''
        self.writer.write(
            f"{self.tests_dir}/manual/manual_test_{self.module}.md",
            content,
        )

    # ═══════════════════════════════════════════════════════════
    #  10. VERIFY
    # ═══════════════════════════════════════════════════════════
    def verify(self) -> None:
        info("[VERIFY] ตรวจสอบ Swagger + Postman + SQL")
        issues: list[str] = []

        swagger_py = self.root / f"{self.mod_root}/presentation/swagger.py"
        if swagger_py.exists():
            ok("swagger.py exists")
            sw_content = swagger_py.read_text(encoding="utf-8")
            if "def register_ai_ml_openapi" in sw_content:
                ok("  ✓ has register_ai_ml_openapi()")
            else:
                issues.append("swagger.py missing register_ai_ml_openapi()")
        else:
            issues.append(f"swagger.py NOT FOUND: {swagger_py}")

        app_file = self.root / self.app_py
        if app_file.exists():
            content = app_file.read_text(encoding="utf-8")
            if "register_ai_ml_openapi(app)" in content:
                ok("app.py: register_ai_ml_openapi(app) ✓")
            else:
                issues.append(
                    "app.py DOES NOT call register_ai_ml_openapi(app)",
                )
            if "ai_ml_router" in content:
                ok("app.py: ai_ml_router imported ✓")
            else:
                issues.append("app.py missing ai_ml_router import")
        else:
            issues.append(f"app.py NOT FOUND: {app_file}")

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

        for ver in ("V001", "V002", "V003"):
            d = self.root / self.sql_dir
            pattern = f"{ver}__*{self.module}*.sql"
            matches = list(d.glob(pattern)) if d.exists() else []
            if matches:
                ok(f"SQL: {matches[0].name}")
            else:
                issues.append(f"SQL {ver} not found in {d}")

        alembic_file = (
            self.root / self.alembic_dir / "yolo_001_add_ai_ml_tables.py"
        )
        if alembic_file.exists():
            ok("alembic: yolo_001_add_ai_ml_tables.py ✓")
        else:
            issues.append(f"alembic NOT FOUND: {alembic_file}")

        print()
        if issues:
            info("═" * 60)
            warn(f"พบ {len(issues)} ปัญหา:")
            for i, msg in enumerate(issues, 1):
                err(f"  {i}. {msg}")
            info("═" * 60)
            print()
            print(f"  {C.YELLOW}แนะนำ:{C.RESET}")
            print(f"    python create_module_ai_ml.py update ai_ml --force")
            print(f"    python create_module_ai_ml.py swagger ai_ml --force")
            print(f"    python create_module_ai_ml.py postman ai_ml --force")
            print()
        else:
            info("═" * 60)
            ok("ALL CHECKS PASSED ✓")
            info("═" * 60)
            print()

    # ═══════════════════════════════════════════════════════════
    #  ALL
    # ═══════════════════════════════════════════════════════════
    def run_all(self) -> None:
        self.create_module()
        self.create_sql()
        self.create_migration()
        self.create_swagger()
        self.create_postman()
        self.create_tests()
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
        print(f"    1. Verify:    python create_module_ai_ml.py verify ai_ml")
        print(f"    2. Alembic:   alembic upgrade head")
        print(f"    3. SQL:       psql $DATABASE_URL -f db/migrations/V001__*.sql")
        print(f"    4. Run:       uvicorn app.app:app --reload")
        print(f"    5. Swagger:   http://localhost:8000/docs")
        print(f"    6. Postman:   Import docs/postman/ai_ml.json")
        print()


# ═══════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════
HELP = f"""
═══════════════════════════════════════════════════════════════
  create_module_ai_ml.py — AI/ML Module Generator v{VERSION}
  Schema: {SCHEMA}  ·  Prefix: yolo_
═══════════════════════════════════════════════════════════════

  USAGE
    python create_module_ai_ml.py <action> <module> [layer] [prefix] [options]

  ACTIONS (11)
    create      [1]  สร้าง module structure (4 layers)
    activate    [2]  Register router + swagger + models
    sql         [3]  สร้าง SQL migrations V001/V002/V003
    update      [4]  Update app/app.py (+ swagger hook)
    update-env  [5]  Update migrations/env.py
    alembic     [6]  สร้าง Alembic migration (7 tables)
    swagger     [7]  สร้าง OpenAPI docs (tag: AI/ML)
    postman     [8]  สร้าง Postman collection
    test        [9]  สร้าง tests (unit/integration/property/manual)
    verify      [10] ตรวจสอบ Swagger + Postman + SQL
    all         ทำทั้งหมด
    help        แสดง help

  POSITIONAL
    module      ชื่อ module (default: ai_ml)
    layer       Layer number 0-7 (default: 5)
    prefix      3-char DB prefix (default: yolo)

  OPTIONS
    --force              เขียนทับไฟล์เดิม
    --template <A-G>     Template (default: A)
    --project-root <path> Project root path

  EXAMPLES
    # Full pipeline
    python create_module_ai_ml.py all ai_ml 5 yolo

    # ทีละขั้น
    python create_module_ai_ml.py create   ai_ml 5 yolo --force
    python create_module_ai_ml.py sql      ai_ml yolo     --force
    python create_module_ai_ml.py alembic  ai_ml yolo     --force
    python create_module_ai_ml.py swagger  ai_ml          --force
    python create_module_ai_ml.py postman  ai_ml          --force
    python create_module_ai_ml.py test     ai_ml          --force
    python create_module_ai_ml.py activate ai_ml
    alembic upgrade head

    # ตรวจสอบ
    python create_module_ai_ml.py verify ai_ml

  RESULT
    Swagger:  http://localhost:8000/docs   → tag "AI/ML"
    Postman:  Import docs/postman/ai_ml.json
    Tables:   7 tables ใน schema public (prefix yolo_)
═══════════════════════════════════════════════════════════════
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("module", nargs="?", default="ai_ml")
    parser.add_argument("layer", nargs="?", default="5")
    parser.add_argument("prefix", nargs="?", default="yolo")
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

    gen = yoloModuleGenerator(
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
        "test": gen.create_tests,
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