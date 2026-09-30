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
