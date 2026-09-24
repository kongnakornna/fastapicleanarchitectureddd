"""Location entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class Location(BaseModelNoPK):
    __tablename__ = "sd_iot_location"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(Integer, name="location_id", primary_key=True, autoincrement=True)
    location_name: Mapped[str] = mapped_column(String(255), name="location_name", default="")
    ipaddress: Mapped[str] = mapped_column(String(255), name="ipaddress", default="")
    location_detail: Mapped[str] = mapped_column(Text, name="location_detail", default="")
    configdata: Mapped[str] = mapped_column(Text, name="configdata", default="")
    status: Mapped[int] = mapped_column(Integer, name="status", default=1)
