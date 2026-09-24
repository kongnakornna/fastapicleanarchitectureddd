"""AirControlDeviceMap — UUID PK"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class AirControlDeviceMap(BaseModel):
    __tablename__ = "sd_air_control_device_map"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    air_control_id: Mapped[int | None] = mapped_column(Integer, name="air_control_id", nullable=True)
    device_id: Mapped[int | None] = mapped_column(Integer, name="device_id", nullable=True)
