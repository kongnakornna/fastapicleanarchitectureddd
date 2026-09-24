"""DeviceType entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class DeviceType(BaseModelNoPK):
    __tablename__ = "sd_iot_device_type"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    type_id: Mapped[int] = mapped_column(Integer, name="type_id", primary_key=True, autoincrement=True)
    type_name: Mapped[str] = mapped_column(String(255), name="type_name", default="")
    status: Mapped[int] = mapped_column(Integer, name="status", default=1)
