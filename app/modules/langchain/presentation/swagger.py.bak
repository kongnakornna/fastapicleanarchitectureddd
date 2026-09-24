"""langchain OpenAPI docs"""
from __future__ import annotations
from typing import Any


def register_langchain_openapi(app: object) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "LangChain" for t in tags):
            tags.append({
                "name": "LangChain",
                "description": (
                    "โมดูล langchain — LCEL + Agents + Memory\n\n"
                    "• LCEL / Sequential / Router / MapReduce / Refine\n"
                    "• ReAct / OpenAI-Tools / Plan-Execute / Reflexion\n"
                    "• Buffer / Window / Summary memory\n"
                    "• Step-by-step trace"
                ),
                "externalDocs": {
                    "description": "langchain Module README",
                    "url": "/docs/README_langchain.md",
                },
            })
        info_ = schema.setdefault("info", {})
        info_.setdefault("x-module", "langchain")
        info_.setdefault("x-layer", "5-Intel")
        info_.setdefault("x-prefix", "lc")
        info_.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
