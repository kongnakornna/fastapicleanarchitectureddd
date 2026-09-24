"""structured_outputs OpenAPI docs"""
from __future__ import annotations
from typing import Any


def register_structured_outputs_openapi(app: object) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "StructuredOutputs" for t in tags):
            tags.append({
                "name": "StructuredOutputs",
                "description": (
                    "โมดูล structured_outputs — JSON Schema enforcement\n\n"
                    "• Schema registry (JSON Schema / Pydantic)\n"
                    "• Generate with auto repair loop\n"
                    "• Validation + repair attempts\n"
                    "• Strict mode (additionalProperties=false)"
                ),
                "externalDocs": {
                    "description": "structured_outputs Module README",
                    "url": "/docs/README_structured_outputs.md",
                },
            })
        info_ = schema.setdefault("info", {})
        info_.setdefault("x-module", "structured_outputs")
        info_.setdefault("x-layer", "5-Intel")
        info_.setdefault("x-prefix", "so")
        info_.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
