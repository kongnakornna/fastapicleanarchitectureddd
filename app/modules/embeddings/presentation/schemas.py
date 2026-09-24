"""embeddings Pydantic schemas"""
from __future__ import annotations
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EmbedRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(min_length=1, max_length=100)
    input: list[str] = Field(min_length=1, max_length=2048)
    normalize: bool = True
    dimensions: Optional[int] = Field(default=None, ge=1, le=8192)


class EmbedOneRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(min_length=1, max_length=100)
    text: str = Field(min_length=1)
    normalize: bool = True
    dimensions: Optional[int] = Field(default=None, ge=1, le=8192)


class BatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(min_length=1, max_length=100)
    texts: list[str] = Field(min_length=1)
    batch_size: int = Field(default=64, ge=1, le=2048)
    max_concurrency: int = Field(default=4, ge=1, le=32)


class EmbeddingOut(BaseModel):
    vector: list[float]
    dimension: int
    tokens: int = 0
    cached: bool = False


class EmbedResponse(BaseModel):
    model: str
    embeddings: list[EmbeddingOut]
    count: int


class BatchResponse(BaseModel):
    batch_id: uuid.UUID
    total: int
    status: str


class EmbModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    display_name: str
    dimension: int
    max_tokens: int
    normalize: bool
    is_active: bool


class EmbProviderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    provider_type: str
    base_url: str
    priority: int
    is_active: bool
