"""Idempotency presentation docs — เอกสาร"""

idempotency_docs = {
    "description": (
        "Idempotency middleware — ทุก mutating request ต้องส่ง Idempotency-Key header"
    ),
    "headers": {
        "Idempotency-Key": {
            "description": "Unique key 8-255 chars",
            "required": True,
        }
    },
}
