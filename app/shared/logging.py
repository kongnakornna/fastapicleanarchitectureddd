"""app.shared.logging — shared logging ที่ทุก module ใช้ร่วม

TH: ระบบ logging กลาง — ใช้ร่วมทุก module (llm, embeddings, rag, ...)
EN: Central logging setup — shared across all modules

Design:
  • stdlib logging เป็นหลัก (ไม่มี hard dep บน loguru)
  • Optional loguru adapter ถ้าติดตั้งไว้
  • Structured JSON output (production) + Pretty (dev)
  • RequestContext propagation ผ่าน contextvars
  • Correlation ID (request_id / trace_id) ฝังในทุก log
  • Sensitive data redaction (api_key, password, token)
  • Drop-in: get_logger(__name__) → returns logging.Logger
"""
from __future__ import annotations

import json
import logging
import logging.config
import os
import re
import sys
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════
#  Context variables — propagate ผ่าน async task boundary
# ═══════════════════════════════════════════════════════════════
_request_id_var: ContextVar[Optional[str]] = ContextVar(
    "request_id", default=None,
)
_trace_id_var: ContextVar[Optional[str]] = ContextVar(
    "trace_id", default=None,
)
_tenant_id_var: ContextVar[Optional[str]] = ContextVar(
    "tenant_id", default=None,
)
_user_id_var: ContextVar[Optional[str]] = ContextVar(
    "user_id", default=None,
)


# ═══════════════════════════════════════════════════════════════
#  Environment detection
# ═══════════════════════════════════════════════════════════════
ENV = os.getenv("APP_ENV", os.getenv("ENV", "development")).lower()
IS_PRODUCTION = ENV in ("production", "prod")
IS_TESTING = ENV in ("test", "testing")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json" if IS_PRODUCTION else "pretty").lower()


# ═══════════════════════════════════════════════════════════════
#  Sensitive data redaction
# ═══════════════════════════════════════════════════════════════
_REDACT_KEYS = frozenset({
    "password", "passwd", "pwd",
    "secret", "client_secret", "api_key", "apikey", "api_token",
    "access_token", "refresh_token", "id_token", "bearer",
    "authorization", "auth", "private_key", "session_key",
    "credit_card", "card_number", "cvv", "ssn",
})

_REDACT_PATTERNS = (
    # OpenAI / Anthropic keys
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    # Bearer tokens
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE),
    # JWT
    re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
)


def _redact_value(value: Any) -> str:
    """TH: ปิดบังค่า sensitive | EN: mask sensitive value"""
    s = str(value)
    if len(s) <= 8:
        return "***"
    return s[:4] + "***" + s[-4:]


def redact(value: str) -> str:
    """TH: ปิดบัง pattern ที่ sensitive ในข้อความ | EN: redact sensitive patterns"""
    if not value:
        return value
    out = value
    for pat in _REDACT_PATTERNS:
        out = pat.sub("***REDACTED***", out)
    return out


def redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    """TH: redact ทั้ง dict (recursive) | EN: redact dict recursively"""
    out: dict[str, Any] = {}
    for k, v in data.items():
        if k.lower() in _REDACT_KEYS:
            out[k] = _redact_value(v)
        elif isinstance(v, dict):
            out[k] = redact_dict(v)
        elif isinstance(v, (list, tuple)):
            out[k] = [
                redact_dict(x) if isinstance(x, dict)
                else (_redact_value(x) if k.lower() in _REDACT_KEYS else x)
                for x in v
            ]
        else:
            out[k] = v
    return out


