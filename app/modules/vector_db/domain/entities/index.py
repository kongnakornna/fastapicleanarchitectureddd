"""VDBIndex entity — alias to ORM"""
from __future__ import annotations
from app.modules.vector_db.infrastructure.models import VDBIndexModel


class VDBIndex(VDBIndexModel):
    """TH: VDBIndex | EN: VDBIndex entity (alias)"""
