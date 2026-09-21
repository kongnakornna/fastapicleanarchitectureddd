"""Idempotency presentation schemas — Pydantic schemas"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IdempotencyRecordSchema(BaseModel):
    """IdempotencyRecordSchema — schema บันทึก idempotency"""
    key: str
    scope: str
    status: str
    request_hash: str
    response_status: int = 0
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)