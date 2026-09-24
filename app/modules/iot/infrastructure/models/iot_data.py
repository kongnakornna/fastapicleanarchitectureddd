"""IotData entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class IotData(BaseModelNoPK):
    __tablename__ = "iot_data"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column("deviceId", String(50), index=True)
    data: Mapped[dict] = mapped_column(JSONB, name="data")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="timestamp", server_default=func.current_timestamp(), index=True)
    location: Mapped[dict | None] = mapped_column(JSONB, name="location", nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    data_type: Mapped[str | None] = mapped_column("dataType", String(20), nullable=True)
    data_quality: Mapped[float | None] = mapped_column("dataQuality", Float, nullable=True)
