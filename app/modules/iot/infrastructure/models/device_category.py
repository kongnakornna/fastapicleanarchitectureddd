"""DeviceCategory entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceCategory(BaseModelNoPK):
    __tablename__ = "sd_device_category"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), name="name")
    description: Mapped[str | None] = mapped_column(Text, name="description", nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), name="icon", nullable=True)
