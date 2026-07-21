from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class PurchaseOrderStatusHistory(BaseModel):
    __tablename__ = "m_purchase_order_status_history"

    po_header_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True), name="po_header_id", comment="Purchase order header ID"
    )
    from_status: Mapped[str] = mapped_column(
        String(20), name="from_status", comment="Previous status"
    )
    to_status: Mapped[str] = mapped_column(
        String(20), name="to_status", comment="New status"
    )
    changed_by: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="changed_by", nullable=True, comment="User who changed the status"
    )
    changed_at: Mapped[datetime | None] = mapped_column(
        DateTime, name="changed_at", nullable=True, comment="Timestamp of status change"
    )
    reason: Mapped[str | None] = mapped_column(
        Text, name="reason", nullable=True, comment="Reason for status change"
    )
