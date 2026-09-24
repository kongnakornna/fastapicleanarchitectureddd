"""ValidationError VO"""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ValidationError(BaseModel):
    """TH: ข้อผิดพลาดการ validate | EN: Validation error"""
    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = ""
    message: str = ""
    kind: str = ""
    value: Optional[Any] = None
