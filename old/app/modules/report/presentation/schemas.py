from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ReportResponse(BaseModel):
    message: str
    report_type: str
    generated_at: str

    model_config = ConfigDict(extra="forbid")
