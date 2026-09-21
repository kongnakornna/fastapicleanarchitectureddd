"""Money enums — Enum ของ money"""
from enum import StrEnum


class MoneyStatus(StrEnum):
    """MoneyStatus — สถานะของ money"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"