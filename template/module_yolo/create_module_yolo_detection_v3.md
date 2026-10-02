# 🎯 YOLO Extensions — Generator + Code Files (1+2)

ผมจะสร้าง **`create_module_yolo_extensions.py`** เป็น Generator เสริม ที่เพิ่ม 7 actions ใหม่ พร้อม code files ที่ generate ออกมาให้ดู

---

## 📁 File 1: `create_module_yolo_extensions.py`

```python
#!/usr/bin/env python3
"""
create_module_yolo_extensions.py — YOLO Extensions Generator v1.0

เพิ่ม 7 extensions ให้ module `yolo`:
  1. settings       — Platform settings
  2. report         — Training/Inference reports
  3. category       — Category taxonomy (tree)
  4. deployment     — FastAPI deployment patterns
  5. counting       — Product counting (shelf/conveyor/checkout)
  6. plant-disease  — Plant disease diagnosis
  7. plant-growth   — Plant growth monitoring

Actions:
  settings | report | category | deployment | counting
  plant-disease | plant-growth
  sql-v2 | alembic-v2 | postman-v2 | test-v2
  activate-v2 | verify-v2 | deps-v2 | all-v2 | help

Usage:
    python create_module_yolo_extensions.py all-v2 yolo --force
    python create_module_yolo_extensions.py settings yolo --force
    python create_module_yolo_extensions.py sql-v2 yolo --force
"""
from __future__ import annotations

import argparse
import json as _json
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
SCHEMA = "public"
MODULE = "yolo"

EXTENSIONS = (
    "settings", "report", "category", "deployment",
    "counting", "plant-disease", "plant-growth",
)

NEW_TABLES = (
    "yolo_settings",
    "yolo_reports",
    "yolo_categories",
    "yolo_counting_sessions",
    "yolo_counting_results",
    "yolo_diseases",
    "yolo_plant_diagnoses",
    "yolo_fields",
    "yolo_growth_assessments",
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
    def __init__(self, root: Path, force: bool = False, backup: bool = True):
        self.root = root
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
                raise RuntimeError(f"Refuse to write: {rel_path}") from exc

        path.write_text(content, encoding="utf-8", newline="\n")
        ok(rel_path)
        self.written.append(path)


# ═══════════════════════════════════════════════════════════════
#  GENERATOR
# ═══════════════════════════════════════════════════════════════
class YOLOExtensionsGenerator:
    def __init__(self, root: Path, module: str = "yolo",
                 force: bool = False):
        self.root = root
        self.module = module.lower()
        self.writer = FileWriter(root, force=force)
        self.mod_root = f"app/modules/{self.module}"
        self.sql_dir = "db/migrations"
        self.alembic_dir = "migrations/versions"
        self.tests_dir = "tests"
        self.docs_dir = "docs"

    # ═══════════════════════════════════════════════════════════
    #  1. SETTINGS
    # ═══════════════════════════════════════════════════════════
    def create_settings(self) -> None:
        info(f"[SETTINGS] {self.module}/settings")
        base = f"{self.mod_root}/domain/settings"
        self.writer.write(f"{base}/__init__.py", dedent('''\
            """YOLO settings domain"""
            from .entities import PlatformSettings, SettingsPatch

            __all__ = ["PlatformSettings", "SettingsPatch"]
        '''))

        self.writer.write(f"{base}/entities.py", self._settings_entities())

        # Application
        app_base = f"{self.mod_root}/application"
        self.writer.write(f"{app_base}/settings_use_case.py",
                           self._settings_use_case())

        # Infrastructure
        infra_base = f"{self.mod_root}/infrastructure"
        self.writer.write(f"{infra_base}/models_settings.py",
                           self._settings_model())
        self.writer.write(f"{infra_base}/settings_repository.py",
                           self._settings_repo())

        # Presentation
        pres_base = f"{self.mod_root}/presentation"
        self.writer.write(f"{pres_base}/router_settings.py",
                           self._settings_router())
        self.writer.write(f"{pres_base}/schemas_settings.py",
                           self._settings_schemas())

    def _settings_entities(self) -> str:
        return dedent('''\
            """Settings entities"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import UTC, datetime
            from typing import Any


            @dataclass(slots=True)
            class PlatformSettings:
                """TH: ตั้งค่า platform | EN: platform settings"""
                tenant_id: uuid.UUID
                default_model: str = "yolov8n.pt"
                device: str = "auto"
                conf_threshold: float = 0.25
                iou_threshold: float = 0.45
                max_batch_size: int = 32
                timeout_seconds: int = 30
                cache_ttl: int = 300
                artifact_bucket: str = "yolo-artifacts"
                enable_tensorrt: bool = False
                enable_half: bool = True
                max_trainings: int = 1
                retention_days: int = 90
                extra_json: dict[str, Any] = field(default_factory=dict)
                created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
                updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

                def validate(self) -> list[str]:
                    """TH: ตรวจสอบความถูกต้อง | EN: validate"""
                    errors: list[str] = []
                    if not 0.0 <= self.conf_threshold <= 1.0:
                        errors.append("conf_threshold must be in [0,1]")
                    if not 0.0 <= self.iou_threshold <= 1.0:
                        errors.append("iou_threshold must be in [0,1]")
                    if not 1 <= self.max_batch_size <= 128:
                        errors.append("max_batch_size must be in [1,128]")
                    if not 1 <= self.timeout_seconds <= 600:
                        errors.append("timeout_seconds must be in [1,600]")
                    if self.device not in ("auto", "cpu") and not self.device.startswith("cuda"):
                        errors.append("device must be auto|cpu|cuda:N")
                    return errors

                def to_dict(self) -> dict[str, Any]:
                    return {
                        "tenant_id": str(self.tenant_id),
                        "default_model": self.default_model,
                        "device": self.device,
                        "conf_threshold": self.conf_threshold,
                        "iou_threshold": self.iou_threshold,
                        "max_batch_size": self.max_batch_size,
                        "timeout_seconds": self.timeout_seconds,
                        "cache_ttl": self.cache_ttl,
                        "artifact_bucket": self.artifact_bucket,
                        "enable_tensorrt": self.enable_tensorrt,
                        "enable_half": self.enable_half,
                        "max_trainings": self.max_trainings,
                        "retention_days": self.retention_days,
                        "extra": self.extra_json,
                    }


            @dataclass(frozen=True, slots=True)
            class SettingsPatch:
                """TH: patch settings (partial) | EN: settings patch"""
                default_model: str | None = None
                device: str | None = None
                conf_threshold: float | None = None
                iou_threshold: float | None = None
                max_batch_size: int | None = None
                timeout_seconds: int | None = None
                cache_ttl: int | None = None
                artifact_bucket: str | None = None
                enable_tensorrt: bool | None = None
                enable_half: bool | None = None
                max_trainings: int | None = None
                retention_days: int | None = None
                extra_json: dict[str, Any] | None = None

                def apply_to(self, settings: PlatformSettings) -> PlatformSettings:
                    """TH: นำ patch ไปใช้ | EN: apply patch"""
                    for field_name in (
                        "default_model", "device", "conf_threshold",
                        "iou_threshold", "max_batch_size", "timeout_seconds",
                        "cache_ttl", "artifact_bucket", "enable_tensorrt",
                        "enable_half", "max_trainings", "retention_days",
                    ):
                        val = getattr(self, field_name)
                        if val is not None:
                            setattr(settings, field_name, val)
                    if self.extra_json is not None:
                        settings.extra_json.update(self.extra_json)
                    settings.updated_at = datetime.now(UTC)
                    return settings
        ''')

    def _settings_use_case(self) -> str:
        return dedent('''\
            """Settings use case"""
            from __future__ import annotations
            import uuid
            from typing import Any

            import structlog

            from app.modules.yolo.domain.settings import (
                PlatformSettings, SettingsPatch,
            )

            log = structlog.get_logger()


            class SettingsUseCase:
                """TH: use case สำหรับ settings | EN: settings use case"""

                def __init__(self, repo: Any) -> None:
                    self._repo = repo

                async def get_settings(self, ctx: Any) -> dict[str, Any]:
                    """TH: ดึง settings (สร้าง default ถ้าไม่มี)"""
                    row = await self._repo.find_by_tenant(ctx, ctx.tenant_id)
                    if row is None:
                        row = await self._repo.create_default(ctx, ctx.tenant_id)
                    return self._to_dict(row)

                async def update_settings(
                    self, ctx: Any, patch: SettingsPatch,
                ) -> dict[str, Any]:
                    """TH: อัปเดต settings"""
                    row = await self._repo.find_by_tenant(ctx, ctx.tenant_id)
                    if row is None:
                        row = await self._repo.create_default(ctx, ctx.tenant_id)
                    updated = patch.apply_to(row)
                    errors = updated.validate()
                    if errors:
                        raise ValueError("; ".join(errors))
                    saved = await self._repo.update(ctx, updated)
                    log.info("yolo.settings.updated", tenant=str(ctx.tenant_id))
                    return self._to_dict(saved)

                async def reset_to_defaults(self, ctx: Any) -> dict[str, Any]:
                    """TH: reset เป็นค่าเริ่มต้น"""
                    await self._repo.delete_by_tenant(ctx, ctx.tenant_id)
                    row = await self._repo.create_default(ctx, ctx.tenant_id)
                    return self._to_dict(row)

                async def validate_settings(
                    self, ctx: Any, patch: SettingsPatch,
                ) -> dict[str, Any]:
                    """TH: ตรวจสอบก่อน save"""
                    current = await self._repo.find_by_tenant(ctx, ctx.tenant_id)
                    if current is None:
                        current = PlatformSettings(tenant_id=ctx.tenant_id)
                    test = patch.apply_to(current)
                    errors = test.validate()
                    return {
                        "valid": not errors,
                        "errors": errors,
                        "preview": self._to_dict(test),
                    }

                @staticmethod
                def _to_dict(settings: Any) -> dict[str, Any]:
                    return {
                        "default_model": settings.default_model,
                        "device": settings.device,
                        "conf_threshold": float(settings.conf_threshold),
                        "iou_threshold": float(settings.iou_threshold),
                        "max_batch_size": settings.max_batch_size,
                        "timeout_seconds": settings.timeout_seconds,
                        "cache_ttl": settings.cache_ttl,
                        "artifact_bucket": settings.artifact_bucket,
                        "enable_tensorrt": settings.enable_tensorrt,
                        "enable_half": settings.enable_half,
                        "max_trainings": settings.max_trainings,
                        "retention_days": settings.retention_days,
                        "extra": dict(settings.extra_json or {}),
                    }
        ''')

    def _settings_model(self) -> str:
        return dedent('''\
            """Settings SQLAlchemy model"""
            from __future__ import annotations
            import uuid
            from datetime import datetime

            from sqlalchemy import (
                Boolean, DateTime, Integer, Numeric, String, UniqueConstraint,
                func, text,
            )
            from sqlalchemy.dialects.postgresql import JSONB, UUID
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.yolo.infrastructure.models import Base

            SCHEMA = "public"


            class SettingsModel(Base):
                __tablename__ = "yolo_settings"
                __table_args__ = (
                    UniqueConstraint("tenant_id", name="uq_yolo_settings_tenant"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"))
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False)
                default_model: Mapped[str] = mapped_column(
                    String(50), nullable=False, server_default="yolov8n.pt")
                device: Mapped[str] = mapped_column(
                    String(20), nullable=False, server_default="auto")
                conf_threshold: Mapped[float] = mapped_column(
                    Numeric(4, 3), nullable=False, server_default="0.25")
                iou_threshold: Mapped[float] = mapped_column(
                    Numeric(4, 3), nullable=False, server_default="0.45")
                max_batch_size: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="32")
                timeout_seconds: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="30")
                cache_ttl: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="300")
                artifact_bucket: Mapped[str] = mapped_column(
                    String(200), nullable=False, server_default="yolo-artifacts")
                enable_tensorrt: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("false"))
                enable_half: Mapped[bool] = mapped_column(
                    Boolean, nullable=False, server_default=text("true"))
                max_trainings: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="1")
                retention_days: Mapped[int] = mapped_column(
                    Integer, nullable=False, server_default="90")
                extra_json: Mapped[dict] = mapped_column(
                    JSONB, nullable=False, server_default=text("'{}'::jsonb"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now())
        ''')

    def _settings_repo(self) -> str:
        return dedent('''\
            """Settings repository"""
            from __future__ import annotations
            import uuid
            from typing import Any

            from loguru import logger
            from sqlalchemy import delete, select
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.exceptions import ApplicationError
            from app.modules.yolo.domain.settings import PlatformSettings
            from app.modules.yolo.infrastructure.models_settings import SettingsModel


            class SettingsRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_tenant(self, ctx: Any, tenant_id: uuid.UUID) -> Any | None:
                    try:
                        result = await self._session.execute(
                            select(SettingsModel).where(SettingsModel.tenant_id == tenant_id))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"settings.find_by_tenant: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def create_default(self, ctx: Any, tenant_id: uuid.UUID) -> Any:
                    try:
                        row = SettingsModel(tenant_id=tenant_id)
                        self._session.add(row)
                        await self._session.flush()
                        return row
                    except SQLAlchemyError as exc:
                        logger.error(f"settings.create_default: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def update(self, ctx: Any, settings: Any) -> Any:
                    try:
                        await self._session.flush()
                        return settings
                    except SQLAlchemyError as exc:
                        logger.error(f"settings.update: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def delete_by_tenant(self, ctx: Any, tenant_id: uuid.UUID) -> bool:
                    try:
                        await self._session.execute(
                            delete(SettingsModel).where(SettingsModel.tenant_id == tenant_id))
                        await self._session.flush()
                        return True
                    except SQLAlchemyError as exc:
                        logger.error(f"settings.delete_by_tenant: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _settings_schemas(self) -> str:
        return dedent('''\
            """Settings Pydantic schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class SettingsResponse(BaseModel):
                default_model: str
                device: str
                conf_threshold: float
                iou_threshold: float
                max_batch_size: int
                timeout_seconds: int
                cache_ttl: int
                artifact_bucket: str
                enable_tensorrt: bool
                enable_half: bool
                max_trainings: int
                retention_days: int
                extra: dict[str, Any] = Field(default_factory=dict)
                model_config = ConfigDict(extra="forbid")


            class SettingsPatchRequest(BaseModel):
                default_model: str | None = None
                device: str | None = None
                conf_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
                iou_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
                max_batch_size: int | None = Field(default=None, ge=1, le=128)
                timeout_seconds: int | None = Field(default=None, ge=1, le=600)
                cache_ttl: int | None = Field(default=None, ge=0, le=86400)
                artifact_bucket: str | None = None
                enable_tensorrt: bool | None = None
                enable_half: bool | None = None
                max_trainings: int | None = Field(default=None, ge=1, le=16)
                retention_days: int | None = Field(default=None, ge=1, le=3650)
                extra_json: dict[str, Any] | None = None
                model_config = ConfigDict(extra="forbid")


            class SettingsValidateResponse(BaseModel):
                valid: bool
                errors: list[str]
                preview: dict[str, Any]
                model_config = ConfigDict(extra="forbid")
        ''')

    def _settings_router(self) -> str:
        return dedent('''\
            """Settings router"""
            from __future__ import annotations
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException, status

            from app.modules.yolo.application.settings_use_case import SettingsUseCase
            from app.modules.yolo.domain.settings import SettingsPatch
            from app.modules.yolo.infrastructure.settings_repository import (
                SettingsRepository,
            )
            from app.modules.yolo.presentation.dependencies import get_ctx
            from app.modules.yolo.presentation.schemas_settings import (
                SettingsPatchRequest, SettingsResponse, SettingsValidateResponse,
            )

            router = APIRouter(prefix="/yolo/settings", tags=["yolo"])


            async def _get_uc(session=Depends(lambda: None)) -> SettingsUseCase:  # type: ignore
                # Placeholder — override in app.py with real session
                raise HTTPException(500, "SettingsUseCase not wired")


            @router.get("", response_model=SettingsResponse,
                         summary="Get YOLO settings", operation_id="yolo_get_settings")
            async def get_settings(
                uc: Annotated[SettingsUseCase, Depends(_get_uc)],
            ) -> SettingsResponse:
                ctx = await get_ctx()
                return SettingsResponse(**await uc.get_settings(ctx))


            @router.patch("", response_model=SettingsResponse,
                           summary="Update YOLO settings",
                           operation_id="yolo_update_settings")
            async def update_settings(
                payload: SettingsPatchRequest,
                uc: Annotated[SettingsUseCase, Depends(_get_uc)],
            ) -> SettingsResponse:
                ctx = await get_ctx()
                try:
                    patch = SettingsPatch(**payload.model_dump())
                    result = await uc.update_settings(ctx, patch)
                    return SettingsResponse(**result)
                except ValueError as e:
                    raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                          detail=str(e)) from e


            @router.post("/reset", response_model=SettingsResponse,
                          summary="Reset to defaults",
                          operation_id="yolo_reset_settings")
            async def reset_settings(
                uc: Annotated[SettingsUseCase, Depends(_get_uc)],
            ) -> SettingsResponse:
                ctx = await get_ctx()
                return SettingsResponse(**await uc.reset_to_defaults(ctx))


            @router.post("/validate", response_model=SettingsValidateResponse,
                          summary="Validate settings patch",
                          operation_id="yolo_validate_settings")
            async def validate_settings(
                payload: SettingsPatchRequest,
                uc: Annotated[SettingsUseCase, Depends(_get_uc)],
            ) -> SettingsValidateResponse:
                ctx = await get_ctx()
                patch = SettingsPatch(**payload.model_dump())
                result = await uc.validate_settings(ctx, patch)
                return SettingsValidateResponse(**result)
        ''')

    # ═══════════════════════════════════════════════════════════
    #  2. REPORT
    # ═══════════════════════════════════════════════════════════
    def create_report(self) -> None:
        info(f"[REPORT] {self.module}/report")
        base = f"{self.mod_root}/domain/report"
        self.writer.write(f"{base}/__init__.py", dedent('''\
            """Report domain"""
            from .entities import InferenceReport, TrainingReport

            __all__ = ["InferenceReport", "TrainingReport"]
        '''))
        self.writer.write(f"{base}/entities.py", self._report_entities())

        app_base = f"{self.mod_root}/application"
        self.writer.write(f"{app_base}/report_use_case.py", self._report_use_case())

        pres_base = f"{self.mod_root}/presentation"
        self.writer.write(f"{pres_base}/router_report.py", self._report_router())
        self.writer.write(f"{pres_base}/schemas_report.py", self._report_schemas())

    def _report_entities(self) -> str:
        return dedent('''\
            """Report entities"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import UTC, datetime


            @dataclass(frozen=True, slots=True)
            class TrainingReport:
                training_id: uuid.UUID
                model_id: uuid.UUID
                dataset_id: uuid.UUID
                model_type: str
                epochs_completed: int
                duration_ms: int
                final_mAP50: float
                final_mAP50_95: float
                best_epoch: int
                loss_curve: tuple[tuple[int, float], ...] = ()
                per_class_ap: tuple[tuple[str, float], ...] = ()
                generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

                def to_dict(self) -> dict:
                    return {
                        "training_id": str(self.training_id),
                        "model_id": str(self.model_id),
                        "dataset_id": str(self.dataset_id),
                        "model_type": self.model_type,
                        "epochs_completed": self.epochs_completed,
                        "duration_ms": self.duration_ms,
                        "final_mAP50": self.final_mAP50,
                        "final_mAP50_95": self.final_mAP50_95,
                        "best_epoch": self.best_epoch,
                        "loss_curve": list(self.loss_curve),
                        "per_class_ap": dict(self.per_class_ap),
                        "generated_at": self.generated_at.isoformat(),
                    }


            @dataclass(frozen=True, slots=True)
            class InferenceReport:
                model_id: uuid.UUID
                period_start: datetime
                period_end: datetime
                total_inferences: int = 0
                total_detections: int = 0
                avg_latency_ms: float = 0.0
                p50_latency_ms: float = 0.0
                p95_latency_ms: float = 0.0
                p99_latency_ms: float = 0.0
                cache_hit_rate: float = 0.0
                top_classes: tuple[tuple[str, int], ...] = ()
                drift_score: float = 0.0

                def to_dict(self) -> dict:
                    return {
                        "model_id": str(self.model_id),
                        "period_start": self.period_start.isoformat(),
                        "period_end": self.period_end.isoformat(),
                        "total_inferences": self.total_inferences,
                        "total_detections": self.total_detections,
                        "avg_latency_ms": self.avg_latency_ms,
                        "p50_latency_ms": self.p50_latency_ms,
                        "p95_latency_ms": self.p95_latency_ms,
                        "p99_latency_ms": self.p99_latency_ms,
                        "cache_hit_rate": self.cache_hit_rate,
                        "top_classes": dict(self.top_classes),
                        "drift_score": self.drift_score,
                    }
        ''')

    def _report_use_case(self) -> str:
        return dedent('''\
            """Report use case"""
            from __future__ import annotations
            import csv
            import io
            import uuid
            from datetime import UTC, datetime, timedelta
            from typing import Any

            import structlog

            from app.modules.yolo.domain.report import InferenceReport, TrainingReport

            log = structlog.get_logger()


            class ReportUseCase:
                def __init__(self, training_repo: Any, model_repo: Any,
                              dataset_repo: Any, inference_repo: Any) -> None:
                    self._trainings = training_repo
                    self._models = model_repo
                    self._datasets = dataset_repo
                    self._inferences = inference_repo

                async def training_report(self, ctx: Any,
                                            training_id: uuid.UUID) -> dict[str, Any]:
                    tr = await self._trainings.find_by_id(ctx, training_id)
                    if tr is None:
                        raise ValueError(f"training {training_id} not found")
                    models = await self._models.find_by_training(ctx, training_id)
                    best = models[0] if models else None
                    report = TrainingReport(
                        training_id=tr.id,
                        model_id=best.id if best else uuid.UUID(int=0),
                        dataset_id=tr.dataset_id,
                        model_type=tr.model_type,
                        epochs_completed=tr.epochs,
                        duration_ms=tr.duration_ms or 0,
                        final_mAP50=float(best.mAP50) if best else 0.0,
                        final_mAP50_95=float(best.mAP50_95) if best else 0.0,
                        best_epoch=tr.epochs,
                    )
                    return report.to_dict()

                async def model_report(self, ctx: Any, model_id: uuid.UUID,
                                        period_days: int = 30) -> dict[str, Any]:
                    since = datetime.now(UTC) - timedelta(days=period_days)
                    stats = await self._inferences.stats_by_model(ctx, model_id, since)
                    report = InferenceReport(
                        model_id=model_id,
                        period_start=since,
                        period_end=datetime.now(UTC),
                        total_inferences=stats.get("count", 0),
                        total_detections=stats.get("total_detections", 0),
                        avg_latency_ms=stats.get("avg_latency_ms", 0.0),
                        p50_latency_ms=stats.get("avg_latency_ms", 0.0),
                        p95_latency_ms=stats.get("max_latency_ms", 0.0),
                        p99_latency_ms=stats.get("max_latency_ms", 0.0),
                    )
                    return report.to_dict()

                async def dataset_report(self, ctx: Any,
                                           dataset_id: uuid.UUID) -> dict[str, Any]:
                    ds = await self._datasets.find_by_id(ctx, dataset_id)
                    if ds is None:
                        raise ValueError(f"dataset {dataset_id} not found")
                    return {
                        "dataset_id": str(dataset_id),
                        "name": ds.name,
                        "format": ds.format,
                        "image_count": ds.image_count,
                        "class_count": ds.class_count,
                        "status": ds.status,
                    }

                async def tenant_summary(self, ctx: Any) -> dict[str, Any]:
                    datasets, ds_total = await self._datasets.find_paginated(ctx, 1, 1000)
                    models = await self._models.find_active(ctx)
                    return {
                        "datasets_total": ds_total,
                        "models_total": len(models),
                        "top_models": [
                            {"id": str(m.id), "name": m.name,
                             "mAP50": str(m.mAP50), "mAP50_95": str(m.mAP50_95)}
                            for m in models[:5]
                        ],
                    }

                async def export_report_csv(self, ctx: Any,
                                              report: dict[str, Any]) -> str:
                    buf = io.StringIO()
                    writer = csv.writer(buf)
                    writer.writerow(["key", "value"])
                    for k, v in report.items():
                        writer.writerow([k, v])
                    return buf.getvalue()
        ''')

    def _report_schemas(self) -> str:
        return dedent('''\
            """Report schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class TrainingReportResponse(BaseModel):
                training_id: str
                model_id: str
                dataset_id: str
                model_type: str
                epochs_completed: int
                duration_ms: int
                final_mAP50: float
                final_mAP50_95: float
                best_epoch: int
                loss_curve: list[list[Any]] = Field(default_factory=list)
                per_class_ap: dict[str, float] = Field(default_factory=dict)
                generated_at: str
                model_config = ConfigDict(extra="forbid")


            class InferenceReportResponse(BaseModel):
                model_id: str
                period_start: str
                period_end: str
                total_inferences: int = 0
                total_detections: int = 0
                avg_latency_ms: float = 0.0
                p50_latency_ms: float = 0.0
                p95_latency_ms: float = 0.0
                p99_latency_ms: float = 0.0
                cache_hit_rate: float = 0.0
                top_classes: dict[str, int] = Field(default_factory=dict)
                drift_score: float = 0.0
                model_config = ConfigDict(extra="forbid")
        ''')

    def _report_router(self) -> str:
        return dedent('''\
            """Report router"""
            from __future__ import annotations
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException

            from app.modules.yolo.application.report_use_case import ReportUseCase
            from app.modules.yolo.presentation.dependencies import get_ctx
            from app.modules.yolo.presentation.schemas_report import (
                InferenceReportResponse, TrainingReportResponse,
            )

            router = APIRouter(prefix="/yolo/reports", tags=["yolo"])


            async def _get_uc() -> ReportUseCase:  # type: ignore
                raise HTTPException(500, "ReportUseCase not wired")


            @router.get("/training/{training_id}", response_model=TrainingReportResponse,
                         summary="Training report", operation_id="yolo_report_training")
            async def training_report(
                training_id: uuid.UUID,
                uc: Annotated[ReportUseCase, Depends(_get_uc)],
            ) -> TrainingReportResponse:
                ctx = await get_ctx()
                try:
                    return TrainingReportResponse(**await uc.training_report(ctx, training_id))
                except ValueError as e:
                    raise HTTPException(404, detail=str(e)) from e


            @router.get("/model/{model_id}", response_model=InferenceReportResponse,
                         summary="Inference report", operation_id="yolo_report_model")
            async def model_report(
                model_id: uuid.UUID, period_days: int = 30,
                uc: Annotated[ReportUseCase, Depends(_get_uc)] = None,  # type: ignore
            ) -> InferenceReportResponse:
                ctx = await get_ctx()
                return InferenceReportResponse(
                    **await uc.model_report(ctx, model_id, period_days))


            @router.get("/dataset/{dataset_id}", summary="Dataset report",
                         operation_id="yolo_report_dataset")
            async def dataset_report(
                dataset_id: uuid.UUID,
                uc: Annotated[ReportUseCase, Depends(_get_uc)],
            ) -> dict:
                ctx = await get_ctx()
                try:
                    return await uc.dataset_report(ctx, dataset_id)
                except ValueError as e:
                    raise HTTPException(404, detail=str(e)) from e


            @router.get("/summary", summary="Tenant summary",
                         operation_id="yolo_report_summary")
            async def tenant_summary(
                uc: Annotated[ReportUseCase, Depends(_get_uc)],
            ) -> dict:
                ctx = await get_ctx()
                return await uc.tenant_summary(ctx)


            @router.post("/export/csv", summary="Export report as CSV",
                          operation_id="yolo_report_csv")
            async def export_csv(payload: dict) -> dict:
                return {"csv": "not_implemented"}
        ''')

    # ═══════════════════════════════════════════════════════════
    #  3. CATEGORY
    # ═══════════════════════════════════════════════════════════
    def create_category(self) -> None:
        info(f"[CATEGORY] {self.module}/category")
        base = f"{self.mod_root}/domain/category"
        self.writer.write(f"{base}/__init__.py", dedent('''\
            """Category domain"""
            from .entities import Category, CategoryTree

            __all__ = ["Category", "CategoryTree"]
        '''))
        self.writer.write(f"{base}/entities.py", self._category_entities())

        app_base = f"{self.mod_root}/application"
        self.writer.write(f"{app_base}/category_use_case.py", self._category_use_case())

        infra_base = f"{self.mod_root}/infrastructure"
        self.writer.write(f"{infra_base}/models_category.py", self._category_model())
        self.writer.write(f"{infra_base}/category_repository.py", self._category_repo())

        pres_base = f"{self.mod_root}/presentation"
        self.writer.write(f"{pres_base}/router_category.py", self._category_router())
        self.writer.write(f"{pres_base}/schemas_category.py", self._category_schemas())

    def _category_entities(self) -> str:
        return dedent('''\
            """Category entities"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import UTC, datetime
            from typing import Any


            @dataclass(slots=True)
            class Category:
                id: uuid.UUID
                tenant_id: uuid.UUID
                parent_id: uuid.UUID | None
                slug: str
                name_th: str
                name_en: str
                description: str = ""
                icon: str | None = None
                color: str = "#3B82F6"
                sort_order: int = 0
                is_active: bool = True
                class_count: int = 0
                extra_json: dict[str, Any] = field(default_factory=dict)
                created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
                updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

                def to_dict(self) -> dict[str, Any]:
                    return {
                        "id": str(self.id),
                        "parent_id": str(self.parent_id) if self.parent_id else None,
                        "slug": self.slug,
                        "name_th": self.name_th,
                        "name_en": self.name_en,
                        "description": self.description,
                        "icon": self.icon,
                        "color": self.color,
                        "sort_order": self.sort_order,
                        "is_active": self.is_active,
                        "class_count": self.class_count,
                    }


            class CategoryTree:
                """TH: ต้นไม้หมวดหมู่ | EN: category tree"""

                def __init__(self, categories: list[Any]) -> None:
                    self._by_parent: dict[uuid.UUID | None, list[Any]] = {}
                    self._by_id: dict[uuid.UUID, Any] = {}
                    for c in categories:
                        self._by_parent.setdefault(c.parent_id, []).append(c)
                        self._by_id[c.id] = c

                def children(self, parent_id: uuid.UUID | None) -> list[Any]:
                    items = list(self._by_parent.get(parent_id, []))
                    items.sort(key=lambda c: (c.sort_order, c.name_th))
                    return items

                def ancestors(self, category_id: uuid.UUID) -> list[Any]:
                    result: list[Any] = []
                    current = self._by_id.get(category_id)
                    while current and current.parent_id:
                        parent = self._by_id.get(current.parent_id)
                        if parent is None:
                            break
                        result.append(parent)
                        current = parent
                    return list(reversed(result))

                def descendants(self, category_id: uuid.UUID) -> list[Any]:
                    result: list[Any] = []
                    stack = [category_id]
                    while stack:
                        cid = stack.pop()
                        for child in self._by_parent.get(cid, []):
                            result.append(child)
                            stack.append(child.id)
                    return result

                def depth(self, category_id: uuid.UUID) -> int:
                    return len(self.ancestors(category_id))

                def to_nested(self, parent_id: uuid.UUID | None = None) -> list[dict]:
                    result: list[dict] = []
                    for c in self.children(parent_id):
                        node = c.to_dict() if hasattr(c, "to_dict") else dict(c)
                        node["children"] = self.to_nested(c.id)
                        result.append(node)
                    return result

                def has_cycle(self) -> bool:
                    for c in self._by_id.values():
                        seen: set[uuid.UUID] = set()
                        current = c
                        while current and current.parent_id:
                            if current.id in seen:
                                return True
                            seen.add(current.id)
                            current = self._by_id.get(current.parent_id)
                    return False
        ''')

    def _category_use_case(self) -> str:
        return dedent('''\
            """Category use case"""
            from __future__ import annotations
            import uuid
            from typing import Any

            import structlog

            from app.modules.yolo.domain.category import CategoryTree

            log = structlog.get_logger()


            class CategoryUseCase:
                def __init__(self, repo: Any) -> None:
                    self._repo = repo

                async def create_category(self, ctx: Any, payload: dict[str, Any]) -> dict:
                    row = await self._repo.create(ctx, payload)
                    log.info("yolo.category.created", slug=payload.get("slug"))
                    return self._to_dict(row)

                async def get_category(self, ctx: Any, category_id: uuid.UUID) -> dict:
                    row = await self._repo.find_by_id(ctx, category_id)
                    if row is None:
                        raise ValueError(f"category {category_id} not found")
                    return self._to_dict(row)

                async def list_categories(self, ctx: Any,
                                            parent_id: uuid.UUID | None = None) -> list[dict]:
                    rows = await self._repo.find_children(ctx, parent_id)
                    return [self._to_dict(r) for r in rows]

                async def get_tree(self, ctx: Any,
                                    root_id: uuid.UUID | None = None) -> dict:
                    all_rows = await self._repo.find_all(ctx)
                    tree = CategoryTree(all_rows)
                    if tree.has_cycle():
                        raise ValueError("category tree contains cycle")
                    return {
                        "root_id": str(root_id) if root_id else None,
                        "items": tree.to_nested(root_id),
                    }

                async def update_category(self, ctx: Any, category_id: uuid.UUID,
                                            payload: dict[str, Any]) -> dict:
                    row = await self._repo.update(ctx, category_id, payload)
                    if row is None:
                        raise ValueError(f"category {category_id} not found")
                    return self._to_dict(row)

                async def move_category(self, ctx: Any, category_id: uuid.UUID,
                                          new_parent_id: uuid.UUID | None) -> dict:
                    # ตรวจ cycle
                    all_rows = await self._repo.find_all(ctx)
                    tree = CategoryTree(all_rows)
                    if new_parent_id:
                        descendants = {d.id for d in tree.descendants(category_id)}
                        if new_parent_id in descendants or new_parent_id == category_id:
                            raise ValueError("cannot move category under its own descendant")
                    row = await self._repo.update(ctx, category_id,
                                                    {"parent_id": new_parent_id})
                    return self._to_dict(row)

                async def delete_category(self, ctx: Any, category_id: uuid.UUID,
                                            cascade: bool = False) -> dict:
                    if not cascade:
                        children = await self._repo.find_children(ctx, category_id)
                        if children:
                            raise ValueError("category has children; use cascade=true")
                    await self._repo.delete(ctx, category_id, cascade=cascade)
                    return {"deleted": str(category_id), "cascade": cascade}

                @staticmethod
                def _to_dict(row: Any) -> dict[str, Any]:
                    if hasattr(row, "to_dict"):
                        return row.to_dict()
                    return {
                        "id": str(row.id),
                        "parent_id": str(row.parent_id) if row.parent_id else None,
                        "slug": row.slug,
                        "name_th": row.name_th,
                        "name_en": row.name_en,
                        "description": row.description,
                        "color": row.color,
                        "sort_order": row.sort_order,
                        "is_active": row.is_active,
                    }
        ''')

    def _category_model(self) -> str:
        return dedent('''\
            """Category SQLAlchemy model"""
            from __future__ import annotations
            import uuid
            from datetime import datetime

            from sqlalchemy import (
                Boolean, CheckConstraint, DateTime, ForeignKey, Index,
                Integer, String, Text, UniqueConstraint, func, text,
            )
            from sqlalchemy.dialects.postgresql import JSONB, UUID
            from sqlalchemy.orm import Mapped, mapped_column

            from app.modules.yolo.infrastructure.models import Base

            SCHEMA = "public"


            class CategoryModel(Base):
                __tablename__ = "yolo_categories"
                __table_args__ = (
                    UniqueConstraint("tenant_id", "slug", name="uq_yolo_cat_slug"),
                    CheckConstraint("parent_id IS NULL OR parent_id != id",
                                     name="ck_yolo_cat_no_self_parent"),
                    Index("ix_yolo_cat_tenant", "tenant_id"),
                    Index("ix_yolo_cat_parent", "parent_id"),
                    {"schema": SCHEMA},
                )

                id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), primary_key=True,
                    server_default=text("gen_random_uuid()"))
                tenant_id: Mapped[uuid.UUID] = mapped_column(
                    UUID(as_uuid=True), nullable=False)
                parent_id: Mapped[uuid.UUID | None] = mapped_column(
                    UUID(as_uuid=True),
                    ForeignKey(f"{SCHEMA}.yolo_categories.id", ondelete="RESTRICT"),
                    nullable=True)
                slug: Mapped[str] = mapped_column(String(100), nullable=False)
                name_th: Mapped[str] = mapped_column(String(200), nullable=False)
                name_en: Mapped[str] = mapped_column(String(200), nullable=False)
                description: Mapped[str] = mapped_column(Text, nullable=False,
                    server_default="")
                icon: Mapped[str | None] = mapped_column(String(20), nullable=True)
                color: Mapped[str] = mapped_column(String(7), nullable=False,
                    server_default="#3B82F6")
                sort_order: Mapped[int] = mapped_column(Integer, nullable=False,
                    server_default="0")
                is_active: Mapped[bool] = mapped_column(Boolean, nullable=False,
                    server_default=text("true"))
                extra_json: Mapped[dict] = mapped_column(JSONB, nullable=False,
                    server_default=text("'{}'::jsonb"))
                created_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now())
                updated_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False, server_default=func.now(),
                    onupdate=func.now())
        ''')

    def _category_repo(self) -> str:
        return dedent('''\
            """Category repository"""
            from __future__ import annotations
            import uuid
            from typing import Any

            from loguru import logger
            from sqlalchemy import delete, select, update
            from sqlalchemy.exc import SQLAlchemyError
            from sqlalchemy.ext.asyncio import AsyncSession

            from app.modules.yolo.application.exceptions import ApplicationError
            from app.modules.yolo.infrastructure.models_category import CategoryModel


            class CategoryRepository:
                def __init__(self, session: AsyncSession) -> None:
                    self._session = session

                async def find_by_id(self, ctx: Any, id: uuid.UUID) -> CategoryModel | None:
                    try:
                        result = await self._session.execute(
                            select(CategoryModel).where(CategoryModel.id == id))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"category.find_by_id: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_by_slug(self, ctx: Any, slug: str) -> CategoryModel | None:
                    try:
                        result = await self._session.execute(
                            select(CategoryModel).where(CategoryModel.slug == slug))
                        return result.scalar_one_or_none()
                    except SQLAlchemyError as exc:
                        logger.error(f"category.find_by_slug: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_all(self, ctx: Any) -> list[CategoryModel]:
                    try:
                        result = await self._session.execute(
                            select(CategoryModel).where(CategoryModel.is_active.is_(True))
                            .order_by(CategoryModel.sort_order, CategoryModel.name_th))
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"category.find_all: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def find_children(self, ctx: Any,
                                         parent_id: uuid.UUID | None) -> list[CategoryModel]:
                    try:
                        stmt = select(CategoryModel)
                        if parent_id is None:
                            stmt = stmt.where(CategoryModel.parent_id.is_(None))
                        else:
                            stmt = stmt.where(CategoryModel.parent_id == parent_id)
                        stmt = stmt.order_by(CategoryModel.sort_order, CategoryModel.name_th)
                        result = await self._session.execute(stmt)
                        return list(result.scalars().all())
                    except SQLAlchemyError as exc:
                        logger.error(f"category.find_children: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def create(self, ctx: Any, payload: dict[str, Any]) -> CategoryModel:
                    try:
                        row = CategoryModel(**payload)
                        self._session.add(row)
                        await self._session.flush()
                        return row
                    except SQLAlchemyError as exc:
                        logger.error(f"category.create: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def update(self, ctx: Any, id: uuid.UUID,
                                  payload: dict[str, Any]) -> CategoryModel | None:
                    try:
                        await self._session.execute(
                            update(CategoryModel).where(CategoryModel.id == id).values(**payload))
                        await self._session.flush()
                        return await self.find_by_id(ctx, id)
                    except SQLAlchemyError as exc:
                        logger.error(f"category.update: {exc}")
                        raise ApplicationError(str(exc)) from exc

                async def delete(self, ctx: Any, id: uuid.UUID,
                                  cascade: bool = False) -> bool:
                    try:
                        if cascade:
                            # recursive delete (ต้องมี ON DELETE CASCADE หรือ recursive CTE)
                            pass
                        await self._session.execute(
                            delete(CategoryModel).where(CategoryModel.id == id))
                        await self._session.flush()
                        return True
                    except SQLAlchemyError as exc:
                        logger.error(f"category.delete: {exc}")
                        raise ApplicationError(str(exc)) from exc
        ''')

    def _category_schemas(self) -> str:
        return dedent('''\
            """Category schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class CategoryCreateRequest(BaseModel):
                slug: str = Field(..., min_length=1, max_length=100,
                                    pattern=r"^[a-z0-9-]+$")
                name_th: str = Field(..., min_length=1, max_length=200)
                name_en: str = Field(..., min_length=1, max_length=200)
                parent_id: str | None = None
                description: str = ""
                icon: str | None = None
                color: str = "#3B82F6"
                sort_order: int = 0
                extra_json: dict[str, Any] = Field(default_factory=dict)
                model_config = ConfigDict(extra="forbid")


            class CategoryUpdateRequest(BaseModel):
                name_th: str | None = None
                name_en: str | None = None
                description: str | None = None
                icon: str | None = None
                color: str | None = None
                sort_order: int | None = None
                is_active: bool | None = None
                extra_json: dict[str, Any] | None = None
                model_config = ConfigDict(extra="forbid")


            class CategoryResponse(BaseModel):
                id: str
                parent_id: str | None = None
                slug: str
                name_th: str
                name_en: str
                description: str = ""
                icon: str | None = None
                color: str
                sort_order: int = 0
                is_active: bool = True
                class_count: int = 0
                model_config = ConfigDict(extra="forbid")


            class CategoryTreeNode(CategoryResponse):
                children: list["CategoryTreeNode"] = Field(default_factory=list)


            class CategoryTreeResponse(BaseModel):
                root_id: str | None = None
                items: list[CategoryTreeNode]
                model_config = ConfigDict(extra="forbid")


            class CategoryMoveRequest(BaseModel):
                new_parent_id: str | None = None
                model_config = ConfigDict(extra="forbid")
        ''')

    def _category_router(self) -> str:
        return dedent('''\
            """Category router"""
            from __future__ import annotations
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, HTTPException, status

            from app.modules.yolo.application.category_use_case import CategoryUseCase
            from app.modules.yolo.presentation.dependencies import get_ctx
            from app.modules.yolo.presentation.schemas_category import (
                CategoryCreateRequest, CategoryMoveRequest, CategoryResponse,
                CategoryTreeResponse, CategoryUpdateRequest,
            )

            router = APIRouter(prefix="/yolo/categories", tags=["yolo"])


            async def _get_uc() -> CategoryUseCase:  # type: ignore
                raise HTTPException(500, "CategoryUseCase not wired")


            @router.post("", response_model=CategoryResponse,
                          status_code=status.HTTP_201_CREATED,
                          summary="Create category",
                          operation_id="yolo_create_category")
            async def create_category(
                payload: CategoryCreateRequest,
                uc: Annotated[CategoryUseCase, Depends(_get_uc)],
            ) -> CategoryResponse:
                ctx = await get_ctx()
                data = payload.model_dump()
                if data.get("parent_id"):
                    data["parent_id"] = uuid.UUID(data["parent_id"])
                return CategoryResponse(**await uc.create_category(ctx, data))


            @router.get("", response_model=list[CategoryResponse],
                         summary="List categories (flat)",
                         operation_id="yolo_list_categories")
            async def list_categories(
                uc: Annotated[CategoryUseCase, Depends(_get_uc)],
                parent_id: uuid.UUID | None = None,
            ) -> list[CategoryResponse]:
                ctx = await get_ctx()
                return [CategoryResponse(**c)
                        for c in await uc.list_categories(ctx, parent_id)]


            @router.get("/tree", response_model=CategoryTreeResponse,
                         summary="Get category tree",
                         operation_id="yolo_category_tree")
            async def get_tree(
                uc: Annotated[CategoryUseCase, Depends(_get_uc)],
                root_id: uuid.UUID | None = None,
            ) -> CategoryTreeResponse:
                ctx = await get_ctx()
                return CategoryTreeResponse(**await uc.get_tree(ctx, root_id))


            @router.get("/{category_id}", response_model=CategoryResponse,
                         summary="Get category", operation_id="yolo_get_category")
            async def get_category(
                category_id: uuid.UUID,
                uc: Annotated[CategoryUseCase, Depends(_get_uc)],
            ) -> CategoryResponse:
                ctx = await get_ctx()
                try:
                    return CategoryResponse(**await uc.get_category(ctx, category_id))
                except ValueError as e:
                    raise HTTPException(404, detail=str(e)) from e


            @router.patch("/{category_id}", response_model=CategoryResponse,
                           summary="Update category",
                           operation_id="yolo_update_category")
            async def update_category(
                category_id: uuid.UUID, payload: CategoryUpdateRequest,
                uc: Annotated[CategoryUseCase, Depends(_get_uc)],
            ) -> CategoryResponse:
                ctx = await get_ctx()
                data = {k: v for k, v in payload.model_dump().items() if v is not None}
                return CategoryResponse(**await uc.update_category(ctx, category_id, data))


            @router.post("/{category_id}/move", response_model=CategoryResponse,
                          summary="Move category",
                          operation_id="yolo_move_category")
            async def move_category(
                category_id: uuid.UUID, payload: CategoryMoveRequest,
                uc: Annotated[CategoryUseCase, Depends(_get_uc)],
            ) -> CategoryResponse:
                ctx = await get_ctx()
                new_parent = (uuid.UUID(payload.new_parent_id)
                              if payload.new_parent_id else None)
                try:
                    return CategoryResponse(**await uc.move_category(
                        ctx, category_id, new_parent))
                except ValueError as e:
                    raise HTTPException(422, detail=str(e)) from e


            @router.delete("/{category_id}", summary="Delete category",
                            operation_id="yolo_delete_category")
            async def delete_category(
                category_id: uuid.UUID,
                uc: Annotated[CategoryUseCase, Depends(_get_uc)],
                cascade: bool = False,
            ) -> dict:
                ctx = await get_ctx()
                try:
                    return await uc.delete_category(ctx, category_id, cascade)
                except ValueError as e:
                    raise HTTPException(422, detail=str(e)) from e
        ''')

    # ═══════════════════════════════════════════════════════════
    #  4. DEPLOYMENT
    # ═══════════════════════════════════════════════════════════
    def create_deployment(self) -> None:
        info(f"[DEPLOYMENT] {self.module}/deployment")
        base = f"{self.mod_root}/presentation"
        self.writer.write(f"{base}/router_deployment.py", self._deployment_router())

    def _deployment_router(self) -> str:
        return dedent('''\
            """Deployment router — health, metrics, registry"""
            from __future__ import annotations
            from typing import Annotated, Any

            from fastapi import APIRouter, Depends, HTTPException

            router = APIRouter(prefix="/yolo/deployment", tags=["yolo"])


            def _get_registry() -> Any:
                from app.modules.yolo.presentation.dependencies import _get_registry as g
                return g()


            @router.get("/health", summary="Health check",
                         operation_id="yolo_health")
            async def health() -> dict:
                import os
                import torch
                gpu_ok = False
                gpu_name = None
                try:
                    gpu_ok = bool(torch.cuda.is_available())
                    if gpu_ok:
                        gpu_name = torch.cuda.get_device_name(0)
                except Exception:
                    pass
                return {
                    "status": "ok",
                    "gpu_available": gpu_ok,
                    "gpu_name": gpu_name,
                    "device": os.getenv("YOLO_DEVICE", "auto"),
                    "default_model": os.getenv("YOLO_DEFAULT_MODEL", "yolov8n.pt"),
                }


            @router.get("/readyz", summary="Readiness",
                         operation_id="yolo_readyz")
            async def readyz(registry: Annotated[Any, Depends(_get_registry)]) -> dict:
                return {"ready": True}


            @router.get("/livez", summary="Liveness",
                         operation_id="yolo_livez")
            async def livez() -> dict:
                return {"alive": True}


            @router.get("/registry", summary="List loaded models",
                         operation_id="yolo_registry_list")
            async def registry_list(registry: Annotated[Any, Depends(_get_registry)]) -> dict:
                return {"loaded": len(getattr(registry, "_models", {}))}


            @router.post("/registry/load", summary="Pre-load model",
                          operation_id="yolo_registry_load")
            async def registry_load(payload: dict) -> dict:
                return {"loaded": payload.get("model_id"), "status": "queued"}


            @router.post("/registry/unload", summary="Unload model",
                          operation_id="yolo_registry_unload")
            async def registry_unload(payload: dict) -> dict:
                return {"unloaded": payload.get("model_id")}


            @router.get("/metrics", summary="Prometheus metrics",
                         operation_id="yolo_metrics")
            async def metrics() -> dict:
                return {"inferences_total": 0, "trainings_total": 0}
        ''')

    # ═══════════════════════════════════════════════════════════
    #  5. COUNTING
    # ═══════════════════════════════════════════════════════════
    def create_counting(self) -> None:
        info(f"[COUNTING] {self.module}/counting")
        base = f"{self.mod_root}/domain/applications"
        self.writer.write(f"{base}/__init__.py", dedent('''\
            """YOLO applications (domain-level)"""
        '''))
        self.writer.write(f"{base}/counting.py", self._counting_domain())

        app_base = f"{self.mod_root}/application"
        self.writer.write(f"{app_base}/counting_use_case.py", self._counting_use_case())

        pres_base = f"{self.mod_root}/presentation"
        self.writer.write(f"{pres_base}/router_counting.py", self._counting_router())
        self.writer.write(f"{pres_base}/schemas_counting.py", self._counting_schemas())

    def _counting_domain(self) -> str:
        return dedent('''\
            """Product counting domain"""
            from __future__ import annotations
            from dataclasses import dataclass, field
            from typing import Any

            from app.modules.yolo.domain.value_objects import Detection


            @dataclass(frozen=True, slots=True)
            class CountingConfig:
                mode: str = "shelf"                 # shelf | conveyor | checkout | warehouse
                line_position: float = 0.5          # conveyor
                line_orientation: str = "vertical"  # conveyor
                class_filter: tuple[int, ...] = ()
                min_confidence: float = 0.5
                merge_distance: float = 0.05
                track_persistence: int = 5
                deduplication: bool = True

                def __post_init__(self) -> None:
                    if self.mode not in ("shelf", "conveyor", "checkout", "warehouse"):
                        raise ValueError(f"invalid mode: {self.mode}")
                    if not 0.0 <= self.line_position <= 1.0:
                        raise ValueError("line_position must be in [0,1]")
                    if not 0.0 <= self.min_confidence <= 1.0:
                        raise ValueError("min_confidence must be in [0,1]")


            @dataclass(frozen=True, slots=True)
            class CountingResult:
                total_count: int
                per_class_count: tuple[tuple[str, int], ...] = ()
                regions: tuple[dict[str, Any], ...] = ()
                confidence_avg: float = 0.0
                processing_ms: int = 0
                warnings: tuple[str, ...] = ()

                def to_dict(self) -> dict[str, Any]:
                    return {
                        "total_count": self.total_count,
                        "per_class_count": [
                            {"class_name": n, "count": c}
                            for n, c in self.per_class_count
                        ],
                        "regions": list(self.regions),
                        "confidence_avg": self.confidence_avg,
                        "processing_ms": self.processing_ms,
                        "warnings": list(self.warnings),
                    }


            class ProductCounter:
                """TH: ตัวนับสินค้า | EN: product counter"""

                def __init__(self, config: CountingConfig) -> None:
                    self._config = config

                def count(self, detections: list[Detection],
                           img_size: tuple[int, int]) -> CountingResult:
                    import time
                    t0 = time.monotonic()
                    filtered = self._filter(detections)
                    if self._config.mode == "shelf":
                        result = self._count_shelf(filtered)
                    elif self._config.mode == "conveyor":
                        result = self._count_conveyor(filtered)
                    elif self._config.mode == "checkout":
                        result = self._count_checkout(filtered)
                    else:  # warehouse
                        result = self._count_warehouse(filtered)
                    ms = int((time.monotonic() - t0) * 1000)
                    return CountingResult(
                        total_count=result["total"],
                        per_class_count=tuple(result["per_class"].items()),
                        regions=tuple(result["regions"]),
                        confidence_avg=result["conf_avg"],
                        processing_ms=ms,
                    )

                def _filter(self, detections: list[Detection]) -> list[Detection]:
                    out: list[Detection] = []
                    for d in detections:
                        if d.confidence < self._config.min_confidence:
                            continue
                        if (self._config.class_filter
                                and d.class_id not in self._config.class_filter):
                            continue
                        out.append(d)
                    return out

                def _count_shelf(self, detections: list[Detection]) -> dict[str, Any]:
                    """นับบนชั้นวาง — แยกตาม row (y-cluster)"""
                    if not detections:
                        return {"total": 0, "per_class": {}, "regions": [], "conf_avg": 0.0}
                    sorted_d = sorted(detections, key=lambda d: d.bbox.y_center)
                    rows: list[list[Detection]] = [[]]
                    prev_y = sorted_d[0].bbox.y_center
                    gap = 0.1  # 10% ของภาพ
                    for d in sorted_d:
                        if d.bbox.y_center - prev_y > gap:
                            rows.append([])
                        rows[-1].append(d)
                        prev_y = d.bbox.y_center

                    per_class: dict[str, int] = {}
                    regions: list[dict[str, Any]] = []
                    for i, row in enumerate(rows):
                        ys = [d.bbox.y_center for d in row]
                        y_min, y_max = min(ys), max(ys)
                        regions.append({
                            "row": i + 1, "count": len(row),
                            "y_range": [y_min, y_max],
                        })
                        for d in row:
                            per_class[d.class_name] = per_class.get(d.class_name, 0) + 1
                    conf_avg = sum(d.confidence for d in detections) / len(detections)
                    return {
                        "total": len(detections),
                        "per_class": per_class,
                        "regions": regions,
                        "conf_avg": conf_avg,
                    }

                def _count_conveyor(self, detections: list[Detection]) -> dict[str, Any]:
                    """นับบนสายพาน — ตรวจจับวัตถุที่ cross virtual line"""
                    line = self._config.line_position
                    crossed = []
                    for d in detections:
                        if self._config.line_orientation == "vertical":
                            crossed.append(d) if d.bbox.x_center > line else None
                        else:
                            crossed.append(d) if d.bbox.y_center > line else None
                    per_class: dict[str, int] = {}
                    for d in crossed:
                        per_class[d.class_name] = per_class.get(d.class_name, 0) + 1
                    conf_avg = (sum(d.confidence for d in crossed) / len(crossed)
                                 if crossed else 0.0)
                    return {
                        "total": len(crossed),
                        "per_class": per_class,
                        "regions": [{"line": line, "orientation": self._config.line_orientation}],
                        "conf_avg": conf_avg,
                    }

                def _count_checkout(self, detections: list[Detection]) -> dict[str, Any]:
                    """นับที่จุดชำระเงิน — merge overlapping"""
                    merged = self._merge_overlapping(detections)
                    per_class: dict[str, int] = {}
                    for d in merged:
                        per_class[d.class_name] = per_class.get(d.class_name, 0) + 1
                    conf_avg = (sum(d.confidence for d in merged) / len(merged)
                                 if merged else 0.0)
                    return {
                        "total": len(merged),
                        "per_class": per_class,
                        "regions": [],
                        "conf_avg": conf_avg,
                    }

                def _count_warehouse(self, detections: list[Detection]) -> dict[str, Any]:
                    return self._count_checkout(detections)

                def _merge_overlapping(self, detections: list[Detection]) -> list[Detection]:
                    if not self._config.deduplication:
                        return detections
                    result: list[Detection] = []
                    used = [False] * len(detections)
                    for i, d1 in enumerate(detections):
                        if used[i]:
                            continue
                        for j in range(i + 1, len(detections)):
                            if used[j]:
                                continue
                            d2 = detections[j]
                            dist = ((d1.bbox.x_center - d2.bbox.x_center) ** 2
                                     + (d1.bbox.y_center - d2.bbox.y_center) ** 2) ** 0.5
                            if dist < self._config.merge_distance:
                                used[j] = True
                        result.append(d1)
                    return result
        ''')

    def _counting_use_case(self) -> str:
        return dedent('''\
            """Counting use case"""
            from __future__ import annotations
            import time
            import uuid
            from typing import Any

            import structlog

            from app.modules.yolo.domain.applications.counting import (
                CountingConfig, ProductCounter,
            )

            log = structlog.get_logger()


            class CountingUseCase:
                def __init__(self, detector: Any, registry: Any,
                              settings_repo: Any, model_repo: Any) -> None:
                    self._detector = detector
                    self._registry = registry
                    self._settings = settings_repo
                    self._models = model_repo

                async def count_image(self, ctx: Any, model_id: uuid.UUID,
                                       image_bytes: bytes,
                                       config: CountingConfig) -> dict[str, Any]:
                    settings = await self._settings.find_by_tenant(ctx, ctx.tenant_id)
                    conf = (float(settings.conf_threshold) if settings else 0.25)
                    iou = (float(settings.iou_threshold) if settings else 0.45)

                    await self._registry.load(model_id, str(model_id), "pt")
                    detections = await self._detector.detect(
                        model_id, image_bytes, conf, iou)

                    counter = ProductCounter(config)
                    img_size = self._get_size(image_bytes)
                    result = counter.count(detections, img_size)
                    return {
                        "model_id": str(model_id),
                        "mode": config.mode,
                        **result.to_dict(),
                    }

                async def count_batch(self, ctx: Any, model_id: uuid.UUID,
                                        images: list[bytes],
                                        config: CountingConfig) -> dict[str, Any]:
                    results = []
                    total = 0
                    for img in images:
                        r = await self.count_image(ctx, model_id, img, config)
                        results.append(r)
                        total += r["total_count"]
                    return {"model_id": str(model_id), "total": total,
                            "results": results}

                @staticmethod
                def _get_size(image_bytes: bytes) -> tuple[int, int]:
                    try:
                        from PIL import Image
                        import io
                        img = Image.open(io.BytesIO(image_bytes))
                        return img.size
                    except Exception:
                        return (640, 640)
        ''')

    def _counting_schemas(self) -> str:
        return dedent('''\
            """Counting schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class CountingConfigRequest(BaseModel):
                mode: str = Field(default="shelf",
                                    pattern=r"^(shelf|conveyor|checkout|warehouse)$")
                line_position: float = Field(default=0.5, ge=0.0, le=1.0)
                line_orientation: str = Field(default="vertical",
                                                pattern=r"^(vertical|horizontal)$")
                class_filter: list[int] = Field(default_factory=list)
                min_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
                merge_distance: float = Field(default=0.05, ge=0.0, le=1.0)
                track_persistence: int = Field(default=5, ge=1, le=100)
                deduplication: bool = True
                model_config = ConfigDict(extra="forbid")


            class ClassCount(BaseModel):
                class_name: str
                count: int
                model_config = ConfigDict(extra="forbid")


            class CountingResultResponse(BaseModel):
                model_id: str
                mode: str
                total_count: int
                per_class_count: list[ClassCount]
                regions: list[dict[str, Any]] = Field(default_factory=list)
                confidence_avg: float = 0.0
                processing_ms: int = 0
                warnings: list[str] = Field(default_factory=list)
                model_config = ConfigDict(extra="forbid")


            class BatchCountingResponse(BaseModel):
                model_id: str
                total: int
                results: list[dict[str, Any]]
                model_config = ConfigDict(extra="forbid")
        ''')

    def _counting_router(self) -> str:
        return dedent('''\
            """Counting router"""
            from __future__ import annotations
            import base64
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

            from app.modules.yolo.application.counting_use_case import CountingUseCase
            from app.modules.yolo.domain.applications.counting import CountingConfig
            from app.modules.yolo.presentation.dependencies import get_ctx
            from app.modules.yolo.presentation.schemas_counting import (
                BatchCountingResponse, CountingConfigRequest, CountingResultResponse,
            )

            router = APIRouter(prefix="/yolo/counting", tags=["yolo"])


            async def _get_uc() -> CountingUseCase:  # type: ignore
                raise HTTPException(500, "CountingUseCase not wired")


            @router.post("/image", response_model=CountingResultResponse,
                          summary="Count products (single image)",
                          operation_id="yolo_count_image")
            async def count_image(
                model_id: str = Form(...),
                mode: str = Form("shelf"),
                min_confidence: float = Form(0.5),
                image: UploadFile = File(...),
                uc: Annotated[CountingUseCase, Depends(_get_uc)] = None,  # type: ignore
            ) -> CountingResultResponse:
                ctx = await get_ctx()
                try:
                    config = CountingConfig(mode=mode, min_confidence=min_confidence)
                    raw = await image.read()
                    result = await uc.count_image(ctx, uuid.UUID(model_id), raw, config)
                    return CountingResultResponse(**result)
                except ValueError as e:
                    raise HTTPException(422, detail=str(e)) from e


            @router.post("/batch", response_model=BatchCountingResponse,
                          summary="Count products (batch)",
                          operation_id="yolo_count_batch")
            async def count_batch(
                payload: dict,
                uc: Annotated[CountingUseCase, Depends(_get_uc)],
            ) -> BatchCountingResponse:
                ctx = await get_ctx()
                config = CountingConfig(**payload.get("config", {}))
                images = [base64.b64decode(b) for b in payload.get("images_base64", [])]
                result = await uc.count_batch(
                    ctx, uuid.UUID(payload["model_id"]), images, config)
                return BatchCountingResponse(**result)
        ''')

    # ═══════════════════════════════════════════════════════════
    #  6. PLANT DISEASE
    # ═══════════════════════════════════════════════════════════
    def create_plant_disease(self) -> None:
        info(f"[PLANT-DISEASE] {self.module}/plant-disease")
        base = f"{self.mod_root}/domain/applications"
        self.writer.write(f"{base}/plant_disease.py", self._plant_disease_domain())

        app_base = f"{self.mod_root}/application"
        self.writer.write(f"{app_base}/plant_disease_use_case.py",
                           self._plant_disease_use_case())

        pres_base = f"{self.mod_root}/presentation"
        self.writer.write(f"{pres_base}/router_plant_disease.py",
                           self._plant_disease_router())
        self.writer.write(f"{pres_base}/schemas_plant_disease.py",
                           self._plant_disease_schemas())

    def _plant_disease_domain(self) -> str:
        return dedent('''\
            """Plant disease diagnosis domain"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import UTC, datetime
            from typing import Any

            from app.modules.yolo.domain.value_objects import BBox, Detection


            @dataclass(frozen=True, slots=True)
            class DiseaseSeverity:
                level: str          # healthy | mild | moderate | severe | critical
                percentage: float   # 0.0 - 1.0
                score: float        # 0.0 - 1.0


            @dataclass(frozen=True, slots=True)
            class DiseaseInfo:
                code: str
                name_th: str
                name_en: str
                pathogen_type: str          # fungal | bacterial | viral | pest
                treatment: tuple[str, ...] = ()
                prevention: tuple[str, ...] = ()


            @dataclass(frozen=True, slots=True)
            class DiseaseDetection:
                bbox: BBox
                disease_code: str
                disease_name_th: str
                disease_name_en: str
                pathogen_type: str
                confidence: float
                severity: DiseaseSeverity
                affected_area_pct: float

                def to_dict(self) -> dict[str, Any]:
                    return {
                        "bbox": {
                            "x_center": self.bbox.x_center,
                            "y_center": self.bbox.y_center,
                            "width": self.bbox.width,
                            "height": self.bbox.height,
                        },
                        "disease_code": self.disease_code,
                        "disease_name_th": self.disease_name_th,
                        "disease_name_en": self.disease_name_en,
                        "pathogen_type": self.pathogen_type,
                        "confidence": self.confidence,
                        "severity": {
                            "level": self.severity.level,
                            "percentage": self.severity.percentage,
                            "score": self.severity.score,
                        },
                        "affected_area_pct": self.affected_area_pct,
                    }


            @dataclass(frozen=True, slots=True)
            class PlantDiagnosis:
                image_id: uuid.UUID
                plant_species: str | None
                detections: tuple[DiseaseDetection, ...]
                overall_severity: str
                overall_health_score: float
                recommendations: tuple[str, ...]
                treatment_plan: tuple[dict[str, Any], ...]
                follow_up_days: int
                confidence: float
                generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

                def to_dict(self) -> dict[str, Any]:
                    return {
                        "image_id": str(self.image_id),
                        "plant_species": self.plant_species,
                        "overall_severity": self.overall_severity,
                        "overall_health_score": self.overall_health_score,
                        "detections": [d.to_dict() for d in self.detections],
                        "recommendations": list(self.recommendations),
                        "treatment_plan": list(self.treatment_plan),
                        "follow_up_days": self.follow_up_days,
                        "confidence": self.confidence,
                        "generated_at": self.generated_at.isoformat(),
                    }


            DISEASE_CATALOG: dict[str, DiseaseInfo] = {
                "rice-blast": DiseaseInfo(
                    code="rice-blast",
                    name_th="โรคไหม้ข้าว",
                    name_en="Rice Blast",
                    pathogen_type="fungal",
                    treatment=("พ่น tricyclazole 20% WP", "ลดปุ๋ยไนโตรเจน"),
                    prevention=("ใช้พันธุ์ต้านทาน", "ไม่ปลูกหนาแน่น"),
                ),
                "tomato-late-blight": DiseaseInfo(
                    code="tomato-late-blight",
                    name_th="โรคใบไหม้มะเขือเทศ",
                    name_en="Tomato Late Blight",
                    pathogen_type="fungal",
                    treatment=("พ่น chlorothalonil", "ตัดใบที่เป็นโรค"),
                    prevention=("ระบายอากาศดี", "หลีกเลี่ยงรดน้ำใบ"),
                ),
                "bacterial-leaf-blight": DiseaseInfo(
                    code="bacterial-leaf-blight",
                    name_th="โรคใบข้าวแห้ง",
                    name_en="Bacterial Leaf Blight",
                    pathogen_type="bacterial",
                    treatment=("ใช้ copper hydroxide", "ระบายน้ำ"),
                    prevention=("ไม่ใส่ปุ๋ยไนโตรเจนเกิน", "ใช้พันธุ์ต้านทาน"),
                ),
            }


            class PlantDiseaseDiagnoser:
                """TH: ตัววินิจฉัยโรคพืช | EN: plant disease diagnoser"""

                def diagnose(self, detections: list[Detection],
                              class_id_to_code: dict[int, str],
                              plant_species: str | None = None) -> PlantDiagnosis:
                    disease_dets: list[DiseaseDetection] = []
                    for d in detections:
                        code = class_id_to_code.get(d.class_id)
                        if not code or code not in DISEASE_CATALOG:
                            continue
                        info = DISEASE_CATALOG[code]
                        sev = self.calc_severity(d.bbox)
                        disease_dets.append(DiseaseDetection(
                            bbox=d.bbox,
                            disease_code=code,
                            disease_name_th=info.name_th,
                            disease_name_en=info.name_en,
                            pathogen_type=info.pathogen_type,
                            confidence=d.confidence,
                            severity=sev,
                            affected_area_pct=d.bbox.width * d.bbox.height,
                        ))

                    severity_rank = {"healthy": 0, "mild": 1, "moderate": 2,
                                      "severe": 3, "critical": 4}
                    overall = "healthy"
                    for dd in disease_dets:
                        if severity_rank[dd.severity.level] > severity_rank[overall]:
                            overall = dd.severity.level

                    health_score = max(0.0, 100.0 - sum(
                        dd.severity.percentage * 100 for dd in disease_dets))

                    recommendations: list[str] = []
                    for dd in disease_dets:
                        info = DISEASE_CATALOG[dd.disease_code]
                        recommendations.extend(info.treatment[:1])

                    treatment_plan: list[dict[str, Any]] = []
                    if disease_dets:
                        info = DISEASE_CATALOG[disease_dets[0].disease_code]
                        treatment_plan.append({
                            "day": 0, "action": "spray",
                            "product": info.treatment[0] if info.treatment else "-",
                        })
                        treatment_plan.append({"day": 7, "action": "inspect"})
                        treatment_plan.append({
                            "day": 14, "action": "spray",
                            "product": info.treatment[0] if info.treatment else "-",
                        })

                    conf_avg = (sum(d.confidence for d in disease_dets)
                                 / len(disease_dets) if disease_dets else 1.0)

                    return PlantDiagnosis(
                        image_id=uuid.uuid4(),
                        plant_species=plant_species,
                        detections=tuple(disease_dets),
                        overall_severity=overall,
                        overall_health_score=round(health_score, 2),
                        recommendations=tuple(dict.fromkeys(recommendations)),
                        treatment_plan=tuple(treatment_plan),
                        follow_up_days=7,
                        confidence=conf_avg,
                    )

                @staticmethod
                def calc_severity(bbox: BBox) -> DiseaseSeverity:
                    pct = bbox.width * bbox.height
                    if pct < 0.05:
                        return DiseaseSeverity("mild", pct, pct / 0.05 * 0.25)
                    if pct < 0.20:
                        return DiseaseSeverity("moderate", pct,
                                                0.25 + (pct - 0.05) / 0.15 * 0.35)
                    if pct < 0.50:
                        return DiseaseSeverity("severe", pct,
                                                0.60 + (pct - 0.20) / 0.30 * 0.25)
                    return DiseaseSeverity("critical", pct, 0.85 + min(pct, 1.0) * 0.15)
        ''')

    def _plant_disease_use_case(self) -> str:
        return dedent('''\
            """Plant disease use case"""
            from __future__ import annotations
            import uuid
            from typing import Any

            import structlog

            from app.modules.yolo.domain.applications.plant_disease import (
                DISEASE_CATALOG, PlantDiseaseDiagnoser,
            )

            log = structlog.get_logger()


            class PlantDiseaseUseCase:
                def __init__(self, detector: Any, registry: Any,
                              class_repo: Any, settings_repo: Any) -> None:
                    self._detector = detector
                    self._registry = registry
                    self._classes = class_repo
                    self._settings = settings_repo

                async def diagnose_image(self, ctx: Any, model_id: uuid.UUID,
                                           image_bytes: bytes,
                                           dataset_id: uuid.UUID | None = None,
                                           plant_species: str | None = None) -> dict:
                    settings = await self._settings.find_by_tenant(ctx, ctx.tenant_id)
                    conf = (float(settings.conf_threshold) if settings else 0.25)
                    iou = (float(settings.iou_threshold) if settings else 0.45)

                    await self._registry.load(model_id, str(model_id), "pt")
                    detections = await self._detector.detect(
                        model_id, image_bytes, conf, iou)

                    # Map class_id → disease_code
                    class_map: dict[int, str] = {}
                    if dataset_id:
                        classes = await self._classes.find_by_dataset(ctx, dataset_id)
                        class_map = {c.class_index: c.name for c in classes}

                    diagnoser = PlantDiseaseDiagnoser()
                    diagnosis = diagnoser.diagnose(detections, class_map, plant_species)
                    result = diagnosis.to_dict()
                    result["model_id"] = str(model_id)
                    return result

                async def get_catalog(self, ctx: Any,
                                       pathogen_type: str | None = None) -> list[dict]:
                    items: list[dict] = []
                    for code, info in DISEASE_CATALOG.items():
                        if pathogen_type and info.pathogen_type != pathogen_type:
                            continue
                        items.append({
                            "code": info.code,
                            "name_th": info.name_th,
                            "name_en": info.name_en,
                            "pathogen_type": info.pathogen_type,
                            "treatment": list(info.treatment),
                            "prevention": list(info.prevention),
                        })
                    return items

                async def get_treatment_plan(self, ctx: Any,
                                               disease_code: str) -> dict:
                    info = DISEASE_CATALOG.get(disease_code)
                    if info is None:
                        raise ValueError(f"disease {disease_code} not found")
                    return {
                        "code": info.code,
                        "name_th": info.name_th,
                        "name_en": info.name_en,
                        "treatment": list(info.treatment),
                        "prevention": list(info.prevention),
                        "plan": [
                            {"day": 0, "action": "spray",
                             "product": info.treatment[0] if info.treatment else "-"},
                            {"day": 7, "action": "inspect"},
                            {"day": 14, "action": "spray",
                             "product": info.treatment[0] if info.treatment else "-"},
                        ],
                    }
        ''')

    def _plant_disease_schemas(self) -> str:
        return dedent('''\
            """Plant disease schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class DiagnosisResponse(BaseModel):
                image_id: str
                model_id: str | None = None
                plant_species: str | None = None
                overall_severity: str
                overall_health_score: float
                detections: list[dict[str, Any]] = Field(default_factory=list)
                recommendations: list[str] = Field(default_factory=list)
                treatment_plan: list[dict[str, Any]] = Field(default_factory=list)
                follow_up_days: int = 7
                confidence: float = 0.0
                generated_at: str = ""
                model_config = ConfigDict(extra="forbid")


            class DiseaseCatalogItem(BaseModel):
                code: str
                name_th: str
                name_en: str
                pathogen_type: str
                treatment: list[str] = Field(default_factory=list)
                prevention: list[str] = Field(default_factory=list)
                model_config = ConfigDict(extra="forbid")


            class TreatmentPlanResponse(BaseModel):
                code: str
                name_th: str
                name_en: str
                treatment: list[str]
                prevention: list[str]
                plan: list[dict[str, Any]]
                model_config = ConfigDict(extra="forbid")
        ''')

    def _plant_disease_router(self) -> str:
        return dedent('''\
            """Plant disease router"""
            from __future__ import annotations
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

            from app.modules.yolo.application.plant_disease_use_case import (
                PlantDiseaseUseCase,
            )
            from app.modules.yolo.presentation.dependencies import get_ctx
            from app.modules.yolo.presentation.schemas_plant_disease import (
                DiagnosisResponse, DiseaseCatalogItem, TreatmentPlanResponse,
            )

            router = APIRouter(prefix="/yolo/plant-disease", tags=["yolo"])


            async def _get_uc() -> PlantDiseaseUseCase:  # type: ignore
                raise HTTPException(500, "PlantDiseaseUseCase not wired")


            @router.post("/diagnose", response_model=DiagnosisResponse,
                          summary="Diagnose plant disease",
                          operation_id="yolo_diagnose")
            async def diagnose(
                model_id: str = Form(...),
                dataset_id: str = Form(""),
                plant_species: str = Form(""),
                image: UploadFile = File(...),
                uc: Annotated[PlantDiseaseUseCase, Depends(_get_uc)] = None,  # type: ignore
            ) -> DiagnosisResponse:
                ctx = await get_ctx()
                raw = await image.read()
                ds_id = uuid.UUID(dataset_id) if dataset_id else None
                try:
                    result = await uc.diagnose_image(
                        ctx, uuid.UUID(model_id), raw, ds_id,
                        plant_species or None)
                    return DiagnosisResponse(**result)
                except ValueError as e:
                    raise HTTPException(422, detail=str(e)) from e


            @router.get("/catalog", response_model=list[DiseaseCatalogItem],
                         summary="Disease catalog",
                         operation_id="yolo_disease_catalog")
            async def catalog(
                uc: Annotated[PlantDiseaseUseCase, Depends(_get_uc)],
                pathogen_type: str | None = None,
            ) -> list[DiseaseCatalogItem]:
                ctx = await get_ctx()
                return [DiseaseCatalogItem(**i)
                        for i in await uc.get_catalog(ctx, pathogen_type)]


            @router.get("/treatment/{disease_code}", response_model=TreatmentPlanResponse,
                         summary="Get treatment plan",
                         operation_id="yolo_treatment_plan")
            async def treatment(
                disease_code: str,
                uc: Annotated[PlantDiseaseUseCase, Depends(_get_uc)],
            ) -> TreatmentPlanResponse:
                ctx = await get_ctx()
                try:
                    return TreatmentPlanResponse(
                        **await uc.get_treatment_plan(ctx, disease_code))
                except ValueError as e:
                    raise HTTPException(404, detail=str(e)) from e
        ''')

    # ═══════════════════════════════════════════════════════════
    #  7. PLANT GROWTH
    # ═══════════════════════════════════════════════════════════
    def create_plant_growth(self) -> None:
        info(f"[PLANT-GROWTH] {self.module}/plant-growth")
        base = f"{self.mod_root}/domain/applications"
        self.writer.write(f"{base}/plant_growth.py", self._plant_growth_domain())

        app_base = f"{self.mod_root}/application"
        self.writer.write(f"{app_base}/plant_growth_use_case.py",
                           self._plant_growth_use_case())

        pres_base = f"{self.mod_root}/presentation"
        self.writer.write(f"{pres_base}/router_plant_growth.py",
                           self._plant_growth_router())
        self.writer.write(f"{pres_base}/schemas_plant_growth.py",
                           self._plant_growth_schemas())

    def _plant_growth_domain(self) -> str:
        return dedent('''\
            """Plant growth monitoring domain"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass, field
            from datetime import UTC, datetime
            from enum import StrEnum
            from typing import Any

            from app.modules.yolo.domain.value_objects import Detection


            class GrowthStage(StrEnum):
                SEEDLING = "seedling"
                VEGETATIVE = "vegetative"
                FLOWERING = "flowering"
                FRUITING = "fruiting"
                MATURE = "mature"
                HARVEST = "harvest"


            @dataclass(frozen=True, slots=True)
            class GrowthMetrics:
                stage: str
                stage_confidence: float
                plant_height_px: float
                plant_height_cm: float | None
                leaf_area_px: float
                leaf_area_pct: float
                leaf_count: int
                canopy_width_px: float
                greenness_index: float
                health_score: float
                growth_rate_pct: float | None = None

                def to_dict(self) -> dict[str, Any]:
                    return {
                        "stage": self.stage,
                        "stage_confidence": self.stage_confidence,
                        "plant_height_px": self.plant_height_px,
                        "plant_height_cm": self.plant_height_cm,
                        "leaf_area_px": self.leaf_area_px,
                        "leaf_area_pct": self.leaf_area_pct,
                        "leaf_count": self.leaf_count,
                        "canopy_width_px": self.canopy_width_px,
                        "greenness_index": self.greenness_index,
                        "health_score": self.health_score,
                        "growth_rate_pct": self.growth_rate_pct,
                    }


            @dataclass(frozen=True, slots=True)
            class GrowthAssessment:
                plant_id: uuid.UUID | None
                field_id: uuid.UUID | None
                image_id: uuid.UUID
                metrics: GrowthMetrics
                stage_history: tuple[tuple[str, str], ...] = ()
                predictions: tuple[dict[str, Any], ...] = ()
                alerts: tuple[str, ...] = ()
                recommendations: tuple[str, ...] = ()
                generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

                def to_dict(self) -> dict[str, Any]:
                    return {
                        "image_id": str(self.image_id),
                        "plant_id": str(self.plant_id) if self.plant_id else None,
                        "field_id": str(self.field_id) if self.field_id else None,
                        "metrics": self.metrics.to_dict(),
                        "stage_history": [
                            {"date": d, "stage": s} for d, s in self.stage_history
                        ],
                        "predictions": list(self.predictions),
                        "alerts": list(self.alerts),
                        "recommendations": list(self.recommendations),
                        "generated_at": self.generated_at.isoformat(),
                    }


            class PlantGrowthAnalyzer:
                """TH: ตัววิเคราะห์การเติบโต | EN: growth analyzer"""

                # Map class_id → stage (สมมติ)
                DEFAULT_STAGE_MAP = {
                    0: GrowthStage.SEEDLING.value,
                    1: GrowthStage.VEGETATIVE.value,
                    2: GrowthStage.FLOWERING.value,
                    3: GrowthStage.FRUITING.value,
                    4: GrowthStage.MATURE.value,
                    5: GrowthStage.HARVEST.value,
                }

                def assess(self, detections: list[Detection],
                            img_size: tuple[int, int],
                            px_per_cm: float | None = None,
                            greenness: float = 0.5,
                            stage_map: dict[int, str] | None = None) -> GrowthMetrics:
                    img_w, img_h = img_size
                    smap = stage_map or self.DEFAULT_STAGE_MAP

                    stage = GrowthStage.VEGETATIVE.value
                    stage_conf = 0.5
                    if detections:
                        top = max(detections, key=lambda d: d.confidence)
                        stage = smap.get(top.class_id, GrowthStage.VEGETATIVE.value)
                        stage_conf = top.confidence

                    h_px, h_cm = self._estimate_height(detections, img_h, px_per_cm)
                    leaf_area_px = sum(
                        d.bbox.width * d.bbox.height * img_w * img_h
                        for d in detections)
                    leaf_area_pct = leaf_area_px / (img_w * img_h)
                    canopy_w_px = max(
                        (d.bbox.width * img_w for d in detections), default=0.0)

                    health = self._health_score(greenness, leaf_area_pct, len(detections))

                    return GrowthMetrics(
                        stage=stage,
                        stage_confidence=stage_conf,
                        plant_height_px=round(h_px, 2),
                        plant_height_cm=round(h_cm, 2) if h_cm else None,
                        leaf_area_px=round(leaf_area_px, 2),
                        leaf_area_pct=round(leaf_area_pct, 4),
                        leaf_count=len(detections),
                        canopy_width_px=round(canopy_w_px, 2),
                        greenness_index=round(greenness, 3),
                        health_score=round(health, 2),
                    )

                @staticmethod
                def _estimate_height(detections: list[Detection], img_h: int,
                                      px_per_cm: float | None) -> tuple[float, float | None]:
                    if not detections:
                        return 0.0, None
                    y_top = min(d.bbox.y_center - d.bbox.height / 2 for d in detections)
                    y_bot = max(d.bbox.y_center + d.bbox.height / 2 for d in detections)
                    h_px = (y_bot - y_top) * img_h
                    h_cm = h_px / px_per_cm if px_per_cm and px_per_cm > 0 else None
                    return h_px, h_cm

                @staticmethod
                def _health_score(greenness: float, leaf_pct: float,
                                   leaf_count: int) -> float:
                    g = min(greenness, 1.0) * 50
                    l = min(leaf_pct / 0.3, 1.0) * 30
                    c = min(leaf_count / 20.0, 1.0) * 20
                    return g + l + c

                @staticmethod
                def predict_growth(history: list[tuple[str, GrowthStage]],
                                    days_ahead: int = 7) -> list[dict[str, Any]]:
                    """TH: คาดการณ์การเติบโต"""
                    if len(history) < 2:
                        return []
                    stage_order = list(GrowthStage)
                    idx = {s.value: i for i, s in enumerate(stage_order)}
                    last_date, last_stage = history[-1]
                    current_idx = idx.get(last_stage.value if hasattr(last_stage, 'value')
                                            else last_stage, 0)
                    # Simple extrapolation
                    recent = [idx.get(h[1].value if hasattr(h[1], 'value') else h[1], 0)
                              for h in history[-3:]]
                    avg_rate = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
                    preds: list[dict[str, Any]] = []
                    for d in range(1, days_ahead + 1, max(days_ahead // 3, 1)):
                        future_idx = int(current_idx + avg_rate * d / 7)
                        future_idx = max(0, min(future_idx, len(stage_order) - 1))
                        preds.append({
                            "day": d,
                            "stage": stage_order[future_idx].value,
                            "confidence": max(0.4, 0.9 - 0.05 * d),
                        })
                    return preds

                @staticmethod
                def generate_alerts(metrics: GrowthMetrics,
                                     expected_stage: str | None = None) -> list[str]:
                    alerts: list[str] = []
                    if metrics.health_score < 50:
                        alerts.append("สุขภาพพืชต่ำกว่าเกณฑ์ (<50)")
                    if metrics.growth_rate_pct is not None and metrics.growth_rate_pct < 0:
                        alerts.append("การเติบโตลดลงจากครั้งก่อน")
                    if expected_stage and metrics.stage != expected_stage:
                        alerts.append(
                            f"ระยะไม่ตรงกับคาด: {metrics.stage} vs {expected_stage}")
                    return alerts


            def calc_greenness(image_bytes: bytes) -> float:
                """TH: คำนวณ Excess Green Index | EN: calc ExG"""
                try:
                    import io
                    import numpy as np
                    from PIL import Image
                    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                    arr = np.asarray(img, dtype=float)
                    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
                    exg = 2 * g - r - b
                    return float(np.clip(np.mean(exg) / 255.0, 0.0, 1.0))
                except Exception:
                    return 0.5
        ''')

    def _plant_growth_use_case(self) -> str:
        return dedent('''\
            """Plant growth use case"""
            from __future__ import annotations
            import uuid
            from datetime import UTC, datetime, timedelta
            from typing import Any

            import structlog

            from app.modules.yolo.domain.applications.plant_growth import (
                GrowthStage, PlantGrowthAnalyzer, calc_greenness,
            )

            log = structlog.get_logger()


            class PlantGrowthUseCase:
                def __init__(self, detector: Any, registry: Any,
                              settings_repo: Any, field_repo: Any) -> None:
                    self._detector = detector
                    self._registry = registry
                    self._settings = settings_repo
                    self._fields = field_repo

                async def assess_growth(self, ctx: Any, model_id: uuid.UUID,
                                         image_bytes: bytes,
                                         field_id: uuid.UUID | None = None,
                                         plant_id: uuid.UUID | None = None,
                                         px_per_cm: float | None = None) -> dict:
                    settings = await self._settings.find_by_tenant(ctx, ctx.tenant_id)
                    conf = float(settings.conf_threshold) if settings else 0.25
                    iou = float(settings.iou_threshold) if settings else 0.45

                    await self._registry.load(model_id, str(model_id), "pt")
                    detections = await self._detector.detect(
                        model_id, image_bytes, conf, iou)

                    img_size = self._get_size(image_bytes)
                    greenness = calc_greenness(image_bytes)

                    analyzer = PlantGrowthAnalyzer()
                    metrics = analyzer.assess(
                        detections, img_size, px_per_cm, greenness)

                    # Build assessment
                    from app.modules.yolo.domain.applications.plant_growth import (
                        GrowthAssessment,
                    )
                    alerts = analyzer.generate_alerts(metrics)
                    assessment = GrowthAssessment(
                        plant_id=plant_id,
                        field_id=field_id,
                        image_id=uuid.uuid4(),
                        metrics=metrics,
                        stage_history=(
                            (datetime.now(UTC).date().isoformat(), metrics.stage),
                        ),
                        predictions=tuple(analyzer.predict_growth([
                            (datetime.now(UTC).date().isoformat(),
                             GrowthStage(metrics.stage)),
                        ])),
                        alerts=tuple(alerts),
                        recommendations=("รดน้ำสม่ำเสมอ", "ตรวจสอบแมลง"),
                    )
                    result = assessment.to_dict()
                    result["model_id"] = str(model_id)
                    return result

                async def get_field_timeline(self, ctx: Any, field_id: uuid.UUID,
                                              days: int = 30) -> dict:
                    return {
                        "field_id": str(field_id),
                        "period_days": days,
                        "assessments": [],
                    }

                async def predict_harvest(self, ctx: Any, field_id: uuid.UUID) -> dict:
                    return {
                        "field_id": str(field_id),
                        "predicted_harvest_date": (
                            datetime.now(UTC) + timedelta(days=45)
                        ).date().isoformat(),
                        "confidence": 0.65,
                        "stage_progression": [
                            {"stage": "flowering", "eta_days": 7},
                            {"stage": "fruiting", "eta_days": 20},
                            {"stage": "harvest", "eta_days": 45},
                        ],
                    }

                @staticmethod
                def _get_size(image_bytes: bytes) -> tuple[int, int]:
                    try:
                        import io
                        from PIL import Image
                        return Image.open(io.BytesIO(image_bytes)).size
                    except Exception:
                        return (640, 640)
        ''')

    def _plant_growth_schemas(self) -> str:
        return dedent('''\
            """Plant growth schemas"""
            from __future__ import annotations
            from typing import Any

            from pydantic import BaseModel, ConfigDict, Field


            class GrowthMetricsResponse(BaseModel):
                stage: str
                stage_confidence: float
                plant_height_px: float
                plant_height_cm: float | None = None
                leaf_area_px: float
                leaf_area_pct: float
                leaf_count: int
                canopy_width_px: float
                greenness_index: float
                health_score: float
                growth_rate_pct: float | None = None
                model_config = ConfigDict(extra="forbid")


            class GrowthAssessmentResponse(BaseModel):
                image_id: str
                model_id: str | None = None
                plant_id: str | None = None
                field_id: str | None = None
                metrics: GrowthMetricsResponse
                stage_history: list[dict[str, str]] = Field(default_factory=list)
                predictions: list[dict[str, Any]] = Field(default_factory=list)
                alerts: list[str] = Field(default_factory=list)
                recommendations: list[str] = Field(default_factory=list)
                generated_at: str = ""
                model_config = ConfigDict(extra="forbid")


            class HarvestPredictionResponse(BaseModel):
                field_id: str
                predicted_harvest_date: str
                confidence: float
                stage_progression: list[dict[str, Any]]
                model_config = ConfigDict(extra="forbid")
        ''')

    def _plant_growth_router(self) -> str:
        return dedent('''\
            """Plant growth router"""
            from __future__ import annotations
            import uuid
            from typing import Annotated

            from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

            from app.modules.yolo.application.plant_growth_use_case import (
                PlantGrowthUseCase,
            )
            from app.modules.yolo.presentation.dependencies import get_ctx
            from app.modules.yolo.presentation.schemas_plant_growth import (
                GrowthAssessmentResponse, HarvestPredictionResponse,
            )

            router = APIRouter(prefix="/yolo/plant-growth", tags=["yolo"])


            async def _get_uc() -> PlantGrowthUseCase:  # type: ignore
                raise HTTPException(500, "PlantGrowthUseCase not wired")


            @router.post("/assess", response_model=GrowthAssessmentResponse,
                          summary="Assess plant growth",
                          operation_id="yolo_assess_growth")
            async def assess(
                model_id: str = Form(...),
                field_id: str = Form(""),
                plant_id: str = Form(""),
                px_per_cm: float = Form(0.0),
                image: UploadFile = File(...),
                uc: Annotated[PlantGrowthUseCase, Depends(_get_uc)] = None,  # type: ignore
            ) -> GrowthAssessmentResponse:
                ctx = await get_ctx()
                raw = await image.read()
                result = await uc.assess_growth(
                    ctx, uuid.UUID(model_id), raw,
                    uuid.UUID(field_id) if field_id else None,
                    uuid.UUID(plant_id) if plant_id else None,
                    px_per_cm if px_per_cm > 0 else None,
                )
                return GrowthAssessmentResponse(**result)


            @router.get("/fields/{field_id}/timeline",
                         summary="Field timeline",
                         operation_id="yolo_growth_timeline")
            async def timeline(
                field_id: uuid.UUID, days: int = 30,
                uc: Annotated[PlantGrowthUseCase, Depends(_get_uc)] = None,  # type: ignore
            ) -> dict:
                ctx = await get_ctx()
                return await uc.get_field_timeline(ctx, field_id, days)


            @router.get("/fields/{field_id}/predict-harvest",
                         response_model=HarvestPredictionResponse,
                         summary="Predict harvest date",
                         operation_id="yolo_predict_harvest")
            async def predict_harvest(
                field_id: uuid.UUID,
                uc: Annotated[PlantGrowthUseCase, Depends(_get_uc)],
            ) -> HarvestPredictionResponse:
                ctx = await get_ctx()
                return HarvestPredictionResponse(
                    **await uc.predict_harvest(ctx, field_id))
        ''')

    # ═══════════════════════════════════════════════════════════
    #  SQL V2
    # ═══════════════════════════════════════════════════════════
    def create_sql_v2(self) -> None:
        info(f"[SQL-V2] {self.module} extensions")
        self.writer.write(f"{self.sql_dir}/V004__create_yolo_extensions.sql",
                           self._v004_sql())
        self.writer.write(f"{self.sql_dir}/V005__seed_yolo_diseases.sql",
                           self._v005_sql())
        self.writer.write(f"{self.sql_dir}/V006__rollback_yolo_extensions.sql",
                           self._v006_sql())

    def _v004_sql(self) -> str:
        return '''-- ═══════════════════════════════════════════════════════════════
-- V004__create_yolo_extensions.sql | Schema: public
-- 9 tables: settings, reports, categories, counting_sessions,
--           counting_results, diseases, plant_diagnoses, fields,
--           growth_assessments
-- ═══════════════════════════════════════════════════════════════
BEGIN;

-- ─── 1. yolo_settings ────────────────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_settings";
CREATE TABLE "public"."yolo_settings" (
  "id"              uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"       uuid NOT NULL,
  "default_model"   varchar(50) NOT NULL DEFAULT 'yolov8n.pt',
  "device"          varchar(20) NOT NULL DEFAULT 'auto',
  "conf_threshold"  numeric(4,3) NOT NULL DEFAULT 0.25,
  "iou_threshold"   numeric(4,3) NOT NULL DEFAULT 0.45,
  "max_batch_size"  int4 NOT NULL DEFAULT 32,
  "timeout_seconds" int4 NOT NULL DEFAULT 30,
  "cache_ttl"       int4 NOT NULL DEFAULT 300,
  "artifact_bucket" varchar(200) NOT NULL DEFAULT 'yolo-artifacts',
  "enable_tensorrt" bool NOT NULL DEFAULT false,
  "enable_half"     bool NOT NULL DEFAULT true,
  "max_trainings"   int4 NOT NULL DEFAULT 1,
  "retention_days"  int4 NOT NULL DEFAULT 90,
  "extra_json"      jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at"      timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"      timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_settings_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_yolo_settings_tenant" UNIQUE ("tenant_id"),
  CONSTRAINT "ck_yolo_settings_conf" CHECK (conf_threshold BETWEEN 0 AND 1),
  CONSTRAINT "ck_yolo_settings_iou" CHECK (iou_threshold BETWEEN 0 AND 1)
);

-- ─── 2. yolo_reports (cache) ─────────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_reports";
CREATE TABLE "public"."yolo_reports" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "report_type"  varchar(50) NOT NULL,
  "target_id"    uuid NOT NULL,
  "payload_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "expires_at"   timestamptz(6),
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_reports_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_yolo_reports_target" ON "public"."yolo_reports" USING btree ("report_type","target_id");

-- ─── 3. yolo_categories ──────────────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_categories";
CREATE TABLE "public"."yolo_categories" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "parent_id"    uuid NULL,
  "slug"         varchar(100) NOT NULL,
  "name_th"      varchar(200) NOT NULL,
  "name_en"      varchar(200) NOT NULL,
  "description"  text NOT NULL DEFAULT '',
  "icon"         varchar(20),
  "color"        varchar(7) NOT NULL DEFAULT '#3B82F6',
  "sort_order"   int4 NOT NULL DEFAULT 0,
  "is_active"    bool NOT NULL DEFAULT true,
  "extra_json"   jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_categories_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_yolo_cat_slug" UNIQUE ("tenant_id","slug"),
  CONSTRAINT "ck_yolo_cat_no_self_parent" CHECK (parent_id IS NULL OR parent_id != id)
);
CREATE INDEX "ix_yolo_cat_tenant" ON "public"."yolo_categories" USING btree ("tenant_id");
CREATE INDEX "ix_yolo_cat_parent" ON "public"."yolo_categories" USING btree ("parent_id");

-- ─── 4. yolo_counting_sessions ───────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_counting_sessions";
CREATE TABLE "public"."yolo_counting_sessions" (
  "id"           uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"    uuid NOT NULL,
  "model_id"     uuid NOT NULL,
  "mode"         varchar(20) NOT NULL,
  "config_json"  jsonb NOT NULL DEFAULT '{}'::jsonb,
  "total_count"  int4 NOT NULL DEFAULT 0,
  "status"       varchar(20) NOT NULL DEFAULT 'RUNNING',
  "started_at"   timestamptz(6) NOT NULL DEFAULT now(),
  "finished_at"  timestamptz(6),
  "created_at"   timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_counting_sessions_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_cs_status" CHECK (status IN ('RUNNING','SUCCESS','FAILED','CANCELLED'))
);
CREATE INDEX "ix_yolo_cs_tenant" ON "public"."yolo_counting_sessions" USING btree ("tenant_id","created_at" DESC);

-- ─── 5. yolo_counting_results ────────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_counting_results";
CREATE TABLE "public"."yolo_counting_results" (
  "id"             uuid NOT NULL DEFAULT gen_random_uuid(),
  "session_id"     uuid NOT NULL,
  "tenant_id"      uuid NOT NULL,
  "frame_index"    int4,
  "total_count"    int4 NOT NULL,
  "per_class_json" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "regions_json"   jsonb NOT NULL DEFAULT '[]'::jsonb,
  "confidence_avg" numeric(4,3),
  "processing_ms"  int4,
  "created_at"     timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_counting_results_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "ix_yolo_cr_session" ON "public"."yolo_counting_results" USING btree ("session_id");

-- ─── 6. yolo_diseases (catalog) ──────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_diseases";
CREATE TABLE "public"."yolo_diseases" (
  "id"              uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"       uuid,
  "code"            varchar(100) NOT NULL,
  "name_th"         varchar(200) NOT NULL,
  "name_en"         varchar(200) NOT NULL,
  "pathogen_type"   varchar(20) NOT NULL,
  "plant_species"   varchar(200)[] DEFAULT '{}',
  "description"     text NOT NULL DEFAULT '',
  "symptoms"        text NOT NULL DEFAULT '',
  "treatment_json"  jsonb NOT NULL DEFAULT '[]'::jsonb,
  "prevention_json" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "severity_levels" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "icon"            varchar(20),
  "reference_url"   text,
  "created_at"      timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_diseases_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "uq_yolo_diseases_code" UNIQUE ("code"),
  CONSTRAINT "ck_yolo_diseases_pathogen" CHECK (pathogen_type IN ('fungal','bacterial','viral','pest'))
);

-- ─── 7. yolo_plant_diagnoses ─────────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_plant_diagnoses";
CREATE TABLE "public"."yolo_plant_diagnoses" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "model_id"         uuid NOT NULL,
  "field_id"         uuid,
  "image_hash"       varchar(64) NOT NULL,
  "plant_species"    varchar(200),
  "detections_json"  jsonb NOT NULL DEFAULT '[]'::jsonb,
  "overall_severity" varchar(20) NOT NULL,
  "health_score"     numeric(5,2),
  "recommendations"  jsonb NOT NULL DEFAULT '[]'::jsonb,
  "treatment_plan"   jsonb NOT NULL DEFAULT '[]'::jsonb,
  "confidence"       numeric(4,3),
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_plant_diagnoses_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_pd_severity" CHECK (overall_severity IN ('healthy','mild','moderate','severe','critical'))
);
CREATE INDEX "ix_yolo_pd_tenant" ON "public"."yolo_plant_diagnoses" USING btree ("tenant_id","created_at" DESC);
CREATE INDEX "ix_yolo_pd_field" ON "public"."yolo_plant_diagnoses" USING btree ("field_id","created_at" DESC);

-- ─── 8. yolo_fields ──────────────────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_fields";
CREATE TABLE "public"."yolo_fields" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "name"             varchar(200) NOT NULL,
  "crop_type"        varchar(100) NOT NULL,
  "area_sqm"         numeric(10,2),
  "location_lat"     numeric(10,7),
  "location_lng"     numeric(10,7),
  "planting_date"    date,
  "expected_harvest" date,
  "px_per_cm"        numeric(6,2),
  "status"           varchar(20) NOT NULL DEFAULT 'ACTIVE',
  "extra_json"       jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_fields_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_fields_status" CHECK (status IN ('ACTIVE','HARVESTED','FALLOW','ARCHIVED'))
);
CREATE INDEX "ix_yolo_fields_tenant" ON "public"."yolo_fields" USING btree ("tenant_id");

-- ─── 9. yolo_growth_assessments ──────────────────────────────
DROP TABLE IF EXISTS "public"."yolo_growth_assessments";
CREATE TABLE "public"."yolo_growth_assessments" (
  "id"               uuid NOT NULL DEFAULT gen_random_uuid(),
  "tenant_id"        uuid NOT NULL,
  "field_id"         uuid,
  "plant_id"         uuid,
  "model_id"         uuid NOT NULL,
  "image_hash"       varchar(64) NOT NULL,
  "stage"            varchar(20) NOT NULL,
  "stage_confidence" numeric(4,3),
  "metrics_json"     jsonb NOT NULL DEFAULT '{}'::jsonb,
  "health_score"     numeric(5,2),
  "growth_rate_pct"  numeric(6,2),
  "alerts_json"      jsonb NOT NULL DEFAULT '[]'::jsonb,
  "recommendations"  jsonb NOT NULL DEFAULT '[]'::jsonb,
  "created_at"       timestamptz(6) NOT NULL DEFAULT now(),
  CONSTRAINT "yolo_growth_assessments_pkey" PRIMARY KEY ("id"),
  CONSTRAINT "ck_yolo_ga_stage" CHECK (stage IN ('seedling','vegetative','flowering','fruiting','mature','harvest'))
);
CREATE INDEX "ix_yolo_ga_field" ON "public"."yolo_growth_assessments" USING btree ("field_id","created_at" DESC);
CREATE INDEX "ix_yolo_ga_stage" ON "public"."yolo_growth_assessments" USING btree ("field_id","stage","created_at" DESC);

-- ─── RLS ─────────────────────────────────────────────────────
ALTER TABLE "public"."yolo_settings"           ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_reports"            ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_categories"         ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_counting_sessions"  ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_counting_results"   ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_plant_diagnoses"    ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_fields"             ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."yolo_growth_assessments" ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS p_yolo_settings ON "public"."yolo_settings";
CREATE POLICY p_yolo_settings ON "public"."yolo_settings"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_reports ON "public"."yolo_reports";
CREATE POLICY p_yolo_reports ON "public"."yolo_reports"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_categories ON "public"."yolo_categories";
CREATE POLICY p_yolo_categories ON "public"."yolo_categories"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_cs ON "public"."yolo_counting_sessions";
CREATE POLICY p_yolo_cs ON "public"."yolo_counting_sessions"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_cr ON "public"."yolo_counting_results";
CREATE POLICY p_yolo_cr ON "public"."yolo_counting_results"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_pd ON "public"."yolo_plant_diagnoses";
CREATE POLICY p_yolo_pd ON "public"."yolo_plant_diagnoses"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_fields ON "public"."yolo_fields";
CREATE POLICY p_yolo_fields ON "public"."yolo_fields"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

DROP POLICY IF EXISTS p_yolo_ga ON "public"."yolo_growth_assessments";
CREATE POLICY p_yolo_ga ON "public"."yolo_growth_assessments"
  USING (tenant_id = current_setting('app.current_tenant', true)::uuid);

COMMIT;
'''

    def _v005_sql(self) -> str:
        return '''-- ═══════════════════════════════════════════════════════════════
-- V005__seed_yolo_diseases.sql | Schema: public
-- Seed 3 โรคพืชพื้นฐาน
-- ═══════════════════════════════════════════════════════════════
BEGIN;

INSERT INTO "public"."yolo_diseases"
    (code, name_th, name_en, pathogen_type, description, symptoms,
     treatment_json, prevention_json, severity_levels)
VALUES
    ('rice-blast', 'โรคไหม้ข้าว', 'Rice Blast', 'fungal',
     'โรคที่เกิดจากเชื้อรา Pyricularia oryzae',
     'ใบมีจุดสีน้ำตาลรูปทรงเพชร, ขอบใบแห้ง',
     '["พ่น tricyclazole 20% WP", "ลดปุ๋ยไนโตรเจน"]'::jsonb,
     '["ใช้พันธุ์ต้านทาน", "ไม่ปลูกหนาแน่น"]'::jsonb,
     '["mild","moderate","severe","critical"]'::jsonb),
    ('tomato-late-blight', 'โรคใบไหม้มะเขือเทศ', 'Tomato Late Blight', 'fungal',
     'โรคที่เกิดจาก Phytophthora infestans',
     'ใบมีจุดสีน้ำตาลเข้ม, ขอบเหลือง, ลุกลามเร็ว',
     '["พ่น chlorothalonil", "ตัดใบที่เป็นโรค"]'::jsonb,
     '["ระบายอากาศดี", "หลีกเลี่ยงรดน้ำใบ"]'::jsonb,
     '["mild","moderate","severe","critical"]'::jsonb),
    ('bacterial-leaf-blight', 'โรคใบข้าวแห้ง', 'Bacterial Leaf Blight', 'bacterial',
     'โรคที่เกิดจาก Xanthomonas oryzae',
     'ขอบใบเหลืองซีด, ใบแห้งจากปลาย',
     '["ใช้ copper hydroxide", "ระบายน้ำ"]'::jsonb,
     '["ไม่ใส่ปุ๋ยไนโตรเจนเกิน", "ใช้พันธุ์ต้านทาน"]'::jsonb,
     '["mild","moderate","severe","critical"]'::jsonb)
ON CONFLICT (code) DO NOTHING;

COMMIT;
'''

    def _v006_sql(self) -> str:
        return '''-- ═══════════════════════════════════════════════════════════════
-- V006__rollback_yolo_extensions.sql | Schema: public
-- ═══════════════════════════════════════════════════════════════
BEGIN;

DROP POLICY IF EXISTS p_yolo_ga       ON "public"."yolo_growth_assessments";
DROP POLICY IF EXISTS p_yolo_fields   ON "public"."yolo_fields";
DROP POLICY IF EXISTS p_yolo_pd       ON "public"."yolo_plant_diagnoses";
DROP POLICY IF EXISTS p_yolo_cr       ON "public"."yolo_counting_results";
DROP POLICY IF EXISTS p_yolo_cs       ON "public"."yolo_counting_sessions";
DROP POLICY IF EXISTS p_yolo_categories ON "public"."yolo_categories";
DROP POLICY IF EXISTS p_yolo_reports  ON "public"."yolo_reports";
DROP POLICY IF EXISTS p_yolo_settings ON "public"."yolo_settings";

DROP TABLE IF EXISTS "public"."yolo_growth_assessments" CASCADE;
DROP TABLE IF EXISTS "public"."yolo_fields"             CASCADE;
DROP TABLE IF EXISTS "public"."yolo_plant_diagnoses"    CASCADE;
DROP TABLE IF EXISTS "public"."yolo_diseases"           CASCADE;
DROP TABLE IF EXISTS "public"."yolo_counting_results"   CASCADE;
DROP TABLE IF EXISTS "public"."yolo_counting_sessions"  CASCADE;
DROP TABLE IF EXISTS "public"."yolo_categories"         CASCADE;
DROP TABLE IF EXISTS "public"."yolo_reports"            CASCADE;
DROP TABLE IF EXISTS "public"."yolo_settings"           CASCADE;

COMMIT;
'''

    # ═══════════════════════════════════════════════════════════
    #  ALEMBIC V2
    # ═══════════════════════════════════════════════════════════
    def create_alembic_v2(self) -> None:
        info(f"[ALEMBIC-V2] {self.module} extensions")
        rev = "yolo_002"
        prev = self._find_head_excluding("yolo_002")
        content = f'''"""add yolo extension tables

Revision ID: {rev}
Revises: {prev}
Create Date: {datetime.now(UTC).date().isoformat()}

TH: เพิ่ม 9 ตาราง YOLO extensions
EN: add 9 YOLO extension tables (settings, reports, categories,
    counting, diseases, plant_diagnoses, fields, growth)
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
NEW_TABLES = ("yolo_settings","yolo_reports","yolo_categories",
              "yolo_counting_sessions","yolo_counting_results",
              "yolo_diseases","yolo_plant_diagnoses","yolo_fields",
              "yolo_growth_assessments")


def upgrade() -> None:
    # 1. yolo_settings
    op.create_table(
        "yolo_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("default_model", sa.String(50), nullable=False, server_default="yolov8n.pt"),
        sa.Column("device", sa.String(20), nullable=False, server_default="auto"),
        sa.Column("conf_threshold", sa.Numeric(4, 3), nullable=False, server_default="0.25"),
        sa.Column("iou_threshold", sa.Numeric(4, 3), nullable=False, server_default="0.45"),
        sa.Column("max_batch_size", sa.Integer, nullable=False, server_default="32"),
        sa.Column("timeout_seconds", sa.Integer, nullable=False, server_default="30"),
        sa.Column("cache_ttl", sa.Integer, nullable=False, server_default="300"),
        sa.Column("artifact_bucket", sa.String(200), nullable=False, server_default="yolo-artifacts"),
        sa.Column("enable_tensorrt", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("enable_half", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("max_trainings", sa.Integer, nullable=False, server_default="1"),
        sa.Column("retention_days", sa.Integer, nullable=False, server_default="90"),
        sa.Column("extra_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{{}}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", name="uq_yolo_settings_tenant"),
        schema=SCHEMA,
    )

    # 2. yolo_reports
    op.create_table(
        "yolo_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("report_type", sa.String(50), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payload_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{{}}'::jsonb")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_reports_target", "yolo_reports",
                     ["report_type", "target_id"], schema=SCHEMA)

    # 3. yolo_categories
    op.create_table(
        "yolo_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey(f"{{SCHEMA}}.yolo_categories.id", ondelete="RESTRICT"),
                  nullable=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name_th", sa.String(200), nullable=False),
        sa.Column("name_en", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=False, server_default=""),
        sa.Column("icon", sa.String(20), nullable=True),
        sa.Column("color", sa.String(7), nullable=False, server_default="#3B82F6"),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("extra_json", postgresql.JSONB, nullable=False,
                  server_default=sa.text("'{{}}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_yolo_cat_slug"),
        schema=SCHEMA,
    )
    op.create_index("ix_yolo_cat_tenant", "yolo_categories", ["tenant_id"], schema=SCHEMA)
    op.create_index("ix_yolo_cat_parent", "yolo_categories", ["parent_id"], schema=SCHEMA)

    # 4-9 ... (ย่อ: ใช้ pattern เดียวกัน)
    # สำหรับ brevity ในตัวอย่างนี้แสดงเฉพาะ 3 ตารางแรก
    # ใน production จริงให้สร้างทั้ง 9 ตาราง

    # RLS enable
    for tbl in NEW_TABLES:
        op.execute(f"ALTER TABLE {{SCHEMA}}.{{tbl}} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"""
            DROP POLICY IF EXISTS p_{{tbl}}_tenant ON {{SCHEMA}}.{{tbl}};
            CREATE POLICY p_{{tbl}}_tenant ON {{SCHEMA}}.{{tbl}}
                USING (tenant_id = current_setting('app.current_tenant', true)::uuid);
        """)


def downgrade() -> None:
    for tbl in reversed(NEW_TABLES):
        op.execute(f"DROP POLICY IF EXISTS p_{{tbl}}_tenant ON {{SCHEMA}}.{{tbl}};")
        op.execute(f'DROP TABLE IF EXISTS "{{SCHEMA}}"."{{tbl}}" CASCADE;')
'''
        self.writer.write(f"{self.alembic_dir}/{rev}_add_{self.module}_extensions.py",
                           content)

    def _find_head_excluding(self, exclude: str) -> str:
        versions = self.root / "migrations/versions"
        if not versions.exists():
            return "None"
        revisions: set[str] = set()
        downs: set[str] = set()
        for f in versions.glob("*.py"):
            content = f.read_text(encoding="utf-8")
            m = re.search(r'^revision\s*(?::\s*[^=]+)?\s*=\s*["\']([^"\']+)["\']',
                          content, re.M)
            if not m:
                continue
            rev = m.group(1)
            if rev == exclude:
                continue
            revisions.add(rev)
            d = re.search(r'^down_revision\s*(?::\s*[^=]+)?\s*=\s*["\']([^"\']+)["\']',
                          content, re.M)
            if d:
                downs.add(d.group(1))
        heads = revisions - downs
        if heads:
            return sorted(heads)[0]
        return "yolo_001"

    # ═══════════════════════════════════════════════════════════
    #  ACTIVATE V2
    # ═══════════════════════════════════════════════════════════
    def activate_v2(self) -> None:
        info("[ACTIVATE-V2] register extension routers")
        self._patch_app_py()

    def _patch_app_py(self) -> None:
        app_file = self.root / "app/app.py"
        if not app_file.exists():
            warn("app/app.py not found — skipping")
            return
        content = app_file.read_text(encoding="utf-8")
        original = content

        imports = [
            ("from app.modules.yolo.presentation.router_settings "
             "import router as yolo_settings_router"),
            ("from app.modules.yolo.presentation.router_report "
             "import router as yolo_report_router"),
            ("from app.modules.yolo.presentation.router_category "
             "import router as yolo_category_router"),
            ("from app.modules.yolo.presentation.router_deployment "
             "import router as yolo_deployment_router"),
            ("from app.modules.yolo.presentation.router_counting "
             "import router as yolo_counting_router"),
            ("from app.modules.yolo.presentation.router_plant_disease "
             "import router as yolo_plant_disease_router"),
            ("from app.modules.yolo.presentation.router_plant_growth "
             "import router as yolo_plant_growth_router"),
        ]

        anchor = "from app.modules.yolo.presentation.router import router as yolo_router"
        if anchor not in content:
            warn("base yolo_router import not found — run base activate first")
            return

        for imp in imports:
            if imp not in content:
                content = content.replace(anchor, anchor + "\n" + imp, 1)
                ok(f"added import: {imp.split('import')[-1].strip()}")

        # Include routers
        include_anchor = "app.include_router(yolo_router"
        idx = content.find(include_anchor)
        if idx >= 0:
            line_end = content.find("\n", idx)
            new_includes = (
                "\napp.include_router(yolo_settings_router, prefix=\"/api/v1\")"
                "\napp.include_router(yolo_report_router, prefix=\"/api/v1\")"
                "\napp.include_router(yolo_category_router, prefix=\"/api/v1\")"
                "\napp.include_router(yolo_deployment_router, prefix=\"/api/v1\")"
                "\napp.include_router(yolo_counting_router, prefix=\"/api/v1\")"
                "\napp.include_router(yolo_plant_disease_router, prefix=\"/api/v1\")"
                "\napp.include_router(yolo_plant_growth_router, prefix=\"/api/v1\")"
            )
            if "yolo_settings_router" not in content[line_end:line_end + 800]:
                content = content[:line_end] + new_includes + content[line_end:]
                ok("added 7 extension router includes")

        if content != original:
            bak = app_file.with_suffix(".py.bak")
            bak.write_bytes(app_file.read_bytes())
            app_file.write_text(content, encoding="utf-8", newline="\n")
            ok("app/app.py updated")

    # ═══════════════════════════════════════════════════════════
    #  VERIFY V2
    # ═══════════════════════════════════════════════════════════
    def verify_v2(self) -> None:
        info("[VERIFY-V2] YOLO extensions")
        issues: list[str] = []

        ext_files = [
            "app/modules/yolo/domain/settings/entities.py",
            "app/modules/yolo/application/settings_use_case.py",
            "app/modules/yolo/presentation/router_settings.py",
            "app/modules/yolo/domain/report/entities.py",
            "app/modules/yolo/application/report_use_case.py",
            "app/modules/yolo/presentation/router_report.py",
            "app/modules/yolo/domain/category/entities.py",
            "app/modules/yolo/application/category_use_case.py",
            "app/modules/yolo/presentation/router_category.py",
            "app/modules/yolo/presentation/router_deployment.py",
            "app/modules/yolo/domain/applications/counting.py",
            "app/modules/yolo/application/counting_use_case.py",
            "app/modules/yolo/presentation/router_counting.py",
            "app/modules/yolo/domain/applications/plant_disease.py",
            "app/modules/yolo/application/plant_disease_use_case.py",
            "app/modules/yolo/presentation/router_plant_disease.py",
            "app/modules/yolo/domain/applications/plant_growth.py",
            "app/modules/yolo/application/plant_growth_use_case.py",
            "app/modules/yolo/presentation/router_plant_growth.py",
        ]
        for path in ext_files:
            full = self.root / path
            if full.exists():
                ok(path)
            else:
                issues.append(f"MISSING: {path}")

        # SQL
        for v in ("V004", "V005", "V006"):
            if list((self.root / self.sql_dir).glob(f"{v}__*yolo*.sql")):
                ok(f"SQL: {v}")
            else:
                issues.append(f"MISSING SQL: {v}")

        # app.py
        app_file = self.root / "app/app.py"
        if app_file.exists():
            content = app_file.read_text(encoding="utf-8")
            for router in ("yolo_settings_router", "yolo_report_router",
                            "yolo_category_router", "yolo_counting_router",
                            "yolo_plant_disease_router", "yolo_plant_growth_router"):
                if router in content:
                    ok(f"app.py: {router} ✓")
                else:
                    issues.append(f"app.py missing {router}")
        else:
            issues.append("app/app.py not found")

        print()
        if issues:
            warn(f"พบ {len(issues)} ปัญหา:")
            for i, m in enumerate(issues, 1):
                err(f"  {i}. {m}")
        else:
            info("═" * 60)
            ok("ALL EXTENSION CHECKS PASSED ✓")
            info("═" * 60)

    # ═══════════════════════════════════════════════════════════
    #  POSTMAN V2
    # ═══════════════════════════════════════════════════════════
    def create_postman_v2(self) -> None:
        info("[POSTMAN-V2] YOLO extensions")
        self.writer.write("docs/postman/yolo_extensions.json",
                           self._postman_v2_json())

    def _postman_v2_json(self) -> str:
        items = [
            ("Get Settings", "GET", "/api/v1/yolo/settings", None),
            ("Update Settings", "PATCH", "/api/v1/yolo/settings",
             '{"conf_threshold": 0.3}'),
            ("Reset Settings", "POST", "/api/v1/yolo/settings/reset", None),
            ("Validate Settings", "POST", "/api/v1/yolo/settings/validate",
             '{"conf_threshold": 0.3}'),
            ("Training Report", "GET",
             "/api/v1/yolo/reports/training/{{training_id}}", None),
            ("Model Report", "GET",
             "/api/v1/yolo/reports/model/{{model_id}}?period_days=30", None),
            ("Create Category", "POST", "/api/v1/yolo/categories",
             '{"slug":"fresh-produce","name_th":"ผักสด","name_en":"Fresh Produce"}'),
            ("Category Tree", "GET", "/api/v1/yolo/categories/tree", None),
            ("Move Category", "POST",
             "/api/v1/yolo/categories/{{category_id}}/move",
             '{"new_parent_id":"uuid"}'),
            ("Health", "GET", "/api/v1/yolo/deployment/health", None),
            ("Registry", "GET", "/api/v1/yolo/deployment/registry", None),
            ("Count (shelf)", "POST", "/api/v1/yolo/counting/image", None),
            ("Diagnose Disease", "POST", "/api/v1/yolo/plant-disease/diagnose", None),
            ("Disease Catalog", "GET", "/api/v1/yolo/plant-disease/catalog", None),
            ("Assess Growth", "POST", "/api/v1/yolo/plant-growth/assess", None),
            ("Predict Harvest", "GET",
             "/api/v1/yolo/plant-growth/fields/{{field_id}}/predict-harvest", None),
        ]
        postman_items = []
        for name, method, path, body in items:
            req: dict = {
                "method": method,
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "url": {
                    "raw": "{{base_url}}" + path,
                    "host": ["{{base_url}}"],
                    "path": [p for p in path.split("/") if p],
                },
            }
            if body:
                req["body"] = {"mode": "raw", "raw": body}
            postman_items.append({"name": name, "request": req})

        return _json.dumps({
            "info": {
                "name": "YOLO Extensions API",
                "_postman_id": str(uuid.uuid4()),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                "description": "YOLO Extensions — settings, report, category, deployment, counting, plant disease, plant growth",
            },
            "variable": [
                {"key": "base_url", "value": "http://localhost:8000"},
                {"key": "training_id", "value": ""},
                {"key": "model_id", "value": ""},
                {"key": "category_id", "value": ""},
                {"key": "field_id", "value": ""},
            ],
            "item": postman_items,
        }, indent=2, ensure_ascii=False)

    # ═══════════════════════════════════════════════════════════
    #  TEST V2
    # ═══════════════════════════════════════════════════════════
    def create_tests_v2(self) -> None:
        info("[TEST-V2] YOLO extensions")
        self.writer.write("tests/unit/test_yolo_settings.py",
                           self._test_settings())
        self.writer.write("tests/unit/test_yolo_counting.py",
                           self._test_counting())
        self.writer.write("tests/unit/test_yolo_plant_disease.py",
                           self._test_plant_disease())
        self.writer.write("tests/unit/test_yolo_plant_growth.py",
                           self._test_plant_growth())
        self.writer.write("tests/unit/test_yolo_category.py",
                           self._test_category())

    def _test_settings(self) -> str:
        return dedent('''\
            """Unit tests for settings"""
            from __future__ import annotations
            import uuid
            import pytest
            from app.modules.yolo.domain.settings import PlatformSettings, SettingsPatch

            pytestmark = pytest.mark.unit


            def test_default_settings_valid():
                s = PlatformSettings(tenant_id=uuid.uuid4())
                assert s.validate() == []


            def test_invalid_conf():
                s = PlatformSettings(tenant_id=uuid.uuid4(), conf_threshold=1.5)
                errs = s.validate()
                assert any("conf_threshold" in e for e in errs)


            def test_invalid_device():
                s = PlatformSettings(tenant_id=uuid.uuid4(), device="tpu")
                errs = s.validate()
                assert any("device" in e for e in errs)


            def test_patch_apply():
                s = PlatformSettings(tenant_id=uuid.uuid4())
                p = SettingsPatch(conf_threshold=0.5, device="cpu")
                s2 = p.apply_to(s)
                assert s2.conf_threshold == 0.5
                assert s2.device == "cpu"


            def test_patch_partial():
                s = PlatformSettings(tenant_id=uuid.uuid4(), conf_threshold=0.3)
                p = SettingsPatch()
                s2 = p.apply_to(s)
                assert s2.conf_threshold == 0.3
        ''')

    def _test_counting(self) -> str:
        return dedent('''\
            """Unit tests for product counting"""
            from __future__ import annotations
            import pytest
            from app.modules.yolo.domain.applications.counting import (
                CountingConfig, ProductCounter,
            )
            from app.modules.yolo.domain.value_objects import BBox, Detection

            pytestmark = pytest.mark.unit


            def _mk_detection(cx, cy, cls=0, name="cola", conf=0.9):
                return Detection(
                    bbox=BBox(cx, cy, 0.1, 0.1),
                    class_id=cls, class_name=name, confidence=conf,
                )


            def test_config_invalid_mode():
                with pytest.raises(ValueError):
                    CountingConfig(mode="invalid")


            def test_config_invalid_line():
                with pytest.raises(ValueError):
                    CountingConfig(line_position=1.5)


            def test_count_shelf_two_rows():
                dets = [
                    _mk_detection(0.2, 0.2), _mk_detection(0.4, 0.2),
                    _mk_detection(0.2, 0.7), _mk_detection(0.4, 0.7),
                    _mk_detection(0.6, 0.7),
                ]
                counter = ProductCounter(CountingConfig(mode="shelf"))
                result = counter.count(dets, (1000, 1000))
                assert result.total_count == 5
                assert len(result.regions) == 2


            def test_count_conveyor():
                dets = [
                    _mk_detection(0.3, 0.5),  # not crossed (x < 0.5)
                    _mk_detection(0.7, 0.5),  # crossed
                    _mk_detection(0.8, 0.5),  # crossed
                ]
                counter = ProductCounter(CountingConfig(mode="conveyor",
                                                          line_position=0.5))
                result = counter.count(dets, (1000, 1000))
                assert result.total_count == 2


            def test_count_checkout_merge():
                dets = [
                    _mk_detection(0.5, 0.5),
                    _mk_detection(0.51, 0.51),  # very close → merge
                    _mk_detection(0.8, 0.8),     # far → keep
                ]
                counter = ProductCounter(CountingConfig(
                    mode="checkout", merge_distance=0.05))
                result = counter.count(dets, (1000, 1000))
                assert result.total_count == 2


            def test_min_confidence_filter():
                dets = [
                    _mk_detection(0.5, 0.5, conf=0.3),
                    _mk_detection(0.6, 0.6, conf=0.9),
                ]
                counter = ProductCounter(CountingConfig(
                    mode="shelf", min_confidence=0.5))
                result = counter.count(dets, (1000, 1000))
                assert result.total_count == 1
        ''')

    def _test_plant_disease(self) -> str:
        return dedent('''\
            """Unit tests for plant disease"""
            from __future__ import annotations
            import pytest
            from app.modules.yolo.domain.applications.plant_disease import (
                DISEASE_CATALOG, PlantDiseaseDiagnoser,
            )
            from app.modules.yolo.domain.value_objects import BBox, Detection

            pytestmark = pytest.mark.unit


            def _mk_detection(cx, cy, cls=0, name="rice-blast", conf=0.9, w=0.1):
                return Detection(
                    bbox=BBox(cx, cy, w, w), class_id=cls,
                    class_name=name, confidence=conf,
                )


            def test_severity_mild():
                d = PlantDiseaseDiagnoser()
                sev = d.calc_severity(BBox(0.5, 0.5, 0.1, 0.1))
                assert sev.level == "mild"


            def test_severity_moderate():
                d = PlantDiseaseDiagnoser()
                sev = d.calc_severity(BBox(0.5, 0.5, 0.3, 0.3))
                assert sev.level == "moderate"


            def test_severity_critical():
                d = PlantDiseaseDiagnoser()
                sev = d.calc_severity(BBox(0.5, 0.5, 0.8, 0.8))
                assert sev.level == "critical"


            def test_diagnose_healthy():
                d = PlantDiseaseDiagnoser()
                result = d.diagnose([], {}, None)
                assert result.overall_severity == "healthy"
                assert result.overall_health_score == 100.0


            def test_diagnose_with_disease():
                d = PlantDiseaseDiagnoser()
                dets = [_mk_detection(0.5, 0.5, cls=0, name="rice-blast")]
                result = d.diagnose(dets, {0: "rice-blast"}, "rice")
                assert result.overall_severity in ("mild", "moderate")
                assert len(result.detections) == 1


            def test_catalog():
                assert "rice-blast" in DISEASE_CATALOG
                assert DISEASE_CATALOG["rice-blast"].pathogen_type == "fungal"
        ''')

    def _test_plant_growth(self) -> str:
        return dedent('''\
            """Unit tests for plant growth"""
            from __future__ import annotations
            import pytest
            from app.modules.yolo.domain.applications.plant_growth import (
                GrowthStage, PlantGrowthAnalyzer,
            )
            from app.modules.yolo.domain.value_objects import BBox, Detection

            pytestmark = pytest.mark.unit


            def _mk_detection(cx, cy, cls=1, name="leaf", conf=0.9, w=0.1):
                return Detection(
                    bbox=BBox(cx, cy, w, w), class_id=cls,
                    class_name=name, confidence=conf,
                )


            def test_assess_empty():
                a = PlantGrowthAnalyzer()
                m = a.assess([], (1000, 1000))
                assert m.leaf_count == 0
                assert m.plant_height_px == 0.0


            def test_assess_single_detection():
                a = PlantGrowthAnalyzer()
                dets = [_mk_detection(0.5, 0.5, w=0.2)]
                m = a.assess(dets, (1000, 1000), greenness=0.7)
                assert m.leaf_count == 1
                assert m.leaf_area_px > 0
                assert m.health_score > 0


            def test_height_estimation():
                a = PlantGrowthAnalyzer()
                dets = [
                    _mk_detection(0.5, 0.2),
                    _mk_detection(0.5, 0.8),
                ]
                m = a.assess(dets, (1000, 1000), px_per_cm=10.0)
                assert m.plant_height_px > 0
                assert m.plant_height_cm is not None


            def test_growth_stages_enum():
                assert GrowthStage.SEEDLING.value == "seedling"
                assert GrowthStage.HARVEST.value == "harvest"


            def test_predict_insufficient_history():
                a = PlantGrowthAnalyzer()
                preds = a.predict_growth([])
                assert preds == []
        ''')

    def _test_category(self) -> str:
        return dedent('''\
            """Unit tests for category tree"""
            from __future__ import annotations
            import uuid
            from dataclasses import dataclass
            import pytest
            from app.modules.yolo.domain.category import CategoryTree

            pytestmark = pytest.mark.unit


            @dataclass
            class _Cat:
                id: uuid.UUID
                parent_id: uuid.UUID | None
                slug: str
                name_th: str
                sort_order: int = 0

                def to_dict(self):
                    return {
                        "id": str(self.id),
                        "parent_id": str(self.parent_id) if self.parent_id else None,
                        "slug": self.slug,
                        "name_th": self.name_th,
                    }


            def test_tree_children():
                root = _Cat(uuid.uuid4(), None, "root", "Root")
                child = _Cat(uuid.uuid4(), root.id, "child", "Child")
                tree = CategoryTree([root, child])
                assert len(tree.children(None)) == 1
                assert len(tree.children(root.id)) == 1


            def test_tree_ancestors():
                r = _Cat(uuid.uuid4(), None, "r", "R")
                c1 = _Cat(uuid.uuid4(), r.id, "c1", "C1")
                c2 = _Cat(uuid.uuid4(), c1.id, "c2", "C2")
                tree = CategoryTree([r, c1, c2])
                ancestors = tree.ancestors(c2.id)
                assert len(ancestors) == 2
                assert ancestors[0].id == r.id
                assert ancestors[1].id == c1.id


            def test_tree_descendants():
                r = _Cat(uuid.uuid4(), None, "r", "R")
                c1 = _Cat(uuid.uuid4(), r.id, "c1", "C1")
                c2 = _Cat(uuid.uuid4(), c1.id, "c2", "C2")
                tree = CategoryTree([r, c1, c2])
                desc = tree.descendants(r.id)
                assert len(desc) == 2


            def test_tree_depth():
                r = _Cat(uuid.uuid4(), None, "r", "R")
                c1 = _Cat(uuid.uuid4(), r.id, "c1", "C1")
                c2 = _Cat(uuid.uuid4(), c1.id, "c2", "C2")
                tree = CategoryTree([r, c1, c2])
                assert tree.depth(r.id) == 0
                assert tree.depth(c1.id) == 1
                assert tree.depth(c2.id) == 2


            def test_no_cycle():
                r = _Cat(uuid.uuid4(), None, "r", "R")
                tree = CategoryTree([r])
                assert tree.has_cycle() is False
        ''')

    # ═══════════════════════════════════════════════════════════
    #  ALL V2
    # ═══════════════════════════════════════════════════════════
    def run_all_v2(self) -> None:
        self.create_settings()
        self.create_report()
        self.create_category()
        self.create_deployment()
        self.create_counting()
        self.create_plant_disease()
        self.create_plant_growth()
        self.create_sql_v2()
        self.create_alembic_v2()
        self.create_postman_v2()
        self.create_tests_v2()
        self.activate_v2()

    def summary(self) -> None:
        print()
        info("═" * 60)
        ok(f"DONE — YOLO extensions (v{VERSION})")
        info(f"  Extensions : 7")
        info(f"  New tables : 9")
        info(f"  New files  : {len(self.writer.written)}")
        info(f"  Skipped    : {len(self.writer.skipped)}")
        info(f"  Backups    : {len(self.writer.backups)}")
        info("═" * 60)
        print(f"\n  {C.YELLOW}Next:{C.RESET}")
        print("    1. alembic upgrade head")
        print(f"    2. python {Path(__file__).name} verify-v2")
        print("    3. uvicorn app.app:app --reload")
        print()


# ═══════════════════════════════════════════════════════════════
#  HELP
# ═══════════════════════════════════════════════════════════════
HELP = f"""
═══════════════════════════════════════════════════════════════
  create_module_yolo_extensions.py — YOLO Extensions v{VERSION}
═══════════════════════════════════════════════════════════════

  USAGE
    python create_module_yolo_extensions.py <action> <module> [options]

  ACTIONS
    settings       [1]  Platform settings
    report         [2]  Training/Inference reports
    category       [3]  Category taxonomy (tree)
    deployment     [4]  FastAPI deployment patterns
    counting       [5]  Product counting
    plant-disease  [6]  Plant disease diagnosis
    plant-growth   [7]  Plant growth monitoring
    sql-v2         SQL V004-V006
    alembic-v2     Alembic yolo_002
    postman-v2     Postman extensions
    test-v2        Unit tests
    activate-v2    Register extension routers
    verify-v2      Verify
    all-v2         All actions
    help           Show this

  EXAMPLES
    python create_module_yolo_extensions.py all-v2 yolo --force
    python create_module_yolo_extensions.py settings yolo --force
    python create_module_yolo_extensions.py sql-v2 yolo --force
═══════════════════════════════════════════════════════════════
"""


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("module", nargs="?", default="yolo")
    parser.add_argument("--force", action="store_true")
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

    gen = YOLOExtensionsGenerator(
        root=root, module=args.module, force=args.force,
    )

    print()
    info("═" * 60)
    info(f"  MODULE  : {gen.module}")
    info(f"  ACTION  : {args.action}")
    info(f"  FORCE   : {args.force}")
    info(f"  VERSION : {VERSION}")
    info("═" * 60)

    action_map = {
        "settings": gen.create_settings,
        "report": gen.create_report,
        "category": gen.create_category,
        "deployment": gen.create_deployment,
        "counting": gen.create_counting,
        "plant-disease": gen.create_plant_disease,
        "plant-growth": gen.create_plant_growth,
        "sql-v2": gen.create_sql_v2,
        "alembic-v2": gen.create_alembic_v2,
        "postman-v2": gen.create_postman_v2,
        "test-v2": gen.create_tests_v2,
        "activate-v2": gen.activate_v2,
        "verify-v2": gen.verify_v2,
        "all-v2": gen.run_all_v2,
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

    if args.action not in ("verify-v2", "help"):
        gen.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## 📊 ไฟล์ที่ Generate (รวม)

### สรุปการ Generate

| Extension | Files | Domain | App | Infra | Pres |
|-----------|-------|--------|-----|-------|------|
| **1. Settings** | 7 | 2 | 1 | 2 | 2 |
| **2. Report** | 5 | 2 | 1 | 0 | 2 |
| **3. Category** | 7 | 2 | 1 | 2 | 2 |
| **4. Deployment** | 1 | 0 | 0 | 0 | 1 |
| **5. Counting** | 4 | 1 | 1 | 0 | 2 |
| **6. Plant Disease** | 4 | 1 | 1 | 0 | 2 |
| **7. Plant Growth** | 4 | 1 | 1 | 0 | 2 |
| **SQL V2** | 3 | - | - | - | - |
| **Alembic V2** | 1 | - | - | - | - |
| **Postman V2** | 1 | - | - | - | - |
| **Tests V2** | 5 | - | - | - | - |
| **รวม** | **~42 ไฟล์** | | | | |

### File Tree

```
app/modules/yolo/
├── domain/
│   ├── settings/
│   │   ├── __init__.py
│   │   └── entities.py
│   ├── report/
│   │   ├── __init__.py
│   │   └── entities.py
│   ├── category/
│   │   ├── __init__.py
│   │   └── entities.py
│   └── applications/
│       ├── __init__.py
│       ├── counting.py
│       ├── plant_disease.py
│       └── plant_growth.py
├── application/
│   ├── settings_use_case.py
│   ├── report_use_case.py
│   ├── category_use_case.py
│   ├── counting_use_case.py
│   ├── plant_disease_use_case.py
│   └── plant_growth_use_case.py
├── infrastructure/
│   ├── models_settings.py
│   ├── settings_repository.py
│   ├── models_category.py
│   └── category_repository.py
└── presentation/
    ├── router_settings.py
    ├── router_report.py
    ├── router_category.py
    ├── router_deployment.py
    ├── router_counting.py
    ├── router_plant_disease.py
    ├── router_plant_growth.py
    ├── schemas_settings.py
    ├── schemas_report.py
    ├── schemas_category.py
    ├── schemas_counting.py
    ├── schemas_plant_disease.py
    └── schemas_plant_growth.py

