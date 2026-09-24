"""GroupNotificationConfig entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import BaseModelNoPK


class GroupNotificationConfig(BaseModelNoPK):
    __tablename__ = "sd_group_notification_config"
    __table_args__ = (
        UniqueConstraint("group_id", "notification_channel_id", "notification_type_id", name="unique_group_channel_type"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_device_group.id"), index=True)
    notification_channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_notification_channel.id"), index=True)
    notification_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("sd_notification_type.id"), index=True)
    config: Mapped[dict | None] = mapped_column(JSONB, name="config", nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, name="is_active", default=True)
    escalation_level: Mapped[int] = mapped_column(Integer, name="escalation_level", default=1)
    escalation_delay_minutes: Mapped[int] = mapped_column(Integer, name="escalation_delay_minutes", default=30)

    group: Mapped["DeviceGroup"] = relationship("DeviceGroup", lazy="selectin")
    notification_channel: Mapped["NotificationChannel"] = relationship("NotificationChannel", lazy="selectin")
    notification_type: Mapped["NotificationType"] = relationship("NotificationType", lazy="selectin")
