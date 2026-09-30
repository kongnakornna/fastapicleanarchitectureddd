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
