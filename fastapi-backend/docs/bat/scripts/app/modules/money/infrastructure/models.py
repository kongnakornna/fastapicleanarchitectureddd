"""Money infrastructure models — SQLAlchemy 2.0"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative — ฐานของ model ทั้งหมด"""


class MoneyModel(Base):
    """MoneyModel — โมเดลฐานข้อมูล"""

    __tablename__ = "moneys"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_money_code"),
        CheckConstraint("amount >= 0", name="ck_money_amount"),
        CheckConstraint(
            "status IN ('ACTIVE','INACTIVE','ARCHIVED')",
            name="ck_money_status",
        ),
        {"schema": "tenant_mon"},
    )

    id:         Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id:  Mapped[uuid.UUID]       = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    code:       Mapped[str]             = mapped_column(String(50), nullable=False)
    name:       Mapped[str]             = mapped_column(String(200), nullable=False)
    status:     Mapped[str]             = mapped_column(String(20), nullable=False, default="ACTIVE")
    amount:     Mapped[float]           = mapped_column(Numeric(15, 2), nullable=False, default=0)
    metadata_:  Mapped[dict]            = mapped_column("metadata", JSONB, nullable=False, default=dict)
    version:    Mapped[int]             = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime]        = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)