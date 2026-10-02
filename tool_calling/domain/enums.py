"""tool_calling enums"""
from __future__ import annotations
from enum import StrEnum


class ToolKind(StrEnum):
    HTTP = "http"
    PYTHON = "python"
    SQL = "sql"
    SHELL = "shell"
    MCP = "mcp"
    OPENAPI = "openapi"


class ToolStatus(StrEnum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    DENIED = "DENIED"
    RATE_LIMITED = "RATE_LIMITED"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ToolVisibility(StrEnum):
    PRIVATE = "private"
    TENANT = "tenant"
    PUBLIC = "public"
