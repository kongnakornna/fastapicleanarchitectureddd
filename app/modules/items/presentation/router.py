from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.items.application.use_case import ItemUseCase
from app.modules.items.domain.entities.item import Item
from app.modules.items.infrastructure.item_repository import ItemRepository
from app.modules.items.presentation.schemas import (
    ItemCreateRequest,
    ItemResponse,
    ItemUpdateRequest,
    PaginatedItemsResponse,
)

router = APIRouter(prefix="/item", tags=["Item"])


async def get_item_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> ItemUseCase:
    return ItemUseCase(item_repository=ItemRepository(session))


def _item_to_response(item: Item) -> ItemResponse:
    return ItemResponse(
        id=str(item.id),
        title=item.title,
        description=item.description,
        owner_id=str(item.owner_id),
        created_at=item.created_at.isoformat() if item.created_at else "",
        updated_at=item.updated_at.isoformat() if item.updated_at else "",
    )


@router.get("/")
async def get_items(
    page: int = 1,
    per_page: int = 10,
    use_case: ItemUseCase = Depends(get_item_use_case),
) -> PaginatedItemsResponse:
    per_page = min(per_page, 100)
    items, total = await use_case.get_items(page=page, page_size=per_page)
    total_pages = (total + per_page - 1) // per_page
    return PaginatedItemsResponse(
        items=[_item_to_response(i) for i in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/")
async def create_item(
    payload: ItemCreateRequest,
    use_case: ItemUseCase = Depends(get_item_use_case),
) -> ItemResponse:
    item = Item(
        title=payload.title,
        description=payload.description,
        owner_id="00000000-0000-0000-0000-000000000000",
    )
    result = await use_case.create_item(item)
    return _item_to_response(result)


@router.get("/{item_id}")
async def get_item(
    item_id: str,
    use_case: ItemUseCase = Depends(get_item_use_case),
) -> ItemResponse:
    from uuid import UUID

    item = await use_case.get_item(UUID(item_id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_to_response(item)


@router.put("/{item_id}")
async def update_item(
    item_id: str,
    payload: ItemUpdateRequest,
    use_case: ItemUseCase = Depends(get_item_use_case),
) -> ItemResponse:
    from uuid import UUID

    values = payload.model_dump(exclude_none=True)
    item = await use_case.update_item(UUID(item_id), values)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _item_to_response(item)


@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    use_case: ItemUseCase = Depends(get_item_use_case),
) -> dict[str, bool]:
    from uuid import UUID

    success = await use_case.delete_item(UUID(item_id))
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"success": True}
