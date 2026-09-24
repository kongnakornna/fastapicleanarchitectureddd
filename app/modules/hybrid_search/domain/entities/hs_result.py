"""HSResult entity — alias to ORM"""
from __future__ import annotations
from app.modules.hybrid_search.infrastructure.models import HSResultModel


class HSResult(HSResultModel):
    """TH: HSResult | EN: HSResult entity (alias)"""
