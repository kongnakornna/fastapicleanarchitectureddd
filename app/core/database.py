"""Database engines + session factories (sync for Alembic, async for FastAPI)"""
from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings
from app.modules.shared.application.exceptions import StandardException


# ═══════════════════════════════════════════════════════════════
# 1) SYNC engine — Alembic / scripts ONLY
# ═══════════════════════════════════════════════════════════════
pg_sync_engine = create_engine(
    settings.POSTGRESQL_DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.APPLICATION_ENVIRONMENT_DEBUG,
    connect_args={"options": "-c timezone=Asia/Bangkok"},
    future=True,
)

# Backwards-compat alias: many templates + alembic/env.py reference `pg_engine`.
# Keep this so existing imports keep working. New code should use
# `pg_sync_engine` (explicit) or `pg_async_engine` (async).
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
pg_async_engine: AsyncEngine = create_async_engine(
    settings.POSTGRESQL_ASYNC_DATABASE_URL,   # must be postgresql+asyncpg://
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
    """TH: async session (FastAPI) | EN: async session (FastAPI)"""
    async with PGAsyncSession() as session:
        try:
            yield session
            await session.commit()
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
async def init_database_client() -> None:
    try:
        logger.info("Establishing database connection.")

        with pg_sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        async with pg_async_engine.connect() as async_conn:
            await async_conn.execute(text("SELECT 1"))

        logger.info("Database connection established successfully.")
    except StandardException:
        raise
    except SQLAlchemyError as e:
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
