"""HSQuery entity — alias to ORM"""
from __future__ import annotations
from app.modules.hybrid_search.infrastructure.models import HSQueryModel


class HSQuery(HSQueryModel):
    """TH: HSQuery | EN: HSQuery entity (alias)"""
