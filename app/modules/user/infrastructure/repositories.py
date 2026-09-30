from __future__ import annotations

from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.shared.application.exceptions import StandardException
from app.modules.user.application.exceptions import UserException
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
)
from app.modules.user.domain.entities import User
from app.modules.user.infrastructure.models import UserModel


class PostgresUserRepository(IUserRepository):
    """PostgreSQL implementation of `IUserRepository`."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ========================================================================
    # INTERNAL HELPERS
    # ========================================================================
    @staticmethod
    def _active_clause():
        """Reusable filter: row is active or has no active_status set."""
        return or_(
            UserModel.active_status == 1,
            UserModel.active_status.is_(None),
        )

    @staticmethod
    def _normalize_email(user: User) -> str:
        """
        Coerce the domain `Email` value object into a plain lowercased str.

        Never pass the value object itself as a bind parameter — some drivers
        silently bind it as an opaque object and match zero rows.
        """
        return str(user.email).strip().lower()

    # ========================================================================
    # CREATE
    # ========================================================================
    async def create(self, user: User) -> User:
        try:
            logger.info(f"Creating user {user.email!s} in database.")

            db_user: UserModel = entity_model_mapper(user)

            self.session.add(db_user)
            await self.session.flush()

            logger.info(
                f"User {user.email!s} with id {db_user.id} created successfully."
            )
            return model_entity_mapper(db_user)
        except StandardException:
            raise
        except SQLAlchemyError as e:
            logger.opt(exception=e).error(
                "Database error in create user repository."
            )
            raise UserException()
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create user repository."
            )
            raise UserException()

    # ========================================================================
    # READ — EXISTS BY EMAIL
    # ========================================================================
    async def exists_by_email(self, user: User) -> bool:
        try:
            email_str = self._normalize_email(user)
            logger.info(f"Checking if user {email_str} exists in database.")

            statement = (
                select(UserModel.id)
                .where(
                    UserModel.email == email_str,
                    self._active_clause(),
                )
                .limit(1)
            )

            result = await self.session.scalar(statement)
            exists = result is not None

            logger.info(
                f"Existence check for user {email_str} completed. "
                f"Exists: {exists}."
            )
            return exists
        except StandardException:
            raise
        except SQLAlchemyError as e:
            logger.opt(exception=e).error(
                "Database error during the existence check of a user."
            )
            raise UserException()
        except Exception as e:
            logger.opt(exception=e).error(
                "Unexpected error during the existence check of a user "
                "in the database."
            )
            raise UserException()

    # ========================================================================
    # READ — BY ID
    # ========================================================================
    async def get_by_id(self, user: User) -> User | None:
        try:
            logger.info(f"Retrieving user with id {user.id} from database.")

            statement = select(UserModel).where(
                UserModel.id == user.id,
                self._active_clause(),
            )

            result = await self.session.execute(statement)
            user_model: UserModel | None = result.scalar_one_or_none()

            if user_model is None:
                logger.info(f"User with id {user.id} not found in database.")
                return None

            domain_user: User = model_entity_mapper(user_model)

            logger.info(
                f"User with id {user.id} retrieved successfully from database."
            )
            return domain_user
        except StandardException:
            raise
        except SQLAlchemyError as e:
            logger.opt(exception=e).error(
                "Database error during the get user by id repository."
            )
            raise UserException()
        except Exception as e:
            logger.opt(exception=e).error(
                "Unexpected error during the get user by id repository."
            )
            raise UserException()

    # ========================================================================
    # READ — BY EMAIL
    # ========================================================================
    async def get_by_email(self, user: User) -> User | None:
        """
        Fetch a user by email.

        Contract (must match `SharedUseCases.get_user_by_email`):
            - found             -> return User (domain entity)
            - not found         -> return None (do NOT raise here)
            - infra / DB error  -> raise UserException
                                  (so the use case can distinguish a real
                                   "not found" from a 500)
        """
        email_str = self._normalize_email(user)

        try:
            logger.info(
                f"Retrieving user with email {email_str!r} from database."
            )

            statement = select(UserModel).where(
                UserModel.email == email_str,
                self._active_clause(),
            )

            result = await self.session.execute(statement)
            user_model: UserModel | None = result.scalar_one_or_none()

            if user_model is None:
                logger.info(
                    f"User with email {email_str!r} not found in database."
                )
                return None

            domain_user: User = model_entity_mapper(user_model)

            logger.info(
                f"User with email {email_str!r} retrieved successfully "
                f"from database."
            )
            return domain_user

        except StandardException:
            raise
        except SQLAlchemyError as e:
            # Any driver/ORM failure — never let this look like "not found".
            logger.opt(exception=e).error(
                f"Database error in get_by_email for {email_str!r}."
            )
            raise UserException()
        except Exception as e:
            logger.opt(exception=e).error(
                f"Unexpected error in get_by_email for {email_str!r}."
            )
            raise UserException()
# ========================================================================
