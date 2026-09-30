"""user SQLAlchemy models — schema=public, prefix=erp_, id=BIGINT"""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Identity,
    Index,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.enums import Role
from app.modules.shared.infrastructure.models import BaseModel
from app.modules.user.domain.enums import (
    Gender,
    OnlineStatus,
    UserStatus,
)

if TYPE_CHECKING:
    from app.modules.authentication.infrastructure.models import (
        AuthenticationModel,
    )


class UserModel(BaseModel):
    """TH: erp_users (mapped from sd_user) | EN: erp_users"""

    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_users"
    __table_args__ = (
        Index("ix_users_email_is_active", "email", "is_active"),
        Index("ix_users_username", "username"),
        Index("ix_users_status", "status"),
    )

    # ─── PK: BIGINT auto-increment (11+ หลัก) ─
    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=False, start=10_000_000_000, increment=1),
        primary_key=True,
        comment="Auto-increment 11+ digit identifier",
    )

    # ─── Identity (SQL: sd_user.*) ────────────
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    preferred_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)

    username: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True,
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True,
    )
    phone: Mapped[str | None] = mapped_column(String(18), nullable=True)
    mobile_number: Mapped[str | None] = mapped_column(String(18), nullable=True)
    line_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    id_card: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ─── Profile ──────────────────────────────
    gender: Mapped[Gender | None] = mapped_column(
        SQLEnum(Gender, name="gender_enum"), nullable=True,
    )
    birthdate: Mapped[date | None] = mapped_column(Date, nullable=True)
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Auth (SQL: password, password_temp) ──
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    temporary_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ─── Status ───────────────────────────────
    # FIX: server_default must match the enum LABEL (uppercase), not the
    #      .value (lowercase). SQLAlchemy Enum emits the member *name* as
    #      the Postgres label, so 'user'/'1'/'0' fail at DDL time with
    #      InvalidTextRepresentation. Use .name to compute the label.
    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="role_enum"),
        nullable=False,
        default=Role.USER,
        server_default=Role.USER.name,
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, name="user_status_enum"),
        nullable=False,
        default=UserStatus.ACTIVE,
        server_default=UserStatus.ACTIVE.name,
    )
    online_status: Mapped[OnlineStatus] = mapped_column(
        SQLEnum(OnlineStatus, name="online_status_enum"),
        nullable=False,
        default=OnlineStatus.OFFLINE,
        server_default=OnlineStatus.OFFLINE.name,
    )
    active_status: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True,
    )

    # ─── Legacy grouping (SQL: int8) ──────────
    network_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=1)
    network_type_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=0)
    type_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, default=0)
    system_id: Mapped[str | None] = mapped_column(String(50), nullable=True, default="1")
    location_id: Mapped[str | None] = mapped_column(String(50), nullable=True, default="1")

    # ─── Soft delete (SQL: deletedate) ────────
    deleted_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ─── Security ─────────────────────────────
    is_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false",
    )
    verification_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    password_reset_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    password_reset_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    login_failed_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0",
    )
    last_sign_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
        default=lambda: datetime.now(BRASILIA_TZ),
    )

    # ─── Preferences (int2 in SQL) ────────────
    public_notification: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0",
    )
    sms_notification: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0",
    )
    email_notification: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0",
    )
    line_notification: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0",
    )
    public_status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0",
    )
    information_agreement_status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default="0",
    )

    # ─── Relationship ─────────────────────────
    authentications: Mapped[list["AuthenticationModel"]] = relationship(
        "AuthenticationModel", back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True, lazy="noload",
    )
