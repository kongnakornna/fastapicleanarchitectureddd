"""validators — never-raise"""
from __future__ import annotations
import re
from typing import Any

_SQL_DANGEROUS = re.compile(
    r"\b(DROP|TRUNCATE|DELETE|ALTER|GRANT|REVOKE|CREATE\s+USER)\b",
    re.IGNORECASE,
)
_SECRET_KEYS = re.compile(
    r"(api_?key|secret|password|token|bearer)", re.IGNORECASE,
)


def validate_arguments(args: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """TH: validate args (minimal) | EN: minimal schema validation"""
    errors: list[str] = []
    required = schema.get("required", []) or []
    properties = schema.get("properties", {}) or {}
    for key in required:
        if key not in args:
            errors.append(f"missing required: {key}")
    for key, val in args.items():
        if key in properties:
            expected = properties[key].get("type")
            if expected == "string" and not isinstance(val, str):
                errors.append(f"{key} must be string")
            elif expected == "integer" and not isinstance(val, int):
                errors.append(f"{key} must be integer")
            elif expected == "number" and not isinstance(val, (int, float)):
                errors.append(f"{key} must be number")
            elif expected == "boolean" and not isinstance(val, bool):
                errors.append(f"{key} must be boolean")
            elif expected == "array" and not isinstance(val, list):
                errors.append(f"{key} must be array")
    return errors


def is_safe_sql(sql: str) -> bool:
    """TH: check SQL | EN: check SQL for danger"""
    return not bool(_SQL_DANGEROUS.search(sql or ""))


def redact_secrets(data: Any) -> Any:
    """TH: ซ่อน secret | EN: redact secrets"""
    if isinstance(data, dict):
        return {
            k: ("***REDACTED***" if _SECRET_KEYS.search(str(k))
                else redact_secrets(v))
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [redact_secrets(x) for x in data]
    return data
