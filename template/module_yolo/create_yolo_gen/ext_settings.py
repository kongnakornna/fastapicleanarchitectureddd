"""Extension #1: Settings generator"""
from __future__ import annotations
from .base import FileWriter, Paths, info, dedent_code


def generate(writer: FileWriter, paths: Paths) -> None:
    info("[SETTINGS] generating...")
    base = f"{paths.mod_root}/domain/settings"

    writer.write(f"{base}/__init__.py", dedent_code('''
        """YOLO settings domain"""
        from .entities import PlatformSettings, SettingsPatch
        __all__ = ["PlatformSettings", "SettingsPatch"]
    '''))

    writer.write(f"{base}/entities.py", dedent_code('''
        """Settings entities"""
        from __future__ import annotations
        import uuid
        from dataclasses import dataclass, field
        from datetime import UTC, datetime
        from typing import Any


        @dataclass(slots=True)
        class PlatformSettings:
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
                for name in (
                    "default_model", "device", "conf_threshold",
                    "iou_threshold", "max_batch_size", "timeout_seconds",
                    "cache_ttl", "artifact_bucket", "enable_tensorrt",
                    "enable_half", "max_trainings", "retention_days",
                ):
                    val = getattr(self, name)
                    if val is not None:
                        setattr(settings, name, val)
                if self.extra_json is not None:
                    settings.extra_json.update(self.extra_json)
                settings.updated_at = datetime.now(UTC)
                return settings
    '''))

    # Application
    app = f"{paths.mod_root}/application"
    writer.write(f"{app}/settings_use_case.py", dedent_code('''
        """Settings use case"""
        from __future__ import annotations
        from typing import Any
        import structlog
        from app.modules.yolo.domain.settings import PlatformSettings, SettingsPatch

        log = structlog.get_logger()


        class SettingsUseCase:
            def __init__(self, repo: Any) -> None:
                self._repo = repo

            async def get_settings(self, ctx: Any) -> dict[str, Any]:
                row = await self._repo.find_by_tenant(ctx, ctx.tenant_id)
                if row is None:
                    row = await self._repo.create_default(ctx, ctx.tenant_id)
                return self._to_dict(row)

            async def update_settings(self, ctx: Any,
                                       patch: SettingsPatch) -> dict[str, Any]:
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
                await self._repo.delete_by_tenant(ctx, ctx.tenant_id)
                row = await self._repo.create_default(ctx, ctx.tenant_id)
                return self._to_dict(row)

            async def validate_settings(self, ctx: Any,
                                         patch: SettingsPatch) -> dict[str, Any]:
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
            def _to_dict(s: Any) -> dict[str, Any]:
                return {
                    "default_model": s.default_model,
                    "device": s.device,
                    "conf_threshold": float(s.conf_threshold),
                    "iou_threshold": float(s.iou_threshold),
                    "max_batch_size": s.max_batch_size,
                    "timeout_seconds": s.timeout_seconds,
                    "cache_ttl": s.cache_ttl,
                    "artifact_bucket": s.artifact_bucket,
                    "enable_tensorrt": s.enable_tensorrt,
                    "enable_half": s.enable_half,
                    "max_trainings": s.max_trainings,
                    "retention_days": s.retention_days,
                    "extra": dict(s.extra_json or {}),
                }
    '''))

    # Infrastructure
    infra = f"{paths.mod_root}/infrastructure"
    writer.write(f"{infra}/models_settings.py", dedent_code('''
        """Settings SQLAlchemy model"""
        from __future__ import annotations
        import uuid
        from datetime import datetime
        from sqlalchemy import (
            Boolean, DateTime, Integer, Numeric, String,
            UniqueConstraint, func, text,
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
    '''))

    writer.write(f"{infra}/settings_repository.py", dedent_code('''
        """Settings repository"""
        from __future__ import annotations
        import uuid
        from typing import Any
        from loguru import logger
        from sqlalchemy import delete, select
        from sqlalchemy.exc import SQLAlchemyError
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.modules.yolo.application.exceptions import ApplicationError
        from app.modules.yolo.infrastructure.models_settings import SettingsModel


        class SettingsRepository:
            def __init__(self, session: AsyncSession) -> None:
                self._session = session

            async def find_by_tenant(self, ctx: Any,
                                      tenant_id: uuid.UUID) -> Any | None:
                try:
                    result = await self._session.execute(
                        select(SettingsModel).where(
                            SettingsModel.tenant_id == tenant_id))
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

            async def delete_by_tenant(self, ctx: Any,
                                        tenant_id: uuid.UUID) -> bool:
                try:
                    await self._session.execute(
                        delete(SettingsModel).where(
                            SettingsModel.tenant_id == tenant_id))
                    await self._session.flush()
                    return True
                except SQLAlchemyError as exc:
                    logger.error(f"settings.delete_by_tenant: {exc}")
                    raise ApplicationError(str(exc)) from exc
    '''))

    # Presentation
    pres = f"{paths.mod_root}/presentation"
    writer.write(f"{pres}/schemas_settings.py", dedent_code('''
        """Settings schemas"""
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
    '''))

    writer.write(f"{pres}/router_settings.py", dedent_code('''
        """Settings router"""
        from __future__ import annotations
        from typing import Annotated
        from fastapi import APIRouter, Depends, HTTPException, status
        from app.modules.yolo.application.settings_use_case import SettingsUseCase
        from app.modules.yolo.domain.settings import SettingsPatch
        from app.modules.yolo.presentation.dependencies import get_ctx
        from app.modules.yolo.presentation.schemas_settings import (
            SettingsPatchRequest, SettingsResponse, SettingsValidateResponse,
        )

        router = APIRouter(prefix="/yolo/settings", tags=["yolo"])


        async def _get_uc() -> SettingsUseCase:  # type: ignore
            raise HTTPException(500, "SettingsUseCase not wired")


        @router.get("", response_model=SettingsResponse,
                     summary="Get YOLO settings",
                     operation_id="yolo_get_settings")
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
                return SettingsResponse(**await uc.update_settings(ctx, patch))
            except ValueError as e:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
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
                      summary="Validate settings",
                      operation_id="yolo_validate_settings")
        async def validate_settings(
            payload: SettingsPatchRequest,
            uc: Annotated[SettingsUseCase, Depends(_get_uc)],
        ) -> SettingsValidateResponse:
            ctx = await get_ctx()
            patch = SettingsPatch(**payload.model_dump())
            return SettingsValidateResponse(
                **await uc.validate_settings(ctx, patch))
    '''))