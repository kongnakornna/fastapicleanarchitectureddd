"""app.shared.types — Type aliases + NewType ที่ทุก module ใช้ร่วม

TH: Type aliases กลาง — ใช้ร่วมทุก module (ลด stringly-typed bugs)
EN: Central type aliases — shared across all modules

Design:
  • Type aliases (semantic) สำหรับ idiomatic typing
  • NewType สำหรับ ID (compile-time safety)
  • JSON types (recursive, mypy-friendly)
  • Literal types สำหรับ enum-like strings
  • Protocol types สำหรับ duck-typed interfaces
  • Runtime helpers (is_json_serializable, coerce_uuid)
  • Python 3.10+ (ใช้ | ไม่ใช่ Union)
  • ไม่มี external deps
"""
from __future__ import annotations

import json
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import (
    Any, Awaitable, Callable, Generic, Iterable, Iterator, Literal,
    Mapping, MutableMapping, NewType, Optional, Protocol, Sequence,
    TypeVar, Union, runtime_checkable,
)


# ═══════════════════════════════════════════════════════════════
#  Semantic aliases (string-ish)
# ═══════════════════════════════════════════════════════════════
UUIDStr = str           # canonical UUID string: "018d5a8b-...-7..."
HexStr = str            # lowercase hex (no prefix)
Base64Str = str         # urlsafe base64
JWTStr = str            # JWT token
URLStr = str            # HTTP(S) URL
EmailStr = str          # email address (runtime validation แยก)
PhoneStr = str          # E.164 phone
IsoDateStr = str        # "2025-01-15"
IsoDateTimeStr = str    # "2025-01-15T14:23:45+00:00"
SemVerStr = str         # "1.2.3"
EnvStr = str            # "development" / "staging" / "production"
CurrencyCode = str      # ISO 4217: "USD", "THB"
LanguageCode = str      # ISO 639-1: "en", "th"


# ═══════════════════════════════════════════════════════════════
#  NewType — runtime-safe nominal typing (สำหรับ ID)
# ═══════════════════════════════════════════════════════════════
TenantId = NewType("TenantId", uuid.UUID)
UserId = NewType("UserId", uuid.UUID)
SessionId = NewType("SessionId", uuid.UUID)
RequestId = NewType("RequestId", str)
TraceId = NewType("TraceId", str)
ApiKey = NewType("ApiKey", str)
CorrelationId = NewType("CorrelationId", str)


# ═══════════════════════════════════════════════════════════════
#  JSON value types (recursive, mypy-friendly)
# ═══════════════════════════════════════════════════════════════
JSONScalar = Union[str, int, float, bool, None]
JSONValue = Union[JSONScalar, list["JSONValue"], dict[str, "JSONValue"]]
JSONArray = list[JSONValue]
JSONObject = dict[str, JSONValue]
JSONDict = dict[str, Any]                # ผ่อนปรนกว่า JSONObject
JSONList = list[Any]


# ═══════════════════════════════════════════════════════════════
#  Time aliases
# ═══════════════════════════════════════════════════════════════
Timestamp = datetime                # UTC datetime
DateOnly = date                     # date ไม่มีเวลา
TimeOnly = time                     # time ไม่มีวันที่
EpochSeconds = int                  # unix seconds
EpochMillis = int                   # unix milliseconds
DurationSeconds = float             # ระยะเวลาเป็นวินาที
DurationMillis = int                # ระยะเวลาเป็น ms


# ═══════════════════════════════════════════════════════════════
#  Numeric aliases
# ═══════════════════════════════════════════════════════════════
Money = Decimal                     # เงิน (ใช้กับ Numeric)
Percentage = float                  # 0.0 – 1.0
Score = float                       # 0.0 – 1.0 (similarity, relevance)
TokenCount = int                    # จำนวน token
ByteSize = int                      # ขนาดเป็น bytes
LatencyMs = int                     # latency (ms)
HttpStatus = int                    # 100–599


