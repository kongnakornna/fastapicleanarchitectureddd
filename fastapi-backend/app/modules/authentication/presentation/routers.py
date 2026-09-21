from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestFormStrict
from loguru import logger

from app.core.security import (
    authenticate_logout,
    authenticate_refresh,
    authenticate_user,
    no_authentication,
)
from app.core.settings import settings
from app.modules.authentication.application.exceptions import AuthenticationException
from app.modules.authentication.application.mappers import (
    entity_forgot_password_mapper,
    entity_lock_screen_mapper,
    entity_login_mapper,
    entity_logout_mapper,
    entity_refresh_mapper,
    entity_reset_password_mapper,
    entity_sign_up_mapper,
    entity_two_step_code_mapper,
    entity_two_step_verification_mapper,
    login_entity_mapper,
    logout_entity_mapper,
    refresh_entity_mapper,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.domain.entities import Authentication
from app.modules.authentication.domain.enums import TokenType
from app.modules.authentication.presentation.dependencies import (
    get_authentication_use_cases,
)
from app.modules.authentication.presentation.docs import (
    forgot_password_docs,
    lock_screen_docs,
    login_docs,
    logout_docs,
    refresh_docs,
    reset_password_docs,
    router_docs,
    sign_up_docs,
    two_step_code_docs,
    two_step_verification_docs,
)
from app.modules.authentication.presentation.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LockScreenRequest,
    LockScreenResponse,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SignUpRequest,
    SignUpResponse,
    TwoStepCodeRequest,
    TwoStepCodeResponse,
    TwoStepVerificationRequest,
    TwoStepVerificationResponse,
)
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import CookieManagementException
from app.modules.user.application.mappers import (
    create_entity_mapper as sign_up_entity_mapper,
)

router = APIRouter(**router_docs)


# ============================================================================
# COOKIE HELPERS
# ============================================================================
def set_cookies(response: Response, authentication: Authentication) -> None:
    """Set HttpOnly cookies for tokens."""
    try:
        response.set_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            value=TokenType.BEARER.value,
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            value=authentication.refresh_token.access_token.token
            if authentication.refresh_token.access_token.token
            else "",
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            value=authentication.refresh_token.token
            if authentication.refresh_token.token
            else "",
            max_age=settings.COOKIES_REFRESH_TOKEN_MAX_AGE,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the set_cookies function.")
        raise CookieManagementException()


def delete_cookies(response: Response) -> None:
    """Delete cookies."""
    try:
        response.delete_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the delete_cookies function."
        )
        raise CookieManagementException()


# ============================================================================
# CREATE: LOGIN
# ============================================================================
@router.post("/login/", **login_docs)
@router.post("/login", include_in_schema=False)
async def login(
    request: Request,
    response: Response,
    _: Annotated[None, Depends(no_authentication)],
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LoginResponse:
    """Login endpoint."""
    try:
        request_domain = login_entity_mapper(form_data, request)
        response_domain = await use_case.login(request_domain)
        output = entity_login_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the login endpoint.")
        raise AuthenticationException()


# ============================================================================
# SIGN UP
# ============================================================================
@router.post("/sign-up/", **sign_up_docs)
@router.post("/sign-up", include_in_schema=False)
async def sign_up(
    _: Annotated[None, Depends(no_authentication)],
    payload: SignUpRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> SignUpResponse:
    """Sign up endpoint."""
    try:
        request_domain = sign_up_entity_mapper(payload)
        response_domain = await use_case.sign_up(request_domain)
        output = entity_sign_up_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the sign up endpoint.")
        raise AuthenticationException()


# ============================================================================
# UPDATE: REFRESH
# ============================================================================
@router.patch("/refresh/", **refresh_docs)
@router.patch("/refresh", include_in_schema=False)
async def refresh(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_refresh)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> RefreshResponse:
    """Refresh tokens endpoint."""
    try:
        request_domain = refresh_entity_mapper(authentication)
        response_domain = await use_case.refresh(request_domain)
        output = entity_refresh_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the refresh endpoint.")
        raise AuthenticationException()


# ============================================================================
# DELETE: LOGOUT
# ============================================================================
@router.delete("/logout/", **logout_docs)
@router.delete("/logout", include_in_schema=False)
async def logout(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_logout)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LogoutResponse:
    """Logout endpoint."""
    try:
        request_domain = logout_entity_mapper(authentication)
        response_domain = await use_case.logout(request_domain)
        output = entity_logout_mapper(response_domain)

        delete_cookies(response)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the logout endpoint.")
        raise AuthenticationException()


# ============================================================================
# FORGOT PASSWORD
# ============================================================================
@router.post("/forgot-password/", **forgot_password_docs)
@router.post("/forgot-password", include_in_schema=False)
async def forgot_password(
    _: Annotated[None, Depends(no_authentication)],
    payload: ForgotPasswordRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> ForgotPasswordResponse:
    """Forgot password endpoint."""
    try:
        await use_case.forgot_password(email=str(payload.email))
        return entity_forgot_password_mapper(None)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the forgot password endpoint."
        )
        raise AuthenticationException()


# ============================================================================
# RESET PASSWORD
# ============================================================================
@router.post("/reset-password/", **reset_password_docs)
@router.post("/reset-password", include_in_schema=False)
async def reset_password(
    _: Annotated[None, Depends(no_authentication)],
    payload: ResetPasswordRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> ResetPasswordResponse:
    """Reset password endpoint."""
    try:
        await use_case.reset_password(
            code=payload.code,
            password=payload.password,
            confirm_password=payload.confirm_password,
        )
        return entity_reset_password_mapper(None)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the reset password endpoint."
        )
        raise AuthenticationException()


# ============================================================================
# LOCK SCREEN
# ============================================================================
@router.post("/lock-screen/", **lock_screen_docs)
@router.post("/lock-screen", include_in_schema=False)
async def lock_screen(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    payload: LockScreenRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LockScreenResponse:
    """Lock screen endpoint."""
    try:
        await use_case.lock_screen(
            authentication=authentication, password=payload.password
        )
        return entity_lock_screen_mapper(authentication.user)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the lock screen endpoint.")
        raise AuthenticationException()


# ============================================================================
# TWO-STEP VERIFICATION
# ============================================================================
@router.post("/two-step-verification/", **two_step_verification_docs)
@router.post("/two-step-verification", include_in_schema=False)
async def two_step_verification(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    payload: TwoStepVerificationRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> TwoStepVerificationResponse:
    """Two-step verification endpoint."""
    try:
        await use_case.two_step_verification(
            authentication=authentication,
            country_code=payload.country_code,
            phone_number=payload.phone_number,
        )
        return entity_two_step_verification_mapper(authentication.user)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the two-step verification endpoint."
        )
        raise AuthenticationException()


# ============================================================================
# TWO-STEP CODE
# ============================================================================
@router.post("/two-step-code/", **two_step_code_docs)
@router.post("/two-step-code", include_in_schema=False)
async def two_step_code(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    payload: TwoStepCodeRequest,
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> TwoStepCodeResponse:
    """Two-step code endpoint."""
    try:
        response_domain = await use_case.two_step_code(
            authentication=authentication,
            code=payload.code,
            dont_ask_again=payload.dont_ask_again,
        )

        set_cookies(response, response_domain)

        return entity_two_step_code_mapper(response_domain)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the two-step code endpoint."
        )
        raise AuthenticationException()
