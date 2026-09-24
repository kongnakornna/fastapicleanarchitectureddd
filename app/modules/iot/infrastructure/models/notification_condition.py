"""NotificationCondition entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import BaseModelNoPK


class NotificationCondition(BaseModelNoPK):
    __tablename__ = "sd_notification_condition"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_iot_device.device_id"), index=True)
    notification_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_notification_type.id"), index=True)
    min_value: Mapped[float | None] = mapped_column(Numeric(10, 2), name="min_value", nullable=True)
    max_value: Mapped[float | None] = mapped_column(Numeric(10, 2), name="max_value", nullable=True)
    condition_operator: Mapped[str] = mapped_column(String(10), name="condition_operator", default="between")
    priority: Mapped[int] = mapped_column(Integer, name="priority", default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, name="is_active", default=True, index=True)

    device: Mapped["Device"] = relationship("Device", lazy="selectin")
    notification_type: Mapped["NotificationType"] = relationship("NotificationType", lazy="selectin")
