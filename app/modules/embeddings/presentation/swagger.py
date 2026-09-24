"""embeddings OpenAPI docs"""
from __future__ import annotations
from typing import Any


def register_embeddings_openapi(app: object) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "Embeddings" for t in tags):
            tags.append({
                "name": "Embeddings",
                "description": (
                    "โมดูล embeddings — Text → Vector\n\n"
                    "• Providers: OpenAI / Cohere / HF / BGE / Local\n"
                    "• Single + Batch embedding\n"
                    "• Hash-based cache (Redis)\n"
                    "• Rate limiting + Retry"
                ),
                "externalDocs": {
                    "description": "embeddings Module README",
                    "url": "/docs/README_embeddings.md",
                },
            })
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "embeddings")
        info.setdefault("x-layer", "5-Intel")
        info.setdefault("x-prefix", "emb")
        info.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
