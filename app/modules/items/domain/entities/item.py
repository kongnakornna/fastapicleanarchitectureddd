from __future__ import annotations

from sqlalchemy import UUID as SQUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.shared.infrastructure.models import BaseModel


class Item(BaseModel):
    __tablename__ = "item"

    title: Mapped[str] = mapped_column(
        String(100), name="title", comment="Item title"
    )
    description: Mapped[str] = mapped_column(
        String(200), name="description", comment="Item description"
    )
    owner_id: Mapped[str] = mapped_column(
        SQUID(as_uuid=True), name="owner_id", comment="Owner user ID"
    )
