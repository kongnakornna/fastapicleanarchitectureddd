"""ApiKey entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class ApiKey(BaseModelNoPK):
    __tablename__ = "sd_api_key"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), name="name")
    description: Mapped[str | None] = mapped_column(Text, name="description", nullable=True)
    api_key: Mapped[str] = mapped_column(String(64), name="api_key", unique=True, index=True)
    api_secret: Mapped[str] = mapped_column(String(128), name="api_secret")
    user_id: Mapped[str | None] = mapped_column(String(255), name="user_id", nullable=True, index=True)
    permissions: Mapped[dict | None] = mapped_column(JSONB, name="permissions", nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="expires_at", nullable=True, index=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="last_used_at", nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, name="usage_count", default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, name="is_active", default=True, index=True)
    ip_whitelist: Mapped[dict | None] = mapped_column(JSONB, name="ip_whitelist", nullable=True)
