"""rag OpenAPI docs"""
from __future__ import annotations
from typing import Any


def register_rag_openapi(app: object) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "RAG" for t in tags):
            tags.append({
                "name": "RAG",
                "description": (
                    "โมดูล rag — Retrieval Augmented Generation\n\n"
                    "• Ingest: chunk → embed → upsert vectors\n"
                    "• Query: retrieve → rerank → generate\n"
                    "• Citations with score + snippet\n"
                    "• Multi-pipeline configs"
                ),
                "externalDocs": {
                    "description": "rag Module README",
                    "url": "/docs/README_rag.md",
                },
            })
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "rag")
        info.setdefault("x-layer", "5-Intel")
        info.setdefault("x-prefix", "rag")
        info.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