# ═══════════════════════════════════════════════════════════════
#  Context helpers — ใช้คู่กับ RequestContext
# ═══════════════════════════════════════════════════════════════
def bind_context(
    *,
    request_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> None:
    """TH: ผูก context เข้า log ทุก entry ใน scope นี้
    | EN: bind context to all logs within this scope"""
    if request_id is not None:
        _request_id_var.set(request_id)
    if trace_id is not None:
        _trace_id_var.set(trace_id)
    if tenant_id is not None:
        _tenant_id_var.set(tenant_id)
    if user_id is not None:
        _user_id_var.set(user_id)


def clear_context() -> None:
    """TH: ล้าง context | EN: clear all bound context"""
    _request_id_var.set(None)
    _trace_id_var.set(None)
    _tenant_id_var.set(None)
    _user_id_var.set(None)


def bind_from_request_ctx(ctx: Any) -> None:
    """TH: ผูก context จาก RequestContext | EN: bind from RequestContext"""
    if ctx is None:
        return
    tenant = getattr(ctx, "tenant_id", None)
    user = getattr(ctx, "user_id", None)
    bind_context(
        request_id=getattr(ctx, "request_id", None),
        trace_id=getattr(ctx, "trace_id", None),
        tenant_id=str(tenant) if tenant else None,
        user_id=str(user) if user else None,
    )


def get_request_id() -> Optional[str]:
    """TH: ดึง request_id ปัจจุบัน | EN: current request id"""
    return _request_id_var.get()


def get_trace_id() -> Optional[str]:
    """TH: ดึง trace_id ปัจจุบัน | EN: current trace id"""
    return _trace_id_var.get()


def new_request_id() -> str:
    """TH: สร้าง request_id ใหม่ | EN: generate new request id"""
    return uuid.uuid4().hex


def new_trace_id() -> str:
    """TH: สร้าง trace_id ใหม่ | EN: generate new trace id"""
    return uuid.uuid4().hex


# ═══════════════════════════════════════════════════════════════
#  Formatters
# ═══════════════════════════════════════════════════════════════
class ContextFilter(logging.Filter):
    """TH: เติม context vars ลงใน record
    | EN: inject context vars into log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = getattr(record, "request_id", None) \
            or _request_id_var.get()
        record.trace_id = getattr(record, "trace_id", None) \
            or _trace_id_var.get()
        record.tenant_id = getattr(record, "tenant_id", None) \
            or _tenant_id_var.get()
        record.user_id = getattr(record, "user_id", None) \
            or _user_id_var.get()
        return True


class JSONFormatter(logging.Formatter):
    """TH: format log เป็น JSON 1 บรรทัด | EN: single-line JSON formatter"""

    def __init__(self, *, service: str = "app", environment: str = ENV) -> None:
        super().__init__()
        self.service = service
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(
                record.created, tz=timezone.utc,
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": redact(record.getMessage()),
            "service": self.service,
            "env": self.environment,
        }

        # context vars
        for key in ("request_id", "trace_id", "tenant_id", "user_id"):
            val = getattr(record, key, None)
            if val:
                payload[key] = val

        # location
        if record.filename:
            payload["src"] = f"{record.filename}:{record.lineno}"
        if record.funcName:
            payload["func"] = record.funcName

        # exception
        if record.exc_info:
            payload["exc_type"] = record.exc_info[0].__name__ \
                if record.exc_info[0] else None
            payload["exc_msg"] = redact(self.formatException(record.exc_info))

        # extra fields (kwargs จากการเรียก logger.info("...", extra={...}))
        reserved = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "asctime", "request_id", "trace_id", "tenant_id", "user_id",
        }
        extras: dict[str, Any] = {}
        for key, val in record.__dict__.items():
            if key in reserved or key.startswith("_"):
                continue
            extras[key] = val
        if extras:
            payload["extra"] = redact_dict(extras)

        try:
            return json.dumps(payload, default=str, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            fallback = {
                "ts": payload["ts"], "level": payload["level"],
                "logger": payload["logger"], "msg": payload["msg"],
                "error": f"json serialize failed: {exc}",
            }
            return json.dumps(fallback, ensure_ascii=False)


# ─── ANSI colors ─────────────────────────────────────────
class _C:
    RESET = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
    BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"; GRAY = "\033[90m"


_LEVEL_COLORS = {
    "DEBUG": _C.GRAY, "INFO": _C.CYAN, "WARNING": _C.YELLOW,
    "ERROR": _C.RED, "CRITICAL": _C.MAGENTA + _C.BOLD,
}


class PrettyFormatter(logging.Formatter):
    """TH: format สวย อ่านง่าย (dev) | EN: human-friendly formatter"""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(
            record.created, tz=timezone.utc,
        ).strftime("%H:%M:%S.%f")[:-3]

        lvl_color = _LEVEL_COLORS.get(record.levelname, "")
        lvl = f"{lvl_color}{record.levelname:<8}{_C.RESET}"

        ctx_bits: list[str] = []
        rid = getattr(record, "request_id", None)
        tid = getattr(record, "trace_id", None)
        ten = getattr(record, "tenant_id", None)
        if tid:
            ctx_bits.append(f"{_C.DIM}trace={tid[:8]}{_C.RESET}")
        elif rid:
            ctx_bits.append(f"{_C.DIM}req={rid[:8]}{_C.RESET}")
        if ten:
            ctx_bits.append(f"{_C.DIM}tenant={ten[:8]}{_C.RESET}")

        ctx = " ".join(ctx_bits)
        ctx_str = f" {ctx}" if ctx else ""

        name = f"{_C.GRAY}{record.name}{_C.RESET}"
        msg = redact(record.getMessage())

        line = f"{_C.DIM}{ts}{_C.RESET} {lvl} {name}{ctx_str} {msg}"

        # extras
        reserved = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "asctime", "request_id", "trace_id", "tenant_id", "user_id",
        }
        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in reserved and not k.startswith("_")
        }
        if extras:
            extras_clean = redact_dict(extras)
            extras_str = " ".join(f"{k}={v!r}" for k, v in extras_clean.items())
            line += f" {_C.DIM}{extras_str}{_C.RESET}"

        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)

        return line


# ═══════════════════════════════════════════════════════════════
#  Configure root logger
# ═══════════════════════════════════════════════════════════════
_CONFIGURED = False


def configure_logging(
    *,
    level: Optional[str] = None,
    fmt: Optional[str] = None,
    service: str = "app",
    force: bool = False,
) -> None:
    """TH: ตั้งค่าระบบ logging (idempotent)
    | EN: configure logging (idempotent)

    Args:
        level:    DEBUG / INFO / WARNING / ERROR / CRITICAL
        fmt:      "json" | "pretty"
        service:  ชื่อ service (ใส่ใน JSON)
        force:    บังคับ reconfigure
    """
    global _CONFIGURED
    if _CONFIGURED and not force:
        return

    eff_level = (level or LOG_LEVEL).upper()
    eff_format = (fmt or LOG_FORMAT).lower()

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())

    if eff_format == "json":
        handler.setFormatter(JSONFormatter(service=service))
    else:
        handler.setFormatter(PrettyFormatter())

    root = logging.getLogger()
    # remove existing handlers เพื่อกันซ้ำ
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    root.setLevel(eff_level)

    # ปิด noisy loggers ที่ไม่จำเป็น
    for noisy in (
        "uvicorn.access", "sqlalchemy.engine.Engine",
        "httpx", "httpcore", "asyncio",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True


# ═══════════════════════════════════════════════════════════════
#  Public logger factory
# ═══════════════════════════════════════════════════════════════
def get_logger(name: str) -> logging.Logger:
    """TH: ดึง logger ตามชื่อ module | EN: get logger by name

    Usage:
        from app.shared.logging import get_logger
        logger = get_logger(__name__)
        logger.info("hello", extra={"user_id": "abc"})
    """
    if not _CONFIGURED:
        configure_logging()
    return logging.getLogger(name)


# ═══════════════════════════════════════════════════════════════
#  Optional: loguru adapter
# ═══════════════════════════════════════════════════════════════
def get_loguru_logger() -> Any:
    """TH: คืน loguru logger ถ้าติดตั้ง (สำหรับโปรเจกต์ที่ชอบ loguru)
    | EN: return loguru logger if installed

    Raises:
        ImportError: ถ้า loguru ไม่ได้ติดตั้ง
    """
    try:
        from loguru import logger as lg  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "loguru not installed. pip install loguru",
        ) from exc

    if not getattr(lg, "_app_configured", False):
        try:
            lg.remove()
            lg.add(
                sys.stdout,
                level=LOG_LEVEL,
                format=(
                    "<green>{time:HH:mm:ss.SSS}</green> "
                    "<level>{level: <8}</level> "
                    "<cyan>{name}</cyan> - <level>{message}</level>"
                ),
                enqueue=False, backtrace=not IS_PRODUCTION,
                diagnose=not IS_PRODUCTION,
            )
            lg._app_configured = True  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass
    return lg


# ═══════════════════════════════════════════════════════════════
#  Timed context manager
# ═══════════════════════════════════════════════════════════════
class timed:
    """TH: วัดเวลาและ log อัตโนมัติ | EN: time and log a block

    Usage:
        with timed(logger, "db.query", table="users"):
            await session.execute(stmt)
    """

    __slots__ = ("_logger", "_label", "_level", "_extra", "_t0")

    def __init__(
        self,
        logger: logging.Logger,
        label: str,
        *,
        level: int = logging.DEBUG,
        **extra: Any,
    ) -> None:
        self._logger = logger
        self._label = label
        self._level = level
        self._extra = extra
        self._t0 = 0.0

    def __enter__(self) -> "timed":
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        elapsed_ms = int((time.perf_counter() - self._t0) * 1000)
        payload = {**self._extra, "elapsed_ms": elapsed_ms}
        if exc is not None:
            payload["error"] = type(exc).__name__
            self._logger.log(
                logging.ERROR, "%s failed in %dms", self._label, elapsed_ms,
                extra=payload,
            )
        else:
            self._logger.log(
                self._level, "%s took %dms", self._label, elapsed_ms,
                extra=payload,
            )


# ═══════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════
__all__ = [
    # Core
    "get_logger",
    "configure_logging",
    "timed",
    # Context binding
    "bind_context",
    "bind_from_request_ctx",
    "clear_context",
    "get_request_id",
    "get_trace_id",
    "new_request_id",
    "new_trace_id",
    # Redaction
    "redact",
    "redact_dict",
    # Formatters (สำหรับ custom setup)
    "JSONFormatter",
    "PrettyFormatter",
    "ContextFilter",
    # Optional
    "get_loguru_logger",
    # Env flags
    "ENV",
    "IS_PRODUCTION",
    "LOG_LEVEL",
    "LOG_FORMAT",
]