"""Database reset and migration script."""
import sys

from sqlalchemy import text

from app.core.database import pg_engine


def reset_database():
    """Drop all tables and alembic_version, then recreate via migration."""
    print("=" * 50)
    print("DATABASE RESET")
    print("=" * 50)

    with pg_engine.connect() as conn:
        # Drop all enums first
        print("\n[1a] Dropping all enums...")
        result = conn.execute(text(
            "SELECT typname FROM pg_type t JOIN pg_namespace n ON t.typnamespace = n.oid "
            "WHERE n.nspname = 'public' AND t.typtype = 'e'"
        ))
        enums = [row[0] for row in result]
        for e in enums:
            conn.execute(text(f'DROP TYPE IF EXISTS "{e}" CASCADE'))
            print(f"    Dropped enum: {e}")

        # Drop all tables
        print("\n[1b] Dropping all tables...")
        result = conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public'"
        ))
        tables = [row[0] for row in result]
        print(f"    Found {len(tables)} tables")

        for table in tables:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            print(f"    Dropped: {table}")

        # Drop alembic_version
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        conn.commit()
        print("    Dropped: alembic_version")
        print(f"    Total dropped: {len(tables)} tables, {len(enums)} enums")

    print("\n[2] Applying all migrations...")
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    # Verify
    with pg_engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
        ))
        tables = [row[0] for row in result]
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        version = result.scalar()

        print(f"\n{'=' * 50}")
        print(f"RESULT")
        print(f"{'=' * 50}")
        print(f"  Migration version: {version}")
        print(f"  Total tables: {len(tables)}")
        for t in tables:
            print(f"    - {t}")
        print(f"{'=' * 50}")


def show_status():
    """Show current database status."""
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    alembic_cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(alembic_cfg)

    with pg_engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        current = result.scalar() or "none"

        result = conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"
        ))
        tables = [row[0] for row in result]

        heads = script.get_heads()
        base = script.get_base()

        print(f"{'=' * 50}")
        print(f"DATABASE STATUS")
        print(f"{'=' * 50}")
        print(f"  Current version : {current}")
        print(f"  Head version    : {heads}")
        print(f"  Base version    : {base}")
        print(f"  Status          : {'UP TO DATE' if current == heads else 'NEEDS MIGRATION'}")
        print(f"  Total tables    : {len(tables)}")
        for t in tables:
            print(f"    - {t}")
        print(f"{'=' * 50}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "reset":
        reset_database()
    elif cmd == "status":
        show_status()
    else:
        print(f"Usage: python scripts/db.py [reset|status]")
