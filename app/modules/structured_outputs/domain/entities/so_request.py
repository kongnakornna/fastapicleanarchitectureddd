"""SORequest entity — alias to ORM"""
from __future__ import annotations
from app.modules.structured_outputs.infrastructure.models import SORequestModel


class SORequest(SORequestModel):
    """TH: SORequest | EN: SORequest entity (alias)"""