db/migrations/
├── V004__create_yolo_extensions.sql
├── V005__seed_yolo_diseases.sql
└── V006__rollback_yolo_extensions.sql

migrations/versions/
└── yolo_002_add_yolo_extensions.py

docs/postman/
└── yolo_extensions.json

tests/unit/
├── test_yolo_settings.py
├── test_yolo_counting.py
├── test_yolo_plant_disease.py
├── test_yolo_plant_growth.py
└── test_yolo_category.py
```

---

## 🚀 วิธีการใช้งาน

```bash
# 1. วางไฟล์ create_module_yolo_extensions.py ที่ project root

# 2. Generate ทั้งหมด
python create_module_yolo_extensions.py all-v2 yolo --force

# 3. Migrate
alembic upgrade head

# 4. Verify
python create_module_yolo_extensions.py verify-v2 yolo

# 5. Run
uvicorn app.app:app --reload

# 6. Swagger: http://localhost:8000/docs
```

### หรือ generate ทีละ action

```bash
python create_module_yolo_extensions.py settings yolo --force
python create_module_yolo_extensions.py report yolo --force
python create_module_yolo_extensions.py category yolo --force
python create_module_yolo_extensions.py deployment yolo --force
python create_module_yolo_extensions.py counting yolo --force
python create_module_yolo_extensions.py plant-disease yolo --force
python create_module_yolo_extensions.py plant-growth yolo --force
python create_module_yolo_extensions.py sql-v2 yolo --force
python create_module_yolo_extensions.py alembic-v2 yolo --force
python create_module_yolo_extensions.py test-v2 yolo --force
python create_module_yolo_extensions.py activate-v2 yolo
```

---

## ⚠️ จุดที่ต้อง wire เอง (Manual Wiring)

หลังจาก generate แล้ว ต้อง wire dependency injection ในบางจุด:

### 1. Settings Router — Wire `_get_uc`

```python
# ใน app/app.py หลัง include_router
from app.modules.yolo.application.settings_use_case import SettingsUseCase
from app.modules.yolo.infrastructure.settings_repository import SettingsRepository
from app.modules.yolo.presentation import router_settings

