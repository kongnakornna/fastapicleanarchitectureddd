from __future__ import annotations

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class EmailLog(BaseModel):
    __tablename__ = "m_email_log"

    to_address: Mapped[str] = mapped_column(
        String(500), name="to_address", comment="Recipient email address"
    )
    cc: Mapped[str | None] = mapped_column(
        String(500), name="cc", nullable=True, comment="CC recipients"
    )
    bcc: Mapped[str | None] = mapped_column(
        String(500), name="bcc", nullable=True, comment="BCC recipients"
    )
    subject: Mapped[str] = mapped_column(
        String(500), name="subject", comment="Email subject"
    )
    body: Mapped[str] = mapped_column(
        Text, name="body", comment="Email body"
    )
    status: Mapped[str] = mapped_column(
        String(20), name="status", default="pending", comment="Email status"
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, name="error_message", nullable=True, comment="Error message if failed"
    )
    sent_at: Mapped[None] = mapped_column(
        DateTime(timezone=True), name="sent_at", nullable=True, comment="When email was sent"
    )
