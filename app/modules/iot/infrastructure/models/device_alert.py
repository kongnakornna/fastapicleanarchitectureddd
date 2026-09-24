"""DeviceAlert entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceAlert(BaseModelNoPK):
    __tablename__ = "device_alert"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(50), name="device_id", index=True)
    type: Mapped[str] = mapped_column(String(50), name="type", index=True)
    metric: Mapped[str | None] = mapped_column(String(100), name="metric", nullable=True)
    value: Mapped[float | None] = mapped_column(Float, name="value", nullable=True)
    threshold: Mapped[dict | None] = mapped_column(JSONB, name="threshold", nullable=True)
    severity: Mapped[str] = mapped_column(String(20), name="severity", default="low")
    message: Mapped[str] = mapped_column(String(500), name="message", default="")
    details: Mapped[dict | None] = mapped_column(JSONB, name="details", nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, name="resolved", default=False)
    resolution_notes: Mapped[str | None] = mapped_column(Text, name="resolution_notes", nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(100), name="resolved_by", nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="resolved_at", nullable=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, name="acknowledged", default=False)
    acknowledged_by: Mapped[str | None] = mapped_column(String(100), name="acknowledged_by", nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="acknowledged_at", nullable=True)
    escalation: Mapped[dict | None] = mapped_column(JSONB, name="escalation", nullable=True)
    data_id: Mapped[int | None] = mapped_column(Integer, name="data_id", nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="expires_at", nullable=True)
    notification_count: Mapped[int] = mapped_column(Integer, name="notification_count", default=0)
