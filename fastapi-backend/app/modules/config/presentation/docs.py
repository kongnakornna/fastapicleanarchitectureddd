"""
Presentation Docs — เอกสารของ router
ใช้รวม metadata สำหรับ OpenAPI
"""

from __future__ import annotations

router_docs = {
    "tags": ["Config"],
    "description": "Module config (Layer 0) — Cross-cutting configuration "
    "with 3-level override: GLOBAL → TENANT → USER",
}


__all__ = ["router_docs"]
