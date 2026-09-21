from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DocumentUploadRequest(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    mime_type: str = Field(..., min_length=1, max_length=100)
    size: int = Field(..., ge=0)

    model_config = ConfigDict(extra="forbid")


class DocumentUpdateRequest(BaseModel):
    filename: str | None = None
    mime_type: str | None = None
    size: int | None = None

    model_config = ConfigDict(extra="forbid")


class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    mime_type: str
    size: int
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class PaginatedDocumentsResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
