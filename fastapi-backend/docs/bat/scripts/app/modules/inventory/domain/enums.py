"""Inventory enums — Enum ของ inventory"""
from enum import StrEnum


class InventoryStatus(StrEnum):
    """InventoryStatus — สถานะของ inventory"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"