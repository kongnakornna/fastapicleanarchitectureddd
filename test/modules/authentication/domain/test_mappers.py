from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.modules.authentication.domain.entities import (
    AccessToken,
    RefreshToken,
    Session,
)
from app.modules.authentication.domain.mappers import (
    access_token_entity_mapper,
    logout_entity_mapper,
    refresh_entity_mapper,
    refresh_token_entity_mapper,
)
from app.modules.authentication.domain.value_objects import RefreshClaims
from app.modules.authentication.presentation.schemas import (
    LogoutResponse,
    RefreshResponse,
)
from app.modules.shared.application.enums import Role
from app.modules.user.domain.entities import User
from app.modules.user.domain.value_objects import Name


def _make_user():
    return User(
        name=Name(first_name="Test", last_name="User"),
        username="testuser",
        email="test@localhost.com",
        password="secret",
    )


def _make_access_claims():
    return {
        "iss": "test-iss",
        "sub": str(uuid4()),
        "aud": "test-aud",
        "iat": int(datetime.now(UTC).timestamp()),
        "nbf": int(datetime.now(UTC).timestamp()),
        "exp": int(datetime.now(UTC).timestamp()) + 3600,
        "jti": str(uuid4()),
        "grant_id": "test@localhost.com",
        "scope": "user",
    }


def _make_refresh_claims():
    return {
        "iss": "test-iss",
        "sub": str(uuid4()),
        "aud": "test-aud",
        "iat": int(datetime.now(UTC).timestamp()),
        "nbf": int(datetime.now(UTC).timestamp()),
        "exp": int(datetime.now(UTC).timestamp()) + 3600,
        "jti": str(uuid4()),
        "client_id": "test-client",
        "grant_id": "test@localhost.com",
        "scope": "user",
    }


# ============================================================
# refresh_entity_mapper
# ============================================================


class TestRefreshEntityMapper:
    @pytest.mark.asyncio
    async def test_returns_session_when_not_output(self):
        session = Session(
            user=_make_user(),
            refresh_token=RefreshToken(access_token=AccessToken()),
        )
        result = await refresh_entity_mapper(session, output=False)
        assert result is session

    @pytest.mark.asyncio
    async def test_returns_refresh_response_when_output(self):
        session = Session(
            user=_make_user(),
            refresh_token=RefreshToken(access_token=AccessToken()),
        )
        result = await refresh_entity_mapper(session, output=True)
        assert isinstance(result, RefreshResponse)


# ============================================================
# logout_entity_mapper
# ============================================================


class TestLogoutEntityMapper:
    @pytest.mark.asyncio
    async def test_returns_session_when_not_output(self):
        session = Session(
            user=_make_user(),
            refresh_token=RefreshToken(access_token=AccessToken()),
        )
        result = await logout_entity_mapper(session, output=False)
        assert result is session

    @pytest.mark.asyncio
    async def test_returns_logout_response_when_output(self):
        session = Session(
            user=_make_user(),
            refresh_token=RefreshToken(access_token=AccessToken()),
        )
        result = await logout_entity_mapper(session, output=True)
        assert isinstance(result, LogoutResponse)

    @pytest.mark.asyncio
    async def test_raises_on_invalid_input(self):
        with pytest.raises(ValueError):
            await logout_entity_mapper("not a session", output=False)


# ============================================================
# access_token_entity_mapper
# ============================================================


class TestAccessTokenEntityMapper:
    @pytest.mark.asyncio
    async def test_returns_session(self):
        claims = _make_access_claims()
        result = await access_token_entity_mapper(claims)
        assert isinstance(result, Session)

    @pytest.mark.asyncio
    async def test_session_has_user(self):
        claims = _make_access_claims()
        result = await access_token_entity_mapper(claims)
        assert result.user is not None
        assert str(result.user.id) == claims["sub"]
        assert result.user.email == claims["grant_id"]

    @pytest.mark.asyncio
    async def test_session_has_refresh_token(self):
        claims = _make_access_claims()
        result = await access_token_entity_mapper(claims)
        assert result.refresh_token is not None
        assert isinstance(result.refresh_token, RefreshToken)

    @pytest.mark.asyncio
    async def test_access_token_has_claims(self):
        claims = _make_access_claims()
        result = await access_token_entity_mapper(claims)
        access = result.refresh_token.access_token
        assert isinstance(access, AccessToken)
        assert access.permission == Role(claims["scope"])


# ============================================================
# refresh_token_entity_mapper
# ============================================================


class TestRefreshTokenEntityMapper:
    @pytest.mark.asyncio
    async def test_returns_session(self):
        claims = _make_refresh_claims()
        result = await refresh_token_entity_mapper(claims)
        assert isinstance(result, Session)

    @pytest.mark.asyncio
    async def test_session_has_user(self):
        claims = _make_refresh_claims()
        result = await refresh_token_entity_mapper(claims)
        assert str(result.user.id) == claims["sub"]
        assert result.user.email == claims["grant_id"]

    @pytest.mark.asyncio
    async def test_refresh_token_has_claims(self):
        claims = _make_refresh_claims()
        result = await refresh_token_entity_mapper(claims)
        rt = result.refresh_token
        assert isinstance(rt.refresh_claims, RefreshClaims)

    @pytest.mark.asyncio
    async def test_refresh_token_has_access_token(self):
        claims = _make_refresh_claims()
        result = await refresh_token_entity_mapper(claims)
        assert isinstance(
            result.refresh_token.access_token, AccessToken
        )
