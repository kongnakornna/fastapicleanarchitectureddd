"""Unit tests for authentication domain"""
from __future__ import annotations
import uuid
from datetime import UTC, datetime

import pytest

from app.modules.authentication.domain.enums import TokenType
from app.modules.authentication.domain.value_objects import (
    Claims, RefreshClaims,
)

pytestmark = pytest.mark.unit


class TestTokenType:
    def test_values(self) -> None:
        assert TokenType.BEARER.value == "Bearer"
        assert TokenType.REFRESH.value == "Refresh"


class TestClaims:
    def _valid(self) -> dict:
        return {
            "iss": "erp-api", "sub": "10000000001",
            "aud": "erp-client",
            "iat": 1700000000, "nbf": 1700000000,
            "exp": 1700003600, "jti": uuid.uuid4(),
            "grant_id": "10000000001", "scope": "admin",
        }

    def test_valid(self) -> None:
        c = Claims(**self._valid())
        assert c.sub == "10000000001"
        assert c.scope == "admin"

    def test_missing_grant_id(self) -> None:
        d = self._valid(); d["grant_id"] = ""
        with pytest.raises(Exception):
            Claims(**d)

    def test_nbf_before_iat_rejected(self) -> None:
        d = self._valid(); d["nbf"] = d["iat"] - 1
        with pytest.raises(Exception):
            Claims(**d)

    def test_immutable(self) -> None:
        c = Claims(**self._valid())
        with pytest.raises(AttributeError):
            c.iss = "other"  # type: ignore[misc]


class TestRefreshClaims:
    def _valid(self) -> dict:
        return {
            "iss": "erp-api", "sub": "10000000001",
            "aud": "erp-client",
            "iat": 1700000000, "nbf": 1700000000,
            "exp": 1700003600, "jti": uuid.uuid4(),
            "client_id": "web", "grant_id": "10000000001",
            "scope": "refresh",
        }

    def test_valid(self) -> None:
        c = RefreshClaims(**self._valid())
        assert c.client_id == "web"
        assert c.sub == "10000000001"

    def test_missing_client_id(self) -> None:
        d = self._valid(); d["client_id"] = ""
        with pytest.raises(Exception):
            RefreshClaims(**d)
