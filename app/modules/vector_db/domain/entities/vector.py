"""VDBVector entity — alias to ORM"""
from __future__ import annotations
from app.modules.vector_db.infrastructure.models import VDBVectorModel


class VDBVector(VDBVectorModel):
    """TH: VDBVector | EN: VDBVector entity (alias)"""
