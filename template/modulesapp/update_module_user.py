#!/usr/bin/env python3
"""
update_module_user.py — User Module Updater v1.1.0

อัปเดต user module ตาม SQL จริง (sd_user.sql + sd_user_role.sql):
  • User.id : UUID → BIGINT (11+ หลัก, auto-increment)
  • เพิ่มฟิลด์ใหม่จาก sd_user (username NOT NULL, nickname,
    id_card, network_id, online_status, active_status,
    preferences, security flags)
  • Enum ใหม่: UserStatus, OnlineStatus, LegacyRoleId (+.to_role())
  • Value Objects ใหม่: UserSecurity, UserPreferences
  • Name VO: full_name + nickname + preferred_name (fallback chain)
  • Authentication FK: user_id BIGINT
  • JWT sub: UUID → str (RFC 7519)
  • Migrate data จาก sd_user → erp_users

Actions (12):
  1.  update-domain          — domain/entities, enums, value_objects
  2.  update-infrastructure  — infrastructure/models (BigInteger ID)
  3.  update-application     — application/mappers, use_cases, exceptions
  4.  update-presentation    — presentation/schemas
  5.  update-auth-fk         — authentication/models (user_id BIGINT)
  6.  update-auth-mappers    — authentication/mappers (int(sub))
  7.  update-auth-vo         — authentication/value_objects (sub: str)
  8.  update-cache-mappers   — authentication/cache mappers
  9.  sql                    — V010__alter_users_bigint_id.sql (migrate sd_user)
 10.  sql-auth-fk            — V011__alter_auth_fk_bigint.sql
 11.  verify                 — ตรวจสอบ
 12.  all                    — ทำทุกอย่าง

Usage:
    python update_module_user.py all user --force
    python update_module_user.py update-domain --force
    python update_module_user.py verify
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

VERSION = "1.1.0"


class C:
    CYAN = "\033[96m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    RED = "\033[91m"; GRAY = "\033[90m"; RESET = "\033[0m"


def info(msg: str) -> None: print(f"{C.CYAN}{msg}{C.RESET}")
def ok(msg: str) -> None: print(f"  {C.GREEN}[OK]{C.RESET} {msg}")
def warn(msg: str) -> None: print(f"  {C.YELLOW}[!!]{C.RESET} {msg}")
def err(msg: str) -> None: print(f"  {C.RED}[XX]{C.RESET} {msg}")
def skip(msg: str) -> None: print(f"  {C.GRAY}[--]{C.RESET} {msg}")


# ═══════════════════════════════════════════════════════════════
#  FILE WRITER
# ═══════════════════════════════════════════════════════════════
class FileWriter:
    def __init__(self, root: Path, force: bool = False, backup: bool = True):
        self.root = root
        self.force = force
        self.backup = backup
        self.written: list[Path] = []
        self.skipped: list[Path] = []
        self.backups: list[Path] = []

    def write(self, rel_path: str, content: str, force: bool = True) -> None:
        path = self.root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not (self.force or force):
            skip(f"skip: {rel_path}")
            self.skipped.append(path)
            return

        if path.exists() and self.backup:
            bak = path.with_suffix(path.suffix + ".bak")
            bak.write_bytes(path.read_bytes())
            self.backups.append(bak)
            ok(f"backup: {rel_path}.bak")

        if rel_path.endswith(".py"):
            try:
                compile(content, rel_path, "exec")
            except SyntaxError as exc:
                err(f"SYNTAX ERROR in {rel_path}: {exc}")
                err(f"  line {exc.lineno}: {exc.text}")
                raise RuntimeError(f"Refuse to write invalid Python: {rel_path}") from exc

        path.write_text(content, encoding="utf-8", newline="\n")
        ok(rel_path)
        self.written.append(path)


# ═══════════════════════════════════════════════════════════════
#  UPDATER
# ═══════════════════════════════════════════════════════════════
class UserModuleUpdater:
    def __init__(self, project_root: Path, module: str = "user", force: bool = False):
        self.root = project_root
        self.module = module.lower()
        self.writer = FileWriter(project_root, force=force)
        self.mod_root = f"app/modules/{self.module}"
        self.auth_root = "app/modules/authentication"
        self.sql_dir = "db/migrations"

    # ═══════════════════════════════════════════════════════════
    #  1. DOMAIN
    # ═══════════════════════════════════════════════════════════
    def update_domain(self) -> None:
        info("[UPDATE-DOMAIN] user domain (id: int, new fields, VOs)")
        self._write_enums()
        self._write_value_objects()
        self._write_entities()
        self._write_exceptions()

    def _write_enums(self) -> None:
        self.writer.write(f"{self.mod_root}/domain/enums.py", dedent('''\
            """user enums — Gender, UserStatus, OnlineStatus, LegacyRoleId"""
            from __future__ import annotations

            from enum import Enum

            from app.modules.shared.domain.enums import Role


            class Gender(str, Enum):
                MALE = "male"
                FEMALE = "female"
                NON_BINARY = "non_binary"
                OTHER = "other"


            class UserStatus(int, Enum):
                """TH: สถานะผู้ใช้ (legacy int2 จาก sd_user.status)"""
                INACTIVE = 0
                ACTIVE = 1
                SUSPENDED = 2
                DELETED = 9


            class OnlineStatus(str, Enum):
                """TH: ออนไลน์ (legacy text จาก sd_user.online_status)"""
                OFFLINE = "0"
                ONLINE = "1"
                AWAY = "2"
                BUSY = "3"


            class LegacyRoleId(int, Enum):
                """TH: role_id จาก sd_user_role.role_id (int8)"""
                DEV = 1
                ADMINISTRATOR = 2
                COMPANY = 3
                STAFF = 4
                HELPDESK = 5
                CUSTOMER = 6
                DONATE = 7
                EDITOR = 8
                USER = 9
                GUEST = 10

                def to_role(self) -> Role:
                    """TH: แปลง legacy role_id → Role enum"""
                    mapping = {
                        LegacyRoleId.DEV: Role.ADMIN,
                        LegacyRoleId.ADMINISTRATOR: Role.ADMIN,
                        LegacyRoleId.COMPANY: Role.USER,
                        LegacyRoleId.STAFF: Role.USER,
                        LegacyRoleId.HELPDESK: Role.USER,
                        LegacyRoleId.CUSTOMER: Role.USER,
                        LegacyRoleId.DONATE: Role.USER,
                        LegacyRoleId.EDITOR: Role.USER,
                        LegacyRoleId.USER: Role.USER,
                        LegacyRoleId.GUEST: Role.GUEST,
                    }
                    return mapping.get(self, Role.USER)

                @classmethod
                def from_int(cls, value: int | None) -> "LegacyRoleId":
                    """TH: int → LegacyRoleId (fallback = USER)"""
                    if value is None:
                        return cls.USER
                    try:
                        return cls(value)
                    except ValueError:
                        return cls.USER
        '''))

    def _write_value_objects(self) -> None:
        self.writer.write(f"{self.mod_root}/domain/value_objects.py", dedent('''\
            """user value objects — Name, UserSecurity, UserPreferences"""
            from __future__ import annotations

            from dataclasses import dataclass
            from datetime import datetime

            from app.modules.shared.domain.entities import DomainError


            @dataclass(frozen=True, slots=True)
            class Name:
                """TH: ชื่อบุคคล (SQL: firstname/lastname เป็น NULL ได้)"""
                first_name: str = ""
                last_name: str = ""
                preferred_name: str | None = None
                full_name: str | None = None       # legacy 'fullname'
                nickname: str | None = None        # legacy 'nickname'

                def __post_init__(self) -> None:
                    # ⚠️ SQL allows NULL → ไม่บังคับ first_name/last_name
                    if len(self.first_name) > 100:
                        raise DomainError("Name.first_name must be ≤ 100 chars.")
                    if len(self.last_name) > 100:
                        raise DomainError("Name.last_name must be ≤ 100 chars.")
                    if self.nickname and len(self.nickname) > 100:
                        raise DomainError("Name.nickname must be ≤ 100 chars.")

                @property
                def display_name(self) -> str:
                    """TH: ลำดับ fallback: preferred → nickname → full → first+last"""
                    if self.preferred_name:
                        return self.preferred_name
                    if self.nickname:
                        return self.nickname
                    return f"{self.first_name} {self.last_name}".strip() or ""


            @dataclass(frozen=True, slots=True)
            class UserSecurity:
                """TH: ฟิลด์ความปลอดภัย (จาก sd_user: verified, loginfailed, ...)"""
                is_verified: bool = False               # SQL: verified
                is_superuser: bool = False              # SQL: is_superuser
                verification_code: str | None = None
                password_reset_token: str | None = None
                password_reset_at: datetime | None = None
                login_failed_count: int = 0             # SQL: loginfailed
                last_sign_in_at: datetime | None = None # SQL: lastsignindate

                def with_login_success(self, when: datetime) -> "UserSecurity":
                    return UserSecurity(
                        is_verified=self.is_verified,
                        is_superuser=self.is_superuser,
                        verification_code=self.verification_code,
                        password_reset_token=self.password_reset_token,
                        password_reset_at=self.password_reset_at,
                        login_failed_count=0,
                        last_sign_in_at=when,
                    )

                def with_login_failure(self) -> "UserSecurity":
                    return UserSecurity(
                        is_verified=self.is_verified,
                        is_superuser=self.is_superuser,
                        verification_code=self.verification_code,
                        password_reset_token=self.password_reset_token,
                        password_reset_at=self.password_reset_at,
                        login_failed_count=self.login_failed_count + 1,
                        last_sign_in_at=self.last_sign_in_at,
                    )


            @dataclass(frozen=True, slots=True)
            class UserPreferences:
                """TH: การตั้งค่า (จาก sd_user: *_notification int2)"""
                public_notification: bool = False
                sms_notification: bool = False
                email_notification: bool = False
                line_notification: bool = False
                public_status: int = 0
                # SQL: 'infomation_agree_status' (typo) → เก็บ typo ไว้ใน comment
                information_agreement_status: int = 0
        '''))

    def _write_entities(self) -> None:
        self.writer.write(f"{self.mod_root}/domain/entities.py", dedent('''\
            """user domain entities — User aggregate (mapped from sd_user)"""
            from __future__ import annotations

            from dataclasses import dataclass, field
            from datetime import date, datetime

            from app.modules.shared.application.utils import BRASILIA_TZ
            from app.modules.shared.domain.entities import BaseEntity
            from app.modules.shared.domain.enums import Role
            from app.modules.shared.domain.exceptions import DomainError
            from app.modules.shared.domain.value_objects import Email, Phone
            from app.modules.user.domain.enums import (
                Gender, OnlineStatus, UserStatus,
            )
            from app.modules.user.domain.value_objects import (
                Name, UserPreferences, UserSecurity,
            )


            @dataclass(kw_only=True, slots=True)
            class User(BaseEntity):
                """TH: User entity — id BIGINT (11+ หลัก) | EN: User entity"""

                # ─── Identity ─────────────────────────────
                name: Name = field(default_factory=Name, repr=True, compare=False)
                # ⚠️ SQL: username NOT NULL UNIQUE
                username: str = field(default="", repr=False, compare=True)
                email: Email | str = field(default=None, repr=True, compare=True)
                phone: Phone | str | None = field(default=None, repr=False, compare=False)
                mobile_number: str | None = field(default=None, repr=False, compare=False)
                line_id: str | None = field(default=None, repr=False, compare=False)
                id_card: str | None = field(default=None, repr=False, compare=False)

                # ─── Profile ──────────────────────────────
                gender: Gender | None = field(default=None, repr=False, compare=False)
                birthdate: date | None = field(default=None, repr=True, compare=False)
                avatar: str | None = field(default=None, repr=False, compare=False)
                avatar_path: str | None = field(default=None, repr=False, compare=False)
                message: str | None = field(default=None, repr=False, compare=False)
                remark: str | None = field(default=None, repr=False, compare=False)

                # ─── Auth ─────────────────────────────────
                password: str | None = field(default=None, repr=False, compare=False)
                hashed_password: str | None = field(default=None, repr=False, compare=False)
                temporary_password: str | None = field(default=None, repr=False, compare=False)

                # ─── Status ───────────────────────────────
                role: Role = field(default=Role.USER, repr=False, compare=False)
                status: UserStatus = field(default=UserStatus.ACTIVE, repr=False, compare=False)
                online_status: OnlineStatus = field(
                    default=OnlineStatus.OFFLINE, repr=False, compare=False,
                )
                # ⚠️ legacy: SQL active_status int2 (raw)
                active_status: int | None = field(default=None, repr=False, compare=False)

                # ─── Legacy grouping ──────────────────────
                network_id: int | None = field(default=None, repr=False, compare=False)
                network_type_id: int | None = field(default=None, repr=False, compare=False)
                type_id: int | None = field(default=None, repr=False, compare=False)
                system_id: str | None = field(default=None, repr=False, compare=False)
                location_id: str | None = field(default=None, repr=False, compare=False)

                # ─── Soft delete ──────────────────────────
                deleted_at: date | None = field(default=None, repr=False, compare=False)

                # ─── Grouped VOs ──────────────────────────
                security: UserSecurity = field(
                    default_factory=UserSecurity, repr=False, compare=False,
                )
                preferences: UserPreferences = field(
                    default_factory=UserPreferences, repr=False, compare=False,
                )

                # ─── Censored cache ───────────────────────
                _censored_email: str = field(init=False, default="", repr=False, compare=False)
                _censored_phone: str = field(init=False, default="", repr=False, compare=False)

                def __post_init__(self) -> None:
                    errors: list[str] = []

                    if isinstance(self.email, str):
                        try:
                            self.email = Email(email=self.email)
                        except DomainError as e:
                            errors.append(getattr(e, "message", str(e)))

                    if isinstance(self.phone, str):
                        try:
                            self.phone = Phone(phone=self.phone)
                        except DomainError as e:
                            errors.append(getattr(e, "message", str(e)))

                    self._calculate_censored_values()

                    # ⚠️ age check: only if birthdate provided
                    if self.birthdate is not None:
                        today = datetime.now(BRASILIA_TZ).date()
                        age = (
                            today.year - self.birthdate.year
                            - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
                        )
                        if age < 18:
                            errors.append("Users must be at least 18 years old.")

                    if errors:
                        raise DomainError(" | ".join(errors))

                def _calculate_censored_values(self) -> None:
                    self._censored_email = self._censor_email()
                    self._censored_phone = self._censor_phone()

                def _censor_email(self) -> str:
                    if not self.email:
                        return ""
                    s = str(self.email)
                    if "@" not in s:
                        return ""
                    local, domain = s.split("@", 1)
                    masked = "*" * len(local) if len(local) <= 1 else local[0] + "*" * (len(local) - 1)
                    return f"{masked}@{domain}"

                def _censor_phone(self) -> str:
                    if not self.phone:
                        return ""
                    s = str(self.phone)
                    digits = "".join(filter(str.isdigit, s))
                    if len(digits) < 4:
                        return "*" * len(s)
                    visible = digits[-4:]
                    censored_len = len(digits) - 4
                    out, idx = [], 0
                    for ch in s:
                        if ch.isdigit():
                            out.append("*" if idx < censored_len
                                       else visible[idx - censored_len])
                            idx += 1
                        else:
                            out.append(ch)
                    return "".join(out)

                @property
                def censored_email(self) -> str:
                    return self._censored_email

                @property
                def censored_phone(self) -> str:
                    return self._censored_phone

                # ─── Behavior ─────────────────────────────
                def soft_delete(self) -> None:
                    self.deleted_at = datetime.now(BRASILIA_TZ).date()
                    self.is_active = False
                    self.status = UserStatus.DELETED

                def record_login(self) -> None:
                    self.security = self.security.with_login_success(
                        datetime.now(BRASILIA_TZ)
                    )
                    self.online_status = OnlineStatus.ONLINE

                def record_login_failure(self) -> None:
                    self.security = self.security.with_login_failure()

                def record_logout(self) -> None:
                    self.online_status = OnlineStatus.OFFLINE
        '''))

    def _write_exceptions(self) -> None:
        self.writer.write(f"{self.mod_root}/application/exceptions.py", dedent('''\
            """user application exceptions"""
            from __future__ import annotations
            from http import HTTPStatus

            from app.modules.shared.application.exceptions import StandardException
            from app.modules.shared.domain.enums import ResponseMessages


            class UserException(StandardException):
                def __init__(self) -> None:
                    super().__init__(
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        message=ResponseMessages.INTERNAL_ERROR.value,
                        data={"errors": "Unexpected error at user module."},
                    )


            class UserEmailAlreadyExistsException(StandardException):
                def __init__(self, email: str) -> None:
                    super().__init__(
                        status_code=HTTPStatus.CONFLICT,
                        message=ResponseMessages.CONFLICT.value,
                        data={"errors": f"User email '{email}' already exists."},
                    )


            class UsernameAlreadyExistsException(StandardException):
                def __init__(self, username: str) -> None:
                    super().__init__(
                        status_code=HTTPStatus.CONFLICT,
                        message=ResponseMessages.CONFLICT.value,
                        data={"errors": f"Username '{username}' already exists."},
                    )


            class UserEmailNotFoundException(StandardException):
                def __init__(self, email: str) -> None:
                    super().__init__(
                        status_code=HTTPStatus.NOT_FOUND,
                        message=ResponseMessages.RESOURCE_NOT_FOUND.value,
                        data={"errors": f"User email '{email}' not found."},
                    )


            class UserIdNotFoundException(StandardException):
                def __init__(self, user_id: int) -> None:
                    super().__init__(
                        status_code=HTTPStatus.NOT_FOUND,
                        message=ResponseMessages.RESOURCE_NOT_FOUND.value,
                        data={"errors": f"User '{user_id}' not found."},
                    )


            class UserAlreadyDeletedException(StandardException):
                def __init__(self, user_id: int) -> None:
                    super().__init__(
                        status_code=HTTPStatus.GONE,
                        message=ResponseMessages.RESOURCE_NOT_FOUND.value,
                        data={"errors": f"User '{user_id}' was soft-deleted."},
                    )


            class CookieManagementException(StandardException):
                def __init__(self) -> None:
                    super().__init__(
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        message=ResponseMessages.INTERNAL_ERROR.value,
                        data={"errors": "Unexpected error while managing user cookie."},
                    )
        '''))

    # ═══════════════════════════════════════════════════════════
    #  2. INFRASTRUCTURE
    # ═══════════════════════════════════════════════════════════
    def update_infrastructure(self) -> None:
        info("[UPDATE-INFRASTRUCTURE] user models (BigInteger ID + sd_user fields)")
        self.writer.write(f"{self.mod_root}/infrastructure/models.py", dedent('''\
            """user SQLAlchemy models — schema=public, prefix=erp_, id=BIGINT"""
            from __future__ import annotations

            from datetime import date, datetime
            from typing import TYPE_CHECKING

            from sqlalchemy import (
                BigInteger, Boolean, Date, DateTime, Identity, Index,
                Integer, SmallInteger, String, Text, func,
            )
            from sqlalchemy import Enum as SQLEnum
            from sqlalchemy.orm import Mapped, mapped_column, relationship

            from app.core.settings import settings
            from app.modules.shared.application.utils import BRASILIA_TZ
            from app.modules.shared.domain.enums import Role
            from app.modules.shared.infrastructure.models import BaseModel
            from app.modules.user.domain.enums import (
                Gender, OnlineStatus, UserStatus,
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
                # ⚠️ SQL: firstname/lastname text (NULLABLE)
                first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
                last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
                # preferred_name: app-level (fallback = nickname || first_name)
                preferred_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
                full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
                nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)

                # ⚠️ SQL: username NOT NULL UNIQUE
                username: Mapped[str] = mapped_column(
                    String(150), nullable=False, unique=True,
                )
                email: Mapped[str] = mapped_column(
                    String(255), nullable=False, unique=True,
                )
                # SQL: phone_number → phone
                phone: Mapped[str | None] = mapped_column(String(18), nullable=True)
                mobile_number: Mapped[str | None] = mapped_column(String(18), nullable=True)
                # SQL: lineid → line_id
                line_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
                # SQL: idcard → id_card
                id_card: Mapped[str | None] = mapped_column(String(20), nullable=True)

                # ─── Profile ──────────────────────────────
                gender: Mapped[Gender | None] = mapped_column(
                    SQLEnum(Gender, name="gender_enum"), nullable=True,
                )
                # SQL: birthday → birthdate
                birthdate: Mapped[date | None] = mapped_column(Date, nullable=True)
                avatar: Mapped[str | None] = mapped_column(Text, nullable=True)
                # SQL: avatarpath → avatar_path
                avatar_path: Mapped[str | None] = mapped_column(Text, nullable=True)
                message: Mapped[str | None] = mapped_column(Text, nullable=True)
                remark: Mapped[str | None] = mapped_column(Text, nullable=True)

                # ─── Auth (SQL: password, password_temp) ──
                hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
                temporary_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

                # ─── Status ───────────────────────────────
                role: Mapped[Role] = mapped_column(
                    SQLEnum(Role, name="role_enum"), nullable=False,
                    default=Role.USER, server_default="user",
                )
                # SQL: status int2 NOT NULL
                status: Mapped[UserStatus] = mapped_column(
                    SQLEnum(UserStatus, name="user_status_enum"),
                    nullable=False, default=UserStatus.ACTIVE, server_default="1",
                )
                # SQL: online_status text DEFAULT '0'
                online_status: Mapped[OnlineStatus] = mapped_column(
                    SQLEnum(OnlineStatus, name="online_status_enum"),
                    nullable=False, default=OnlineStatus.OFFLINE, server_default="0",
                )
                # ⚠️ legacy raw int2 (SQL: active_status)
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

                # ─── Security (SQL: verified, is_superuser, ...) ──
                # SQL: verified bool DEFAULT false
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
                # SQL: loginfailed int2
                login_failed_count: Mapped[int] = mapped_column(
                    SmallInteger, nullable=False, default=0, server_default="0",
                )
                # SQL: lastsignindate timestamptz NOT NULL DEFAULT now()
                last_sign_in_at: Mapped[datetime | None] = mapped_column(
                    DateTime(timezone=True), nullable=True,
                    default=lambda: datetime.now(BRASILIA_TZ),
                )

                # ─── Preferences (SQL: *_notification int2) ──
                # ⚠️ เก็บเป็น int2 เพื่อให้ migrate ตรง — app layer แปลงเป็น bool
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
                # SQL: 'infomation_agree_status' (typo) → เก็บเป็น information_agreement_status
                information_agreement_status: Mapped[int] = mapped_column(
                    SmallInteger, nullable=False, default=0, server_default="0",
                )

                # ─── Relationship ─────────────────────────
                authentications: Mapped[list["AuthenticationModel"]] = relationship(
                    "AuthenticationModel", back_populates="user",
                    cascade="all, delete-orphan",
                    passive_deletes=True, lazy="noload",
                )
        '''))

    # ═══════════════════════════════════════════════════════════
    #  3. APPLICATION
    # ═══════════════════════════════════════════════════════════
    def update_application(self) -> None:
        info("[UPDATE-APPLICATION] user mappers + use_cases")
        self._write_user_mappers()
        self._write_user_use_cases()

    def _write_user_mappers(self) -> None:
        self.writer.write(f"{self.mod_root}/application/mappers.py", dedent('''\
            """user mappers — entity ↔ model ↔ response (SQL-aligned)"""
            from __future__ import annotations

            from datetime import datetime

            from app.modules.shared.application.utils import BRASILIA_TZ
            from app.modules.shared.domain.enums import ResponseMessages, Role
            from app.modules.user.domain.entities import User
            from app.modules.user.domain.enums import (
                Gender, OnlineStatus, UserStatus,
            )
            from app.modules.user.domain.value_objects import (
                Name, UserPreferences, UserSecurity,
            )
            from app.modules.user.infrastructure.models import UserModel


            # ═════════════════════════════════════════════════════════
            # HELPERS
            # ═════════════════════════════════════════════════════════
            def _int_to_bool(value: int | None) -> bool:
                """TH: SQL int2 (0/1) → bool"""
                if value is None:
                    return False
                return bool(value)


            # ═════════════════════════════════════════════════════════
            # ENTITY ↔ MODEL
            # ═════════════════════════════════════════════════════════
            def model_entity_mapper(model: UserModel) -> User:
                """TH: DB row → User entity (จาก sd_user)"""
                return User(
                    id=model.id,
                    name=Name(
                        first_name=model.first_name or "",
                        last_name=model.last_name or "",
                        preferred_name=model.preferred_name or model.nickname,
                        full_name=model.full_name,
                        nickname=model.nickname,
                    ),
                    username=model.username or "",
                    email=str(model.email) if model.email else "",
                    phone=str(model.phone) if model.phone else None,
                    mobile_number=model.mobile_number,
                    line_id=model.line_id,
                    id_card=model.id_card,
                    gender=model.gender,
                    birthdate=model.birthdate,
                    avatar=model.avatar,
                    avatar_path=model.avatar_path,
                    message=model.message,
                    remark=model.remark,
                    hashed_password=model.hashed_password,
                    temporary_password=model.temporary_password,
                    role=model.role,
                    status=model.status,
                    online_status=model.online_status,
                    # ⚠️ map active_status int2 → is_active bool
                    is_active=_int_to_bool(model.active_status)
                        if model.active_status is not None
                        else bool(getattr(model, "is_active", True)),
                    active_status=model.active_status,
                    network_id=model.network_id,
                    network_type_id=model.network_type_id,
                    type_id=model.type_id,
                    system_id=model.system_id,
                    location_id=model.location_id,
                    deleted_at=model.deleted_at,
                    security=UserSecurity(
                        is_verified=model.is_verified,
                        is_superuser=model.is_superuser,
                        verification_code=model.verification_code,
                        password_reset_token=model.password_reset_token,
                        password_reset_at=model.password_reset_at,
                        login_failed_count=model.login_failed_count,
                        last_sign_in_at=model.last_sign_in_at,
                    ),
                    preferences=UserPreferences(
                        public_notification=_int_to_bool(model.public_notification),
                        sms_notification=_int_to_bool(model.sms_notification),
                        email_notification=_int_to_bool(model.email_notification),
                        line_notification=_int_to_bool(model.line_notification),
                        public_status=model.public_status,
                        information_agreement_status=model.information_agreement_status,
                    ),
                    created_at=model.created_at,
                    updated_at=model.updated_at,
                )


            def entity_model_mapper(user: User) -> UserModel:
                """TH: User entity → DB model"""
                if not user.hashed_password:
                    raise ValueError(
                        "entity_model_mapper: hashed_password is None — hash first"
                    )
                return UserModel(
                    id=user.id,
                    first_name=(user.name.first_name if user.name else None) or None,
                    last_name=(user.name.last_name if user.name else None) or None,
                    preferred_name=(user.name.preferred_name if user.name else None),
                    full_name=user.name.full_name if user.name else None,
                    nickname=user.name.nickname if user.name else None,
                    username=user.username or "",
                    email=str(user.email) if user.email else "",
                    phone=str(user.phone) if user.phone else None,
                    mobile_number=user.mobile_number,
                    line_id=user.line_id,
                    id_card=user.id_card,
                    gender=user.gender,
                    birthdate=user.birthdate,
                    avatar=user.avatar,
                    avatar_path=user.avatar_path,
                    message=user.message,
                    remark=user.remark,
                    hashed_password=user.hashed_password,
                    temporary_password=user.temporary_password,
                    role=user.role,
                    status=user.status,
                    online_status=user.online_status,
                    # ⚠️ is_active → active_status int2
                    active_status=1 if user.is_active else 0,
                    network_id=user.network_id,
                    network_type_id=user.network_type_id,
                    type_id=user.type_id,
                    system_id=user.system_id,
                    location_id=user.location_id,
                    deleted_at=user.deleted_at,
                    is_verified=user.security.is_verified,
                    is_superuser=user.security.is_superuser,
                    verification_code=user.security.verification_code,
                    password_reset_token=user.security.password_reset_token,
                    password_reset_at=user.security.password_reset_at,
                    login_failed_count=user.security.login_failed_count,
                    last_sign_in_at=user.security.last_sign_in_at,
                    public_notification=int(user.preferences.public_notification),
                    sms_notification=int(user.preferences.sms_notification),
                    email_notification=int(user.preferences.email_notification),
                    line_notification=int(user.preferences.line_notification),
                    public_status=user.preferences.public_status,
                    information_agreement_status=user.preferences.information_agreement_status,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                )


            # ═════════════════════════════════════════════════════════
            # DTOS
            # ═════════════════════════════════════════════════════════
            def create_entity_mapper(payload) -> User:
                """TH: request payload → User entity"""
                first_name = getattr(payload, "first_name", None) or ""
                last_name = getattr(payload, "last_name", None) or ""
                preferred_name = getattr(payload, "preferred_name", None)
                nickname = getattr(payload, "nickname", None)

                name = Name(
                    first_name=first_name,
                    last_name=last_name,
                    preferred_name=preferred_name or nickname or first_name or None,
                    full_name=f"{first_name} {last_name}".strip() or None,
                    nickname=nickname,
                )

                raw_password = getattr(payload, "password", None)
                if not raw_password:
                    raise ValueError("password is required")

                return User(
                    name=name,
                    username=getattr(payload, "username", None) or "",
                    email=getattr(payload, "email", None),
                    phone=getattr(payload, "phone", None),
                    mobile_number=getattr(payload, "mobile_number", None),
                    line_id=getattr(payload, "line_id", None),
                    id_card=getattr(payload, "id_card", None),
                    gender=getattr(payload, "gender", None),
                    birthdate=getattr(payload, "birthdate", None),
                    password=raw_password,
                    network_id=getattr(payload, "network_id", None),
                    network_type_id=getattr(payload, "network_type_id", None),
                    type_id=getattr(payload, "type_id", None),
                    system_id=getattr(payload, "system_id", None),
                    location_id=getattr(payload, "location_id", None),
                )


            def entity_me_mapper(user: User) -> dict:
                """TH: User → /me response dict"""
                if user is None:
                    raise ValueError("entity_me_mapper: user is None")
                name = user.name
                return {
                    "id": user.id,
                    "first_name": (name.first_name if name else "") or "",
                    "last_name": (name.last_name if name else "") or "",
                    "preferred_name": (name.preferred_name if name else "") or "",
                    "full_name": (name.full_name if name else None),
                    "nickname": (name.nickname if name else None),
                    "username": user.username,
                    "email": str(user.email) if user.email else "",
                    "phone": str(user.phone) if user.phone else None,
                    "mobile_number": user.mobile_number,
                    "line_id": user.line_id,
                    "gender": user.gender.value if user.gender else None,
                    "birthdate": user.birthdate.isoformat() if user.birthdate else None,
                    "avatar": user.avatar,
                    "avatar_path": user.avatar_path,
                    "role": user.role.value if user.role else Role.USER.value,
                    "status": int(user.status.value) if user.status else 1,
                    "online_status": user.online_status.value if user.online_status else "0",
                    "is_verified": user.security.is_verified,
                    "is_superuser": user.security.is_superuser,
                    "last_sign_in_at": (
                        user.security.last_sign_in_at.isoformat()
                        if user.security.last_sign_in_at else None
                    ),
                    "created_at": (
                        user.created_at.isoformat() if user.created_at
                        else datetime.now(BRASILIA_TZ).isoformat()
                    ),
                }
        '''))

    def _write_user_use_cases(self) -> None:
        self.writer.write(f"{self.mod_root}/application/use_cases.py", dedent('''\
            """user use cases — create / me"""
            from __future__ import annotations

            from loguru import logger

            from app.core.security import hash_password
            from app.modules.shared.application.exceptions import (
                DomainException, StandardException,
            )
            from app.modules.shared.domain.entities import DomainError
            from app.modules.user.application.exceptions import (
                UserEmailAlreadyExistsException, UserException,
            )
            from app.modules.user.application.interfaces import IUserRepository
            from app.modules.user.domain.entities import User


            class UserUseCases:
                """TH: use cases ของ user | EN: user use cases"""

                def __init__(self, repository: IUserRepository) -> None:
                    self.repository = repository

                async def create(self, user: User) -> User:
                    try:
                        if await self.repository.exists_by_email(user):
                            raise UserEmailAlreadyExistsException(email=str(user.email))

                        if not user.hashed_password:
                            if not user.password:
                                raise ValueError("password is required")
                            user.hashed_password = hash_password(user.password)
                            user.password = None

                        user = await self.repository.create(user)
                        return user
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("user.create failed")
                        raise UserException()

                async def me(self, user: User) -> User:
                    try:
                        return user
                    except StandardException:
                        raise
                    except DomainError as e:
                        raise DomainException(e)
                    except Exception as e:
                        logger.opt(exception=e).error("user.me failed")
                        raise UserException()
        '''))

    # ═══════════════════════════════════════════════════════════
    #  4. PRESENTATION
    # ═══════════════════════════════════════════════════════════
    def update_presentation(self) -> None:
        info("[UPDATE-PRESENTATION] user schemas")
        self.writer.write(f"{self.mod_root}/presentation/schemas.py", dedent('''\
            """user Pydantic v2 schemas"""
            from __future__ import annotations

            import re
            from datetime import date, datetime

            from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

            from app.modules.shared.domain.enums import Role
            from app.modules.user.domain.enums import (
                Gender, OnlineStatus, UserStatus,
            )


            # ═════════════════════════════════════════════════════════
            # REQUEST
            # ═════════════════════════════════════════════════════════
            class CreateRequest(BaseModel):
                """TH: request สร้าง user | EN: create-user request"""

                first_name: str = Field(min_length=1, max_length=100)
                last_name: str = Field(min_length=1, max_length=100)
                preferred_name: str | None = Field(default=None, max_length=100)
                nickname: str | None = Field(default=None, max_length=100)

                # ⚠️ SQL: username NOT NULL UNIQUE
                username: str = Field(min_length=1, max_length=150)
                email: EmailStr
                phone: str | None = None
                mobile_number: str | None = None
                line_id: str | None = Field(default=None, max_length=100)
                id_card: str | None = Field(default=None, max_length=20)

                gender: Gender | None = None
                birthdate: date | None = None

                password: str = Field(min_length=8, max_length=64)

                network_id: int | None = None
                network_type_id: int | None = None
                type_id: int | None = None
                system_id: str | None = None
                location_id: str | None = None

                @field_validator("first_name", "last_name")
                @classmethod
                def validate_name(cls, value: str) -> str:
                    if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\\s'-]+$", value):
                        raise ValueError("Name contains invalid characters.")
                    return value

                @field_validator("username")
                @classmethod
                def validate_username(cls, value: str) -> str:
                    if not re.match(r"^[a-zA-Z0-9_.@-]+$", value):
                        raise ValueError(
                            "Username may contain letters, digits, '.', '_', '@', '-'."
                        )
                    return value

                @field_validator("password")
                @classmethod
                def validate_password(cls, password: str) -> str:
                    if len(password) < 8:
                        raise ValueError("Password must be ≥ 8 chars.")
                    if not re.search(r"[A-Z]", password):
                        raise ValueError("Password must contain uppercase.")
                    if not re.search(r"[a-z]", password):
                        raise ValueError("Password must contain lowercase.")
                    if not re.search(r"[0-9]", password):
                        raise ValueError("Password must contain digit.")
                    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                        raise ValueError("Password must contain special char.")
                    return password

                model_config = ConfigDict(
                    title="CreateRequest", extra="forbid",
                    str_strip_whitespace=True,
                )


            # ═════════════════════════════════════════════════════════
            # RESPONSE
            # ═════════════════════════════════════════════════════════
            class MeResponse(BaseModel):
                """TH: response /me | EN: /me response"""

                id: int
                first_name: str
                last_name: str
                preferred_name: str
                full_name: str | None = None
                nickname: str | None = None
                username: str
                email: str
                phone: str | None = None
                mobile_number: str | None = None
                line_id: str | None = None
                gender: Gender | None = None
                birthdate: date | None = None
                avatar: str | None = None
                avatar_path: str | None = None
                role: Role
                status: UserStatus
                online_status: OnlineStatus
                is_verified: bool = False
                is_superuser: bool = False
                last_sign_in_at: datetime | None = None
                created_at: datetime

                model_config = ConfigDict(
                    title="MeResponse", extra="forbid",
                    str_strip_whitespace=True,
                )
        '''))

    # ═══════════════════════════════════════════════════════════
    #  5. AUTH FK
    # ═══════════════════════════════════════════════════════════
    def update_auth_fk(self) -> None:
        info("[UPDATE-AUTH-FK] authentication/models → user_id BIGINT")
        models_file = self.root / f"{self.auth_root}/infrastructure/models.py"
        if not models_file.exists():
            warn(f"{models_file} not found — skipping")
            return
        content = models_file.read_text(encoding="utf-8")
        original = content

        content = content.replace(
            "from sqlalchemy import (\n    UUID as SQUID,\n)",
            "from sqlalchemy import UUID as SQUID\nfrom sqlalchemy import BigInteger",
            1,
        )
        if "BigInteger" not in content:
            content = content.replace(
                "from sqlalchemy import UUID as SQUID",
                "from sqlalchemy import UUID as SQUID\nfrom sqlalchemy import BigInteger",
                1,
            )

        content = re.sub(
            r'(user_id:\s*Mapped\[)[^\]]+(\]\s*=\s*mapped_column\(\s*)SQUID\(as_uuid=True\)',
            r"\1int\2BigInteger",
            content,
            count=1,
        )

        if content != original:
            bak = models_file.with_suffix(".py.bak")
            bak.write_bytes(models_file.read_bytes())
            ok(f"backup: {models_file.relative_to(self.root)}.bak")
            models_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"updated: {models_file.relative_to(self.root)}")
        else:
            skip("authentication/models.py unchanged")

    # ═══════════════════════════════════════════════════════════
    #  6. AUTH MAPPERS
    # ═══════════════════════════════════════════════════════════
    def update_auth_mappers(self) -> None:
        info("[UPDATE-AUTH-MAPPERS] UUID(sub) → int(sub)")
        mappers = self.root / f"{self.auth_root}/application/mappers.py"
        if not mappers.exists():
            warn(f"{mappers} not found — skipping")
            return
        content = mappers.read_text(encoding="utf-8")
        original = content

        content = content.replace(
            'id=UUID(claims["sub"]) if isinstance(claims["sub"], str) else claims["sub"]',
            'id=int(claims["sub"])',
        )

        if content != original:
            bak = mappers.with_suffix(".py.bak")
            bak.write_bytes(mappers.read_bytes())
            ok(f"backup: {mappers.relative_to(self.root)}.bak")
            mappers.write_text(content, encoding="utf-8", newline="\n")
            ok(f"updated: {mappers.relative_to(self.root)}")
        else:
            skip("authentication/mappers.py — no UUID(sub) found")

    # ═══════════════════════════════════════════════════════════
    #  7. AUTH VALUE OBJECTS
    # ═══════════════════════════════════════════════════════════
    def update_auth_vo(self) -> None:
        info("[UPDATE-AUTH-VO] sub: UUID → str")
        vo_file = self.root / f"{self.auth_root}/domain/value_objects.py"
        if not vo_file.exists():
            warn(f"{vo_file} not found — skipping")
            return
        content = vo_file.read_text(encoding="utf-8")
        original = content

        content = content.replace(
            '    sub: UUID  # subject',
            '    sub: str  # subject (user id as string)',
        )
        content = content.replace("    sub: UUID\n", "    sub: str\n")
        content = content.replace(
            "        sub: UUID | None = None,",
            "        sub: str | None = None,",
        )
        content = content.replace(
            'object.__setattr__(self, "sub", sub)',
            'object.__setattr__(self, "sub", str(sub) if sub is not None else sub)',
        )
        content = content.replace(
            '"sub": UUID(data["sub"]) if isinstance(data["sub"], str) else data["sub"],',
            '"sub": str(data["sub"]),',
        )

        if content != original:
            bak = vo_file.with_suffix(".py.bak")
            bak.write_bytes(vo_file.read_bytes())
            ok(f"backup: {vo_file.relative_to(self.root)}.bak")
            vo_file.write_text(content, encoding="utf-8", newline="\n")
            ok(f"updated: {vo_file.relative_to(self.root)}")
        else:
            skip("authentication/value_objects.py unchanged")

    # ═══════════════════════════════════════════════════════════
    #  8. CACHE MAPPERS
    # ═══════════════════════════════════════════════════════════
    def update_cache_mappers(self) -> None:
        info("[UPDATE-CACHE-MAPPERS] UUID(id) → int(id)")
        mappers = self.root / f"{self.auth_root}/application/mappers.py"
        if not mappers.exists():
            warn(f"{mappers} not found — skipping")
            return
        content = mappers.read_text(encoding="utf-8")
        original = content

        content = content.replace(
            'id=UUID(data["id"]) if data["id"] else None,',
            'id=int(data["id"]) if data["id"] is not None else None,',
        )

        if content != original:
            bak = mappers.with_suffix(".py.bak")
            bak.write_bytes(mappers.read_bytes())
            ok(f"backup: {mappers.relative_to(self.root)}.bak")
            mappers.write_text(content, encoding="utf-8", newline="\n")
            ok(f"updated cache mapper in: {mappers.relative_to(self.root)}")
        else:
            skip("cache mapper — no UUID(id) found")

    # ═══════════════════════════════════════════════════════════
    #  9. SQL — alter users (migrate sd_user)
    # ═══════════════════════════════════════════════════════════
    def create_sql(self) -> None:
        info("[SQL] users ALTER (UUID → BIGINT + migrate sd_user)")
        self.writer.write(
            f"{self.sql_dir}/V010__alter_users_bigint_id.sql",
            self._v010_sql(),
        )

    def _v010_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V010__alter_users_bigint_id.sql
-- Convert erp_users.id UUID → BIGINT (11+ digit auto-increment)
-- + migrate data from sd_user + seed sd_user_role → erp_user_roles
-- ═══════════════════════════════════════════════════════════════
BEGIN;

-- ═══════════════════════════════════════════════════════════════
-- Step 1: legacy role mapping table (จาก sd_user_role)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.erp_user_roles (
    role_id      BIGINT PRIMARY KEY,       -- = sd_user_role.role_id (int8)
    title        VARCHAR(50) NOT NULL,
    lang         VARCHAR(10) NOT NULL DEFAULT 'en',
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO public.erp_user_roles (role_id, title) VALUES
    (1,  'Dev'),
    (2,  'Administrator'),
    (3,  'Company'),
    (4,  'Staff'),
    (5,  'Helpdask'),
    (6,  'Customer'),
    (7,  'Donate'),
    (8,  'Edittor'),
    (9,  'User'),
    (10, 'gaust')
ON CONFLICT (role_id) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════
-- Step 2: create new erp_users with BIGINT id
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS public.erp_users_new (
    id                             BIGINT GENERATED BY DEFAULT AS IDENTITY
                                       (START WITH 10000000000 INCREMENT BY 1)
                                       PRIMARY KEY,
    created_at                     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at                     DATE,
    is_active                      BOOLEAN NOT NULL DEFAULT TRUE,

    -- legacy role_id (int8) from sd_user.role_id
    role_id                        BIGINT NOT NULL DEFAULT 9,
    -- app-level Role enum string
    role                           VARCHAR(20) NOT NULL DEFAULT 'user',

    -- ─── Identity (SQL: sd_user) ─────────────────
    first_name                     VARCHAR(100),                 -- SQL: NULLABLE
    last_name                      VARCHAR(100),                 -- SQL: NULLABLE
    preferred_name                 VARCHAR(100),
    full_name                      VARCHAR(200),
    nickname                       VARCHAR(100),
    username                       VARCHAR(150) NOT NULL UNIQUE,  -- SQL: NOT NULL
    email                          VARCHAR(255) NOT NULL UNIQUE,
    phone                          VARCHAR(18),                  -- SQL: phone_number
    mobile_number                  VARCHAR(18),
    line_id                        VARCHAR(100),                 -- SQL: lineid
    id_card                        VARCHAR(20),                  -- SQL: idcard

    -- ─── Profile ──────────────────────────────────
    gender                         VARCHAR(20),
    birthdate                      DATE,                         -- SQL: birthday
    avatar                         TEXT,
    avatar_path                    TEXT,                         -- SQL: avatarpath
    message                        TEXT,
    remark                         TEXT,

    -- ─── Auth ─────────────────────────────────────
    hashed_password                VARCHAR(255) NOT NULL,        -- SQL: password
    temporary_password             VARCHAR(255),                 -- SQL: password_temp

    -- ─── Status ───────────────────────────────────
    status                         SMALLINT NOT NULL DEFAULT 1,
    online_status                  VARCHAR(10) NOT NULL DEFAULT '0',
    active_status                  SMALLINT,                     -- legacy int2

    -- ─── Legacy grouping ──────────────────────────
    network_id                     BIGINT DEFAULT 1,
    network_type_id                BIGINT DEFAULT 0,
    type_id                        BIGINT DEFAULT 0,
    system_id                      VARCHAR(50) DEFAULT '1',
    location_id                    VARCHAR(50) DEFAULT '1',

    -- ─── Security ─────────────────────────────────
    is_verified                    BOOLEAN NOT NULL DEFAULT FALSE,  -- SQL: verified
    is_superuser                   BOOLEAN NOT NULL DEFAULT FALSE,
    verification_code              VARCHAR(64),
    password_reset_token           VARCHAR(64),
    password_reset_at              TIMESTAMPTZ,
    login_failed_count             SMALLINT NOT NULL DEFAULT 0,   -- SQL: loginfailed
    last_sign_in_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),  -- SQL: lastsignindate

    -- ─── Preferences (SQL: *_notification int2) ──
    public_notification            SMALLINT NOT NULL DEFAULT 0,
    sms_notification               SMALLINT NOT NULL DEFAULT 0,
    email_notification             SMALLINT NOT NULL DEFAULT 0,
    line_notification              SMALLINT NOT NULL DEFAULT 0,
    public_status                  SMALLINT NOT NULL DEFAULT 0,
    information_agreement_status   SMALLINT NOT NULL DEFAULT 0,  -- SQL: infomation_agree_status

    CONSTRAINT ck_users_new_status CHECK (status IN (0,1,2,9))
);

-- ═══════════════════════════════════════════════════════════════
-- Step 3: migrate data from sd_user
-- ═══════════════════════════════════════════════════════════════
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema='public' AND table_name='sd_user') THEN

        INSERT INTO public.erp_users_new (
            created_at, updated_at, deleted_at, is_active,
            role_id, role,
            first_name, last_name, preferred_name, full_name, nickname,
            username, email, phone, mobile_number, line_id, id_card,
            gender, birthdate, avatar, avatar_path, message, remark,
            hashed_password, temporary_password,
            status, online_status, active_status,
            network_id, network_type_id, type_id, system_id, location_id,
            is_verified, is_superuser, verification_code,
            password_reset_token, password_reset_at,
            login_failed_count, last_sign_in_at,
            public_notification, sms_notification,
            email_notification, line_notification,
            public_status, information_agreement_status
        )
        SELECT
            u.createddate,
            u.updateddate,
            u.deletedate,
            CASE
                WHEN u.active_status IS NULL THEN
                    CASE WHEN u.status = 1 THEN TRUE ELSE FALSE END
                ELSE (u.active_status = 1)
            END,
            COALESCE(u.role_id, 9),
            CASE u.role_id
                WHEN 1 THEN 'admin'
                WHEN 2 THEN 'admin'
                WHEN 10 THEN 'guest'
                ELSE 'user'
            END,
            NULLIF(u.firstname, ''),
            NULLIF(u.lastname, ''),
            COALESCE(NULLIF(u.nickname, ''), NULLIF(u.firstname, '')),
            NULLIF(u.fullname, ''),
            NULLIF(u.nickname, ''),
            u.username,
            u.email,
            NULLIF(NULLIF(u.phone_number, '0'), ''),
            NULLIF(NULLIF(u.mobile_number, '0'), ''),
            NULLIF(NULLIF(u.lineid, '0'), ''),
            NULLIF(u.idcard, ''),
            NULLIF(u.gender, ''),
            u.birthday,
            NULLIF(u.avatar, ''),
            NULLIF(u.avatarpath, ''),
            u.message,
            u.remark,
            u.password,
            u.password_temp,
            COALESCE(u.status, 1),
            COALESCE(NULLIF(u.online_status, ''), '0'),
            u.active_status,
            COALESCE(u.network_id, 1),
            COALESCE(u.network_type_id, 0),
            COALESCE(u.type_id, 0),
            COALESCE(u.system_id, '1'),
            COALESCE(u.location_id, '1'),
            COALESCE(u.verified, FALSE),
            COALESCE(u.is_superuser, FALSE),
            u.verification_code,
            u.password_reset_token,
            u.password_reset_at,
            COALESCE(u.loginfailed, 0),
            u.lastsignindate,
            COALESCE(u.public_notification, 0),
            COALESCE(u.sms_notification, 0),
            COALESCE(u.email_notification, 0),
            COALESCE(u.line_notification, 0),
            COALESCE(u.public_status, 0),
            COALESCE(u.infomation_agree_status, 0)
        FROM public.sd_user u
        WHERE u.email IS NOT NULL AND u.username IS NOT NULL
        ON CONFLICT (email) DO NOTHING;
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════
-- Step 4: swap tables
-- ═══════════════════════════════════════════════════════════════
DROP TABLE IF EXISTS public.erp_users CASCADE;
ALTER TABLE public.erp_users_new RENAME TO erp_users;

-- ═══════════════════════════════════════════════════════════════
-- Step 5: indexes
-- ═══════════════════════════════════════════════════════════════
CREATE INDEX IF NOT EXISTS ix_users_email_is_active
    ON public.erp_users (email, is_active);
CREATE INDEX IF NOT EXISTS ix_users_username
    ON public.erp_users (username);
CREATE INDEX IF NOT EXISTS ix_users_status
    ON public.erp_users (status);
CREATE INDEX IF NOT EXISTS ix_users_role
    ON public.erp_users (role);
CREATE INDEX IF NOT EXISTS ix_users_created_at
    ON public.erp_users (created_at DESC);

-- ═══════════════════════════════════════════════════════════════
-- Step 6: updated_at trigger
-- ═══════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION public.set_updated_at_users()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated ON public.erp_users;
CREATE TRIGGER trg_users_updated BEFORE UPDATE ON public.erp_users
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at_users();

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  10. SQL — alter auth FK
    # ═══════════════════════════════════════════════════════════
    def sql_auth_fk(self) -> None:
        info("[SQL] auth_authentications.user_id UUID → BIGINT")
        self.writer.write(
            f"{self.sql_dir}/V011__alter_auth_fk_bigint.sql",
            self._v011_sql(),
        )

    def _v011_sql(self) -> str:
        return """-- ═══════════════════════════════════════════════════════════════
