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
        {"schema": SCHEMA},
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
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
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
        {"schema": SCHEMA},
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
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
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
        {"schema": SCHEMA},
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
    config_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
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
        {"schema": SCHEMA},
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
        {"schema": SCHEMA},
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
    details_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
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
        {"schema": SCHEMA},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    summary_json: Mapped[str] = mapped_column(Text, nullable=False, server_default="{}")
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
