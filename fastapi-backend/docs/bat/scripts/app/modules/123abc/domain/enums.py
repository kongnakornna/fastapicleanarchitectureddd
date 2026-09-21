"""123Abc enums — Enum ของ 123abc"""
from enum import StrEnum


class 123AbcStatus(StrEnum):
    """123AbcStatus — สถานะของ 123abc"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"