-- V011__alter_auth_fk_bigint.sql
-- Convert auth_authentications.user_id UUID → BIGINT
-- Requires: erp_users.id is now BIGINT (V010)
-- NOTE: existing sessions become invalid — force re-login.
-- ═══════════════════════════════════════════════════════════════
BEGIN;

-- Drop FK constraint first
ALTER TABLE public.auth_authentications
    DROP CONSTRAINT IF EXISTS auth_authentications_user_id_fkey;

-- Drop the old column (sessions become orphaned → cleared)
ALTER TABLE public.auth_authentications
    DROP COLUMN IF EXISTS user_id;

-- Add new BIGINT column
ALTER TABLE public.auth_authentications
    ADD COLUMN user_id BIGINT NOT NULL DEFAULT 0;

-- Re-add FK
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_schema='public' AND table_name='erp_users') THEN
        ALTER TABLE public.auth_authentications
            ADD CONSTRAINT auth_authentications_user_id_fkey
            FOREIGN KEY (user_id)
            REFERENCES public.erp_users (id)
            ON DELETE CASCADE;
    END IF;
END $$;

-- Recreate the unique constraint
ALTER TABLE public.auth_authentications
    DROP CONSTRAINT IF EXISTS uq_auth_user_agent_device;
ALTER TABLE public.auth_authentications
    ADD CONSTRAINT uq_auth_user_agent_device
        UNIQUE (user_id, user_agent, device);