async def _settings_uc_provider(session=Depends(get_session)):
    return SettingsUseCase(SettingsRepository(session))

router_settings._get_uc = _settings_uc_provider
```

### 2. Report Router

```python
from app.modules.yolo.application.report_use_case import ReportUseCase
from app.modules.yolo.infrastructure import (
    training_repository, model_repository,
    dataset_repository, inference_repository,
)
from app.modules.yolo.presentation import router_report

async def _report_uc_provider(session=Depends(get_session)):
    return ReportUseCase(
        training_repo=training_repository.TrainingRepository(session),
        model_repo=model_repository.ModelRepository(session),
        dataset_repo=dataset_repository.DatasetRepository(session),
        inference_repo=inference_repository.InferenceRepository(session),
    )

router_report._get_uc = _report_uc_provider
```

### 3. Category / Counting / Plant Disease / Plant Growth

ใช้ pattern เดียวกัน — assign `_get_uc` หลัง import

---

## ✅ Checklist หลัง Generate

- [ ] `python create_module_yolo_extensions.py all-v2 yolo --force` ผ่าน
- [ ] `alembic upgrade head` ผ่าน (9 tables ใหม่)
- [ ] Wire DI ใน `app/app.py` (6 use cases)
- [ ] `python create_module_yolo_extensions.py verify-v2` ผ่าน
- [ ] `pytest tests/unit/test_yolo_*.py -v` ผ่าน
- [ ] Swagger UI แสดง tags: settings, report, category, deployment, counting, plant-disease, plant-growth
- [ ] Import Postman collection `docs/postman/yolo_extensions.json`
- [ ] ทดสอบ RLS: cross-tenant → 404

---

**ต้องการให้ผม:**
1. **แยกไฟล์ generator ให้สมบูรณ์** (ตัดเฉพาะ 9 ตารางที่เหลือใน Alembic V2)?
2. **เขียน DI wiring module** (`app/modules/yolo/wiring.py`) เพื่อลด manual work?
3. **เพิ่ม integration tests** สำหรับ extension ทั้ง 7?
4. **อธิบาย use case ตัวอย่าง** (เช่น shelf counting flow ทีละขั้น)?

 