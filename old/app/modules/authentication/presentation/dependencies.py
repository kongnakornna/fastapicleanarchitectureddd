from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.authentication.application.interfaces import IAuthenticationRepository
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.infrastructure.repositories import (
    PostgresSessionRepository,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.presentation.dependencies import get_shared_use_cases
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.application.use_cases import UserUseCases
from app.modules.user.infrastructure.repositories import PostgresUserRepository


def get_authentication_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IAuthenticationRepository:
    return PostgresSessionRepository(session=session)


def get_user_repository_for_auth(
    session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    return PostgresUserRepository(session=session)


def get_user_use_cases_for_auth(
    repository: IUserRepository = Depends(get_user_repository_for_auth),
    shared_service: SharedUseCases = Depends(get_shared_use_cases),
) -> UserUseCases:
    return UserUseCases(repository=repository, shared_service=shared_service)


def get_authentication_use_cases(
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    shared_service: SharedUseCases = Depends(get_shared_use_cases),
) -> AuthenticationUseCases:
    return AuthenticationUseCases(repository=repository, shared_service=shared_service)
