"""llamaindex OpenAPI docs"""
from __future__ import annotations
from typing import Any


def register_llamaindex_openapi(app: object) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "LlamaIndex" for t in tags):
            tags.append({
                "name": "LlamaIndex",
                "description": (
                    "โมดูล llamaindex — Index + QueryEngine + Synthesis\n\n"
                    "• Index types: VectorStore, Summary, Tree, KG\n"
                    "• Response modes: compact, refine, tree_summarize\n"
                    "• Node relationships (parent/child/prev/next)\n"
                    "• Source nodes + citations"
                ),
                "externalDocs": {
                    "description": "llamaindex Module README",
                    "url": "/docs/README_llamaindex.md",
                },
            })
        info_ = schema.setdefault("info", {})
        info_.setdefault("x-module", "llamaindex")
        info_.setdefault("x-layer", "5-Intel")
        info_.setdefault("x-prefix", "li")
        info_.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
