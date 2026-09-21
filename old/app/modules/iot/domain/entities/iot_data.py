from __future__ import annotations

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class IoTData(BaseModel):
    """IoT data record - translated from Go: internal/modules/iot/models/iot_data.go"""

    __tablename__ = "iot_data"

    device_id: Mapped[int] = mapped_column(
        Integer, name="device_id", comment="Device ID"
    )
    data_json: Mapped[str] = mapped_column(
        Text, name="data_json", default="{}", comment="Data payload JSON"
    )
    timestamp: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), name="timestamp", nullable=True, comment="Data timestamp"
    )
    location_id: Mapped[int] = mapped_column(
        Integer, name="location_id", default=0, comment="Location ID"
    )
    metadata_json: Mapped[str] = mapped_column(
        Text, name="metadata_json", default="{}", comment="Metadata JSON"
    )
