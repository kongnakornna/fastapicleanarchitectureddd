from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class PaymentHistory(BaseModel):
    __tablename__ = "m_payment_history"

    payment_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True), name="payment_id", comment="Payment ID"
    )
    from_status: Mapped[str] = mapped_column(
        String(20), name="from_status", comment="Previous status"
    )
    to_status: Mapped[str] = mapped_column(
        String(20), name="to_status", comment="New status"
    )
    changed_by: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="changed_by", nullable=True, comment="Changed by user ID"
    )
    changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), name="changed_at", nullable=True, comment="Changed at"
    )
    reason: Mapped[str | None] = mapped_column(
        Text, name="reason", nullable=True, comment="Reason"
    )
