"""SOOutput entity — alias to ORM"""
from __future__ import annotations
from app.modules.structured_outputs.infrastructure.models import SOOutputModel


class SOOutput(SOOutputModel):
    """TH: SOOutput | EN: SOOutput entity (alias)"""
