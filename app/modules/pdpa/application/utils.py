"""pdpa application utils"""
from __future__ import annotations
from datetime import UTC, datetime, timedelta
from typing import Any


def anonymize_pii(data: dict[str, Any]) -> dict[str, Any]:
    """TH: ปิดบัง PII ก่อนส่ง LLM | EN: Anonymize PII before LLM"""
    MASK_FIELDS = {
        "email", "phone", "national_id", "full_name",
        "address", "ip_address", "user_agent",
    }
    return {
        k: ("***" if k in MASK_FIELDS else v)
        for k, v in data.items()
    }


def dsar_sla_deadline(days: int = 30) -> datetime:
    """TH: deadline มาตรฐาน | EN: standard deadline"""
    return datetime.now(UTC) + timedelta(days=days)


def scoped_idempotency_scope(scope: str, method: str, path: str) -> str:
    """TH: สร้าง scope key ให้เหมาะกับ log | EN: compose a scope string"""
    return f"{scope}:{method.upper()}:{path}"