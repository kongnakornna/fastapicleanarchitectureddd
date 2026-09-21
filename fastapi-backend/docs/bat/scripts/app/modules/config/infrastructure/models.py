"""
Infrastructure Models — โมเดลฐานข้อมูล
ConfigEntryModel: ตาราง config_entries (per-tenant schema)
"""

from __future__ import annotations

from core.infrastructure.models import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    String,
    Text,
    UniqueConstraint,
)


class ConfigEntryModel(BaseModel):
    """
    ConfigEntry ORM — ตาราง config_entries
    อยู่ใน schema ของ tenant: tenant_{tid}.config_entries
    """

    __tablename__ = "config_entries"
    __table_args__ = (
        UniqueConstraint("key", "scope", "scope_id", name="uq_config_key_scope"),
    )

    key = Column(String(200), nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), nullable=False, default="string")
    scope = Column(String(20), nullable=False, index=True)
    scope_id = Column(String(36), nullable=False, index=True)
    is_secret = Column(Boolean, default=False, nullable=False)
    description = Column(Text, default="", nullable=False)
