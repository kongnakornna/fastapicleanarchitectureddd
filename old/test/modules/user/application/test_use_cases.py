from datetime import date
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.user.application.enums import Gender
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.application.use_cases import UserUseCases
from app.modules.user.domain.entities import User
from app.modules.user.domain.value_objects import Name
from app.modules.user.presentation.exceptions import (
    UserEmailAlreadyExistsException,
    UserEmailNotFoundException,
    UserException,
    UsernameAlreadyExistsException,
)

HASH_PW = "app.modules.user.application.use_cases.hash_password"


def _make_user(**overrides):
    defaults = {
        "name": Name(first_name="John", last_name="Doe"),
        "username": "johndoe",
        "gender": Gender.MALE,
        "birthdate": date(1990, 1, 15),
        "email": "john@localhost.com",
        "phone": "+66812345678",
        "password": "secret123",
    }
    defaults.update(overrides)
    return User(**defaults)


@pytest.fixture
def repository_mock():
    return Mock(spec=IUserRepository)


@pytest.fixture
def shared_service_mock():
    mock = Mock(spec=SharedUseCases)
    mock.get_user_by_id = AsyncMock()
    return mock


@pytest.fixture
def usecase(repository_mock, shared_service_mock):
    return UserUseCases(repository=repository_mock, shared_service=shared_service_mock)


# ============================================================
# CREATE
# ============================================================


class TestCreateUser:
    @pytest.mark.asyncio
    async def test_create_calls_repository_create(self, usecase, repository_mock):
        repository_mock.exists_by_email.return_value = False
        repository_mock.exists_by_username.return_value = False
        repository_mock.create = AsyncMock()
        user = _make_user()

        with patch(
            HASH_PW, new_callable=AsyncMock, return_value="hashed"
        ):
            result = await usecase.create(user)

        repository_mock.create.assert_called_once()
        assert result == user

    @pytest.mark.asyncio
    async def test_create_hashes_password(self, usecase, repository_mock):
        repository_mock.exists_by_email.return_value = False
        repository_mock.exists_by_username.return_value = False
        repository_mock.create = AsyncMock()
        user = _make_user()

        with patch(
            HASH_PW, new_callable=AsyncMock, return_value="hashed123"
        ) as hash_mock:
            await usecase.create(user)

        hash_mock.assert_called_once_with("secret123")
        assert user.hashed_password == "hashed123"

    @pytest.mark.asyncio
    async def test_create_raises_when_email_exists(self, usecase, repository_mock):
        repository_mock.exists_by_email.return_value = True
        user = _make_user()

        with pytest.raises(UserEmailAlreadyExistsException):
            await usecase.create(user)

        repository_mock.exists_by_username.assert_not_called()
        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_raises_when_username_exists(self, usecase, repository_mock):
        repository_mock.exists_by_email.return_value = False
        repository_mock.exists_by_username.return_value = True
        user = _make_user()

        with pytest.raises(UsernameAlreadyExistsException):
            await usecase.create(user)

        repository_mock.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_raises_user_exception_on_unexpected_error(self, usecase, repository_mock):
        repository_mock.exists_by_email.return_value = False
        repository_mock.exists_by_username.return_value = False
        repository_mock.create = AsyncMock(side_effect=RuntimeError("db boom"))
        user = _make_user()

        with (
            patch(HASH_PW, new_callable=AsyncMock, return_value="hashed"),
            pytest.raises(UserException),
        ):
            await usecase.create(user)


# ============================================================
# ME
# ============================================================


class TestMe:
    @pytest.mark.asyncio
    async def test_me_returns_user(self, usecase, shared_service_mock):
        user = _make_user()
        shared_service_mock.get_user_by_id.return_value = user

        result = await usecase.me(user)

        assert result == user
        shared_service_mock.get_user_by_id.assert_called_once_with(user)

    @pytest.mark.asyncio
    async def test_me_raises_when_not_found(self, usecase, shared_service_mock):
        user = _make_user()
        shared_service_mock.get_user_by_id.return_value = None

        with pytest.raises(UserEmailNotFoundException):
            await usecase.me(user)

    @pytest.mark.asyncio
    async def test_me_raises_user_exception_on_unexpected_error(self, usecase, shared_service_mock):
        user = _make_user()
        shared_service_mock.get_user_by_id.side_effect = RuntimeError("boom")

        with pytest.raises(UserException):
            await usecase.me(user)
