"""app.shared.pagination — pagination helpers ที่ทุก module ใช้ร่วม

TH: ระบบ pagination กลาง — รองรับ offset + cursor
EN: Central pagination — supports offset + cursor-based

Design:
  • Offset-based: Page[T] → เหมาะกับ admin UI, จำนวนน้อย
  • Cursor-based: CursorPage[T] → เหมาะกับ feed, จำนวนมาก, เรียงตามเวลา
  • SortSpec → เรียงลำดับ + validate
  • Cursor encode/decode แบบ base64 + HMAC signature (กัน tamper)
  • SQLAlchemy helpers (optional, ไม่ import บังคับ)
  • FastAPI dependency (PaginationParams) พร้อมใช้
  • Generic types (PEP 695 style) — Python 3.10+ ใช้ TypeVar
  • ไม่มี external deps
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import math
import os
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Generic, Iterable, Iterator, Literal, Optional,
    Sequence, TypeVar, Union,
)


# ═══════════════════════════════════════════════════════════════
#  Type variables
# ═══════════════════════════════════════════════════════════════
T = TypeVar("T")
K = TypeVar("K")  # cursor key type (str | int | uuid ...)

SortOrder = Literal["asc", "desc"]


# ═══════════════════════════════════════════════════════════════
#  Constants
# ═══════════════════════════════════════════════════════════════
DEFAULT_PAGE_SIZE = 20
DEFAULT_MAX_PAGE_SIZE = 100
ABSOLUTE_MAX_PAGE_SIZE = 1000

_CURSOR_SECRET = os.getenv("CURSOR_SECRET", "dev-cursor-secret-change-me")
_CURSOR_VERSION = 1


# ═══════════════════════════════════════════════════════════════
#  SortSpec — specification ของการเรียง
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class SortSpec:
    """TH: ข้อกำหนดการเรียงลำดับ | EN: Sort specification

    Usage:
        spec = SortSpec(field="created_at", order="desc")
        spec = SortSpec.parse("created_at:desc")
    """

    field: str
    order: SortOrder = "desc"

    def __post_init__(self) -> None:
        if not self.field:
            raise ValueError("sort field required")
        if self.order not in ("asc", "desc"):
            raise ValueError(f"invalid order: {self.order}")

    @classmethod
    def parse(cls, raw: str, *, default_order: SortOrder = "desc") -> "SortSpec":
        """TH: parse จาก string 'field' หรือ 'field:desc' | EN: parse string"""
        if not raw:
            return cls(field="created_at", order=default_order)
        if ":" in raw:
            field_name, order = raw.split(":", 1)
            order = order.strip().lower()  # type: ignore[assignment]
            if order not in ("asc", "desc"):
                order = default_order
        else:
            field_name, order = raw, default_order
        return cls(field=field_name.strip(), order=order)  # type: ignore[arg-type]

    def to_dict(self) -> dict[str, str]:
        return {"field": self.field, "order": self.order}

    def __str__(self) -> str:
        return f"{self.field}:{self.order}"


# ═══════════════════════════════════════════════════════════════
#  PaginationParams — query params (ใช้กับ FastAPI ได้)
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class PaginationParams:
    """TH: พารามิเตอร์ pagination | EN: Pagination parameters

    Usage (FastAPI):
        from fastapi import Depends, Query

        async def list_items(
            page: int = Query(1, ge=1),
            limit: int = Query(20, ge=1, le=100),
            sort: str = Query("created_at:desc"),
        ):
            params = PaginationParams.from_query(page=page, limit=limit, sort=sort)
            ...
    """

    page: int = 1
    limit: int = DEFAULT_PAGE_SIZE
    sort: SortSpec = field(default_factory=lambda: SortSpec("created_at", "desc"))

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if self.limit < 1:
            raise ValueError("limit must be >= 1")
        if self.limit > ABSOLUTE_MAX_PAGE_SIZE:
            raise ValueError(f"limit exceeds max ({ABSOLUTE_MAX_PAGE_SIZE})")

    @property
    def offset(self) -> int:
        """TH: offset = (page - 1) * limit | EN: SQL offset"""
        return (self.page - 1) * self.limit

    @classmethod
    def from_query(
        cls,
        *,
        page: int = 1,
        limit: int = DEFAULT_PAGE_SIZE,
        sort: Union[str, SortSpec, None] = None,
        max_page_size: int = DEFAULT_MAX_PAGE_SIZE,
    ) -> "PaginationParams":
        """TH: สร้างจาก query params | EN: build from query params"""
        effective_limit = min(max(1, limit), max_page_size)
        effective_page = max(1, page)
        sort_spec = (
            sort if isinstance(sort, SortSpec)
            else SortSpec.parse(sort or "created_at:desc")
        )
        return cls(page=effective_page, limit=effective_limit, sort=sort_spec)

    def to_dict(self) -> dict[str, Any]:
        return {
            "page": self.page,
            "limit": self.limit,
            "offset": self.offset,
            "sort": self.sort.to_dict(),
        }

    def __str__(self) -> str:
        return f"PaginationParams(page={self.page}, limit={self.limit}, sort={self.sort})"


# ═══════════════════════════════════════════════════════════════
#  Page[T] — offset-based result
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class Page(Generic[T]):
    """TH: ผลลัพธ์แบบ offset pagination | EN: Offset-based page result

    Attributes:
        items:     รายการในหน้านี้
        total:     จำนวนทั้งหมด
        page:      หน้าปัจจุบัน (1-indexed)
        limit:     ขนาดหน้า
        sort:      การเรียงที่ใช้ (optional)
    """

    items: list[T]
    total: int
    page: int
    limit: int
    sort: Optional[SortSpec] = None

    def __post_init__(self) -> None:
        if self.total < 0:
            raise ValueError("total must be >= 0")
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if self.limit < 1:
            raise ValueError("limit must be >= 1")

    # ─── Properties ─────────────────────────────────────────

    @property
    def total_pages(self) -> int:
        """TH: จำนวนหน้าทั้งหมด | EN: total page count"""
        if self.limit <= 0:
            return 1
        return max(1, math.ceil(self.total / self.limit))

    @property
    def has_next(self) -> bool:
        """TH: มีหน้าถัดไปหรือไม่ | EN: has next page?"""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """TH: มีหน้าก่อนหรือไม่ | EN: has previous page?"""
        return self.page > 1

    @property
    def next_page(self) -> Optional[int]:
        return self.page + 1 if self.has_next else None

    @property
    def prev_page(self) -> Optional[int]:
        return self.page - 1 if self.has_prev else None

    @property
    def first_page(self) -> int:
        return 1

    @property
    def last_page(self) -> int:
        return self.total_pages

    @property
    def count(self) -> int:
        """TH: จำนวนในหน้านี้ | EN: items in this page"""
        return len(self.items)

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

    # ─── Transformations ────────────────────────────────────

    def map(self, fn: Callable[[T], K]) -> "Page[K]":
        """TH: map items → ชนิดใหม่ | EN: map items to a new type"""
        return Page(
            items=[fn(x) for x in self.items],
            total=self.total, page=self.page,
            limit=self.limit, sort=self.sort,
        )

    def filter(self, fn: Callable[[T], bool]) -> "Page[T]":
        """TH: กรอง items (total ไม่เปลี่ยน) | EN: filter items"""
        return Page(
            items=[x for x in self.items if fn(x)],
            total=self.total, page=self.page,
            limit=self.limit, sort=self.sort,
        )

    # ─── Serialization ──────────────────────────────────────

    def to_dict(
        self, *, item_serializer: Optional[Callable[[T], Any]] = None,
    ) -> dict[str, Any]:
        ser = item_serializer or (lambda x: x)
        return {
            "items": [ser(x) for x in self.items],
            "total": self.total,
            "page": self.page,
            "limit": self.limit,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
            "next_page": self.next_page,
            "prev_page": self.prev_page,
            "sort": self.sort.to_dict() if self.sort else None,
        }

    # ─── Iteration ──────────────────────────────────────────

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> T:
        return self.items[idx]

    def __bool__(self) -> bool:
        return bool(self.items)


# ═══════════════════════════════════════════════════════════════
#  CursorPage[T] — cursor-based result (แนะนำสำหรับ feed)
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class CursorPage(Generic[T]):
    """TH: ผลลัพธ์แบบ cursor pagination | EN: Cursor-based page result

    ข้อดี:
      • Performance คงที่ (keyset scan ผ่าน index)
      • ไม่มีปัญหาข้อมูลเปลี่ยนกลางหน้า (stable)
      • รองรับ real-time feed ได้
    """

    items: list[T]
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    limit: int = DEFAULT_PAGE_SIZE
    has_more: bool = False
    sort: Optional[SortSpec] = None

    # ─── Properties ─────────────────────────────────────────

    @property
    def count(self) -> int:
        return len(self.items)

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    @property
    def has_next(self) -> bool:
        return bool(self.next_cursor) and self.has_more

    @property
    def has_prev(self) -> bool:
        return bool(self.prev_cursor)

    # ─── Transformations ────────────────────────────────────

    def map(self, fn: Callable[[T], K]) -> "CursorPage[K]":
        return CursorPage(
            items=[fn(x) for x in self.items],
            next_cursor=self.next_cursor, prev_cursor=self.prev_cursor,
            limit=self.limit, has_more=self.has_more, sort=self.sort,
        )

    # ─── Serialization ──────────────────────────────────────

    def to_dict(
        self, *, item_serializer: Optional[Callable[[T], Any]] = None,
    ) -> dict[str, Any]:
        ser = item_serializer or (lambda x: x)
        return {
            "items": [ser(x) for x in self.items],
            "next_cursor": self.next_cursor,
            "prev_cursor": self.prev_cursor,
            "limit": self.limit,
            "has_more": self.has_more,
            "count": self.count,
            "sort": self.sort.to_dict() if self.sort else None,
        }

    # ─── Iteration ──────────────────────────────────────────

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        return bool(self.items)


# ═══════════════════════════════════════════════════════════════
#  Cursor encode/decode (HMAC-signed, tamper-resistant)
# ═══════════════════════════════════════════════════════════════
def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def _sign(payload: bytes) -> bytes:
    return hmac.new(_CURSOR_SECRET.encode("utf-8"), payload, hashlib.sha256).digest()


def encode_cursor(data: dict[str, Any]) -> str:
    """TH: encode cursor → string (signed) | EN: encode cursor (signed)

    Format: <version>.<payload_b64>.<sig_b64>
    """
    payload = {
        "v": _CURSOR_VERSION,
        **data,
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True, default=str)
    raw_bytes = raw.encode("utf-8")
    sig = _sign(raw_bytes)
    return f"{_CURSOR_VERSION}.{_b64encode(raw_bytes)}.{_b64encode(sig)}"


def decode_cursor(cursor: str) -> dict[str, Any]:
    """TH: decode cursor → dict (verify signature)
    | EN: decode cursor (verify signature)

    Raises:
        ValueError: cursor malformed หรือ signature ไม่ผ่าน
    """
    if not cursor:
        raise ValueError("empty cursor")

    parts = cursor.split(".")
    if len(parts) != 3:
        raise ValueError("invalid cursor format")

    try:
        version = int(parts[0])
    except ValueError as exc:
        raise ValueError("invalid cursor version") from exc

    if version != _CURSOR_VERSION:
        raise ValueError(f"unsupported cursor version: {version}")

    try:
        raw_bytes = _b64decode(parts[1])
        sig = _b64decode(parts[2])
    except Exception as exc:
        raise ValueError("cursor base64 decode failed") from exc

    expected_sig = _sign(raw_bytes)
    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("cursor signature mismatch")

    try:
        payload = json.loads(raw_bytes.decode("utf-8"))
    except Exception as exc:
        raise ValueError("cursor json decode failed") from exc

    payload.pop("v", None)
    return payload


def try_decode_cursor(cursor: Optional[str]) -> Optional[dict[str, Any]]:
    """TH: decode แบบไม่โยน exception | EN: safe decode"""
    if not cursor:
        return None
    try:
        return decode_cursor(cursor)
    except ValueError:
        return None


# ═══════════════════════════════════════════════════════════════
#  Cursor key helpers
# ═══════════════════════════════════════════════════════════════
def make_cursor_key(
    *,
    last_id: Any,
    last_value: Any = None,
    sort_field: str = "id",
    sort_order: SortOrder = "desc",
) -> str:
    """TH: สร้าง cursor จาก key ของ record ล่าสุด | EN: build cursor from last record"""
    return encode_cursor({
        "last_id": str(last_id),
        "last_value": str(last_value) if last_value is not None else None,
        "sort_field": sort_field,
        "sort_order": sort_order,
    })


def split_keyset_cursor(
    cursor: Optional[str],
) -> tuple[Optional[str], Optional[str], str, SortOrder]:
    """TH: แยก cursor → (last_id, last_value, sort_field, sort_order)
    | EN: split cursor into keyset parts"""
    payload = try_decode_cursor(cursor)
    if not payload:
        return None, None, "id", "desc"
    return (
        payload.get("last_id"),
        payload.get("last_value"),
        payload.get("sort_field", "id"),
        payload.get("sort_order", "desc"),
    )


# ═══════════════════════════════════════════════════════════════
#  In-memory pagination helpers (สำหรับ list/dict)
# ═══════════════════════════════════════════════════════════════
def paginate_list(
    items: Sequence[T],
    *,
    page: int = 1,
    limit: int = DEFAULT_PAGE_SIZE,
    sort: Optional[SortSpec] = None,
) -> Page[T]:
    """TH: paginate list ในหน่วยความจำ | EN: paginate a list in memory

    Usage:
        result = paginate_list(users, page=2, limit=20)
    """
    total = len(items)
    start = max(0, (page - 1) * limit)
    end = start + limit
    return Page(
        items=list(items[start:end]),
        total=total, page=page, limit=limit, sort=sort,
    )


def paginate_iter(
    iterable: Iterable[T],
    *,
    page: int = 1,
    limit: int = DEFAULT_PAGE_SIZE,
    sort: Optional[SortSpec] = None,
) -> Page[T]:
    """TH: paginate iterable (materialize) | EN: paginate iterable"""
    return paginate_list(list(iterable), page=page, limit=limit, sort=sort)


# ═══════════════════════════════════════════════════════════════
#  SQLAlchemy helpers (optional)
# ═══════════════════════════════════════════════════════════════
def apply_sort_clause(query: Any, model: Any, sort: SortSpec) -> Any:
    """TH: apply ORDER BY กับ SQLAlchemy query | EN: apply ORDER BY

    Usage:
        stmt = apply_sort_clause(select(User), User, params.sort)
    """
    if not hasattr(model, sort.field):
        # fallback to id / created_at
        for candidate in ("created_at", "id"):
            if hasattr(model, candidate):
                col = getattr(model, candidate)
                return query.order_by(col.desc() if sort.order == "desc" else col.asc())
        return query

    col = getattr(model, sort.field)
    return query.order_by(col.asc() if sort.order == "asc" else col.desc())


def apply_offset_limit(query: Any, params: PaginationParams) -> Any:
    """TH: apply LIMIT + OFFSET | EN: apply LIMIT + OFFSET"""
    return query.offset(params.offset).limit(params.limit)


def apply_cursor_filter(
    query: Any,
    model: Any,
    *,
    last_value: Any,
    sort_field: str = "id",
    sort_order: SortOrder = "desc",
) -> Any:
    """TH: apply keyset WHERE (id < last_value) | EN: keyset filter

    ใช้สำหรับ cursor pagination + index บน sort_field
    """
    if last_value is None:
        return query
    if not hasattr(model, sort_field):
        return query
    col = getattr(model, sort_field)
    if sort_order == "desc":
        return query.where(col < last_value)
    return query.where(col > last_value)


# ═══════════════════════════════════════════════════════════════
#  FastAPI helpers (optional)
# ═══════════════════════════════════════════════════════════════
def build_pagination_response(
    page: Page[T],
    *,
    item_serializer: Optional[Callable[[T], Any]] = None,
) -> dict[str, Any]:
    """TH: สร้าง response dict พร้อม metadata | EN: build pagination response"""
    return page.to_dict(item_serializer=item_serializer)


def build_cursor_response(
    page: CursorPage[T],
    *,
    item_serializer: Optional[Callable[[T], Any]] = None,
) -> dict[str, Any]:
    """TH: สร้าง cursor response | EN: build cursor response"""
    return page.to_dict(item_serializer=item_serializer)


# ═══════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════
__all__ = [
    # Constants
    "DEFAULT_PAGE_SIZE", "DEFAULT_MAX_PAGE_SIZE", "ABSOLUTE_MAX_PAGE_SIZE",
    "SortOrder",
    # Specs
    "SortSpec", "PaginationParams",
    # Results
    "Page", "CursorPage",
    # Cursor
    "encode_cursor", "decode_cursor", "try_decode_cursor",
    "make_cursor_key", "split_keyset_cursor",
    # In-memory
    "paginate_list", "paginate_iter",
    # SQLAlchemy
    "apply_sort_clause", "apply_offset_limit", "apply_cursor_filter",
    # FastAPI
    "build_pagination_response", "build_cursor_response",
]