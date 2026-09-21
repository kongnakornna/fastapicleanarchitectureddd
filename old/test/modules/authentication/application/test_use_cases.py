from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.modules.authentication.application.interfaces import (
    IAuthenticationRepository,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.domain.entities import (
    AccessToken,
    RefreshToken,
    Session,
)
from app.modules.authentication.presentation.exceptions import (
    AuthenticationException,
    SessionInvalidCredentialsException,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.user.domain.entities import User
from app.modules.user.domain.value_objects import Name

HASH_PW = "app.modules.authentication.application.use_cases.verify_password"
GEN_TOKENS = "app.modules.authentication.application.use_cases.generate_tokens"
HASH_TOKENS = "app.modules.authentication.application.use_cases.hash_tokens"
ADD_BLACKLIST = "app.modules.authentication.application.use_cases.add_to_blacklist"


def _make_user(**overrides):
    defaults = {
        "name": Name(first_name="John", last_name="Doe"),
        "username": "johndoe",
        "email": "john@localhost.com",
        "phone": "+66812345678",
        "password": "secret",
        "hashed_password": "hashed_secret",
    }
    defaults.update(overrides)
    return User(**defaults)


def _make_access_token(**overrides):
    defaults = {
        "expires_at": datetime.now(BRASILIA_TZ) + timedelta(hours=1),
    }
    defaults.update(overrides)
    return AccessToken(**defaults)


def _make_refresh_token(**overrides):
    defaults = {
        "expires_at": datetime.now(BRASILIA_TZ) + timedelta(days=7),
        "access_token": _make_access_token(),
    }
    defaults.update(overrides)
    return RefreshToken(**defaults)


def _make_session(**overrides):
    defaults = {
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
        "device": "chrome-windows",
        "user": _make_user(),
    }
    defaults.update(overrides)
    return Session(**defaults)


def _make_session_with_tokens(**overrides):
    session = _make_session(**overrides)
    session.refresh_token = _make_refresh_token()
    session.refresh_token.access_token = _make_access_token()
    return session


@pytest.fixture
def repository_mock():
    return Mock(spec=IAuthenticationRepository)


@pytest.fixture
def shared_service_mock():
    mock = Mock(spec=SharedUseCases)
    mock.get_user_by_username = AsyncMock()
    return mock


@pytest.fixture
def usecase(repository_mock, shared_service_mock):
    return AuthenticationUseCases(
        repository=repository_mock, shared_service=shared_service_mock
    )


# ============================================================
# LOGIN
# ============================================================


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_new_session_creates(
        self, usecase, repository_mock, shared_service_mock
    ):
        user = _make_user()
        shared_service_mock.get_user_by_username.return_value = user
        repository_mock.get_by_user_id_agent_and_device = AsyncMock(return_value=None)
        repository_mock.create = AsyncMock()
        session = _make_session(user=user)

        with (
            patch(HASH_PW, new_callable=AsyncMock, return_value=True),
            patch(GEN_TOKENS, new_callable=AsyncMock) as gen_mock,
            patch(HASH_TOKENS, new_callable=AsyncMock) as hash_mock,
        ):
            gen_session = _make_session_with_tokens(user=user)
            gen_mock.return_value = gen_session
            hash_mock.return_value = gen_session

            result = await usecase.login(session)

        repository_mock.create.assert_called_once()
        assert result == gen_session

    @pytest.mark.asyncio
    async def test_login_existing_session_updates(
        self, usecase, repository_mock, shared_service_mock
    ):
        user = _make_user()
        shared_service_mock.get_user_by_username.return_value = user

        existing = _make_session_with_tokens(user=user)
        repository_mock.get_by_user_id_agent_and_device = AsyncMock(
            return_value=existing
        )
        repository_mock.update = AsyncMock()
        session = _make_session(user=user)

        with (
            patch(HASH_PW, new_callable=AsyncMock, return_value=True),
            patch(GEN_TOKENS, new_callable=AsyncMock) as gen_mock,
            patch(HASH_TOKENS, new_callable=AsyncMock) as hash_mock,
        ):
            gen_session = _make_session_with_tokens(user=user)
            gen_mock.return_value = gen_session
            hash_mock.return_value = gen_session

            result = await usecase.login(session)

        repository_mock.update.assert_called_once()
        assert result == gen_session

    @pytest.mark.asyncio
    async def test_login_wrong_password_raises(
        self, usecase, repository_mock, shared_service_mock
    ):
        user = _make_user()
        shared_service_mock.get_user_by_username.return_value = user
        session = _make_session(user=user)

        with (
            patch(HASH_PW, new_callable=AsyncMock, return_value=False),
            pytest.raises(SessionInvalidCredentialsException),
        ):
            await usecase.login(session)

        repository_mock.create.assert_not_called()
        repository_mock.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_login_unexpected_error_raises_auth_exception(
        self, usecase, repository_mock, shared_service_mock
    ):
        shared_service_mock.get_user_by_username.side_effect = RuntimeError("boom")
        session = _make_session()

        with pytest.raises(AuthenticationException):
            await usecase.login(session)


# ============================================================
# REFRESH
# ============================================================


class TestRefresh:
    @pytest.mark.asyncio
    async def test_refresh_updates_tokens(self, usecase, repository_mock):
        repository_mock.update = AsyncMock()
        session = _make_session_with_tokens()

        with (
            patch(GEN_TOKENS, new_callable=AsyncMock) as gen_mock,
            patch(HASH_TOKENS, new_callable=AsyncMock) as hash_mock,
        ):
            gen_session = _make_session_with_tokens()
            gen_mock.return_value = gen_session
            hash_mock.return_value = gen_session

            result = await usecase.refresh(session)

        repository_mock.update.assert_called_once()
        assert result == gen_session

    @pytest.mark.asyncio
    async def test_refresh_unexpected_error_raises(self, usecase, repository_mock):
        repository_mock.update = AsyncMock(side_effect=RuntimeError("boom"))
        session = _make_session_with_tokens()

        with pytest.raises(AuthenticationException):
            await usecase.refresh(session)


# ============================================================
# LOGOUT
# ============================================================


class TestLogout:
    @pytest.mark.asyncio
    async def test_logout_deletes_session_and_blacklists(
        self, usecase, repository_mock
    ):
        repository_mock.delete = AsyncMock()
        session = _make_session_with_tokens()
        session.refresh_token.hashed_jti = "refresh-hash"
        session.refresh_token.access_token.hashed_jti = "access-hash"

        with patch(ADD_BLACKLIST, new_callable=AsyncMock) as bl_mock:
            result = await usecase.logout(session)

        repository_mock.delete.assert_called_once_with(session)
        assert bl_mock.call_count == 2
        assert result == session

    @pytest.mark.asyncio
    async def test_logout_unexpected_error_raises(self, usecase, repository_mock):
        repository_mock.delete = AsyncMock(side_effect=RuntimeError("boom"))
        session = _make_session_with_tokens()

        with pytest.raises(AuthenticationException):
            await usecase.logout(session)
