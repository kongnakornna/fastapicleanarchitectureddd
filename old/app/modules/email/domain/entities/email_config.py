from __future__ import annotations

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class EmailConfig(BaseModel):
    __tablename__ = "m_email_config"

    smtp_host: Mapped[str] = mapped_column(
        String(200), name="smtp_host", comment="SMTP server host"
    )
    smtp_port: Mapped[int] = mapped_column(
        Integer, name="smtp_port", comment="SMTP server port"
    )
    smtp_user: Mapped[str] = mapped_column(
        String(200), name="smtp_user", comment="SMTP username"
    )
    from_email: Mapped[str] = mapped_column(
        String(200), name="from_email", comment="Sender email address"
    )
    from_name: Mapped[str] = mapped_column(
        String(200), name="from_name", comment="Sender display name"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, name="is_active", default=True, comment="Whether config is active"
    )
