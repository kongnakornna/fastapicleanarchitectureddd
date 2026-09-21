"""TH: Health + readiness | EN: Health + readiness"""
from __future__ import annotations

from fastapi import APIRouter, status
from sqlalchemy import text

from app.core.db import engine

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    """TH: liveness | EN: liveness"""
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def ready() -> dict[str, str]:
    """TH: readiness (ตรวจ DB) | EN: readiness (checks DB)"""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ready"}