# ═══════════════════════════════════════════════════════════════
#  Literal types (enum-like strings)
# ═══════════════════════════════════════════════════════════════
SortOrder = Literal["asc", "desc"]
PageDirection = Literal["next", "prev"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
Environment = Literal["development", "staging", "production", "test"]
UserRole = Literal["system", "admin", "user", "guest"]


# ═══════════════════════════════════════════════════════════════
#  Generic TypeVars
# ═══════════════════════════════════════════════════════════════
T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
E = TypeVar("E", bound=BaseException)

# Aliases ที่อ่านง่าย
AsyncCallable = Callable[..., Awaitable[T]]
SyncCallable = Callable[..., T]
Predicate = Callable[[T], bool]
Mapper = Callable[[T], U]
Reducer = Callable[[U, T], U]
Factory = Callable[[], T]
EventHandler = Callable[[T], Awaitable[None]]
VoidCallback = Callable[[], None]
AnyDict = Mapping[str, Any]
MutableAnyDict = MutableMapping[str, Any]


# ═══════════════════════════════════════════════════════════════
#  Protocols — duck-typed contracts
# ═══════════════════════════════════════════════════════════════
@runtime_checkable
class HasId(Protocol):
    """TH: มี id | EN: has an id"""
    id: uuid.UUID


@runtime_checkable
class HasTenantId(Protocol):
    """TH: มี tenant_id | EN: has a tenant id"""
    tenant_id: uuid.UUID


@runtime_checkable
class Timestamped(Protocol):
    """TH: มี timestamps | EN: has timestamps"""
    created_at: datetime
    updated_at: datetime


@runtime_checkable
class Versioned(Protocol):
    """TH: มี version | EN: has version"""
    version: int


@runtime_checkable
class Auditable(HasId, HasTenantId, Timestamped, Protocol):
    """TH: entity มาตรฐาน | EN: standard auditable entity"""
    pass


@runtime_checkable
class Identifiable(HasId, Protocol):
    """TH: มี id เท่านั้น | EN: only has id"""
    pass


@runtime_checkable
class Closeable(Protocol):
    """TH: ปิดได้ | EN: closeable resource"""
    async def close(self) -> None: ...


@runtime_checkable
class Serializable(Protocol):
    """TH: serialize ได้ | EN: serializable to dict"""
    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class Deserializable(Protocol):
    """TH: deserialize ได้ | EN: constructible from dict"""
    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T: ...


# ═══════════════════════════════════════════════════════════════
#  Container aliases
# ═══════════════════════════════════════════════════════════════
StrList = list[str]
StrSet = set[str]
StrDict = dict[str, str]
AnyList = list[Any]
AnyTuple = tuple[Any, ...]
UUIDList = list[uuid.UUID]
ReadonlySequence = Sequence[T]
MutableSequenceAlias = MutableMapping[str, Any]
IteratorAlias = Iterator[T]
IterableAlias = Iterable[T]


# ═══════════════════════════════════════════════════════════════
#  Result-like types (light)
# ═══════════════════════════════════════════════════════════════
Ok = tuple[Literal[True], T]
Err = tuple[Literal[False], E]
Result = Union[tuple[Literal[True], T], tuple[Literal[False], E]]


# ═══════════════════════════════════════════════════════════════
#  Runtime helpers
# ═══════════════════════════════════════════════════════════════
def is_json_scalar(value: Any) -> bool:
    """TH: เป็น scalar ที่ JSON รองรับ | EN: is JSON scalar"""
    return isinstance(value, (str, int, float, bool)) or value is None


def is_json_serializable(value: Any) -> bool:
    """TH: serialize เป็น JSON ได้หรือไม่ | EN: is JSON-serializable"""
    try:
        json.dumps(value)
        return True
    except (TypeError, ValueError):
        return False


def coerce_uuid(value: Any) -> Optional[uuid.UUID]:
    """TH: แปลงค่าเป็น UUID (คืน None ถ้าไม่ได้)
    | EN: coerce to UUID (None if impossible)"""
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return value
    if isinstance(value, str):
        try:
            return uuid.UUID(value)
        except (ValueError, AttributeError):
            return None
    if isinstance(value, int):
        try:
            return uuid.UUID(int=value)
        except (ValueError, OverflowError):
            return None
    return None


def coerce_datetime(value: Any) -> Optional[datetime]:
    """TH: แปลงค่าเป็น datetime | EN: coerce to datetime"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
    if isinstance(value, (int, float)):
        from datetime import timezone
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            return None
    return None


def coerce_decimal(value: Any) -> Optional[Decimal]:
    """TH: แปลงค่าเป็น Decimal | EN: coerce to Decimal"""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (ValueError, ArithmeticError, TypeError):
        return None


def coerce_bool(value: Any) -> bool:
    """TH: แปลงค่าเป็น bool (แบบ deterministic)
    | EN: deterministic bool coercion"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "y", "on")
    if isinstance(value, (int, float)):
        return value != 0
    return bool(value)


def assert_non_empty(value: Any, name: str = "value") -> Any:
    """TH: ตรวจว่าไม่ว่าง | EN: assert not empty"""
    if value is None:
        raise ValueError(f"{name} must not be None")
    if isinstance(value, (str, list, tuple, dict, set)) and len(value) == 0:
        raise ValueError(f"{name} must not be empty")
    return value


def to_json(value: Any, *, default: str = "null") -> str:
    """TH: serialize เป็น JSON string (never-raise)
    | EN: serialize to JSON string (never-raise)"""
    try:
        return json.dumps(value, default=str, ensure_ascii=False)
    except (TypeError, ValueError):
        return default


# ═══════════════════════════════════════════════════════════════
#  Cast helpers (type-narrowing ที่ปลอดภัย)
# ═══════════════════════════════════════════════════════════════
def as_uuid_str(value: uuid.UUID | str) -> UUIDStr:
    """TH: UUID → canonical string | EN: UUID → string"""
    return str(value)


def as_tenant_id(value: uuid.UUID | str) -> TenantId:
    """TH: cast → TenantId | EN: cast to TenantId"""
    u = coerce_uuid(value)
    if u is None:
        raise ValueError(f"invalid tenant_id: {value!r}")
    return TenantId(u)


def as_user_id(value: uuid.UUID | str) -> UserId:
    """TH: cast → UserId | EN: cast to UserId"""
    u = coerce_uuid(value)
    if u is None:
        raise ValueError(f"invalid user_id: {value!r}")
    return UserId(u)


def as_request_id(value: str) -> RequestId:
    """TH: cast → RequestId | EN: cast to RequestId"""
    if not value:
        raise ValueError("request_id required")
    return RequestId(value)


# ═══════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════
__all__ = [
    # String aliases
    "UUIDStr", "HexStr", "Base64Str", "JWTStr", "URLStr", "EmailStr",
    "PhoneStr", "IsoDateStr", "IsoDateTimeStr", "SemVerStr", "EnvStr",
    "CurrencyCode", "LanguageCode",
    # NewType IDs
    "TenantId", "UserId", "SessionId", "RequestId", "TraceId",
    "ApiKey", "CorrelationId",
    # JSON
    "JSONScalar", "JSONValue", "JSONArray", "JSONObject",
    "JSONDict", "JSONList",
    # Time
    "Timestamp", "DateOnly", "TimeOnly",
    "EpochSeconds", "EpochMillis",
    "DurationSeconds", "DurationMillis",
    # Numeric
    "Money", "Percentage", "Score", "TokenCount", "ByteSize",
    "LatencyMs", "HttpStatus",
    # Literal
    "SortOrder", "PageDirection", "LogLevel", "Environment", "UserRole",
    # TypeVars
    "T", "U", "K", "V", "T_co", "T_contra", "E",
    # Callables
    "AsyncCallable", "SyncCallable", "Predicate", "Mapper",
    "Reducer", "Factory", "EventHandler", "VoidCallback",
    "AnyDict", "MutableAnyDict",
    # Protocols
    "HasId", "HasTenantId", "Timestamped", "Versioned",
    "Auditable", "Identifiable",
    "Closeable", "Serializable", "Deserializable",
    # Containers
    "StrList", "StrSet", "StrDict", "AnyList", "AnyTuple", "UUIDList",
    "ReadonlySequence", "MutableSequenceAlias",
    "IteratorAlias", "IterableAlias",
    # Result
    "Ok", "Err", "Result",
    # Helpers
    "is_json_scalar", "is_json_serializable",
    "coerce_uuid", "coerce_datetime", "coerce_decimal", "coerce_bool",
    "assert_non_empty", "to_json",
    # Casts
    "as_uuid_str", "as_tenant_id", "as_user_id", "as_request_id",
]