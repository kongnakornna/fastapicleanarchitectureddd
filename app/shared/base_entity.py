"""app.shared.base_entity — Domain entity base ที่ทุก module ใช้ร่วม

TH: Base class สำหรับ domain entities (DDD)
EN: Base class for domain entities (DDD)

Design:
  • Pydantic v2 เป็นหลัก (matches modules ที่ generate ไว้)
  • Immutable option (`FrozenEntity`) + Mutable option (`BaseEntity`)
  • UUID v7 id (time-ordered)
  • Domain event collection (DDD)
  • Optimistic locking (version)
  • Snapshot / restore สำหรับ event sourcing (light)
  • to_dict() / from_dict() / to_orm_dict() helpers
  • Dataclass variant สำหรับ lightweight use
  • Python 3.10+
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from app.shared.uuid7 import uuid7_default

T = TypeVar("T", bound="BaseEntity")


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ═══════════════════════════════════════════════════════════════
#  BaseEntity — Pydantic v2 (recommended)
# ═══════════════════════════════════════════════════════════════
class BaseEntity(BaseModel):
    """TH: Domain entity base (Pydantic v2)
    | EN: Domain entity base (Pydantic v2)

    Usage:
        class User(BaseEntity):
            name: str
            email: str

        u = User(tenant_id=tid, name="Jane", email="j@x.com")
        u.add_event(UserCreated(user_id=u.id))
        events = u.pull_events()
    """

    # ─── Pydantic config ────────────────────────────────────

    model_config = ConfigDict(
        from_attributes=True,       # ORM row → entity
        populate_by_name=True,      # รองรับ alias
        extra="ignore",             # ไม่ error ถ้า ORM มี column เกิน
        validate_assignment=True,   # validate ตอน assign
        arbitrary_types_allowed=True,
    )

    # ─── Core fields ────────────────────────────────────────

    id: uuid.UUID = Field(default_factory=uuid7_default)
    tenant_id: uuid.UUID
    version: int = Field(default=1, ge=0)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)

    # ─── Domain event buffer (PrivateAttr → ไม่ถูก serialize)
    _events: list[Any] = PrivateAttr(default_factory=list)
    _snapshot: Optional[dict[str, Any]] = PrivateAttr(default=None)

    # ─── Class-level config ─────────────────────────────────

    _events_enabled: ClassVar[bool] = True

    # ─── Lifecycle ──────────────────────────────────────────

    def mark_updated(self) -> None:
        """TH: อัปเดต updated_at + bump version | EN: touch timestamps"""
        self.updated_at = _now()
        self.bump_version()

    def bump_version(self) -> None:
        """TH: เพิ่ม version (optimistic lock) | EN: increment version"""
        self.version = (self.version or 0) + 1

    # ─── Domain events (DDD) ────────────────────────────────

    def add_event(self, event: Any) -> None:
        """TH: เพิ่ม domain event เข้า buffer | EN: add domain event"""
        if not self._events_enabled:
            return
        self._events.append(event)

    def pull_events(self) -> list[Any]:
        """TH: ดึง + ล้าง event buffer | EN: drain event buffer"""
        events = list(self._events)
        self._events.clear()
        return events

    def peek_events(self) -> list[Any]:
        """TH: ดึง event โดยไม่ล้าง | EN: peek events"""
        return list(self._events)

    def clear_events(self) -> None:
        """TH: ล้าง event buffer | EN: clear events"""
        self._events.clear()

    @property
    def has_events(self) -> bool:
        return len(self._events) > 0

    # ─── Snapshot / restore (light event sourcing) ──────────

    def take_snapshot(self) -> None:
        """TH: บันทึก snapshot ปัจจุบัน | EN: capture snapshot"""
        self._snapshot = self.model_dump()

    def restore_snapshot(self) -> bool:
        """TH: คืนค่าจาก snapshot | EN: restore from snapshot"""
        if self._snapshot is None:
            return False
        for key, value in self._snapshot.items():
            try:
                setattr(self, key, value)
            except (ValueError, TypeError):
                pass
        return True

    def has_snapshot(self) -> bool:
        return self._snapshot is not None

    # ─── Serialization ──────────────────────────────────────

    def to_dict(
        self,
        *,
        exclude: tuple[str, ...] = (),
        exclude_none: bool = False,
    ) -> dict[str, Any]:
        """TH: แปลงเป็น dict (พร้อม stringify UUID/datetime)
        | EN: entity → dict"""
        data = self.model_dump(exclude=set(exclude), exclude_none=exclude_none)
        return _stringify(data)

    def to_json_dict(self) -> dict[str, Any]:
        """TH: JSON-safe dict | EN: JSON-safe dict"""
        return self.to_dict()

    def to_orm_dict(
        self, *, exclude: tuple[str, ...] = ("version",),
    ) -> dict[str, Any]:
        """TH: dict สำหรับ upsert ORM (ไม่รวม PK ถ้าจำเป็น)
        | EN: dict for ORM upsert"""
        skip = set(exclude) | {"created_at", "updated_at"}
        return self.model_dump(exclude=skip)

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """TH: สร้าง entity จาก dict | EN: entity from dict"""
        return cls(**data)

    @classmethod
    def from_orm(cls: type[T], row: Any) -> T:
        """TH: สร้าง entity จาก ORM row (from_attributes)
        | EN: entity from ORM row"""
        return cls.model_validate(row)

    # ─── Comparison ─────────────────────────────────────────

    def __eq__(self, other: object) -> bool:
        """TH: เทียบจาก (class, id) | EN: identity by (class, id)"""
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.id))

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} "
            f"id={self.id} tenant={self.tenant_id} v={self.version}>"
        )


# ═══════════════════════════════════════════════════════════════
#  FrozenEntity — immutable variant
# ═══════════════════════════════════════════════════════════════
class FrozenEntity(BaseEntity):
    """TH: entity แบบ immutable (value object-like)
    | EN: immutable entity (value-object style)"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore",
        frozen=True,                # ← ปิดการ mutate
        arbitrary_types_allowed=True,
    )

    # ─── Immutable helpers ──────────────────────────────────

    def with_changes(self: T, **changes: Any) -> T:
        """TH: คืน entity ใหม่พร้อมการเปลี่ยนแปลง
        | EN: return new entity with changes"""
        data = self.model_dump()
        data.update(changes)
        return type(self)(**data)


