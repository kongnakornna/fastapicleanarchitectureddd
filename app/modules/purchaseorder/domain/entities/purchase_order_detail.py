from __future__ import annotations

from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class PurchaseOrderDetail(BaseModel):
    __tablename__ = "m_purchase_order_detail"

    po_header_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True), name="po_header_id", comment="Purchase order header ID"
    )
    part_id: Mapped[UUID | None] = mapped_column(
        SQUID(as_uuid=True), name="part_id", nullable=True, comment="Part ID"
    )
    quantity_ordered: Mapped[int] = mapped_column(
        Integer, name="quantity_ordered", default=0, comment="Quantity ordered"
    )
    quantity_received: Mapped[int] = mapped_column(
        Integer, name="quantity_received", default=0, comment="Quantity received"
    )
    unit_price: Mapped[float] = mapped_column(
        Float, name="unit_price", default=0, comment="Unit price"
    )
    total_price: Mapped[float] = mapped_column(
        Float, name="total_price", default=0, comment="Total price"
    )
    discount: Mapped[float] = mapped_column(
        Float, name="discount", default=0, comment="Discount amount"
    )
    net_price: Mapped[float] = mapped_column(
        Float, name="net_price", default=0, comment="Net price after discount"
    )
    note: Mapped[str | None] = mapped_column(
        Text, name="note", nullable=True, comment="Note"
    )
