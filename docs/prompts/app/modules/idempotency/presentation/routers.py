"""Idempotency presentation routers — ว่าง (ใช้ middleware)

Public router ว่าง — ใช้ middleware/dependency แทน
No public endpoints — handled via middleware/dependency
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/idempotency", tags=["Idempotency"])

__all__ = ["router"]