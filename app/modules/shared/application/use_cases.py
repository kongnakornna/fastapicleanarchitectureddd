from __future__ import annotations

from loguru import logger

from app.modules.notification.application.exceptions import NotificationException
from app.modules.notification.application.interfaces import INotificationRepository
from app.modules.notification.domain.entities import Notification
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import (
    UserEmailNotFoundException,
    UserException,
    UserIdNotFoundException,
)
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.domain.entities import User
from app.modules.websocket.application.interfaces import IConnectionManagerService
from app.modules.websocket.domain.entities import WebSocketMessage


class SharedUseCases:
    """
    Use cases shared across modules (user, notification, websocket).

    Special flag `_raise_exceptions`:
        - True (default)  -> lookup methods raise when the row is missing
        - False           -> lookup methods return None when the row is missing

    IMPORTANT CONTRACT:
        The flag ONLY governs the "row not found" outcome (a business result).
        Infrastructure failures (DB down, mapping error, unexpected exception)
        ALWAYS raise, regardless of the flag. This prevents a real 500 from
        being silently reported to clients as "user not found".

    Note: mutation methods (create/update/delete) always raise — they never
    honor this flag.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        notification_repository: INotificationRepository,
        connection_manager: IConnectionManagerService,
    ) -> None:
        self.user_repository = user_repository
        self.notification_repository = notification_repository
        self.connection_manager = connection_manager
        self._raise_exceptions = True

    @property
    def raise_exceptions(self) -> bool:
        return self._raise_exceptions

    def enable_exceptions(self) -> "SharedUseCases":
        """Enable raise-on-not-found. Returns self so it can be chained."""
        self._raise_exceptions = True
        return self

    def disable_exceptions(self) -> "SharedUseCases":
        """Disable raise-on-not-found. Returns self so it can be chained."""
        self._raise_exceptions = False
        return self

    # ========================================================================
    # NOTIFICATION
    # ========================================================================
    async def create_notification(self, notification: Notification) -> Notification:
        try:
            logger.debug(
                f"Initializing create notification use case for user "
                f"{notification.user.id}."
            )

            result = await self.notification_repository.create(notification)
            await self._dispatch_user_notification_message(result)

            logger.debug(
                f"Create notification use case completed successfully for user "
                f"{notification.user.id}."
            )
            return result
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create notification use case."
            )
            raise NotificationException()

    async def create_broadcast_notification(
        self, notification: Notification
    ) -> list[Notification]:
        try:
            logger.debug(
                f"Initializing create broadcast notification use case "
                f"targeting role '{notification.originated_from_broadcast}'."
            )

            result = await self.notification_repository.create_broadcast(notification)
            if result:
                await self._dispatch_broadcast_notification_message(result[0])

            logger.debug(
                f"Broadcast notification use case completed. "
                f"Created {len(result)} notification(s)."
            )
            return result
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create broadcast "
                "notification use case."
            )
            raise NotificationException()

    async def _dispatch_user_notification_message(
        self, notification: Notification
    ) -> None:
        try:
            ws_message = WebSocketMessage(
                user_id=notification.user.id,
                body=notification,
            )
            await self.connection_manager.send_to_user(ws_message)
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Failed to dispatch user WebSocket notification message "
                f"for user '{notification.user.id}'; continuing best-effort."
            )

    async def _dispatch_broadcast_notification_message(
        self, notification: Notification
    ) -> None:
        try:
            ws_message = WebSocketMessage(body=notification)
            await self.connection_manager.broadcast_to(
                ws_message,
                minimum_role=notification.originated_from_broadcast,
            )
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Failed to dispatch broadcast WebSocket notification message "
                f"targeting role '{notification.originated_from_broadcast}'; "
                f"continuing best-effort."
            )

    # ========================================================================
    # USER — MUTATION
    # ========================================================================
    async def create_user(self, user: User) -> User:
        """
        Create a new user in the database.

        This method ALWAYS raises on failure — it never honors the
        `_raise_exceptions` flag because a silent `None` here would let the
        caller believe the create succeeded.

        Raises:
            UserException: on any unexpected error during persistence.
        """
        try:
            logger.debug(
                f"Initializing create user use case for user: {user.censored_email}."
            )

            created: User = await self.user_repository.create(user)

            logger.debug(
                f"Create user use case completed successfully for user: "
                f"{created.censored_email} with id {created.id}."
            )
            return created
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create user use case."
            )
            raise UserException()

    # ========================================================================
    # USER — LOOKUP
    # ========================================================================
    async def get_user_by_id(self, user: User) -> User | None:
        """
        Fetch a user by id.

        Contract:
            - found                              -> User
            - not found & raise_exceptions=True  -> raise UserIdNotFoundException
            - not found & raise_exceptions=False -> None
            - infra / mapping / unexpected error -> ALWAYS raise UserException
              (never silently becomes "not found")
        """
        try:
            logger.debug(f"-get_user_by_id- querying id={user.id}.")

            db_user: User | None = await self.user_repository.get_by_id(user)
            logger.debug(f"-get_user_by_id- db_user={db_user!r}")

            if db_user is None:
                if self._raise_exceptions:
                    logger.info(
                        f"User with identifier {user.id} not found. "
                        f"Raising UserIdNotFoundException."
                    )
                    raise UserIdNotFoundException(str(user.id))
                logger.debug(
                    f"User with identifier {user.id} not found. Returning None."
                )
                return None

            logger.debug(f"User with identifier {user.id} retrieved successfully.")
            return db_user

        except StandardException:
            # Business exceptions (incl. UserIdNotFoundException) bubble up.
            raise
        except DomainError as e:
            logger.opt(exception=e).error("Domain error during get_user_by_id.")
            raise DomainException(e)
        except Exception as e:
            # Infra / unexpected errors are NEVER masked as "not found".
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get user by identifier "
                "use case."
            )
            raise UserException()

    async def get_user_by_email(self, user: User) -> User | None:
        """
        Fetch a user by email.

        Contract:
            - found                              -> User
            - not found & raise_exceptions=True  -> raise UserEmailNotFoundException
            - not found & raise_exceptions=False -> None
            - infra / mapping / unexpected error -> ALWAYS raise UserException
              (never silently becomes "not found")

        Use `disable_exceptions()` when you need a duplicate-email check that
        returns `None` instead of raising — e.g. in the sign-up or login flow.
        """
        try:
            # Force string coercion at the boundary so any downstream binding
            # sees a plain str, never an `Email` value object.
            email_str = str(user.email)

            logger.debug(
                f"-get_user_by_email- querying email={email_str} "
                f"(censored={user.censored_email})."
            )

            db_user: User | None = await self.user_repository.get_by_email(user)
            logger.debug(f"-get_user_by_email- db_user={db_user!r}")

            if db_user is None:
                if self._raise_exceptions:
                    logger.info(
                        f"User with email {email_str} not found. "
                        f"Raising UserEmailNotFoundException."
                    )
                    raise UserEmailNotFoundException(email=email_str)
                logger.debug(
                    f"User with email {email_str} not found. Returning None."
                )
                return None

            logger.debug(
                f"User with email {email_str} retrieved from database successfully."
            )
            return db_user

        except StandardException:
            # Business exceptions (incl. UserEmailNotFoundException) bubble up.
            raise
        except DomainError as e:
            logger.opt(exception=e).error("Domain error during get_user_by_email.")
            raise DomainException(e)
        except Exception as e:
            # Infra / unexpected errors are NEVER masked as "not found".
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get user by email "
                "use case."
            )
            raise UserException()
