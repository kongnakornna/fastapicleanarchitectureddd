"""VDBCollection entity — alias to ORM"""
from __future__ import annotations
from app.modules.vector_db.infrastructure.models import VDBCollectionModel


class VDBCollection(VDBCollectionModel):
    """TH: VDBCollection | EN: VDBCollection entity (alias)"""
