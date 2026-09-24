# alembic/env.py
from app.core.database import pg_sync_engine  # was: pg_engine

config.set_main_option("sqlalchemy.url", str(pg_sync_engine.url))