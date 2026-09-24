"""app.shared.errors — shared errors ที่ทุก module ใช้ร่วม

TH: ระบบ error กลาง — ใช้ร่วมทุก module
EN: Central error hierarchy — shared across all modules

Design:
  • 2 base classes: DomainError, AppError
  • ~30 standard subclasses พร้อม code + http_status
  • HTTP status mapping
  • Error code registry (unique, documented)
  • Serialization (to_dict) + factory (from_exception)
  • Retry classification (is_retryable)
  • Safe message (production ไม่ leak internal details)
  • Python 3.10+, ไม่มี external deps
"""
from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, ClassVar, Optional

logger = logging.getLogger(__name__)

ENV = os.getenv("APP_ENV", os.getenv("ENV", "development")).lower()
IS_PRODUCTION = ENV in ("production", "prod")


# ═══════════════════════════════════════════════════════════════
#  Base classes
# ═══════════════════════════════════════════════════════════════
class BaseError(Exception):
    """TH: รากของ error ทั้งหมด | EN: Root of all errors

    Class attributes:
        code:        error code (unique, uppercase snake_case)
        http_status: HTTP status ที่แนะนำ
        retryable:   retry ได้หรือไม่ (สำหรับ retry policy)
        safe_message: แสดงกับ user ได้หรือไม่ (production)
    """

    code: ClassVar[str] = "ERROR"
    http_status: ClassVar[int] = 500
    retryable: ClassVar[bool] = False
    safe_message: ClassVar[bool] = True

    def __init__(
        self,
        message: str = "",
        *,
        code: Optional[str] = None,
        http_status: Optional[int] = None,
        retryable: Optional[bool] = None,
        safe_message: Optional[bool] = None,
        details: Optional[dict[str, Any]] = None,
        cause: Optional[BaseException] = None,
        error_id: Optional[str] = None,
    ) -> None:
        self.message = message or self.__class__.__name__
        self.details: dict[str, Any] = dict(details or {})
        self.cause = cause
        self.error_id = error_id or uuid.uuid4().hex[:12]

        if code:
            self.code = code
        if http_status is not None:
            self.http_status = http_status
        if retryable is not None:
            self.retryable = retryable
        if safe_message is not None:
            self.safe_message = safe_message

        super().__init__(self.message)

    # ─── Serialization ────────────────────────────────────────

    def to_dict(self, *, include_details: bool = True) -> dict[str, Any]:
        """TH: แปลงเป็น dict | EN: serialize to dict"""
        out: dict[str, Any] = {
            "code": self.code,
            "message": self.message if (not IS_PRODUCTION or self.safe_message)
                       else "internal error",
            "error_id": self.error_id,
            "http_status": self.http_status,
        }
        if include_details and self.details:
            out["details"] = self.details
        if self.cause is not None and not IS_PRODUCTION:
            out["cause"] = f"{type(self.cause).__name__}: {self.cause}"
        return out

    def to_http_response(self) -> dict[str, Any]:
        """TH: รูปแบบ response สำหรับ FastAPI | EN: FastAPI error payload"""
        return {"detail": self.to_dict()}

    # ─── Chaining ─────────────────────────────────────────────

    def with_details(self, **kwargs: Any) -> "BaseError":
        """TH: เพิ่ม details | EN: attach extra details"""
        self.details.update(kwargs)
        return self

    def with_cause(self, cause: BaseException) -> "BaseError":
        """TH: กำหนด cause | EN: set cause"""
        self.cause = cause
        return self

    # ─── Introspection ────────────────────────────────────────

    def is_retryable(self) -> bool:
        """TH: ควร retry หรือไม่ | EN: should retry?"""
        return bool(self.retryable)

    def is_client_error(self) -> bool:
        """TH: เป็นความผิด client (4xx) | EN: client error (4xx)?"""
        return 400 <= self.http_status < 500

    def is_server_error(self) -> bool:
        """TH: เป็นความผิด server (5xx) | EN: server error (5xx)?"""
        return 500 <= self.http_status < 600

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"code={self.code!r}, "
            f"http={self.http_status}, "
            f"msg={self.message!r})"
        )


# ═══════════════════════════════════════════════════════════════
#  2 families: DomainError (business) + AppError (application)
# ═══════════════════════════════════════════════════════════════
class DomainError(BaseError):
    """TH: ข้อผิดพลาดระดับ domain (business rules)
    | EN: Domain-level error (business rules)"""
    code = "DOMAIN_ERROR"
    http_status = 400


class AppError(BaseError):
    """TH: ข้อผิดพลาดระดับ application (use case, infra)
    | EN: Application-level error (use case, infra)"""
    code = "APP_ERROR"
    http_status = 500


