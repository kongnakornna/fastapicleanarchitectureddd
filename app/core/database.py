"""Database engines + session factories (sync for Alembic, async for FastAPI)"""
from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from fastapi.exceptions import RequestValidationError
from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.settings import settings
from app.modules.shared.application.exceptions import StandardException


# ═══════════════════════════════════════════════════════════════
# 0) Helper — describe a DB URL safely (never logs password)
# ═══════════════════════════════════════════════════════════════
def _describe_db_target(url) -> str:
    """One-line summary of a DB URL — password shown only as a boolean flag."""
    try:
        u = url if hasattr(url, "username") else make_url(url)
        return (
            f"driver={u.drivername} user={u.username!r} "
            f"host={u.host!r} port={u.port} db={u.database!r} "
            f"password_set={bool(u.password)}"
        )
    except Exception:
        return "<unable to describe>"


# ═══════════════════════════════════════════════════════════════
# 1) SYNC engine — Alembic / scripts ONLY
# ═══════════════════════════════════════════════════════════════
# ⚠️  CRITICAL — ต้องส่ง URL object ตรงๆ ห้ามครอบด้วย str()
#     `str(URL)` ใช้ hide_password=True → รหัสผ่านกลายเป็น "***"
#     → Postgres ตอบ 28P01 "password authentication failed".
pg_sync_engine = create_engine(
    settings.POSTGRESQL_DATABASE_URL,       # ← URL object (ไม่ใช่ str!)
    pool_pre_ping=True,
    echo=settings.APPLICATION_ENVIRONMENT_DEBUG,
    future=True,
)

# Backwards-compat alias: some templates / alembic/env.py reference `pg_engine`.
pg_engine = pg_sync_engine

PGSession = sessionmaker(
    pg_sync_engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_sync_session() -> Iterator[Session]:
    """TH: sync session (scripts / Alembic) | EN: sync session (scripts)"""
    session = PGSession()
    try:
        yield session
        session.commit()
    except StandardException:
        session.rollback()
        raise
    except SQLAlchemyError as e:
        logger.opt(exception=e).error("A database error occurred during the session.")
        session.rollback()
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred during the database session."
        )
        session.rollback()
        raise
    finally:
        session.close()


# ═══════════════════════════════════════════════════════════════
# 2) ASYNC engine — FastAPI runtime
# ═══════════════════════════════════════════════════════════════
# NOTE: asyncpg supports `server_settings` (unlike pg8000).
#       ✅ URL object passed directly — same rule as the sync engine.
pg_async_engine: AsyncEngine = create_async_engine(
    settings.POSTGRESQL_ASYNC_DATABASE_URL,   # already a URL object
    pool_pre_ping=True,
    echo=settings.APPLICATION_ENVIRONMENT_DEBUG,
    connect_args={"server_settings": {"timezone": "Asia/Bangkok"}},
    future=True,
)

# NOTE: `autocommit` is not a valid kwarg for `async_sessionmaker`
# in SQLAlchemy 2.0. It was being swallowed by **kw and is now removed.
PGAsyncSession = async_sessionmaker(
    bind=pg_async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """
    TH: async session (FastAPI)
    EN: async session (FastAPI)

    Client-side errors (RequestValidationError / StarletteHTTPException) are
    re-raised WITHOUT logging as internal errors, so 4xx responses don't
    pollute the error log. Server-side failures are logged + rolled back.
    """
    async with PGAsyncSession() as session:
        try:
            yield session
            await session.commit()

        # ✅ Client-side errors — don't log as internal errors
        except (RequestValidationError, StarletteHTTPException):
            await session.rollback()
            raise

        except StandardException:
            await session.rollback()
            raise

        except SQLAlchemyError as e:
            logger.opt(exception=e).error(
                "An asynchronous database error occurred during the session."
            )
            await session.rollback()
            raise

        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the asynchronous database session."
            )
            await session.rollback()
            raise
        # NOTE: no `finally: await session.close()` — `async with` handles it.


# ═══════════════════════════════════════════════════════════════
# 3) Startup / shutdown hooks
# ═══════════════════════════════════════════════════════════════
def _log_auth_hint(exc: BaseException) -> None:
    """Translate the most common Postgres errors into actionable hints."""
    text_ = str(exc)
    if "28P01" in text_ or "password authentication failed" in text_:
        logger.error(
            "════════ HINT (28P01) ════════\n"
            "PostgreSQL rejected the password.\n"
            "  1) ยืนยันว่ารหัสผ่านใน .env ตรงกับที่ Postgres เก็บไว้\n"
            "  2) ตรวจว่ามีอักขระพิเศษ (@ : / # ?) — URL.create() จัดการให้แล้ว\n"
            "  3) ตรวจว่า engine ไม่ได้สร้างจาก str(URL) (จะ mask เป็น ***)\n"
            "  4) ถ้าใช้ Docker + เปลี่ยน POSTGRES_PASSWORD หลังสร้าง volume:\n"
            "     docker compose down -v && docker compose up -d"
        )
    elif "3D000" in text_ or "does not exist" in text_:
        logger.error(
            "════════ HINT (3D000) ════════\n"
            "Database name ใน .env ไม่มีอยู่ใน Postgres — ตรวจ POSTGRESQL_DATABASE"
        )
    elif "Connection refused" in text_ or "could not connect" in text_:
        logger.error(
            "════════ HINT (connection) ════════\n"
            "Postgres ไม่ได้ listen ที่ host:port นี้ — ตรวจ POSTGRESQL_HOST/PORT"
        )


async def init_database_client() -> None:
    """
    Verify BOTH engines can connect + execute a trivial query.
    Logs the connection target (no password) so failures are diagnosable
    from the log alone.
    """
    # ─── log targets (safe — no password leaked) ────────────────
    logger.info(f"DB target (sync) : {_describe_db_target(settings.POSTGRESQL_DATABASE_URL)}")
    logger.info(f"DB target (async): {_describe_db_target(settings.POSTGRESQL_ASYNC_DATABASE_URL)}")

    try:
        # ─── sync handshake ──────────────────────────────────────
        logger.info("Establishing sync database connection...")
        with pg_sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Sync DB connection OK.")

        # ─── async handshake ─────────────────────────────────────
        logger.info("Establishing async database connection...")
        async with pg_async_engine.connect() as async_conn:
            await async_conn.execute(text("SELECT 1"))
        logger.info("Async DB connection OK.")

        logger.info("Database connection established successfully.")

    except SQLAlchemyError as e:
        _log_auth_hint(e)
        logger.opt(exception=e).error(
            "An error occurred while initializing the database."
        )
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred while initializing the database."
        )
        raise


async def close_database_client() -> None:
    try:
        pg_sync_engine.dispose()
        await pg_async_engine.dispose()

        logger.info("Database connection closed successfully.")
    except SQLAlchemyError as e:
        logger.opt(exception=e).error(
            "An error occurred while closing the database connection."
        )
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred while closing the database connection."
        )
        raise


__all__ = [
    # sync
    "pg_sync_engine", "pg_engine", "PGSession", "get_sync_session",
    # async
    "pg_async_engine", "PGAsyncSession", "get_async_session",
    # lifecycle
    "init_database_client", "close_database_client",
]
