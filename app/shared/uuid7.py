"""app.shared.uuid7 — RFC 9562 UUID v7 (time-ordered)

TH: UUID v7 — เรียงตามเวลา (timestamp ระดับ ms) + randomness
EN: UUID v7 — time-ordered (ms-precision timestamp) + randomness

ทำไม UUID v7?
  • เร็วกว่า UUID v4 บน B-tree index (sequential locality)
  • ยัง global unique เหมือน v4
  • เรียงได้ตามเวลา → ORDER BY created_at ไม่จำเป็น
  • ปลอดภัยกว่า ULID (128-bit vs 128-bit แต่ v7 มี variant/version bits)

Structure (RFC 9562):
   0                   1                   2                   3
   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                           unix_ts_ms                          |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |          unix_ts_ms           |  ver  |       rand_a          |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |var|                        rand_b                             |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
  |                            rand_b                             |
  +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

Design:
  • Pure Python, ไม่มี external deps
  • Monotonic counter (rand_a) เพื่อรับประกัน ordering ภายใน ms เดียวกัน
  • Thread-safe (ใช้ lock)
  • รองรับการแปลง ↔ UUID, str, int, bytes, และคืน timestamp
  • Drop-in compatible กับ uuid.UUID (คืน uuid.UUID เสมอ)
"""
from __future__ import annotations

import os
import struct
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Union


# ═══════════════════════════════════════════════════════════════
#  Constants (RFC 9562)
# ═══════════════════════════════════════════════════════════════
_UUID_VERSION = 7
_VARIANT_RFC = 0b10  # RFC 4122/9562 variant

# Bit masks
_MASK_48 = (1 << 48) - 1
_MASK_12 = (1 << 12) - 1
_MASK_62 = (1 << 62) - 1


# ═══════════════════════════════════════════════════════════════
#  Monotonic state (สำหรับ same-millisecond ordering)
# ═══════════════════════════════════════════════════════════════
_lock = threading.Lock()
_last_ms: int = 0
_last_counter: int = 0
_max_counter: int = (1 << 12) - 1  # 12 bits → 4096 values/ms


def _next_counter_ms() -> tuple[int, int]:
    """TH: คืน (timestamp_ms, counter) แบบ monotonic
    | EN: return (timestamp_ms, counter) monotonic pair

    ถ้า ms เดิม → เพิ่ม counter
    ถ้า ms ใหม่ → reset counter = 0
    ถ้า counter เต็ม → รอ ms ถัดไป (หรือ overflow → reset)
    """
    global _last_ms, _last_counter

    with _lock:
        now_ms = int(time.time() * 1000)

        if now_ms > _last_ms:
            _last_ms = now_ms
            _last_counter = 0
            return _last_ms, _last_counter

        # same ms → เพิ่ม counter
        if _last_counter < _max_counter:
            _last_counter += 1
            return _last_ms, _last_counter

        # counter overflow → borrow from future ms (safe in practice)
        _last_ms += 1
        _last_counter = 0
        return _last_ms, _last_counter


# ═══════════════════════════════════════════════════════════════
#  Core generator
# ═══════════════════════════════════════════════════════════════
def uuid7() -> uuid.UUID:
    """TH: สร้าง UUID v7 ใหม่ | EN: generate a new UUID v7

    Returns:
        uuid.UUID (version=7, variant=RFC4122)
    """
    ts_ms, counter = _next_counter_ms()

    # 48-bit timestamp
    ts_ms &= _MASK_48

    # rand_a = 12-bit counter (monotonic within same ms)
    rand_a = counter & _MASK_12

    # rand_b = 62 bits random
    rand_b = int.from_bytes(os.urandom(8), "big") & _MASK_62

    # Compose 128-bit integer
    value = (
        (ts_ms << 80)
        | (_UUID_VERSION << 76)
        | (rand_a << 64)
        | (_VARIANT_RFC << 62)
        | rand_b
    )

    return uuid.UUID(int=value)


def uuid7_as_str() -> str:
    """TH: สร้าง UUID v7 เป็น string | EN: UUID v7 as string"""
    return str(uuid7())


def uuid7_as_int() -> int:
    """TH: สร้าง UUID v7 เป็น int | EN: UUID v7 as int"""
    return uuid7().int