DROP INDEX IF EXISTS public.ix_auth_user_agent_device;
CREATE INDEX ix_auth_user_agent_device
    ON public.auth_authentications (user_id, user_agent, device);

COMMIT;
"""

    # ═══════════════════════════════════════════════════════════
    #  11. VERIFY
    # ═══════════════════════════════════════════════════════════
    def verify(self) -> None:
        info("[VERIFY] user module (after update)")
        issues: list[str] = []

        entities = self.root / f"{self.mod_root}/domain/entities.py"
        if entities.exists():
            c = entities.read_text(encoding="utf-8")
            if "class User(BaseEntity)" in c:
                ok("entities.py: User inherits BaseEntity ✓")
            else:
                issues.append("entities.py: User does not inherit BaseEntity")
            if "from uuid import UUID" in c:
                issues.append("entities.py still imports UUID")
            if "UserSecurity" in c and "UserPreferences" in c:
                ok("entities.py: uses UserSecurity + UserPreferences ✓")
            if "username: str" in c and "username: str | None" not in c:
                ok("entities.py: username NOT NULL ✓")
            else:
                issues.append("entities.py: username should be `str` (NOT NULL)")
        else:
            issues.append(f"NOT FOUND: {entities}")

        enums = self.root / f"{self.mod_root}/domain/enums.py"
        if enums.exists():
            c = enums.read_text(encoding="utf-8")
            if "class UserStatus" in c and "class OnlineStatus" in c:
                ok("enums.py: UserStatus + OnlineStatus ✓")
            else:
                issues.append("enums.py: missing UserStatus/OnlineStatus")
            if "def to_role" in c:
                ok("enums.py: LegacyRoleId.to_role() ✓")
            else:
                issues.append("enums.py: missing LegacyRoleId.to_role()")
        else:
            issues.append(f"NOT FOUND: {enums}")

        models = self.root / f"{self.mod_root}/infrastructure/models.py"
        if models.exists():
            c = models.read_text(encoding="utf-8")
            if "BigInteger" in c and "Identity(" in c:
                ok("models.py: BigInteger + Identity ✓")
            else:
                issues.append("models.py: missing BigInteger/Identity")
            if "active_status" in c:
                ok("models.py: active_status ✓")
            else:
                issues.append("models.py: missing active_status")
            if "username: Mapped[str] = mapped_column" in c and "nullable=False" in c:
                ok("models.py: username NOT NULL ✓")
        else:
            issues.append(f"NOT FOUND: {models}")

        auth_models = self.root / f"{self.auth_root}/infrastructure/models.py"
        if auth_models.exists():
            c = auth_models.read_text(encoding="utf-8")
            if "user_id: Mapped[int]" in c:
                ok("auth/models.py: user_id Mapped[int] ✓")
            else:
                issues.append("auth/models.py: user_id still not int")

        auth_vo = self.root / f"{self.auth_root}/domain/value_objects.py"
        if auth_vo.exists():
            c = auth_vo.read_text(encoding="utf-8")
            if "sub: str" in c:
                ok("auth/value_objects.py: sub: str ✓")
            else:
                issues.append("auth/value_objects.py: sub still UUID")

        sql_dir = self.root / self.sql_dir
        for name in ("V010__alter_users_bigint_id.sql",
                     "V011__alter_auth_fk_bigint.sql"):
            p = sql_dir / name
            if p.exists():
                ok(f"SQL: {name}")
            else:
                issues.append(f"SQL NOT FOUND: {name}")

        print()
        if issues:
            info("═" * 60)
            warn(f"พบ {len(issues)} ปัญหา:")
            for i, msg in enumerate(issues, 1):
                err(f"  {i}. {msg}")
            info("═" * 60)
        else:
            info("═" * 60)
            ok("ALL CHECKS PASSED ✓")
            info("═" * 60)

    def run_all(self) -> None:
        self.update_domain()
        self.update_infrastructure()
        self.update_application()
        self.update_presentation()
        self.update_auth_fk()
        self.update_auth_vo()
        self.update_auth_mappers()
        self.update_cache_mappers()
        self.create_sql()
        self.sql_auth_fk()

    def summary(self) -> None:
        print()
        info("═" * 60)
        ok(f"DONE — user module update (v{VERSION})")
        info(f"  Written : {len(self.writer.written)} files")
        info(f"  Backups : {len(self.writer.backups)} files")
        info("═" * 60)
        print()
        print(f"  {C.YELLOW}Next steps:{C.RESET}")
        print(f"    1. Verify:      python update_module_user.py verify")
        print(f"    2. Backup DB:   pg_dump -t erp_users -t sd_user > backup.sql")
        print(f"    3. Apply V010:  psql $DATABASE_URL -f db/migrations/V010__alter_users_bigint_id.sql")
        print(f"    4. Apply V011:  psql $DATABASE_URL -f db/migrations/V011__alter_auth_fk_bigint.sql")
        print(f"    5. Restart:     uvicorn app.app:app --reload")
        print(f"    6. {C.RED}Force re-login — all existing JWT invalid{RESET}")
        print()


HELP = f"""
═══════════════════════════════════════════════════════════════
  update_module_user.py v{VERSION}
  Purpose: UUID → BIGINT + migrate sd_user → erp_users
