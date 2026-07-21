from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TranslationCreateRequest(BaseModel):
    locale: str = Field(..., min_length=2, max_length=10)
    key: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class TranslationUpdateRequest(BaseModel):
    locale: str | None = Field(None, min_length=2, max_length=10)
    key: str | None = Field(None, min_length=1, max_length=255)
    value: str | None = None

    model_config = ConfigDict(extra="forbid")


class TranslationResponse(BaseModel):
    id: str
    locale: str
    key: str
    value: str
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class PaginatedTranslationsResponse(BaseModel):
    translations: list[TranslationResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
