from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ItemCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=200)

    model_config = ConfigDict(extra="forbid")


class ItemUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None

    model_config = ConfigDict(extra="forbid")


class ItemResponse(BaseModel):
    id: str
    title: str
    description: str
    owner_id: str
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(extra="forbid")


class PaginatedItemsResponse(BaseModel):
    items: list[ItemResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    model_config = ConfigDict(extra="forbid")
