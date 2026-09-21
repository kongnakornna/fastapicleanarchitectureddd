"""tenant_context presentation docs — เอกสาร API."""

router_docs = {
    "tags": ["Tenant Context"],
    "description": (
        "Module tenant_context (Layer 0) — จัดการบริบทผู้เช่าสำหรับ multi-tenant"
    ),
}

current_docs = {
    "summary": "Get current tenant context — ดึง context ปัจจุบัน",
    "responses": {
        200: {"description": "Current context"},
        400: {"description": "Context not set"},
    },
}

switch_docs = {
    "summary": "Switch tenant — เปลี่ยน tenant",
    "responses": {
        200: {"description": "Switched successfully"},
        404: {"description": "Tenant not found"},
    },
}