# ═══════════════════════════════════════════════════════════════
#  Generic standard errors (ใช้ร่วมทุก module)
# ═══════════════════════════════════════════════════════════════
class ValidationError(DomainError):
    """TH: ข้อมูลไม่ถูกต้อง | EN: Validation error"""
    code = "VALIDATION_ERROR"
    http_status = 422


class NotFoundError(DomainError):
    """TH: ไม่พบข้อมูล | EN: Not found"""
    code = "NOT_FOUND"
    http_status = 404


class ConflictError(DomainError):
    """TH: ข้อมูลซ้ำ / conflict | EN: Conflict"""
    code = "CONFLICT"
    http_status = 409


class AlreadyExistsError(ConflictError):
    """TH: มีอยู่แล้ว | EN: Already exists"""
    code = "ALREADY_EXISTS"


class PreconditionFailedError(DomainError):
    """TH: เงื่อนไขไม่ผ่าน | EN: Precondition failed"""
    code = "PRECONDITION_FAILED"
    http_status = 412


class UnauthorizedError(DomainError):
    """TH: ยังไม่ authenticate | EN: Unauthorized"""
    code = "UNAUTHORIZED"
    http_status = 401
    safe_message = True


class ForbiddenError(DomainError):
    """TH: ไม่มีสิทธิ์ | EN: Forbidden"""
    code = "FORBIDDEN"
    http_status = 403


class PermissionDeniedError(ForbiddenError):
    """TH: ปฏิเสธการเข้าถึง | EN: Permission denied"""
    code = "PERMISSION_DENIED"


class RateLimitError(DomainError):
    """TH: เกิน rate limit | EN: Rate limit exceeded"""
    code = "RATE_LIMITED"
    http_status = 429
    retryable = True


class QuotaExceededError(DomainError):
    """TH: เกินโควต้า | EN: Quota exceeded"""
    code = "QUOTA_EXCEEDED"
    http_status = 429


class LimitExceededError(DomainError):
    """TH: เกินขีดจำกัด | EN: Limit exceeded"""
    code = "LIMIT_EXCEEDED"
    http_status = 402


class TokenLimitExceededError(LimitExceededError):
    """TH: เกิน token limit | EN: Token limit exceeded"""
    code = "TOKEN_LIMIT_EXCEEDED"


class PaymentRequiredError(DomainError):
    """TH: ต้องชำระเงิน | EN: Payment required"""
    code = "PAYMENT_REQUIRED"
    http_status = 402


class TimeoutError(DomainError):  # noqa: A001 - intentional shadow
    """TH: หมดเวลา | EN: Timeout"""
    code = "TIMEOUT"
    http_status = 504
    retryable = True


class CancelledError(DomainError):
    """TH: ถูกยกเลิก | EN: Cancelled"""
    code = "CANCELLED"
    http_status = 499


# ═══════════════════════════════════════════════════════════════
#  Provider / external service errors
# ═══════════════════════════════════════════════════════════════
class ProviderError(AppError):
    """TH: provider ภายนอก error | EN: External provider error"""
    code = "PROVIDER_ERROR"
    http_status = 502
    retryable = True
    safe_message = False


class ProviderAuthError(ProviderError):
    """TH: provider auth ผิด | EN: Provider auth failed"""
    code = "PROVIDER_AUTH_ERROR"
    http_status = 502
    retryable = False


class ProviderRateLimitError(ProviderError):
    """TH: provider rate limit | EN: Provider rate limit"""
    code = "PROVIDER_RATE_LIMITED"
    http_status = 429
    retryable = True


class ProviderTimeoutError(ProviderError):
    """TH: provider timeout | EN: Provider timeout"""
    code = "PROVIDER_TIMEOUT"
    http_status = 504
    retryable = True


class ProviderUnavailableError(ProviderError):
    """TH: provider ไม่พร้อมใช้งาน | EN: Provider unavailable"""
    code = "PROVIDER_UNAVAILABLE"
    http_status = 503
    retryable = True


class ProviderBadRequestError(ProviderError):
    """TH: provider reject request | EN: Provider bad request"""
    code = "PROVIDER_BAD_REQUEST"
    http_status = 400
    retryable = False


# ═══════════════════════════════════════════════════════════════
#  Infrastructure errors
# ═══════════════════════════════════════════════════════════════
class DatabaseError(AppError):
    """TH: ฐานข้อมูล error | EN: Database error"""
    code = "DB_ERROR"
    http_status = 500
    retryable = True
    safe_message = False


