"""Category router"""
from __future__ import annotations
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.yolo.application.category_use_case import CategoryUseCase
from app.modules.yolo.presentation.dependencies import get_ctx
from app.modules.yolo.presentation.schemas_category import (
    CategoryCreateRequest, CategoryMoveRequest, CategoryResponse,
    CategoryTreeResponse, CategoryUpdateRequest,
)

router = APIRouter(prefix="/yolo/categories", tags=["yolo"])

_uc_holder: dict = {"uc": None}


async def _get_uc() -> CategoryUseCase:
    if _uc_holder["uc"] is None:
        raise HTTPException(500, "CategoryUseCase not wired")
    return _uc_holder["uc"]


def set_use_case(uc: CategoryUseCase) -> None:
    _uc_holder["uc"] = uc


@router.post("", response_model=CategoryResponse,
              status_code=status.HTTP_201_CREATED,
              summary="Create category", operation_id="yolo_create_category")
async def create_category(
    payload: CategoryCreateRequest,
    uc: Annotated[CategoryUseCase, Depends(_get_uc)],
) -> CategoryResponse:
    ctx = await get_ctx()
    data = payload.model_dump()
    if data.get("parent_id"):
        data["parent_id"] = uuid.UUID(data["parent_id"])
    return CategoryResponse(**await uc.create_category(ctx, data))


@router.get("", response_model=list[CategoryResponse],
             summary="List categories", operation_id="yolo_list_categories")
async def list_categories(
    uc: Annotated[CategoryUseCase, Depends(_get_uc)],
    parent_id: uuid.UUID | None = None,
) -> list[CategoryResponse]:
    ctx = await get_ctx()
    return [CategoryResponse(**c)
            for c in await uc.list_categories(ctx, parent_id)]


@router.get("/tree", response_model=CategoryTreeResponse,
             summary="Category tree", operation_id="yolo_category_tree")
async def get_tree(
    uc: Annotated[CategoryUseCase, Depends(_get_uc)],
    root_id: uuid.UUID | None = None,
) -> CategoryTreeResponse:
    ctx = await get_ctx()
    return CategoryTreeResponse(**await uc.get_tree(ctx, root_id))


@router.get("/{category_id}", response_model=CategoryResponse,
             summary="Get category", operation_id="yolo_get_category")
async def get_category(
    category_id: uuid.UUID,
    uc: Annotated[CategoryUseCase, Depends(_get_uc)],
) -> CategoryResponse:
    ctx = await get_ctx()
    try:
        return CategoryResponse(**await uc.get_category(ctx, category_id))
    except ValueError as e:
        raise HTTPException(404, detail=str(e)) from e


@router.patch("/{category_id}", response_model=CategoryResponse,
               summary="Update category", operation_id="yolo_update_category")
async def update_category(
    category_id: uuid.UUID, payload: CategoryUpdateRequest,
    uc: Annotated[CategoryUseCase, Depends(_get_uc)],
) -> CategoryResponse:
    ctx = await get_ctx()
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return CategoryResponse(**await uc.update_category(ctx, category_id, data))


@router.post("/{category_id}/move", response_model=CategoryResponse,
              summary="Move category", operation_id="yolo_move_category")
async def move_category(
    category_id: uuid.UUID, payload: CategoryMoveRequest,
    uc: Annotated[CategoryUseCase, Depends(_get_uc)],
) -> CategoryResponse:
    ctx = await get_ctx()
    new_parent = uuid.UUID(payload.new_parent_id) if payload.new_parent_id else None
    try:
        return CategoryResponse(**await uc.move_category(ctx, category_id, new_parent))
    except ValueError as e:
        raise HTTPException(422, detail=str(e)) from e


@router.delete("/{category_id}", summary="Delete category",
                operation_id="yolo_delete_category")
async def delete_category(
    category_id: uuid.UUID,
    uc: Annotated[CategoryUseCase, Depends(_get_uc)],
    cascade: bool = False,
) -> dict:
    ctx = await get_ctx()
    try:
        return await uc.delete_category(ctx, category_id, cascade)
    except ValueError as e:
        raise HTTPException(422, detail=str(e)) from e