# ═══════════════════════════════════════════════════════════════
#  Parsing & introspection
# ═══════════════════════════════════════════════════════════════
def is_uuid7(value: Union[str, uuid.UUID]) -> bool:
    """TH: ตรวจว่าเป็น UUID v7 หรือไม่ | EN: check if UUID v7"""
    try:
        u = _coerce(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return u.version == _UUID_VERSION


def extract_timestamp_ms(value: Union[str, uuid.UUID]) -> Optional[int]:
    """TH: ดึง unix timestamp (ms) จาก UUID v7
    | EN: extract unix timestamp (ms) from UUID v7

    Returns:
        milliseconds since epoch, หรือ None ถ้าไม่ใช่ v7
    """
    try:
        u = _coerce(value)
    except (ValueError, AttributeError, TypeError):
        return None
    if u.version != _UUID_VERSION:
        return None
    return (u.int >> 80) & _MASK_48


def extract_datetime(value: Union[str, uuid.UUID]) -> Optional[datetime]:
    """TH: ดึง datetime (UTC) จาก UUID v7
    | EN: extract UTC datetime from UUID v7"""
    ts_ms = extract_timestamp_ms(value)
    if ts_ms is None:
        return None
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)


def extract_counter(value: Union[str, uuid.UUID]) -> Optional[int]:
    """TH: ดึง counter (12-bit) จาก UUID v7
    | EN: extract 12-bit counter from UUID v7"""
    try:
        u = _coerce(value)
    except (ValueError, AttributeError, TypeError):
        return None
    if u.version != _UUID_VERSION:
        return None
    return (u.int >> 64) & _MASK_12


# ═══════════════════════════════════════════════════════════════
#  Conversion helpers
# ═══════════════════════════════════════════════════════════════
def _coerce(value: Union[str, uuid.UUID, bytes, int]) -> uuid.UUID:
    """TH: แปลงค่าต่าง ๆ เป็น uuid.UUID | EN: coerce to uuid.UUID"""
    if isinstance(value, uuid.UUID):
        return value
    if isinstance(value, str):
        return uuid.UUID(value)
    if isinstance(value, int):
        return uuid.UUID(int=value)
    if isinstance(value, (bytes, bytearray)):
        if len(value) != 16:
            raise ValueError(f"bytes must be 16, got {len(value)}")
        return uuid.UUID(bytes=bytes(value))
    raise TypeError(f"cannot coerce {type(value).__name__} to UUID")


def from_str(value: str) -> uuid.UUID:
    """TH: parse string → UUID | EN: parse string to UUID"""
    return _coerce(value)


def from_bytes(value: bytes) -> uuid.UUID:
    """TH: parse 16 bytes → UUID | EN: parse 16 bytes to UUID"""
    return _coerce(value)


def from_int(value: int) -> uuid.UUID:
    """TH: parse int → UUID | EN: parse int to UUID"""
    return _coerce(value)


def to_bytes(value: Union[str, uuid.UUID]) -> bytes:
    """TH: UUID → 16 bytes | EN: UUID to 16 bytes"""
    return _coerce(value).bytes


def to_int(value: Union[str, uuid.UUID]) -> int:
    """TH: UUID → int | EN: UUID to int"""
    return _coerce(value).int


def to_str(value: Union[str, uuid.UUID]) -> str:
    """TH: UUID → string | EN: UUID to string"""
    return str(_coerce(value))


# ═══════════════════════════════════════════════════════════════
#  Sortable / comparable helpers
# ═══════════════════════════════════════════════════════════════
def sort_key(value: Union[str, uuid.UUID]) -> bytes:
    """TH: คืน sort key (bytes) สำหรับเรียงลำดับ
    | EN: sort key (bytes) for ordering"""
    return _coerce(value).bytes


def is_before(a: Union[str, uuid.UUID], b: Union[str, uuid.UUID]) -> bool:
    """TH: a มาก่อน b หรือไม่ | EN: is a before b?"""
    return sort_key(a) < sort_key(b)


def is_after(a: Union[str, uuid.UUID], b: Union[str, uuid.UUID]) -> bool:
    """TH: a มาหลัง b หรือไม่ | EN: is a after b?"""
    return sort_key(a) > sort_key(b)


