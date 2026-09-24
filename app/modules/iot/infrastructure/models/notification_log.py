"""NotificationLog entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.shared.infrastructure.models import BaseModelNoPK


class NotificationLog(BaseModelNoPK):
    __tablename__ = "sd_notification_log"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("sd_iot_device.device_id"), nullable=True, index=True)
    notification_type_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("sd_notification_type.id"), nullable=True, index=True)
    notification_channel_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("sd_notification_channel.id"), nullable=True, index=True)
    template_id: Mapped[int | None] = mapped_column(Integer, name="template_id", nullable=True)
    message: Mapped[str] = mapped_column(Text, name="message", default="")
    status: Mapped[str] = mapped_column(String(20), name="status", default="pending", index=True)
    response_data: Mapped[dict | None] = mapped_column(JSONB, name="response_data", nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="sent_at", nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="delivered_at", nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="read_at", nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, name="retry_count", default=0)
    error_message: Mapped[str | None] = mapped_column(Text, name="error_message", nullable=True)
    message_id: Mapped[str | None] = mapped_column(String(100), name="message_id", nullable=True)
    recipient: Mapped[str | None] = mapped_column(String(255), name="recipient", nullable=True)

    device: Mapped["Device"] = relationship("Device", lazy="selectin")
    notification_type: Mapped["NotificationType"] = relationship("NotificationType", lazy="selectin")
    channel: Mapped["NotificationChannel"] = relationship("NotificationChannel", lazy="selectin")
