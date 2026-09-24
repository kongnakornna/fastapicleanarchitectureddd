"""AuditLog entity"""
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class AuditLog(BaseModelNoPK):
    __tablename__ = "sd_audit_log"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    audit_id: Mapped[int] = mapped_column(Integer, name="audit_id", primary_key=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(String, name="user_id", nullable=True, index=True)
    user_name: Mapped[str | None] = mapped_column(String(200), name="user_name", nullable=True)
    action: Mapped[str] = mapped_column(String(50), name="action", index=True)
    entity_type: Mapped[str] = mapped_column(String(100), name="entity_type", index=True)
    entity_id: Mapped[int] = mapped_column(Integer, name="entity_id", index=True)
    before: Mapped[dict | None] = mapped_column(JSONB, name="before", nullable=True)
    after: Mapped[dict | None] = mapped_column(JSONB, name="after", nullable=True)
    changes: Mapped[dict | None] = mapped_column(JSONB, name="changes", nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), name="ip_address", nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, name="user_agent", nullable=True)
    action_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), name="action_time", server_default=func.current_timestamp(), index=True)
    description: Mapped[str | None] = mapped_column(Text, name="description", nullable=True)
