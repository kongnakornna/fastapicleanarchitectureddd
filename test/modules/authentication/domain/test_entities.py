from datetime import datetime, timedelta

from app.modules.authentication.application.enums import TokenType
from app.modules.authentication.domain.entities import (
    AccessToken,
    RefreshToken,
    Session,
)
from app.modules.shared.application.enums import Role
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.user.domain.entities import User
from app.modules.user.domain.value_objects import Name


def _make_user(**overrides):
    defaults = {
        "name": Name(first_name="John", last_name="Doe"),
        "username": "johndoe",
        "email": "john@localhost.com",
        "phone": "+66812345678",
        "password": "secret",
    }
    defaults.update(overrides)
    return User(**defaults)


def _make_session(**overrides):
    defaults = {
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
        "device": "chrome-windows",
        "user": _make_user(),
    }
    defaults.update(overrides)
    return Session(**defaults)


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


# ============================================================
# Session
# ============================================================


class TestSessionNormalization:
    def test_lowercases_ip_address(self):
        s = _make_session(ip_address="192.168.1.1")
        assert s.ip_address == "192.168.1.1"

    def test_lowercases_and_strips_user_agent(self):
        s = _make_session(user_agent="  Mozilla/5.0  ")
        assert s.user_agent == "mozilla/5.0"

    def test_normalizes_optional_fields(self):
        s = _make_session(
            accept_language="  EN-US  ",
            accept_encoding="  GZIP  ",
            origin="  HTTP://LOCALHOST  ",
            referer="  HTTP://LOCALHOST/REF  ",
            location="  BANGKOK  ",
        )
        assert s.accept_language == "en-us"
        assert s.accept_encoding == "gzip"
        assert s.origin == "http://localhost"
        assert s.referer == "http://localhost/ref"
        assert s.location == "bangkok"

    def test_handles_none_optional_fields(self):
        s = _make_session(
            accept_language=None,
            accept_encoding=None,
            origin=None,
            referer=None,
            location=None,
        )
        assert s.accept_language is None
        assert s.accept_encoding is None


class TestSessionDefaults:
    def test_defaults_to_bearer_token_type(self):
        s = _make_session()
        assert s.token_type == TokenType.BEARER

    def test_defaults_not_blacklisted(self):
        s = _make_session()
        assert s.blacklisted is False


class TestSessionUpdateLastUpdatedAt:
    def test_sets_last_updated_at(self):
        s = _make_session()
        assert s.last_updated_at is None
        s.update_last_updated_at()
        assert s.last_updated_at is not None
        assert s.last_updated_at.tzinfo == BRASILIA_TZ


# ============================================================
# RefreshToken
# ============================================================


class TestRefreshTokenDefaults:
    def test_defaults_not_revoked(self):
        rt = _make_refresh_token()
        assert rt.revoked is False
        assert rt.revoked_at is None


class TestRefreshTokenRevoke:
    def test_revoke_sets_revoked_true(self):
        rt = _make_refresh_token()
        rt.revoke()
        assert rt.revoked is True
        assert rt.revoked_at is not None

    def test_activate_after_revoke(self):
        rt = _make_refresh_token()
        rt.revoke()
        rt.activate()
        assert rt.revoked is False
        assert rt.revoked_at is None


class TestRefreshTokenValidation:
    def test_revoked_defaults_to_false(self):
        rt = _make_refresh_token()
        assert rt.revoked is False
        assert rt.revoked_at is None


class TestRefreshTokenHelpers:
    def test_generate_created_at(self):
        rt = _make_refresh_token()
        assert rt.created_at is None
        rt.generate_created_at()
        assert rt.created_at is not None

    def test_generate_updated_at(self):
        rt = _make_refresh_token()
        assert rt.updated_at is None
        rt.generate_updated_at()
        assert rt.updated_at is not None

    def test_update_previous_hashed_jti(self):
        rt = _make_refresh_token(hashed_jti="current-hash")
        assert rt.previous_hashed_jti is None
        rt.update_previous_hashed_jti()
        assert rt.previous_hashed_jti == "current-hash"


# ============================================================
# AccessToken
# ============================================================


class TestAccessTokenDefaults:
    def test_defaults_not_revoked(self):
        at = _make_access_token()
        assert at.revoked is False
        assert at.revoked_at is None

    def test_defaults_to_user_role(self):
        at = _make_access_token()
        assert at.permission == Role.USER


class TestAccessTokenRevoke:
    def test_revoke_sets_revoked_true(self):
        at = _make_access_token()
        at.revoke()
        assert at.revoked is True
        assert at.revoked_at is not None

    def test_activate_after_revoke(self):
        at = _make_access_token()
        at.revoke()
        at.activate()
        assert at.revoked is False
        assert at.revoked_at is None


class TestAccessTokenHelpers:
    def test_generate_created_at(self):
        at = _make_access_token()
        assert at.created_at is None
        at.generate_created_at()
        assert at.created_at is not None

    def test_update_previous_hashed_jti(self):
        at = _make_access_token(hashed_jti="tok-hash")
        assert at.previous_hashed_jti is None
        at.update_previous_hashed_jti()
        assert at.previous_hashed_jti == "tok-hash"
