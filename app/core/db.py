"""Database session — async façade for FastAPI DI

TH: ไฟล์นี้เป็น façade บาง ๆ ให้ FastAPI DI ใช้งาน
    — ใช้ engine async จาก app.core.database เท่านั้น
    — ชื่อ `get_session` คงไว้เพื่อ backward compat กับทุก module

EN: Thin async façade for FastAPI dependency injection.
    - Uses ONLY the async engine from app.core.database.
    - Keeps the public name `get_session` for backwards compatibility.
"""
from __future__ import annotations

from app.core.database import (
    PGAsyncSession,
    get_async_session as get_session,
    pg_async_engine,
)

__all__ = ["PGAsyncSession", "get_session", "pg_async_engine"]
