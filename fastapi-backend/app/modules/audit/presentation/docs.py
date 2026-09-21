"""
Audit Router Docs — เอกสาร router audit
Audit Router Docs — OpenAPI documentation metadata
"""

from __future__ import annotations

router_docs = {
    "tags_metadata": [
        {
            "name": "Audit",
            "description": (
                "**Audit Logs (append-only)** — บันทึก audit แบบ append-only\n\n"
                "- Immutable: no UPDATE / DELETE — immutable ห้าม update/delete\n"
                "- Stores before/after state (ChangeSet)\n"
                "- Event-sourced: replayable — event-sourced เล่นซ้ำได้\n"
                "- Retention: 7 years (accounting law) — เก็บ 7 ปี\n"
                "- ทุก log มี actor_id, correlation_id, occurred_at"
            ),
        }
    ],
    "endpoints": {
        "list_logs": {
            "summary": "List audit logs",
            "description": "Query audit logs with filters + pagination",
        },
        "get_log": {
            "summary": "Get audit log",
            "description": "Fetch single audit log by id",
        },
        "resource_history": {
            "summary": "Resource history",
            "description": "Full chronological history of a resource",
        },
    },
}
