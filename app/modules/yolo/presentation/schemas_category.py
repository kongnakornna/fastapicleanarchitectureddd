"""Category schemas"""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class CategoryCreateRequest(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100,
                        pattern=r"^[a-z0-9-]+$")
    name_th: str = Field(..., min_length=1, max_length=200)
    name_en: str = Field(..., min_length=1, max_length=200)
    parent_id: str | None = None
    description: str = ""
    icon: str | None = None
    color: str = "#3B82F6"
    sort_order: int = 0
    extra_json: dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="forbid")


class CategoryUpdateRequest(BaseModel):
    name_th: str | None = None
    name_en: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None
    model_config = ConfigDict(extra="forbid")


class CategoryResponse(BaseModel):
    id: str
    parent_id: str | None = None
    slug: str
    name_th: str
    name_en: str
    description: str = ""
    icon: str | None = None
    color: str
    sort_order: int = 0
    is_active: bool = True
    class_count: int = 0
    model_config = ConfigDict(extra="forbid")


class CategoryTreeNode(CategoryResponse):
    children: list["CategoryTreeNode"] = Field(default_factory=list)


class CategoryTreeResponse(BaseModel):
    root_id: str | None = None
    items: list[CategoryTreeNode]
    model_config = ConfigDict(extra="forbid")


class CategoryMoveRequest(BaseModel):
    new_parent_id: str | None = None
    model_config = ConfigDict(extra="forbid")
