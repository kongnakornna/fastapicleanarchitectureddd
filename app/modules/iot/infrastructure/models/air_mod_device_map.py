"""AirModDeviceMap — UUID PK"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class AirModDeviceMap(BaseModel):
    __tablename__ = "sd_air_mod_device_map"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    air_mod_id: Mapped[int | None] = mapped_column(Integer, name="air_mod_id", nullable=True)
    air_control_id: Mapped[int | None] = mapped_column(Integer, name="air_control_id", nullable=True)
    device_id: Mapped[int | None] = mapped_column(Integer, name="device_id", nullable=True)
