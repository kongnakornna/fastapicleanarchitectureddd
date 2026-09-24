"""ToolRegistration entity — alias to ORM"""
from __future__ import annotations
from app.modules.tool_calling.infrastructure.models import ToolRegistrationModel


class ToolRegistration(ToolRegistrationModel):
    """TH: ToolRegistration | EN: ToolRegistration entity (alias)"""
