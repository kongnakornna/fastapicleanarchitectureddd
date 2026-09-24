from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.core.security import authenticate_user, no_authentication
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import UserException
from app.modules.user.application.mappers import (
    create_entity_mapper,
    entity_create_mapper,
    entity_me_mapper,
    me_entity_mapper,
)
from app.modules.user.application.use_cases import UserUseCases
from app.modules.user.presentation.dependencies import get_user_use_cases
from app.modules.user.presentation.docs import create_docs, me_docs, router_docs
from app.modules.user.presentation.schemas import (
    CreateRequest,
    CreateResponse,
    MeResponse,
)

router = APIRouter(**router_docs)


@router.post("/", **create_docs)
@router.post("", include_in_schema=False)
async def create(
    payload: CreateRequest,
    _: Annotated[None, Depends(no_authentication)],
    use_case: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> CreateResponse:
    """TH: สร้าง user (public) | EN: create user (public)"""
    try:
        logger.debug("http.create_user.start", email=str(payload.email))

        request_domain = create_entity_mapper(payload)
        response_domain = await use_case.create(request_domain)
        output = entity_create_mapper(response_domain)

        logger.debug("http.create_user.done", user_id=str(response_domain.id))
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e) from e
    except Exception as e:
        logger.opt(exception=e).error(
            "http.create_user.unexpected",
            email=str(payload.email),
        )
        raise UserException() from e


@router.get("/me/", **me_docs)
@router.get("/me", include_in_schema=False)
async def me(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    use_case: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> MeResponse:
    """TH: user ที่ login อยู่ | EN: current authenticated user"""
    try:
        request_domain = me_entity_mapper(authentication)
        response_domain = await use_case.me(request_domain)
        output = entity_me_mapper(response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e) from e
    except Exception as e:
        logger.opt(exception=e).error("http.me.unexpected")
        raise UserException() from e