═══════════════════════════════════════════════════════════════

  USAGE
    python update_module_user.py <action> [module] [options]

  ACTIONS
    update-domain        — entities, enums, value_objects, exceptions
    update-infrastructure— models (BigInteger ID + sd_user columns)
    update-application   — mappers, use_cases
    update-presentation  — schemas
    update-auth-fk       — auth models user_id → BIGINT
    update-auth-vo       — auth value_objects sub → str
    update-auth-mappers  — auth mappers UUID(sub) → int(sub)
    update-cache-mappers — cache mappers UUID → int
    sql                  — V010 (ALTER + migrate sd_user)
    sql-auth-fk          — V011 (ALTER auth FK)
    verify               — ตรวจสอบ
    all                  — ทำทั้งหมด
    help                 — แสดง help

  EXAMPLES
    python update_module_user.py all user --force
    python update_module_user.py update-domain --force
    python update_module_user.py verify

  ⚠️  SIDE EFFECTS
    • JWT sub: UUID → str(int)  → existing tokens INVALID
    • Session cookies → force re-login
    • auth.user_id FK changes   → sessions may be dropped
    • User ids regenerated on BIGINT (10000000000+)
    • sd_user data migrated → erp_users_new → renamed
═══════════════════════════════════════════════════════════════
"""


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", nargs="?", default="help")
    parser.add_argument("module", nargs="?", default="user")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--help", action="store_true")

    args, _ = parser.parse_known_args()

    if args.help or args.action == "help":
        print(HELP)
        return 0

    root = Path(args.project_root).resolve()
    if not root.exists():
        err(f"Project root not found: {root}")
        return 1

    gen = UserModuleUpdater(
        project_root=root, module=args.module, force=args.force,
    )

    print()
    info("═" * 60)
    info(f"  MODULE  : {gen.module}")
    info(f"  ACTION  : {args.action}")
    info(f"  VERSION : {VERSION}")
    info("═" * 60)

    action_map = {
        "update-domain": gen.update_domain,
        "update-infrastructure": gen.update_infrastructure,
        "update-application": gen.update_application,
        "update-presentation": gen.update_presentation,
        "update-auth-fk": gen.update_auth_fk,
        "update-auth-vo": gen.update_auth_vo,
        "update-auth-mappers": gen.update_auth_mappers,
        "update-cache-mappers": gen.update_cache_mappers,
        "sql": gen.create_sql,
        "sql-auth-fk": gen.sql_auth_fk,
        "verify": gen.verify,
        "all": gen.run_all,
    }

    if args.action not in action_map:
        err(f"Unknown action: {args.action}")
        print(HELP)
        return 1

    try:
        action_map[args.action]()
    except Exception as e:
        err(f"Aborted: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if args.action != "verify":
        gen.summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())