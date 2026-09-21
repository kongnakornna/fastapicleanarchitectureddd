from __future__ import annotations

from loguru import logger

from app.core.security import hash_password
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import (
    UserEmailAlreadyExistsException,
    UserException,
)
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.domain.entities import User


class UserUseCases:
    """TH: Use cases ของ user | EN: user use cases"""

    def __init__(self, repository: IUserRepository) -> None:
        self.repository = repository

    # ─── CREATE ─────────────────────────────────────────────
    async def create(self, user: User) -> User:
        try:
            logger.debug(
                f"Initializing create user use case with user: {user.censored_email}."
            )

            if await self.repository.exists_by_email(user):
                logger.info(
                    f"User with email {user.censored_email} already exists."
                )
                raise UserEmailAlreadyExistsException(email=str(user.email))

            if not user.hashed_password:
                if not user.password:
                    logger.error(
                        "user.create: password is None — cannot hash",
                        email=str(user.email),
                    )
                    raise ValueError(
                        "password is required to create user (cannot hash None)"
                    )
                user.hashed_password = hash_password(user.password)
                user.password = None

            user = await self.repository.create(user)

            logger.debug(
                f"User {user.censored_email} with id {user.id} created successfully."
            )
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create user use case."
            )
            raise UserException()

    # ─── READ ───────────────────────────────────────────────
    async def me(self, user: User) -> User:
        try:
            logger.debug(f"Initializing /me user use case for user {user.id}.")
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("An error occurred in the me use case.")
            raise UserException()