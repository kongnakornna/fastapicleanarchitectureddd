"""ChannelTemplate entity"""
from __future__ import annotations
import uuid
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModelNoPK


class ChannelTemplate(BaseModelNoPK):
    __tablename__ = "sd_channel_template"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), name="tenant_id", nullable=False, index=True)
    id: Mapped[int] = mapped_column(Integer, name="id", primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), name="name")
    description: Mapped[str | None] = mapped_column(Text, name="description", nullable=True)
    channel_id: Mapped[int] = mapped_column(Integer, name="channel_id", index=True)
    notification_type_id: Mapped[int] = mapped_column(Integer, name="notification_type_id", index=True)
    template: Mapped[str] = mapped_column(Text, name="template")
    variables: Mapped[dict | None] = mapped_column(JSONB, name="variables", nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, name="is_active", default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, name="is_default", default=False)
