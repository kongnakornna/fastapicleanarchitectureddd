"""ToolDefinition entity — alias to ORM"""
from __future__ import annotations
from tool_calling.infrastructure.models import ToolDefinitionModel


class ToolDefinition(ToolDefinitionModel):
    """TH: ToolDefinition | EN: ToolDefinition entity (alias)"""
