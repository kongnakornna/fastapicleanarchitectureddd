"""tool_calling OpenAPI response examples"""
from __future__ import annotations

RESPONSE_TOOL_200 = {
    "description": "Tool detail",
    "content": {"application/json": {"example": {
        "id": "uuid", "name": "get_weather",
        "description": "Get weather by city",
        "parameters_json": {"type": "object"},
        "kind": "http", "is_active": True,
    }}},
}
RESPONSE_INVOKE_200 = {
    "description": "Tool invoked",
    "content": {"application/json": {"example": {
        "invocation_id": "uuid",
        "tool_name": "get_weather",
        "status": "SUCCESS",
        "output": {"temp": 32},
        "latency_ms": 145,
    }}},
}
RESPONSE_ERROR_403 = {
    "description": "Permission denied",
    "content": {"application/json": {"example": {
        "detail": "role 'guest' not allowed to invoke get_weather",
        "code": "PERMISSION_DENIED",
    }}},
}
RESPONSE_ERROR_404 = {
    "description": "Not found",
    "content": {"application/json": {"example": {
        "detail": "tool not found", "code": "NOT_FOUND",
    }}},
}
RESPONSE_ERROR_409 = {
    "description": "Conflict",
    "content": {"application/json": {"example": {
        "detail": "tool exists: get_weather", "code": "CONFLICT",
    }}},
}
RESPONSE_ERROR_422 = {
    "description": "Validation error",
    "content": {"application/json": {"example": {
        "detail": "invalid arguments: missing required: city",
        "code": "VALIDATION_ERROR",
    }}},
}
RESPONSE_ERROR_429 = {
    "description": "Rate limit exceeded",
    "content": {"application/json": {"example": {
        "detail": "rate limit exceeded for get_weather",
        "code": "RATE_LIMITED",
    }}},
}
RESPONSE_ERROR_504 = {
    "description": "Timeout",
    "content": {"application/json": {"example": {
        "detail": "tool get_weather timed out",
        "code": "TIMEOUT",
    }}},
}
