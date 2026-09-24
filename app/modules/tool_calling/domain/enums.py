"""tool_calling enums"""
from __future__ import annotations
from enum import StrEnum


class ToolKind(StrEnum):
    """TH: ประเภท tool | EN: Tool kind"""
    HTTP = "http"
    PYTHON = "python"
    SQL = "sql"
    SHELL = "shell"
    MCP = "mcp"
    OPENAPI = "openapi"


class ToolStatus(StrEnum):
    """TH: สถานะการเรียก | EN: Invocation status"""
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    DENIED = "DENIED"
    RATE_LIMITED = "RATE_LIMITED"


class RiskLevel(StrEnum):
    """TH: ความเสี่ยง | EN: Risk level"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ToolVisibility(StrEnum):
    """TH: การมองเห็น | EN: Visibility"""
    PRIVATE = "private"
    TENANT = "tenant"
    PUBLIC = "public"
