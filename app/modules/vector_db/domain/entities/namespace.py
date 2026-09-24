"""VDBNamespace entity — alias to ORM"""
from __future__ import annotations
from app.modules.vector_db.infrastructure.models import VDBNamespaceModel


class VDBNamespace(VDBNamespaceModel):
    """TH: VDBNamespace | EN: VDBNamespace entity (alias)"""
