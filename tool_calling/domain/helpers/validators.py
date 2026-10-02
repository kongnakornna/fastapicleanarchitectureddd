"""tool_calling validators — never-raise"""
from __future__ import annotations
import re
from typing import Any

_SECRET_KEYS = re.compile(r"(api_?key|secret|password|token|bearer)", re.IGNORECASE)
_SQL_DANGER = re.compile(r"\b(DROP|TRUNCATE|DELETE|ALTER|GRANT|REVOKE)\b", re.IGNORECASE)


def validate_arguments(args: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = schema.get("required", []) or []
    props = schema.get("properties", {}) or {}
    for k in required:
        if k not in args:
            errors.append(f"missing required: {k}")
    for k, v in args.items():
        if k in props:
            t = props[k].get("type")
            if t == "string" and not isinstance(v, str):
                errors.append(f"{k} must be string")
            elif t == "integer" and not isinstance(v, int):
                errors.append(f"{k} must be integer")
            elif t == "number" and not isinstance(v, (int, float)):
                errors.append(f"{k} must be number")
            elif t == "boolean" and not isinstance(v, bool):
                errors.append(f"{k} must be boolean")
            elif t == "array" and not isinstance(v, list):
                errors.append(f"{k} must be array")
    return errors


def is_safe_sql(sql: str) -> bool:
    return not bool(_SQL_DANGER.search(sql or ""))


def redact_secrets(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: ("***REDACTED***" if _SECRET_KEYS.search(str(k))
                    else redact_secrets(v)) for k, v in data.items()}
    if isinstance(data, list):
        return [redact_secrets(x) for x in data]
    return data
