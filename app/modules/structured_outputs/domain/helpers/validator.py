"""validator — jsonschema wrapper + basic fallback"""
from __future__ import annotations
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def build_strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """TH: เติม additionalProperties=false | EN: strict schema"""
    if not isinstance(schema, dict):
        return schema
    s = dict(schema)
    if s.get("type") == "object" and "additionalProperties" not in s:
        s["additionalProperties"] = False
    if isinstance(s.get("properties"), dict):
        s["properties"] = {
            k: build_strict_schema(v)
            for k, v in s["properties"].items()
        }
    if isinstance(s.get("items"), dict):
        s["items"] = build_strict_schema(s["items"])
    return s


def _basic_check(
    value: Any, schema: dict[str, Any], path: str = "$",
) -> list[dict[str, Any]]:
    """TH: ตรวจแบบ basic | EN: basic check"""
    errors: list[dict[str, Any]] = []
    if not isinstance(schema, dict):
        return errors

    expected = schema.get("type")
    _TYPE_MAP = {
        "object": dict, "array": list, "string": str,
        "number": (int, float), "integer": int,
        "boolean": bool, "null": type(None),
    }

    if expected in _TYPE_MAP:
        py_type = _TYPE_MAP[expected]
        if expected == "number" and isinstance(value, bool):
            errors.append({"path": path, "message": "boolean is not number"})
            return errors
        if expected == "integer" and isinstance(value, bool):
            errors.append({"path": path, "message": "boolean is not integer"})
            return errors
        if not isinstance(value, py_type):
            errors.append({
                "path": path,
                "message": f"expected {expected}, got {type(value).__name__}",
            })
            return errors

    if expected == "object" and isinstance(value, dict):
        required = schema.get("required") or []
        for key in required:
            if key not in value:
                errors.append({
                    "path": f"{path}.{key}",
                    "message": "missing required",
                })
        props = schema.get("properties") or {}
        for k, sub in props.items():
            if k in value:
                errors.extend(_basic_check(value[k], sub, f"{path}.{k}"))
        if schema.get("additionalProperties") is False:
            extras = set(value.keys()) - set(props.keys())
            for k in extras:
                errors.append({
                    "path": f"{path}.{k}",
                    "message": "additional property not allowed",
                })

    if expected == "array" and isinstance(value, list):
        items_schema = schema.get("items")
        if isinstance(items_schema, dict):
            for i, item in enumerate(value):
                errors.extend(_basic_check(item, items_schema, f"{path}[{i}]"))

    if "enum" in schema and value not in schema["enum"]:
        errors.append({
            "path": path,
            "message": f"value not in enum {schema['enum']}",
        })

    if expected == "string" and isinstance(value, str):
        if "minLength" in schema and len(value) < int(schema["minLength"]):
            errors.append({"path": path, "message": "string too short"})
        if "maxLength" in schema and len(value) > int(schema["maxLength"]):
            errors.append({"path": path, "message": "string too long"})

    return errors


def validate_schema(
    value: Any, schema: dict[str, Any],
) -> list[dict[str, Any]]:
    """TH: validate object กับ schema | EN: validate against schema"""
    if not isinstance(schema, dict) or not schema:
        return []

    try:
        import jsonschema  # type: ignore
        validator = jsonschema.Draft7Validator(schema)
        errors = list(validator.iter_errors(value))
        return [
            {
                "path": "/".join(str(p) for p in e.absolute_path) or "$",
                "message": e.message,
                "kind": e.validator or "",
            }
            for e in errors
        ]
    except ImportError:
        logger.debug("jsonschema not available, using basic check")
        return _basic_check(value, schema)
    except Exception as exc:
        logger.debug("jsonschema failed, fallback: %s", exc)
        return _basic_check(value, schema)
