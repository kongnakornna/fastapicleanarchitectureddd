"""OpenAPI docs — bigo module"""
from __future__ import annotations
from typing import Any


def register_bigo_openapi(app: object) -> None:
    """TH: register OpenAPI metadata"""
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "Big-O Monitoring" for t in tags):
            tags.append({
                "name": "Big-O Monitoring",
                "description": (
                    "โมดูล bigo — Big-O Monitoring & Resource Optimization\n\n"
                    "• Big-O complexity analysis per function\n"
                    "• Memory LRU+TTL manager + snapshots + leak detection\n"
                    "• Kafka priority queue + retry + DLQ + lag monitoring\n"
                    "• Backpressure control (Redis-based)\n"
                    "• Prometheus-style metrics (counter/gauge/histogram)\n"
                    "• Pipeline orchestrator (/bigo/pipeline/*)\n"
                    "• Redis Cache + WebSocket + Admin (/bigo/admin/*)"
                ),
            })
        if not any(t.get("name") == "Big-O Admin" for t in tags):
            tags.append({
                "name": "Big-O Admin",
                "description": "Admin ops — config, cache, ws, health",
            })
        if not any(t.get("name") == "Big-O WebSocket" for t in tags):
            tags.append({
                "name": "Big-O WebSocket",
                "description": "Realtime stream — rooms, broadcast, heartbeat",
            })
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "bigo")
        info.setdefault("x-layer", "6-Monitor")
        info.setdefault("x-prefix", "bigo")
        info.setdefault("x-schema", "public")
        info.setdefault("x-version", "1.2.0")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
