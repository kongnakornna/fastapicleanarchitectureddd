# app/core/migrations.py (ฉบับแก้ไข)
from __future__ import annotations

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.util.exc import CommandError
from loguru import logger
from sqlalchemy import inspect, text

from app.core.database import pg_engine
from app.modules.shared.application.exceptions import StandardException


def init_alembic_management() -> None:
    """ตรวจสอบและ apply Alembic migrations ตอน startup."""
    try:
        logger.info("Checking Alembic migration status...")

        alembic_cfg = Config("alembic.ini")
        if not alembic_cfg.get_main_option("script_location"):
            alembic_cfg.set_main_option("script_location", "migrations")

        inspector = inspect(pg_engine)
        has_alembic_table = "alembic_version" in inspector.get_table_names()

        script = ScriptDirectory.from_config(alembic_cfg)
        head_revision = script.get_current_head()

        # ─────────────────────────────────────────────────────────────
        # Case 0: ไม่มี migration ไฟล์ในโค้ดเลย (head = None)
        # ─────────────────────────────────────────────────────────────
        if head_revision is None:
            logger.error(
                "No migration scripts found in 'migrations/versions/'. "
                "Cannot apply migrations. "
                "Please run: alembic revision --autogenerate -m 'initial schema'"
            )
            # ล้าง alembic_version ใน DB เพราะไม่มี revision ที่ valid
            if has_alembic_table:
                with pg_engine.begin() as conn:
                    conn.execute(text("DELETE FROM alembic_version"))
                logger.warning(
                    "Cleared stale alembic_version table. "
                    "Please create a new migration before next startup."
                )
            return  # ← ไม่ raise เพื่อให้ app ยัง start ได้

        # ─────────────────────────────────────────────────────────────
        # Case 1: ยังไม่มีตาราง alembic_version → ฐานข้อมูลว่าง
        # ─────────────────────────────────────────────────────────────
        if not has_alembic_table:
            logger.warning(
                "Alembic version table not found. Initializing management..."
            )
            command.upgrade(alembic_cfg, "head")
            logger.info("Successfully applied all migrations.")
            return

        # ─────────────────────────────────────────────────────────────
        # Case 2: มีตาราง alembic_version → อ่าน revision ปัจจุบัน
        # ─────────────────────────────────────────────────────────────
        with pg_engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current_revision = result.scalar()

        logger.info(
            f"Current revision: {current_revision}, Head revision: {head_revision}"
        )

        # ─────────────────────────────────────────────────────────────
        # Case 2a: revision ปัจจุบันไม่มีในโค้ด
        # ─────────────────────────────────────────────────────────────
        if current_revision and not _revision_exists(script, current_revision):
            logger.error(
                f"Current revision '{current_revision}' not found in scripts. "
                f"Head revision available: {head_revision}"
            )
            logger.warning("Auto-stamping database to head revision.")
            command.stamp(alembic_cfg, "head")
            logger.info(f"Successfully stamped database to head: {head_revision}")
            return

        # ─────────────────────────────────────────────────────────────
        # Case 3: revision ตรงกันแล้ว
        # ─────────────────────────────────────────────────────────────
        if current_revision == head_revision:
            logger.info("Database is up to date. No migrations needed.")
            return

        # ─────────────────────────────────────────────────────────────
        # Case 4: มี pending migrations → upgrade
        # ─────────────────────────────────────────────────────────────
        logger.info(
            f"Pending migrations detected. Current: {current_revision}, "
            f"Target: {head_revision}. Upgrading..."
        )
        command.upgrade(alembic_cfg, "head")
        logger.info("Successfully applied pending migrations.")

    except StandardException:
        raise
    except CommandError as e:
        logger.opt(exception=e).error(
            f"Alembic command failed: {e}. "
            f"Check your migration files and alembic_version table."
        )
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred while managing Alembic migrations."
        )
        raise


def _revision_exists(script: ScriptDirectory, revision: str) -> bool:
    """ตรวจสอบว่า revision มีอยู่ใน migrations/versions หรือไม่."""
    try:
        script.get_revision(revision)
        return True
    except Exception:
        return False
