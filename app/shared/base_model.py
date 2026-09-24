"""app.shared.base_model — SQLAlchemy 2.0 declarative base + mixins ที่ทุก module ใช้ร่วม

TH: Base + mixins สำหรับ SQLAlchemy 2.0 (Mapped/mapped_column)
    ใช้ Base ตัวเดียวร่วมทุก module เพื่อให้ Alembic เห็น metadata ครบ
EN: SQLAlchemy 2.0 declarative base + mixins
    Single Base across all modules → Alembic sees full metadata

Design:
  • SQLAlchemy 2.0 style (DeclarativeBase + Mapped + mapped_column)
  • UUID v7 primary key (time-ordered, index-friendly)
  • Mixins: UUIDPk, Timestamp, Version, Tenant, SoftDelete, Audit
  • Single Base for Alembic autogenerate
  • SCHEMA constant = "public"
  • to_dict() / __repr__() helper
  • Column name convention (ix_/uq_/ck_/fk_/pk_)
  • RLS-friendly (tenant_id indexed)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, ClassVar

from sqlalchemy import (
    DateTime, Integer, MetaData, String, func, text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, declared_attr, mapped_column,
)

from app.shared.uuid7 import uuid7_default


# ═══════════════════════════════════════════════════════════════
#  Schema + naming convention
# ═══════════════════════════════════════════════════════════════
SCHEMA = "public"

NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


# ═══════════════════════════════════════════════════════════════
#  Root Base — shared across all modules
# ═══════════════════════════════════════════════════════════════
class Base(DeclarativeBase):
    """TH: Root declarative base — import อันนี้เท่านั้น
    | EN: Root declarative base — import this one

    Usage:
        from app.shared.base_model import Base

        class UserModel(Base):
            __tablename__ = "users"
            ...

    Notes:
        - ใช้ Base เดียวกันทุก module → Alembic เห็น metadata ครบ
        - SCHEMA ถูก set ผ่าน `__table_args__` ของ mixins
    """

    metadata = MetaData(
        schema=SCHEMA,
        naming_convention=NAMING_CONVENTION,
    )

    # ─── Helper methods ─────────────────────────────────────

    def to_dict(self, *, exclude: tuple[str, ...] = ()) -> dict[str, Any]:
        """TH: แปลง instance เป็น dict | EN: instance → dict"""
        out: dict[str, Any] = {}
        for col in self.__table__.columns:
            if col.name in exclude:
                continue
            value = getattr(self, col.name, None)
            if isinstance(value, uuid.UUID):
                out[col.name] = str(value)
            elif isinstance(value, datetime):
                out[col.name] = value.isoformat()
            else:
                out[col.name] = value
        return out

    def apply_dict(self, data: dict[str, Any]) -> "Base":
        """TH: apply dict ให้ instance (ข้าม key ที่ไม่รู้จัก)
        | EN: apply dict to instance (skip unknown keys)"""
        valid_cols = {c.name for c in self.__table__.columns}
        for key, value in data.items():
            if key in valid_cols:
                setattr(self, key, value)
        return self

    def __repr__(self) -> str:
        pk = getattr(self, "id", None)
        tenant = getattr(self, "tenant_id", None)
        if tenant is not None:
            return f"<{type(self).__name__} id={pk} tenant={tenant}>"
        return f"<{type(self).__name__} id={pk}>"


# ═══════════════════════════════════════════════════════════════
#  Mixins
# ═══════════════════════════════════════════════════════════════

class UUIDPkMixin:
    """TH: primary key แบบ UUID v7 + DB fallback
    | EN: UUID v7 primary key + DB fallback"""

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid7_default,
        server_default=text("gen_random_uuid()"),
        comment="UUID v7 (time-ordered) primary key",
    )


class TimestampMixin:
    """TH: created_at / updated_at (auto)
    | EN: created_at / updated_at (auto)"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
        comment="สร้างเมื่อ (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="อัปเดตล่าสุด (UTC)",
    )


class VersionMixin:
    """TH: optimistic locking version counter
    | EN: optimistic locking version"""

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
        comment="optimistic locking version",
    )

    def bump_version(self) -> None:
        self.version = (self.version or 0) + 1


class TenantMixin:
    """TH: tenant_id (multi-tenant / RLS)
    | EN: tenant_id for multi-tenant RLS"""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="tenant UUID (RLS key)",
    )


class SoftDeleteMixin:
    """TH: soft delete + timestamp | EN: soft delete support"""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
        comment="ถูกลบเมื่อ (NULL = ไม่ถูกลบ)",
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        self.deleted_at = None


class AuditMixin:
    """TH: audit ว่าใครสร้าง/แก้ | EN: who created/updated"""

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="ผู้สร้าง (user_id)",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="ผู้แก้ล่าสุด (user_id)",
    )


class FullMixin(
    UUIDPkMixin, TenantMixin, TimestampMixin, VersionMixin,
):
    """TH: รวม pk + tenant + timestamps + version (ใช้บ่อยสุด)
    | EN: pk + tenant + timestamps + version (most common)"""
    pass


# ═══════════════════════════════════════════════════════════════
#  Schema helper for __table_args__
# ═══════════════════════════════════════════════════════════════
def schema_args(
    *constraints: Any,
    schema: str = SCHEMA,
    **kwargs: Any,
) -> tuple:
    """TH: สร้าง __table_args__ ที่มี schema ถูกต้อง
    | EN: build __table_args__ with schema

    Usage:
        class UserModel(Base):
            __tablename__ = "users"
            __table_args__ = schema_args(
                UniqueConstraint("tenant_id", "email"),
                Index("ix_users_tenant", "tenant_id"),
            )
    """
    return (*constraints, {"schema": schema, **kwargs})


# ═══════════════════════════════════════════════════════════════
#  Legacy compatibility (SQLAlchemy 1.x Column style)
# ═══════════════════════════════════════════════════════════════
class LegacyTenantMixin:
    """TH: mixin แบบ 1.x (Column) สำหรับของเก่า
    | EN: legacy 1.x style mixin (Column)

    หมายเหตุ: แนะนำให้ migrate ไปใช้ TenantMixin (Mapped) แทน
    """

    from sqlalchemy import Column as _C  # local import

    @declared_attr
    def tenant_id(cls) -> Any:  # noqa: N805
        return cls._C(  # type: ignore[attr-defined]
            PGUUID(as_uuid=True), nullable=False, index=True,
        )

    @declared_attr
    def version(cls) -> Any:  # noqa: N805
        return cls._C(Integer, nullable=False, default=1)  # type: ignore[attr-defined]

    @declared_attr
    def created_at(cls) -> Any:  # noqa: N805
        return cls._C(  # type: ignore[attr-defined]
            DateTime(timezone=True), server_default=func.now(),
        )

    @declared_attr
    def updated_at(cls) -> Any:  # noqa: N805
        return cls._C(  # type: ignore[attr-defined]
            DateTime(timezone=True),
            server_default=func.now(), onupdate=func.now(),
        )


# ═══════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════
__all__ = [
    # Core
    "Base",
    "SCHEMA",
    "NAMING_CONVENTION",
    # Mixins (2.0 style — recommended)
    "UUIDPkMixin",
    "TimestampMixin",
    "VersionMixin",
    "TenantMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    "FullMixin",
    # Helpers
    "schema_args",
    # Legacy
    "LegacyTenantMixin",
]