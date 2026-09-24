"""llm OpenAPI metadata — response examples"""
from __future__ import annotations

RESPONSE_CHAT_200 = {
    "description": "Chat completion",
    "content": {"application/json": {"example": {
        "conversation_id": "uuid",
        "model": "gpt-4o-mini",
        "content": "Hello!",
        "finish_reason": "stop",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
        },
        "latency_ms": 850,
    }}},
}
RESPONSE_ERROR_400 = {
    "description": "Domain error",
    "content": {"application/json": {"example": {
        "detail": "model not found", "code": "DOMAIN_ERROR",
    }}},
}
RESPONSE_ERROR_402 = {
    "description": "Token limit exceeded",
    "content": {"application/json": {"example": {
        "detail": "token limit exceeded",
        "code": "LIMIT_EXCEEDED",
    }}},
}
RESPONSE_ERROR_404 = {
    "description": "Not found",
    "content": {"application/json": {"example": {
        "detail": "conversation not found",
        "code": "NOT_FOUND",
    }}},
}
RESPONSE_ERROR_429 = {
    "description": "Rate limit exceeded",
    "content": {"application/json": {"example": {
        "detail": "rate limit exceeded",
        "code": "RATE_LIMITED",
    }}},
}
RESPONSE_ERROR_502 = {
    "description": "Provider error",
    "content": {"application/json": {"example": {
        "detail": "openai API error",
        "code": "PROVIDER_ERROR",
    }}},
}