class UniqueViolationError(DatabaseError):
    """TH: ละเมิด unique constraint | EN: Unique violation"""
    code = "DB_UNIQUE_VIOLATION"
    http_status = 409
    retryable = False


class ForeignKeyViolationError(DatabaseError):
    """TH: ละเมิด FK | EN: FK violation"""
    code = "DB_FK_VIOLATION"
    http_status = 409
    retryable = False


class ConnectionError(DatabaseError):  # noqa: A001
    """TH: การเชื่อมต่อล้มเหลว | EN: Connection failed"""
    code = "DB_CONNECTION_ERROR"
    http_status = 503
    retryable = True


class CacheError(AppError):
    """TH: cache error | EN: Cache error"""
    code = "CACHE_ERROR"
    http_status = 500
    retryable = True
    safe_message = False


class StorageError(AppError):
    """TH: storage (S3, disk) error | EN: Storage error"""
    code = "STORAGE_ERROR"
    http_status = 500
    retryable = True


class QueueError(AppError):
    """TH: message queue error | EN: Queue error"""
    code = "QUEUE_ERROR"
    http_status = 500
    retryable = True


# ═══════════════════════════════════════════════════════════════
#  Configuration / system errors
# ═══════════════════════════════════════════════════════════════
class ConfigurationError(AppError):
    """TH: config ผิด | EN: Configuration error"""
    code = "CONFIG_ERROR"
    http_status = 500
    retryable = False
    safe_message = False


class NotImplementedError(AppError):  # noqa: A001
    """TH: ยังไม่ implement | EN: Not implemented"""
    code = "NOT_IMPLEMENTED"
    http_status = 501


class InternalError(AppError):
    """TH: ข้อผิดพลาดภายใน | EN: Internal error"""
    code = "INTERNAL_ERROR"
    http_status = 500
    safe_message = False


class ServiceUnavailableError(AppError):
    """TH: service ไม่พร้อมใช้งาน | EN: Service unavailable"""
    code = "SERVICE_UNAVAILABLE"
    http_status = 503
    retryable = True


# ═══════════════════════════════════════════════════════════════
#  Error code registry (สำหรับตรวจ uniqueness + documentation)
# ═══════════════════════════════════════════════════════════════
ERROR_REGISTRY: dict[str, type[BaseError]] = {}


def register(cls: type[BaseError]) -> type[BaseError]:
    """TH: ลงทะเบียน error class | EN: register error class"""
    ERROR_REGISTRY[cls.code] = cls
    return cls


def _auto_register() -> None:
    """TH: auto-register ทุก subclass ที่ประกาศไว้ | EN: auto register all"""
    for cls in (
        DomainError, AppError,
        ValidationError, NotFoundError, ConflictError, AlreadyExistsError,
        PreconditionFailedError, UnauthorizedError, ForbiddenError,
        PermissionDeniedError, RateLimitError, QuotaExceededError,
        LimitExceededError, TokenLimitExceededError, PaymentRequiredError,
        TimeoutError, CancelledError,
        ProviderError, ProviderAuthError, ProviderRateLimitError,
        ProviderTimeoutError, ProviderUnavailableError, ProviderBadRequestError,
        DatabaseError, UniqueViolationError, ForeignKeyViolationError,
        ConnectionError, CacheError, StorageError, QueueError,
        ConfigurationError, NotImplementedError, InternalError,
        ServiceUnavailableError,
    ):
        register(cls)


_auto_register()


# ═══════════════════════════════════════════════════════════════
#  HTTP status → error class mapping
# ═══════════════════════════════════════════════════════════════
HTTP_STATUS_MAP: dict[int, type[BaseError]] = {
    400: ValidationError,
    401: UnauthorizedError,
    402: PaymentRequiredError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    412: PreconditionFailedError,
    422: ValidationError,
    429: RateLimitError,
    499: CancelledError,
    500: InternalError,
    501: NotImplementedError,
    502: ProviderError,
    503: ServiceUnavailableError,
    504: TimeoutError,
}


