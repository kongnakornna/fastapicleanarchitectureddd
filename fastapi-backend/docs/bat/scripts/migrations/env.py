from logging.config import fileConfig

from alembic import context

from app.core.database import pg_engine

# --- module money (auto-registered) ---
from app.modules.money2.infrastructure.models import MoneyModel  # noqa: F401

# --- module money (auto-registered) ---
from app.modules.money.infrastructure.models import MoneyModel  # noqa: F401

# --- module 123abc (auto-registered) ---
from app.modules.123abc.infrastructure.models import 123AbcModel  # noqa: F401

# --- module inventory (auto-registered) ---
from app.modules.inventory.infrastructure.models import InventoryModel  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    url = pg_engine.url
    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with pg_engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
