"""DeviceGroup entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceGroup(BaseModelNoPK):
    __tablename__ = "sd_device_group"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), name="name")
    description: Mapped[str | None] = mapped_column(Text, name="description", nullable=True)
    group_type: Mapped[str] = mapped_column(String(50), name="group_type", default="custom", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, name="is_active", default=True, index=True)
    config: Mapped[dict | None] = mapped_column(JSONB, name="config", nullable=True)
