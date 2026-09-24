"""VDBStats entity — alias to ORM"""
from __future__ import annotations
from app.modules.vector_db.infrastructure.models import VDBStatsModel


class VDBStats(VDBStatsModel):
    """TH: VDBStats | EN: VDBStats entity (alias)"""
