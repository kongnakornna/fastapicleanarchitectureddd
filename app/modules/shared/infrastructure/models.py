"""
Shared base models.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

try:
    from app.modules.shared.application.utils import BRASILIA_TZ
except Exception:
    from datetime import timezone, timedelta
    BRASILIA_TZ = timezone(timedelta(hours=-3))


class Base(DeclarativeBase):
    __mapper_args__: ClassVar[dict[str, Any]] = {"eager_defaults": True}


class BaseModel(Base):
    """Base with UUID PK + is_active + timestamps."""
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True), name="id", primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, name="is_active", default=True, server_default="true",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), name="created_at",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), name="updated_at",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(), onupdate=func.now(),
    )


class BaseModelNoPK(Base):
    """Base WITHOUT id — for int/custom PK models."""
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), name="created_at",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), name="updated_at",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(), onupdate=func.now(),
    )


__all__ = ["Base", "BaseModel", "BaseModelNoPK"]
