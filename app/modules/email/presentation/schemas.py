from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EmailSendRequest(BaseModel):
    to: str = Field(..., min_length=1, max_length=500)
    cc: str | None = None
    bcc: str | None = None
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class EmailConfigUpdateRequest(BaseModel):
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_user: str | None = None
    from_email: str | None = None
    from_name: str | None = None

    model_config = ConfigDict(extra="forbid")


class EmailLogResponse(BaseModel):
    id: str
    to_address: str
    subject: str
    status: str
    error_message: str | None = None
    sent_at: str | None = None
    created_at: str = ""

    model_config = ConfigDict(extra="forbid")


class EmailConfigResponse(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: str
    from_email: str
    from_name: str
    is_active: bool

    model_config = ConfigDict(extra="forbid")


class PaginatedEmailLogsResponse(BaseModel):
    logs: list[EmailLogResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
