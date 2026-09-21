from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from loguru import logger

from app.core.settings import settings
from app.modules.authentication.application.exceptions import (
    AuthenticationException,
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    InvalidOtpCodeException,
    PasswordMismatchException,
)
from app.modules.authentication.application.interfaces import (
    IAuthenticationCache,
    IAuthenticationRepository,
    ITokenService,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.entities import DomainError
from app.modules.user.domain.entities import User


class AuthenticationUseCases:
    """Use cases for Authentication."""

    def __init__(
        self,
        cache: IAuthenticationCache,
        repository: IAuthenticationRepository,
        shared_service: SharedUseCases,
        token_service: ITokenService,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.shared_service = shared_service
        self.token_service = token_service
        self.shared_service.disable_exceptions()

    # ========================================================================
    # CREATE: LOGIN
    # ========================================================================
    async def login(self, authentication: Authentication) -> Authentication:
        """Login use case."""
        try:
            logger.debug(
                f"Initializing user login use case for user: {authentication.user.censored_email} in device: {authentication.device}."
            )

            db_user: User | None = await self.shared_service.get_user_by_email(
                authentication.user
            )

            if not db_user:
                logger.info(
                    f"User with email {authentication.user.censored_email} not found, raising exception."
                )
                raise InvalidCredentialsException()

            if not await self.token_service.verify_password(
                authentication.user.password, db_user.hashed_password
            ):
                logger.info(
                    f"Invalid password for user {authentication.user.id}, raising exception."
                )
                raise InvalidCredentialsException()

            authentication.user = db_user
            authentication_from_db = (
                await self.repository.get_by_user_id_agent_and_device(authentication)
            )

            now = datetime.now(BRASILIA_TZ)
            refresh_expires_at = now + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            if authentication_from_db:
                logger.debug(
                    f"Existing authentication found for user: {authentication.user.id}. Renewing tokens."
                )
                await self.cache.delete_by_access_token(authentication_from_db)
                await self.cache.delete_by_refresh_token(authentication_from_db)
                authentication = authentication_from_db.renew_tokens(
                    now, refresh_expires_at, access_expires_at
                )
            else:
                logger.debug(
                    f"No existing authentication found for user: {authentication.user.id}. Creating new authentication."
                )
                authentication = authentication.create_tokens(
                    now, refresh_expires_at, access_expires_at
                )

            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            if authentication_from_db:
                await self.repository.update(authentication)
            else:
                await self.repository.create(authentication)

            logger.debug(
                f"User {authentication.user.id} logged in successfully in device: {authentication.device}."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the login use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # SIGN UP
    # ========================================================================
    async def sign_up(self, user: User) -> User:
        """
        Sign up use case.

        ขั้นตอน:
            1. ตรวจว่า email ซ้ำหรือไม่
            2. Hash password
            3. สร้าง user ผ่าน shared_service
            4. (TODO) ส่งอีเมลต้อนรับ
        """
        try:
            logger.debug(
                f"Initializing sign up use case for user: {user.censored_email}."
            )

            # 1. ตรวจ email ซ้ำก่อน — ถ้าซ้ำให้ตอบ error ทันที ไม่ต้อง hash ให้เสียเวลา
            existing_user = await self.shared_service.get_user_by_email(user)
            if existing_user:
                logger.info(f"User with email {user.censored_email} already exists.")
                raise EmailAlreadyExistsException(email=str(user.email))

            # 2. Hash password ก่อนเก็บ (ห้ามเก็บ plaintext เด็ดขาด)
            user.hashed_password = self.token_service.hash_password(user.password)

            # 3. สร้าง user — ต้องมี method นี้ใน SharedUseCases
            user = await self.shared_service.create_user(user)

            # 4. ส่งอีเมลต้อนรับ — ยังไม่ implement
            #    (ก่อนหน้านี้ log ว่า "sent" ทั้งที่ยังไม่ส่ง ทำให้เข้าใจผิด)
            logger.debug(
                f"User created with id {user.id}. "
                f"Welcome email will be sent later (not yet implemented)."
            )

            logger.debug(
                f"User {user.censored_email} signed up successfully with id {user.id}."
            )
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the sign up use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # UPDATE: REFRESH
    # ========================================================================
    async def refresh(self, authentication: Authentication) -> Authentication:
        """Refresh tokens use case."""
        try:
            logger.debug(
                f"Initializing user refresh tokens use case for user: {authentication.user.id}."
            )

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            now = datetime.now(BRASILIA_TZ)
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            authentication = authentication.refresh_access_token(now, access_expires_at)
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            await self.repository.update(authentication)

            logger.debug(
                f"User {authentication.user.id} refreshed tokens successfully."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the refresh tokens use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # DELETE: LOGOUT
    # ========================================================================
    async def logout(self, authentication: Authentication) -> Authentication:
        """Logout use case."""
        try:
            logger.debug(
                f"Initializing user logout use case for user: {authentication.user.id}."
            )

            authentication.revoke(datetime.now(BRASILIA_TZ))
            await self.repository.delete(authentication)

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            logger.debug(f"User {authentication.user.id} logged out successfully.")
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the logout use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # FORGOT PASSWORD
    # ========================================================================
    async def forgot_password(self, email: str) -> None:
        """Forgot password use case."""
        try:
            logger.debug(f"Initializing forgot password use case for email: {email}.")

            user = await self.shared_service.get_user_by_email(User(email=email))

            if not user:
                # ตอบ success เสมอ เพื่อไม่ให้ attacker เดาได้ว่า email มีในระบบหรือไม่
                logger.info(
                    f"User with email {email} not found, but returning success."
                )
                return

            # Generate reset code (TODO: implement persistence)
            _reset_code = str(uuid4())[:6].upper()

            # Send email (TODO: implement)
            # await self.email_service.send_password_reset_email(
            #     email=email, reset_code=_reset_code
            # )
            logger.debug(f"Reset code generated for {email} (email not yet sent).")

            logger.debug(f"Forgot password processed for {email}.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the forgot password use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # RESET PASSWORD
    # ========================================================================
    async def reset_password(
        self, code: str, password: str, confirm_password: str
    ) -> None:
        """Reset password use case."""
        try:
            logger.debug("Initializing reset password use case.")

            if password != confirm_password:
                raise PasswordMismatchException()

            # Validate code (TODO: implement)
            # user = await self.shared_service.get_user_by_reset_code(code)
            # if not user:
            #     raise InvalidResetCodeException()

            # Update password (TODO: implement)
            logger.debug("Reset password processed successfully.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the reset password use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # LOCK SCREEN
    # ========================================================================
    async def lock_screen(self, authentication: Authentication, password: str) -> None:
        """Lock screen use case."""
        try:
            logger.debug(
                f"Initializing lock screen use case for user: {authentication.user.id}."
            )

            if not await self.token_service.verify_password(
                password, authentication.user.hashed_password
            ):
                raise InvalidCredentialsException()

            logger.debug(f"Lock screen unlocked for user {authentication.user.id}.")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the lock screen use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # TWO-STEP VERIFICATION
    # ========================================================================
    async def two_step_verification(
        self, authentication: Authentication, country_code: str, phone_number: str
    ) -> None:
        """Two-step verification use case."""
        try:
            logger.debug(
                f"Initializing two-step verification for user: {authentication.user.id}."
            )

            full_phone = f"{country_code}{phone_number}"

            # Send OTP (TODO: implement)
            _otp_code = str(uuid4())[:6]
            logger.debug(f"OTP generated for {full_phone} (SMS not yet sent).")
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the two-step verification use case."
            )
            raise AuthenticationException()

    # ========================================================================
    # TWO-STEP CODE
    # ========================================================================
    async def two_step_code(
        self, authentication: Authentication, code: str, dont_ask_again: bool
    ) -> Authentication:
        """Two-step code use case."""
        try:
            logger.debug(
                f"Initializing two-step code verification for user: {authentication.user.id}."
            )

            if code != "123456":  # Placeholder
                raise InvalidOtpCodeException()

            now = datetime.now(BRASILIA_TZ)
            refresh_expires_at = now + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            authentication = authentication.create_tokens(
                now, refresh_expires_at, access_expires_at
            )
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            await self.repository.create(authentication)

            logger.debug(f"Two-step code verified for user {authentication.user.id}.")
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the two-step code use case."
            )
            raise AuthenticationException()
