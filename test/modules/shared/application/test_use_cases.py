from unittest.mock import AsyncMock, Mock

import pytest

from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.presentation.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.user.domain.entities import User
from app.modules.user.domain.value_objects import Name
from app.modules.user.presentation.exceptions import (
    UserEmailNotFoundException,
    UserException,
)


def _make_user(**overrides):
    defaults = {
        "name": Name(first_name="Jane", last_name="Doe"),
        "username": "janedoe",
        "email": "jane@localhost.com",
        "password": "secret",
    }
    defaults.update(overrides)
    return User(**defaults)


def _make_use_case():
    repo = Mock()
    return SharedUseCases(user_repository=repo), repo


# ============================================================
# enable/disable exceptions
# ============================================================


class TestExceptionToggle:
    def test_raises_exceptions_by_default(self):
        uc, _ = _make_use_case()
        assert uc.raise_exceptions is True

    def test_disable_exceptions(self):
        uc, _ = _make_use_case()
        uc.disable_exceptions()
        assert uc.raise_exceptions is False

    def test_enable_exceptions(self):
        uc, _ = _make_use_case()
        uc.disable_exceptions()
        uc.enable_exceptions()
        assert uc.raise_exceptions is True


# ============================================================
# get_user_by_id
# ============================================================


class TestGetUserById:
    @pytest.mark.asyncio
    async def test_returns_user_when_found(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(return_value=user)
        result = await uc.get_user_by_id(user)
        assert result == user

    @pytest.mark.asyncio
    async def test_raises_when_not_found(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(UserEmailNotFoundException):
            await uc.get_user_by_id(user)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found_and_disabled(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(return_value=None)
        uc.disable_exceptions()
        result = await uc.get_user_by_id(user)
        assert result is None

    @pytest.mark.asyncio
    async def test_raises_domain_exception_on_domain_error(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(side_effect=DomainError("bad"))
        with pytest.raises(DomainException):
            await uc.get_user_by_id(user)

    @pytest.mark.asyncio
    async def test_raises_user_exception_on_unexpected_error(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(side_effect=RuntimeError("oops"))
        with pytest.raises(UserException):
            await uc.get_user_by_id(user)

    @pytest.mark.asyncio
    async def test_returns_none_on_unexpected_error_when_disabled(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(side_effect=RuntimeError("oops"))
        uc.disable_exceptions()
        result = await uc.get_user_by_id(user)
        assert result is None

    @pytest.mark.asyncio
    async def test_reraises_standard_exception(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(
            side_effect=StandardException(status_code=400, message="bad")
        )
        with pytest.raises(StandardException):
            await uc.get_user_by_id(user)


# ============================================================
# get_user_by_username
# ============================================================


class TestGetUserByUsername:
    @pytest.mark.asyncio
    async def test_returns_user_when_found(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_username = AsyncMock(return_value=user)
        result = await uc.get_user_by_username(user)
        assert result == user

    @pytest.mark.asyncio
    async def test_raises_when_not_found(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_username = AsyncMock(return_value=None)
        with pytest.raises(UserEmailNotFoundException):
            await uc.get_user_by_username(user)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found_and_disabled(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_username = AsyncMock(return_value=None)
        uc.disable_exceptions()
        result = await uc.get_user_by_username(user)
        assert result is None

    @pytest.mark.asyncio
    async def test_raises_user_exception_on_unexpected_error(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_username = AsyncMock(side_effect=RuntimeError("oops"))
        with pytest.raises(UserException):
            await uc.get_user_by_username(user)


# ============================================================
# get_user_by_email
# ============================================================


class TestGetUserByEmail:
    @pytest.mark.asyncio
    async def test_returns_user_when_found(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(return_value=user)
        result = await uc.get_user_by_email(user)
        assert result == user

    @pytest.mark.asyncio
    async def test_raises_when_not_found(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(return_value=None)
        with pytest.raises(UserEmailNotFoundException):
            await uc.get_user_by_email(user)

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found_and_disabled(self):
        uc, repo = _make_use_case()
        user = _make_user()
        repo.get_by_id = AsyncMock(return_value=None)
        uc.disable_exceptions()
        result = await uc.get_user_by_email(user)
        assert result is None
