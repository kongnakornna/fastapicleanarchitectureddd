"""ToolInvocation entity — alias to ORM"""
from __future__ import annotations
from tool_calling.infrastructure.models import ToolInvocationModel


class ToolInvocation(ToolInvocationModel):
    """TH: ToolInvocation | EN: ToolInvocation entity (alias)"""
