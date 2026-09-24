"""DeviceNotificationConfig entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceNotificationConfig(BaseModelNoPK):
    __tablename__ = "sd_device_notification_config"
    __table_args__ = (
        UniqueConstraint("device_id", "notification_channel_id", "notification_type_id", name="unique_Device_channel_type"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_iot_device.device_id"), index=True)
    notification_channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_notification_channel.id"), index=True)
    notification_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_notification_type.id"), index=True)
    config: Mapped[dict | None] = mapped_column(JSONB, name="config", nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, name="is_active", default=True, index=True)
    retry_count: Mapped[int] = mapped_column(Integer, name="retry_count", default=3)
    retry_delay_minutes: Mapped[int] = mapped_column(Integer, name="retry_delay_minutes", default=5)

    device: Mapped["Device"] = relationship("Device", lazy="selectin")
    channel: Mapped["NotificationChannel"] = relationship("NotificationChannel", lazy="selectin")
    notification_type: Mapped["NotificationType"] = relationship("NotificationType", lazy="selectin")
