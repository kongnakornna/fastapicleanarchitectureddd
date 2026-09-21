"""Idempotency presentation dependencies — FastAPI dependency"""
from fastapi import Header, HTTPException


async def require_idempotency_key(
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")
) -> str:
    """ต้องมี Idempotency-Key header — Require idempotency key"""
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key header required",
        )
    if len(idempotency_key) < 8 or len(idempotency_key) > 255:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key must be 8-255 characters",
        )
    return idempotency_key