# ═══════════════════════════════════════════════════════════════
#  DataclassEntity — lightweight (no Pydantic)
# ═══════════════════════════════════════════════════════════════
@dataclass
class DataclassEntity:
    """TH: entity แบบ dataclass (lightweight, ไม่ validate)
    | EN: dataclass entity (lightweight, no validation)

    เหมาะกับ:
      • Domain logic ที่ไม่ต้องการ Pydantic
      • Hot path ที่ validation เป็น overhead
      • Unit test ที่ต้องการ control เต็ม
    """

    id: uuid.UUID = field(default_factory=uuid7_default)
    tenant_id: uuid.UUID = field(default_factory=lambda: uuid.UUID(int=0))
    version: int = 1
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def mark_updated(self) -> None:
        self.updated_at = _now()
        self.version = (self.version or 0) + 1

    def to_dict(self, *, exclude: tuple[str, ...] = ()) -> dict[str, Any]:
        return _stringify({
            k: v for k, v in self.__dict__.items() if k not in exclude
        })

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DataclassEntity):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.id))


# ═══════════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════════
def _stringify(data: dict[str, Any]) -> dict[str, Any]:
    """TH: แปลง UUID/datetime เป็น string (recursive)
    | EN: stringify UUID/datetime recursively"""
    out: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, uuid.UUID):
            out[key] = str(value)
        elif isinstance(value, datetime):
            out[key] = value.isoformat()
        elif isinstance(value, dict):
            out[key] = _stringify(value)
        elif isinstance(value, list):
            out[key] = [
                str(x) if isinstance(x, uuid.UUID)
                else x.isoformat() if isinstance(x, datetime)
                else _stringify(x) if isinstance(x, dict)
                else x
                for x in value
            ]
        else:
            out[key] = value
    return out


def attach_event(entity: BaseEntity, event: Any) -> None:
    """TH: helper สำหรับเพิ่ม event (อ่านง่าย)
    | EN: helper to attach event"""
    entity.add_event(event)


def mark_updated(entity: BaseEntity) -> None:
    """TH: helper mark_updated | EN: helper mark updated"""
    entity.mark_updated()


# ═══════════════════════════════════════════════════════════════
#  Type alias
# ═══════════════════════════════════════════════════════════════
EntityId = uuid.UUID
TenantId = uuid.UUID
UserId = uuid.UUID


# ═══════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════
__all__ = [
    "BaseEntity",
    "FrozenEntity",
    "DataclassEntity",
    "EntityId",
    "TenantId",
    "UserId",
    "attach_event",
    "mark_updated",
]
