"""
Config Module — โมดูลการตั้งค่า
Module 0.5: Cross-cutting configuration for GLOBAL → TENANT → USER override.

Config Module — รองรับ 3 ระดับ: GLOBAL, TENANT, USER
"""

from __future__ import annotations

__version__ = "1.0.0"

__all__ = [
    "application",
    "domain",
    "infrastructure",
    "presentation",
]
