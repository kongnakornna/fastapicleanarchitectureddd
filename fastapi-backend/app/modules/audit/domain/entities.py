"""
Audit Log Entity — เอนทิตีบันทึก audit
Audit Log Entity — audit log entity (append-only, immutable)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from audit.domain.exceptions import (
    AuditDomainError,
    AuditImmutableDomainError,
    AuditMissingActorError,
    AuditMissingResourceError,
)
from app.shared.base_entity import BaseEntity


@dataclass
class AuditLog(BaseEntity):
    """
    Audit log entity — เอนทิตีบันทึก audit

    Immutable append-only record of every action touching money/stock/critical data.
    บันทึก immutable แบบ append-only สำหรับทุก action ที่แตะเงิน/สต็อก/ข้อมูลสำคัญ
    """

    action: str = ""
    resource_type: str = ""
    resource_id: str = ""
    actor_id: str = ""
    before_state: dict[str, Any] = field(default_factory=dict)
    after_state: dict[str, Any] = field(default_factory=dict)
    changes: list[dict[str, Any]] = field(default_factory=list)
    ip_address: str = ""
    user_agent: str = ""
    correlation_id: str = ""
    severity: str = "INFO"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Fields that may be mutated internally after construction
    # ฟิลด์ที่อนุญาตให้แก้ภายในหลังสร้าง
    _MUTABLE_FIELDS = frozenset({"changes", "id", "created_at", "updated_at"})
    # Flag set True after __post_init__ completes
    _frozen: bool = False

    def __post_init__(self) -> None:
        # Allow BaseEntity to set its own fields before we freeze
        # อนุญาตให้ BaseEntity set field ของตัวเองก่อน freeze
        super().__post_init__()
        self._validate()
        if not self.changes:
            self.changes = self.diff()
        # Freeze after init — หลัง init ห้ามแก้
        object.__setattr__(self, "_frozen", True)

    def _validate(self) -> None:
        """Validate invariants — ตรวจสอบ invariants"""
        if not self.action:
            raise AuditDomainError("Action is required")
        if not self.resource_type or not self.resource_id:
            raise AuditMissingResourceError()
        if not self.actor_id:
            raise AuditMissingActorError()

    def diff(self) -> list[dict[str, Any]]:
        """
        Compute diff between before/after — คำนวณส่วนต่างระหว่าง before/after

        Returns list of {field, before, after} for changed keys only.
        """
        keys = set(self.before_state) | set(self.after_state)
        return [
            {
                "field": k,
                "before": self.before_state.get(k),
                "after": self.after_state.get(k),
            }
            for k in sorted(keys)
            if self.before_state.get(k) != self.after_state.get(k)
        ]

    def is_immutable(self) -> bool:
        """Audit log is always immutable — audit log เป็น immutable เสมอ"""
        return True

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Block mutation after freeze — บล็อคการแก้ไขหลัง freeze

        Allows initial dataclass field assignment before _frozen=True.
        """
        if getattr(self, "_frozen", False) and name not in self._MUTABLE_FIELDS:
            raise AuditImmutableDomainError(f"cannot modify '{name}'")
        object.__setattr__(self, name, value)
