"""ai_evaluation OpenAPI docs"""
from __future__ import annotations
from typing import Any


def register_ai_evaluation_openapi(app: object) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "AIEvaluation" for t in tags):
            tags.append({
                "name": "AIEvaluation",
                "description": (
                    "โมดูล ai_evaluation — LLM/RAG Evaluation\n\n"
                    "• RAGAS, faithfulness, answer_relevance\n"
                    "• MRR, NDCG, precision@k, recall@k\n"
                    "• Hallucination detection\n"
                    "• Dataset + Run + Report"
                ),
                "externalDocs": {
                    "description": "ai_evaluation Module README",
                    "url": "/docs/README_ai_evaluation.md",
                },
            })
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "ai_evaluation")
        info.setdefault("x-layer", "5-Intel")
        info.setdefault("x-prefix", "eval")
        info.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