# ═══════════════════════════════════════════════════════════════
#  Factories
# ═══════════════════════════════════════════════════════════════
def from_exception(
    exc: BaseException,
    *,
    default: type[BaseError] = InternalError,
    cause: Optional[BaseException] = None,
) -> BaseError:
    """TH: แปลง exception ใด ๆ เป็น BaseError
    | EN: normalize any exception to BaseError

    Args:
        exc: exception ต้นฉบับ
        default: ถ้าไม่รู้จัก ใช้ class นี้
        cause: exception ที่จะเก็บไว้ใน .cause (default = exc)

    Returns:
        BaseError instance (เดิม ถ้าเป็น BaseError อยู่แล้ว)
    """
    if isinstance(exc, BaseError):
        return exc

    # map stdlib exceptions ที่พบบ่อย
    cls: type[BaseError] = default
    if isinstance(exc, ValueError):
        cls = ValidationError
    elif isinstance(exc, KeyError):
        cls = NotFoundError
    elif isinstance(exc, PermissionError):
        cls = PermissionDeniedError
    elif isinstance(exc, FileNotFoundError):
        cls = NotFoundError
    elif isinstance(exc, (TimeoutError,)):  # stdlib TimeoutError
        cls = TimeoutError
    elif isinstance(exc, ConnectionError):  # stdlib ConnectionError
        cls = ConnectionError
    elif isinstance(exc, NotImplementedError):
        cls = NotImplementedError
    elif isinstance(exc, AssertionError):
        cls = InternalError

    return cls(
        str(exc) or type(exc).__name__,
        cause=cause if cause is not None else exc,
    )


def from_http_status(
    status: int,
    message: str = "",
    *,
    details: Optional[dict[str, Any]] = None,
) -> BaseError:
    """TH: สร้าง error จาก HTTP status | EN: build error from HTTP status"""
    cls = HTTP_STATUS_MAP.get(status, InternalError)
    return cls(message or cls.__name__, details=details)


def is_retryable(exc: BaseException) -> bool:
    """TH: ตรวจว่า exception ควร retry หรือไม่
    | EN: check if exception is retryable"""
    if isinstance(exc, BaseError):
        return exc.is_retryable()
    # stdlib defaults
    return isinstance(exc, (
        TimeoutError, ConnectionError, OSError,
    ))


# ═══════════════════════════════════════════════════════════════
#  Retry policy helper
# ═══════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class RetryPolicy:
    """TH: นโยบายการ retry | EN: Retry policy"""
    max_attempts: int = 3
    backoff: tuple[float, ...] = (1.0, 2.0, 4.0)
    retry_on: tuple[type[BaseException], ...] = (BaseError,)
    jitter: bool = True

    def should_retry(self, exc: BaseException, attempt: int) -> bool:
        """TH: ควร retry ต่อหรือไม่ | EN: should retry?"""
        if attempt >= self.max_attempts:
            return False
        if not isinstance(exc, self.retry_on):
            return False
        return is_retryable(exc)

    def delay_for(self, attempt: int) -> float:
        """TH: หน่วงเวลา (วินาที) ก่อน retry ครั้งต่อไป
        | EN: delay before next retry (seconds)"""
        if attempt < 1:
            return 0.0
        idx = min(attempt - 1, len(self.backoff) - 1)
        base = self.backoff[idx]
        if self.jitter:
            import random
            return base * (0.5 + random.random())
        return base


# ═══════════════════════════════════════════════════════════════
#  Error payload VO (สำหรับ API contract)
# ═══════════════════════════════════════════════════════════════
@dataclass
class ErrorPayload:
    """TH: payload มาตรฐานของ error | EN: Standard error payload"""
    code: str
    message: str
    error_id: str = ""
    http_status: int = 500
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )

    @classmethod
    def from_error(cls, exc: BaseError) -> "ErrorPayload":
        d = exc.to_dict()
        return cls(
            code=d["code"], message=d["message"],
            error_id=d.get("error_id", ""),
            http_status=d["http_status"],
            details=d.get("details", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "error_id": self.error_id,
            "http_status": self.http_status,
            "timestamp": self.timestamp,
        }
        if self.details:
            out["details"] = self.details
        return out


# ═══════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════
__all__ = [
    # Base
    "BaseError", "DomainError", "AppError",
    # Generic
    "ValidationError", "NotFoundError", "ConflictError",
    "AlreadyExistsError", "PreconditionFailedError",
    "UnauthorizedError", "ForbiddenError", "PermissionDeniedError",
    "RateLimitError", "QuotaExceededError", "LimitExceededError",
    "TokenLimitExceededError", "PaymentRequiredError",
    "TimeoutError", "CancelledError",
    # Provider
    "ProviderError", "ProviderAuthError", "ProviderRateLimitError",
    "ProviderTimeoutError", "ProviderUnavailableError",
    "ProviderBadRequestError",
    # Infra
    "DatabaseError", "UniqueViolationError", "ForeignKeyViolationError",
    "ConnectionError", "CacheError", "StorageError", "QueueError",
    # System
    "ConfigurationError", "NotImplementedError",
    "InternalError", "ServiceUnavailableError",
    # Registry / Factory / Helpers
    "ERROR_REGISTRY", "HTTP_STATUS_MAP",
    "from_exception", "from_http_status", "is_retryable",
    "RetryPolicy", "ErrorPayload", "register",
]