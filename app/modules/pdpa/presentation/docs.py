"""pdpa OpenAPI metadata"""
from __future__ import annotations

RESPONSE_CREATE_201 = {
    "description": "สร้างสำเร็จ",
    "content": {"application/json": {"example": {
        "id": "01HXYZ...", "purpose_code": "DATA_COLLECTION",
        "status": "GRANTED", "version": 1,
    }}},
}
RESPONSE_ERROR_400 = {
    "description": "Domain error",
    "content": {"application/json": {"example": {
        "detail": "invalid state", "code": "DOMAIN_ERROR",
    }}},
}
RESPONSE_ERROR_404 = {
    "description": "ไม่พบ entity",
    "content": {"application/json": {"example": {
        "detail": "not found", "code": "NOT_FOUND",
    }}},
}
RESPONSE_ERROR_409 = {
    "description": "Conflict (duplicate / idempotency in progress)",
    "content": {"application/json": {"example": {
        "detail": "consent already granted", "code": "CONFLICT",
    }}},
}
RESPONSE_ERROR_422 = {
    "description": "Validation error",
    "content": {"application/json": {"example": {
        "detail": [{"loc": ["body"], "msg": "invalid", "type": "value_error"}],
    }}},
}