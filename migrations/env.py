"""
TH: Alembic environment — โหลด models ทั้งหมด + run migration
EN: Alembic environment — load all models + run migration
"""
from __future__ import annotations

import importlib
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
# TH: import ทุก module ที่มี models เพื่อให้ Alembic เห็น metadata
#     module ที่ไม่มีอยู่ จะถูกข้ามไปเงียบ ๆ
# EN: import every module that declares models so Alembic sees the
#     metadata. Modules that don't exist are silently skipped.
#
#     Importing the package is enough: each module's models/__init__.py
#     re-exports its classes, and any `class Foo(BaseModel)` registers
#     its table on BaseModel.metadata at import time.

_MODEL_MODULES = (
    # ─── Layer 0-2: core ─────────────────────────────────────────────
    "app.modules.user.infrastructure.models",
    "app.modules.authentication.infrastructure.models",
    "app.modules.notification.infrastructure.models",
    "app.modules.key.infrastructure.models",          # ← เพิ่ม (erp_keys)
    "app.modules.knowledge.infrastructure.models",    # ← เพิ่ม (erp_knowledges)
    "app.modules.audit.infrastructure.models",
    # ─── Layer 3: compliance ─────────────────────────────────────────
    "app.modules.pdpa.infrastructure.models",
    # ─── Layer 5: Intel / AI ─────────────────────────────────────────
    "app.modules.llm.infrastructure.models",
    "app.modules.tool_calling.infrastructure.models",
    "app.modules.structured_outputs.infrastructure.models",
    "app.modules.hybrid_search.infrastructure.models",
    "app.modules.langchain.infrastructure.models",
    "app.modules.llamaindex.infrastructure.models",
    "app.modules.rag.infrastructure.models",
    "app.modules.ai_evaluation.infrastructure.models",
    "app.modules.vector_db.infrastructure.models",
    "app.modules.bigo.infrastructure.models",
    # ─── Layer 6: Monitor / IoT ──────────────────────────────────────
    "app.modules.iot.infrastructure.models",
    "app.modules.fullschedule.infrastructure.models",
    "app.modules.health.infrastructure.models",
)

for _module_path in _MODEL_MODULES:
    try:
        importlib.import_module(_module_path)
    except ImportError:
        # Module doesn't exist in this build — that's fine, just skip.
        pass


# ═════════════════════════════════════════════════════════════════
# ALEMBIC CONFIG
# ═════════════════════════════════════════════════════════════════
# --- module yolo (Detection) ---
try:
    from app.modules.yolo.infrastructure.models import (  # noqa: F401
        AnnotationModel, ClassModel, DatasetModel, ImageModel,
        InferenceModel, ModelModel, TrainingModel,
    )
except ImportError:
    pass


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# TH: metadata ที่ Alembic ใช้ autogenerate
# EN: metadata used by Alembic for autogenerate
target_metadata = BaseModel.metadata


# ═════════════════════════════════════════════════════════════════
# INCLUDE OBJECT FILTER
# ═════════════════════════════════════════════════════════════════
def include_object(object, name, type_, reflected, compare_to):  # noqa: A002
    """Restrict Alembic to only managing tables declared in our models.

    This database is shared with other systems that own `sd_*`, `auth_*`,
    and various legacy tables. Without this filter, autogenerate emits
    `DROP TABLE` statements for every reflected table it doesn't find in
    our metadata — which is both wrong and destructive.

    Returning `False` tells Alembic "ignore this object entirely."
    """
    if type_ == "table":
        return name in target_metadata.tables
    return True


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
        include_object=include_object,
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
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
