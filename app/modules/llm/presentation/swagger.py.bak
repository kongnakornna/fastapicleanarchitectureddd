"""OpenAPI docs — llm module

TH: register OpenAPI metadata (tag, externalDocs, x-*)
EN: register OpenAPI metadata
"""
from __future__ import annotations
from typing import Any


def register_llm_openapi(app: object) -> None:
    """TH: register OpenAPI metadata | EN: register OpenAPI metadata"""
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "LLM" for t in tags):
            tags.append({
                "name": "LLM",
                "description": (
                    "โมดูล llm — Unified LLM Gateway\n\n"
                    "• Multi-provider (OpenAI / Anthropic / Local)\n"
                    "• Chat completion (sync + SSE streaming)\n"
                    "• Conversation management\n"
                    "• Token tracking + Cost (Decimal)\n"
                    "• Rate limiting + Caching + Failover"
                ),
                "externalDocs": {
                    "description": "llm Module README",
                    "url": "/docs/README_llm.md",
                },
            })
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "llm")
        info.setdefault("x-layer", "5-Intel")
        info.setdefault("x-prefix", "llm")
        info.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
