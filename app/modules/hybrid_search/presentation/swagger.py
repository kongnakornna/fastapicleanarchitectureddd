"""hybrid_search OpenAPI docs"""
from __future__ import annotations
from typing import Any


def register_hybrid_search_openapi(app: object) -> None:
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "HybridSearch" for t in tags):
            tags.append({
                "name": "HybridSearch",
                "description": (
                    "โมดูล hybrid_search — BM25 + Vector + Fusion\n\n"
                    "• Fusion: RRF, WeightedSum, CombSUM, CombMNZ\n"
                    "• Rerank: cross_encoder, cohere, bge\n"
                    "• Metrics: MRR, NDCG, Recall@k, Precision@k"
                ),
                "externalDocs": {
                    "description": "hybrid_search Module README",
                    "url": "/docs/README_hybrid_search.md",
                },
            })
        info_ = schema.setdefault("info", {})
        info_.setdefault("x-module", "hybrid_search")
        info_.setdefault("x-layer", "5-Intel")
        info_.setdefault("x-prefix", "hs")
        info_.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
