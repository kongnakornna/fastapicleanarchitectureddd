from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.i18n.application.use_case import I18nUseCase
from app.modules.i18n.domain.entities.translation import Translation
from app.modules.i18n.infrastructure.translation_repository import (
    TranslationRepository,
)
from app.modules.i18n.presentation.schemas import (
    PaginatedTranslationsResponse,
    TranslationCreateRequest,
    TranslationResponse,
    TranslationUpdateRequest,
)

router = APIRouter(prefix="/i18n", tags=["I18n"])


async def get_i18n_use_case(
    session: AsyncSession = Depends(get_async_session),
) -> I18nUseCase:
    return I18nUseCase(
        translation_repository=TranslationRepository(session)
    )


def _translation_to_response(translation: Translation) -> TranslationResponse:
    return TranslationResponse(
        id=str(translation.id),
        locale=translation.locale,
        key=translation.key,
        value=translation.value,
        created_at=(
            translation.created_at.isoformat() if translation.created_at else ""
        ),
        updated_at=(
            translation.updated_at.isoformat() if translation.updated_at else ""
        ),
    )


@router.get("/translations")
async def get_translations(
    locale: str | None = Query(None),
    page: int = 1,
    per_page: int = 10,
    use_case: I18nUseCase = Depends(get_i18n_use_case),
) -> PaginatedTranslationsResponse:
    per_page = min(per_page, 100)
    translations, total = await use_case.get_translations(
        locale=locale, page=page, page_size=per_page
    )
    total_pages = (total + per_page - 1) // per_page
    return PaginatedTranslationsResponse(
        translations=[
            _translation_to_response(t) for t in translations
        ],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/translations")
async def create_translation(
    payload: TranslationCreateRequest,
    use_case: I18nUseCase = Depends(get_i18n_use_case),
) -> TranslationResponse:
    translation = Translation(
        locale=payload.locale,
        key=payload.key,
        value=payload.value,
    )
    result = await use_case.create_translation(translation)
    return _translation_to_response(result)


@router.get("/translations/{key}")
async def get_translation_by_key(
    key: str,
    locale: str = Query(...),
    use_case: I18nUseCase = Depends(get_i18n_use_case),
) -> TranslationResponse:
    translation = await use_case.get_by_locale_and_key(locale, key)
    if not translation:
        raise HTTPException(
            status_code=404, detail="Translation not found"
        )
    return _translation_to_response(translation)


@router.put("/translations/{key}")
async def update_translation(
    key: str,
    payload: TranslationUpdateRequest,
    locale: str = Query(...),
    use_case: I18nUseCase = Depends(get_i18n_use_case),
) -> TranslationResponse:
    translation = await use_case.get_by_locale_and_key(locale, key)
    if not translation:
        raise HTTPException(
            status_code=404, detail="Translation not found"
        )
    values = payload.model_dump(exclude_none=True)
    updated = await use_case.update_translation(translation.id, values)
    if not updated:
        raise HTTPException(
            status_code=404, detail="Translation not found"
        )
    return _translation_to_response(updated)


@router.delete("/translations/{key}")
async def delete_translation(
    key: str,
    locale: str = Query(...),
    use_case: I18nUseCase = Depends(get_i18n_use_case),
) -> dict[str, bool]:
    translation = await use_case.get_by_locale_and_key(locale, key)
    if not translation:
        raise HTTPException(
            status_code=404, detail="Translation not found"
        )
    success = await use_case.delete_translation(translation.id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Translation not found"
        )
    return {"success": True}
