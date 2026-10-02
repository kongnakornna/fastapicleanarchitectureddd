"""OpenAPI docs — tool_calling module"""
from __future__ import annotations
from typing import Any


def register_tool_calling_openapi(app: object) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "Tools" for t in tags):
            tags.append({
                "name": "Tools",
                "description": "Tool Calling — registry + invoke + permissions.",
            })
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "tool_calling")
        info.setdefault("x-layer", "5-Intel")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
