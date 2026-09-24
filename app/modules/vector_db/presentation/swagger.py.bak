"""vector_db OpenAPI docs"""
from __future__ import annotations
from typing import Any


def register_vector_db_openapi(app: object) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "VectorDB" for t in tags):
            tags.append({
                "name": "VectorDB",
                "description": (
                    "โมดูล vector_db — ANN Store\n\n"
                    "• Collections + vectors\n"
                    "• Query: cosine / L2 / IP\n"
                    "• ANN indexes: HNSW / IVFFlat\n"
                    "• Multi-backend: pgvector / Qdrant"
                ),
                "externalDocs": {
                    "description": "vector_db Module README",
                    "url": "/docs/README_vector_db.md",
                },
            })
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "vector_db")
        info.setdefault("x-layer", "5-Intel")
        info.setdefault("x-prefix", "vdb")
        info.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
