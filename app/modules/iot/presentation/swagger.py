"""OpenAPI docs — iot module"""
from __future__ import annotations
from typing import Any


def register_iot_openapi(app: object) -> None:
    """TH: register OpenAPI metadata | EN: register OpenAPI metadata"""
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "iot" for t in tags):
            tags.append({
                "name": "iot",
                "description": (
                    "โมดูล iot — Real-time Sensor & Alarm Monitoring\n\n"
                    "• MQTT Ingest\n"
                    "• Alarm Evaluation (hardware_id 1-4)\n"
                    "• Device Control\n"
                    "• Time-series (InfluxDB)\n"
                    "• WebSocket Real-time"
                ),
                "externalDocs": {
                    "description": "iot Module README",
                    "url": "/docs/README_iot.md",
                },
            })
        schema["info"] = schema.get("info", {})
        schema["info"].setdefault("x-module", "iot")
        schema["info"].setdefault("x-layer", "6-Monitor")
        schema["info"].setdefault("x-prefix", "iot")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
