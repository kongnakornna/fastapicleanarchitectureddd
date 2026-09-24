"""DeviceStatusHistory entity"""
from __future__ import annotations
import uuid
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceStatusHistory(BaseModelNoPK):
    __tablename__ = "sd_device_status_history"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_iot_device.device_id"), index=True)
    status: Mapped[str | None] = mapped_column(String(50), name="status", nullable=True)
    value: Mapped[float | None] = mapped_column(Numeric(10, 2), name="value", nullable=True)
    notification_type_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("sd_notification_type.id"), nullable=True, index=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, name="duration_minutes", nullable=True)
    previous_status: Mapped[str | None] = mapped_column(String(50), name="previous_status", nullable=True)
    previous_value: Mapped[float | None] = mapped_column(Numeric(10, 2), name="previous_value", nullable=True)
    change_reason: Mapped[str | None] = mapped_column(Text, name="change_reason", nullable=True)
