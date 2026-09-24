"""DeviceStatus entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceStatus(BaseModelNoPK):
    __tablename__ = "device_status"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column("deviceId", String(50), unique=True)
    is_online: Mapped[bool] = mapped_column("isOnline", Boolean, default=True, index=True)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, default=True, index=True)
    last_seen: Mapped[datetime] = mapped_column("lastSeen", DateTime(timezone=True), default=datetime.utcnow, index=True)
    last_data: Mapped[dict | None] = mapped_column("lastData", JSONB, nullable=True)
    battery_level: Mapped[int | None] = mapped_column("batteryLevel", Integer, nullable=True)
    signal_strength: Mapped[int | None] = mapped_column("signalStrength", Integer, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, name="temperature", nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, name="humidity", nullable=True)
    firmware_version: Mapped[str | None] = mapped_column("firmwareVersion", String(20), nullable=True)
    uptime: Mapped[int | None] = mapped_column(Integer, name="uptime", nullable=True)
    location: Mapped[dict | None] = mapped_column(JSONB, name="location", nullable=True)