# ═══════════════════════════════════════════════════════════════
#  Class wrapper (สะดวกเวลาใช้งานใน DDD entity)
# ═══════════════════════════════════════════════════════════════
class UUID7:
    """TH: wrapper คลาสสำหรับ UUID v7
    | EN: UUID v7 wrapper class

    Usage:
        uid = UUID7.new()
        str(uid)                # '018d...'
        uid.datetime            # datetime ของ timestamp
        uid.counter             # 12-bit counter
        UUID7.parse(s)          # parse จาก string
    """

    __slots__ = ("_uuid",)

    def __init__(self, value: uuid.UUID) -> None:
        if value.version != _UUID_VERSION:
            raise ValueError(
                f"expected UUID v7, got v{value.version}",
            )
        self._uuid = value

    # ─── Factories ───────────────────────────────────────────

    @classmethod
    def new(cls) -> "UUID7":
        """TH: สร้างใหม่ | EN: create new"""
        return cls(uuid7())

    @classmethod
    def parse(cls, value: Union[str, uuid.UUID, bytes, int]) -> "UUID7":
        """TH: parse จากค่าต่าง ๆ | EN: parse from various"""
        return cls(_coerce(value))

    @classmethod
    def try_parse(
        cls, value: Union[str, uuid.UUID, bytes, int],
    ) -> Optional["UUID7"]:
        """TH: parse แบบไม่โยน exception | EN: safe parse"""
        try:
            return cls.parse(value)
        except (ValueError, TypeError, AttributeError):
            return None

    # ─── Properties ──────────────────────────────────────────

    @property
    def uuid(self) -> uuid.UUID:
        return self._uuid

    @property
    def timestamp_ms(self) -> int:
        return extract_timestamp_ms(self._uuid) or 0

    @property
    def datetime(self) -> datetime:
        return extract_datetime(self._uuid) or datetime.now(timezone.utc)

    @property
    def counter(self) -> int:
        return extract_counter(self._uuid) or 0

    # ─── Conversion ──────────────────────────────────────────

    def as_str(self) -> str:
        return str(self._uuid)

    def as_int(self) -> int:
        return self._uuid.int

    def as_bytes(self) -> bytes:
        return self._uuid.bytes

    # ─── Dunder ──────────────────────────────────────────────

    def __str__(self) -> str:
        return str(self._uuid)

    def __repr__(self) -> str:
        return f"UUID7({self._uuid})"

    def __hash__(self) -> int:
        return hash(self._uuid)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UUID7):
            return self._uuid == other._uuid
        if isinstance(other, uuid.UUID):
            return self._uuid == other
        if isinstance(other, str):
            try:
                return self._uuid == uuid.UUID(other)
            except ValueError:
                return False
        return NotImplemented

    def __lt__(self, other: "UUID7") -> bool:
        return self._uuid < other._uuid

    def __le__(self, other: "UUID7") -> bool:
        return self._uuid <= other._uuid

    def __gt__(self, other: "UUID7") -> bool:
        return self._uuid > other._uuid

    def __ge__(self, other: "UUID7") -> bool:
        return self._uuid >= other._uuid


# ═══════════════════════════════════════════════════════════════
#  SQLAlchemy helper (optional)
# ═══════════════════════════════════════════════════════════════
def uuid7_default() -> uuid.UUID:
    """TH: default factory สำหรับ SQLAlchemy (ใช้กับ Python-side default)
    | EN: default factory for SQLAlchemy (Python-side default)

    Usage:
        from sqlalchemy import Column
        from sqlalchemy.dialects.postgresql import UUID as PGUUID
        from app.shared.uuid7 import uuid7_default

        id = Column(
            PGUUID(as_uuid=True), primary_key=True,
            default=uuid7_default,
        )
    """
    return uuid7()


# ═══════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════
__all__ = [
    # Core
    "uuid7", "uuid7_as_str", "uuid7_as_int", "uuid7_default",
    # Parsing
    "is_uuid7", "extract_timestamp_ms", "extract_datetime",
    "extract_counter",
    # Conversion
    "from_str", "from_bytes", "from_int",
    "to_bytes", "to_int", "to_str",
    # Sorting
    "sort_key", "is_before", "is_after",
    # Wrapper
    "UUID7",
]