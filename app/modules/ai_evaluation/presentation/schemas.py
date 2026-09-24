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
