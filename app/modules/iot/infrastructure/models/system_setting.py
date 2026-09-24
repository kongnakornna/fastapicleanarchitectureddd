"""SystemSetting entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class SystemSetting(BaseModelNoPK):
    __tablename__ = "sd_system_setting"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), name="key", unique=True, index=True)
    value: Mapped[dict] = mapped_column(JSONB, name="value")
    category: Mapped[str | None] = mapped_column(String(50), name="category", nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, name="description", nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, name="is_public", default=False)
