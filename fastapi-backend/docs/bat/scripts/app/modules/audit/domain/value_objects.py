"""
Audit Value Objects — วัตถุค่า audit
Audit Value Objects — value objects for audit module
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChangeSet:
    """
    Change set VO — วัตถุชุดการเปลี่ยนแปลง

    Immutable set of field-level changes.
    ชุดการเปลี่ยนแปลงระดับ field แบบ immutable
    """

    entity: str
    entity_id: str
    changes: tuple[tuple[str, Any, Any], ...]  # (field, before, after)

    def is_empty(self) -> bool:
        """Check if changeset is empty — เช็คว่าว่างเปล่าหรือไม่"""
        return len(self.changes) == 0

    def fields(self) -> tuple[str, ...]:
        """List changed fields — แสดง field ที่เปลี่ยนแปลง"""
        return tuple(c[0] for c in self.changes)

    def to_list(self) -> list[dict[str, Any]]:
        """Convert to list of dicts — แปลงเป็น list ของ dict"""
        return [{"field": f, "before": b, "after": a} for f, b, a in self.changes]

    @classmethod
    def from_dicts(
        cls,
        entity: str,
        entity_id: str,
        before: dict[str, Any],
        after: dict[str, Any],
    ) -> ChangeSet:
        """Build ChangeSet from before/after dicts — สร้าง ChangeSet จาก dict"""
        keys = set(before) | set(after)
        changes = tuple(
            (k, before.get(k), after.get(k))
            for k in sorted(keys)
            if before.get(k) != after.get(k)
        )
        return cls(entity=entity, entity_id=entity_id, changes=changes)


@dataclass(frozen=True)
class AuditContext:
    """Audit context VO — วัตถุบริบท audit"""

    actor_id: str
    correlation_id: str
    ip_address: str = ""
    user_agent: str = ""
