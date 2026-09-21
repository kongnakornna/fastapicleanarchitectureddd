"""
TH: Alembic environment — โหลด models ทั้งหมด + run migration
EN: Alembic environment — load all models + run migration
"""
from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context

# ═════════════════════════════════════════════════════════════════
# PATH SETUP
# ═════════════════════════════════════════════════════════════════
# TH: เพิ่ม project root เข้า sys.path เพื่อ import app.* ได้
# EN: add project root to sys.path so app.* imports work
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.database import pg_engine  # noqa: E402

# ═════════════════════════════════════════════════════════════════
# IMPORT BASE METADATA
# ═════════════════════════════════════════════════════════════════
# TH: BaseModel คือ declarative base — metadata ที่ Alembic จะ autogenerate
# EN: BaseModel is the declarative base — metadata for autogenerate
from app.modules.shared.infrastructure.models import BaseModel  # noqa: E402

# ═════════════════════════════════════════════════════════════════
# AUTO-REGISTERED MODELS
# ═════════════════════════════════════════════════════════════════
# TH: import ทุก model เพื่อให้ Alembic เห็น metadata
#     ใช้ try/except กัน module ที่ไม่มี models (pure VO / ไม่มีไฟล์)
# EN: import every model so Alembic sees the metadata
#     try/except for modules without models (pure VO / no file)

# --- module user ---
try:
    from app.modules.user.infrastructure.models import UserModel  # noqa: F401
except ImportError:
    pass

# --- module authentication ---
try:
    from app.modules.authentication.infrastructure.models import (  # noqa: F401
        AccessTokenModel,
        AuthenticationModel,
        RefreshTokenModel,
    )
except ImportError:
    pass

# --- module notification ---
try:
    from app.modules.notification.infrastructure.models import (  # noqa: F401
        NotificationModel,
    )
except ImportError:
    pass

# --- module money ---
# TH: money เป็น pure VO — ไม่มี DB models
# EN: money is a pure VO module — no DB models
try:
    from app.modules.money.infrastructure.models import MoneyModel  # noqa: F401
except ImportError:
    pass

# --- module audit ---
try:
    from app.modules.audit.infrastructure.models import AuditLogModel  # noqa: F401
except ImportError:
    pass

# --- module websocket (no DB models) ---
# TH: websocket ไม่มี DB models
# EN: websocket has no DB models


# ═════════════════════════════════════════════════════════════════
# ALEMBIC CONFIG
# ═════════════════════════════════════════════════════════════════
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# TH: metadata ที่ Alembic ใช้ autogenerate
# EN: metadata used by Alembic for autogenerate
target_metadata = BaseModel.metadata


# ═════════════════════════════════════════════════════════════════
# RUN MIGRATIONS
# ═════════════════════════════════════════════════════════════════
def run_migrations_offline() -> None:
    """TH: run migration แบบ offline (generate SQL) | EN: offline mode"""
    url = pg_engine.url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """TH: run migration แบบ online (ต่อ DB จริง) | EN: online mode"""
    with pg_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
