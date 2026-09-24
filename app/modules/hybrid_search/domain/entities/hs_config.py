"""HSConfig entity — alias to ORM"""
from __future__ import annotations
from app.modules.hybrid_search.infrastructure.models import HSConfigModel


class HSConfig(HSConfigModel):
    """TH: HSConfig | EN: HSConfig entity (alias)"""
