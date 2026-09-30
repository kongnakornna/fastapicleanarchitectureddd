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
