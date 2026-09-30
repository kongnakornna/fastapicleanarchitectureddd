"""user use cases — create / me"""
from __future__ import annotations

from loguru import logger

from app.core.security import hash_password
from app.modules.shared.application.exceptions import (
    DomainException, StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import (
    UserEmailAlreadyExistsException, UserException,
)
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.domain.entities import User


class UserUseCases:
    """TH: use cases ของ user | EN: user use cases"""

    def __init__(self, repository: IUserRepository) -> None:
        self.repository = repository

    async def create(self, user: User) -> User:
        try:
            if await self.repository.exists_by_email(user):
                raise UserEmailAlreadyExistsException(email=str(user.email))

            if not user.hashed_password:
                if not user.password:
                    raise ValueError("password is required")
                user.hashed_password = hash_password(user.password)
                user.password = None

            user = await self.repository.create(user)
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("user.create failed")
            raise UserException()

    async def me(self, user: User) -> User:
        try:
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("user.me failed")
            raise UserException()
