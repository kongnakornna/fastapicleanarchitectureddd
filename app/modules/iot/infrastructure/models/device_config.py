"""DeviceConfig entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceConfig(BaseModelNoPK):
    __tablename__ = "device_config"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(50), name="deviceId", unique=True)
    config: Mapped[dict | None] = mapped_column(JSONB, name="config", nullable=True)
    status: Mapped[str] = mapped_column(String(20), name="status", default="active")
    notes: Mapped[str | None] = mapped_column(Text, name="notes", nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(100), name="updatedBy", nullable=True)
    last_applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="lastAppliedAt", nullable=True)
