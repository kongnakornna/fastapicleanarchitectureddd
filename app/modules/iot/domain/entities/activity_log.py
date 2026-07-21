from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class ActivityLog(BaseModel):
    """Activity log - translated from Go: internal/modules/iot/models/activity_log.go"""

    __tablename__ = "iot_activity_log"

    log_type: Mapped[str] = mapped_column(
        String(50), name="log_type", default="", comment="Log type"
    )
    device_id: Mapped[int] = mapped_column(
        Integer, name="device_id", default=0, comment="Device ID"
    )
    user_id: Mapped[int] = mapped_column(
        Integer, name="user_id", default=0, comment="User ID"
    )
    severity: Mapped[str] = mapped_column(
        String(20), name="severity", default="info", comment="Severity level"
    )
    data_json: Mapped[str] = mapped_column(
        Text, name="data_json", default="{}", comment="Data JSON"
    )
    description: Mapped[str] = mapped_column(
        Text, name="description", default="", comment="Description"
    )
