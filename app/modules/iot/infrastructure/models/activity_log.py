"""ActivityLog entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class ActivityLog(BaseModelNoPK):
    __tablename__ = "activity_log"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(50), name="type", default="")
    device_id: Mapped[str | None] = mapped_column(String(50), name="device_id", nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(100), name="user_id", nullable=True)
    details: Mapped[str] = mapped_column(String(500), name="details", default="")
    data: Mapped[dict | None] = mapped_column(JSONB, name="data", nullable=True)
    severity: Mapped[str] = mapped_column(String(20), name="severity", default="info")
    ip_address: Mapped[str | None] = mapped_column(String(45), name="ip_address", nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), name="user_agent", nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), name="session_id", nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(100), name="correlation_id", nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="timestamp", default=datetime.utcnow)
    stack_trace: Mapped[str | None] = mapped_column(Text, name="stack_trace", nullable=True)
