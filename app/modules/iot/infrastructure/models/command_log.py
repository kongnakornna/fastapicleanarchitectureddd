"""CommandLog entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class CommandLog(BaseModelNoPK):
    __tablename__ = "command_log"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(String(50), name="device_id", index=True)
    action: Mapped[str] = mapped_column(String(100), name="action")
    parameters: Mapped[dict | None] = mapped_column(JSONB, name="parameters", nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(50), name="status", default="pending")
    issued_by: Mapped[str | None] = mapped_column(String(100), name="issued_by", nullable=True)
    client_ip: Mapped[str | None] = mapped_column(String(45), name="client_ip", nullable=True)
    response: Mapped[dict | None] = mapped_column(JSONB, name="response", nullable=True)
    error: Mapped[str | None] = mapped_column(String(500), name="error", nullable=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="issued_at", default=datetime.utcnow)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="sent_at", nullable=True)
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="executed_at", nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), name="failed_at", nullable=True)
