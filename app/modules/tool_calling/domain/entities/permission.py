"""ToolPermission entity — alias to ORM"""
from __future__ import annotations
from app.modules.tool_calling.infrastructure.models import ToolPermissionModel


class ToolPermission(ToolPermissionModel):
    """TH: ToolPermission | EN: ToolPermission entity (alias)"""
