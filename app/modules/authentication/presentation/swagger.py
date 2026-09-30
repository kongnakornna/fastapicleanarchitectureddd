"""OpenAPI docs — authentication module"""
from __future__ import annotations
from typing import Any


def register_authentication_openapi(app: object) -> None:
    """TH: register OpenAPI metadata | EN: register OpenAPI metadata"""
    original_openapi = app.openapi

    def custom_openapi() -> dict[str, Any]:
        if getattr(app, "openapi_schema", None):
            return app.openapi_schema
        schema = original_openapi()
        tags = schema.setdefault("tags", [])
        if not any(t.get("name") == "Authentication" for t in tags):
            tags.append({
                "name": "Authentication",
                "description": (
                    "โมดูล authentication — Login (username OR email) / "
                    "Sign Up / Refresh / Logout / Password Recovery / 2FA"
                ),
            })
        info = schema.setdefault("info", {})
        info.setdefault("x-module", "authentication")
        info.setdefault("x-layer", "0-Core")
        info.setdefault("x-prefix", "auth_")
        info.setdefault("x-schema", "public")
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
