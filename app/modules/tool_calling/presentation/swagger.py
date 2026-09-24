"""OpenAPI docs — tool_calling module"""
from __future__ import annotations
from typing import Any


def register_tool_calling_openapi(app: object) -> None:
    """TH: register OpenAPI metadata | EN: register OpenAPI metadata"""
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "Tools" for t in tags):
            tags.append({
                "name": "Tools",
                "description": (
                    "โมดูล tool_calling — Function/Tool Calling\n\n"
                    "• Tool registry (HTTP / Python / SQL / MCP)\n"
                    "• Invocation + permissions + rate limit\n"
                    "• Idempotency-Key support\n"
                    "• ReAct loop compatible (ใช้กับ llm module)"
                ),
                "externalDocs": {
                    "description": "tool_calling Module README",
                    "url": "/docs/README_tool_calling.md",
                },
            })
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "tool_calling")
        info.setdefault("x-layer", "5-Intel")
        info.setdefault("x-prefix", "tool")
        info.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
