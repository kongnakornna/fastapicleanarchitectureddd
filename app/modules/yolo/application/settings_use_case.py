"""Settings use case"""
from __future__ import annotations
import uuid
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

    async def update_settings(self, ctx: Any, patch: SettingsPatch) -> dict[str, Any]:
        row = await self._repo.find_by_tenant(ctx, ctx.tenant_id)
        if row is None:
            row = await self._repo.create_default(ctx, ctx.tenant_id)
        updated = patch.apply_to(row)
        errors = updated.validate()
        if errors:
            raise ValueError("; ".join(errors))
        saved = await self._repo.update(ctx, updated)
        return self._to_dict(saved)

    async def reset_to_defaults(self, ctx: Any) -> dict[str, Any]:
        await self._repo.delete_by_tenant(ctx, ctx.tenant_id)
        row = await self._repo.create_default(ctx, ctx.tenant_id)
        return self._to_dict(row)

    async def validate_settings(self, ctx: Any, patch: SettingsPatch) -> dict[str, Any]:
        current = await self._repo.find_by_tenant(ctx, ctx.tenant_id)
        if current is None:
            current = PlatformSettings(tenant_id=ctx.tenant_id)
        test = patch.apply_to(current)
        errors = test.validate()
        return {"valid": not errors, "errors": errors,
                "preview": self._to_dict(test)}

    @staticmethod
    def _to_dict(s: Any) -> dict[str, Any]:
        return {"default_model": s.default_model, "device": s.device,
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
                "extra": dict(s.extra_json or {})}
