"""NotificationType entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class NotificationType(BaseModelNoPK):
    __tablename__ = "sd_notification_type"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), name="name")
    description: Mapped[str | None] = mapped_column(Text, name="description", nullable=True)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, name="cooldown_minutes", default=10)
    is_active: Mapped[bool] = mapped_column(Boolean, name="is_active", default=True)
    icon: Mapped[str | None] = mapped_column(String(100), name="icon", nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), name="color", nullable=True)
