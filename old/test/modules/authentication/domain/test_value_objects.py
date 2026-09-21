from uuid import uuid4

import pytest

from app.modules.authentication.domain.value_objects import Claims, RefreshClaims
from app.modules.shared.domain.entities import DomainError


def _make_claims(**overrides):
    defaults = {
        "iss": "test-issuer",
        "sub": uuid4(),
        "aud": "test-audience",
        "iat": 1000,
        "nbf": 1000,
        "exp": 9999,
        "jti": uuid4(),
        "grant_id": "grant-1",
        "scope": "openid profile",
    }
    defaults.update(overrides)
    return Claims(**defaults)


def _make_refresh_claims(**overrides):
    defaults = {
        "iss": "test-issuer",
        "sub": uuid4(),
        "aud": "test-audience",
        "iat": 1000,
        "nbf": 1000,
        "exp": 9999,
        "jti": uuid4(),
        "client_id": "client-1",
        "grant_id": "grant-1",
        "scope": "openid profile",
    }
    defaults.update(overrides)
    return RefreshClaims(**defaults)


# ============================================================
# Claims
# ============================================================


class TestClaimsValidation:
    def test_accepts_valid_claims(self):
        claims = _make_claims()
        assert claims.iss == "test-issuer"
        assert claims.scope == "openid profile"

    def test_normalizes_scope_lowercase(self):
        claims = _make_claims(scope="  OPENID   Profile  ")
        assert claims.scope == "openid   profile"

    def test_normalizes_iss_strip(self):
        claims = _make_claims(iss="  issuer  ")
        assert claims.iss == "issuer"

    def test_rejects_missing_iss(self):
        with pytest.raises(DomainError, match="issuer.*required"):
            _make_claims(iss=None)

    def test_rejects_empty_iss(self):
        with pytest.raises(DomainError, match="issuer.*required"):
            _make_claims(iss="")

    def test_rejects_missing_sub(self):
        with pytest.raises(DomainError, match="subject.*required"):
            _make_claims(sub=None)

    def test_rejects_missing_aud(self):
        with pytest.raises(DomainError, match="audience.*required"):
            _make_claims(aud="")

    def test_rejects_missing_iat(self):
        with pytest.raises(DomainError, match="issued at.*required"):
            _make_claims(iat=None)

    def test_rejects_negative_iat(self):
        with pytest.raises(DomainError, match="positive integer"):
            _make_claims(iat=-1)

    def test_rejects_missing_nbf(self):
        with pytest.raises(DomainError, match="not before.*required"):
            _make_claims(nbf=None)

    def test_rejects_nbf_before_iat(self):
        with pytest.raises(DomainError, match="cannot be earlier than issued at"):
            _make_claims(iat=2000, nbf=1000)

    def test_rejects_missing_exp(self):
        with pytest.raises(DomainError, match="expiration.*required"):
            _make_claims(exp=None)

    def test_rejects_exp_before_iat(self):
        with pytest.raises(DomainError, match="must be after issued at"):
            _make_claims(iat=5000, nbf=5000, exp=3000)

    def test_rejects_missing_jti(self):
        with pytest.raises(DomainError, match="JWT ID.*required"):
            _make_claims(jti=None)

    def test_rejects_missing_grant_id(self):
        with pytest.raises(DomainError, match="grant_id.*required"):
            _make_claims(grant_id="")

    def test_rejects_missing_scope(self):
        with pytest.raises(DomainError, match="scope.*required"):
            _make_claims(scope="")


class TestClaimsConstructionFromDict:
    def test_from_dict(self):
        sub = uuid4()
        jti = uuid4()
        data = {
            "iss": "issuer",
            "sub": str(sub),
            "aud": "audience",
            "iat": 1000,
            "nbf": 1000,
            "exp": 9999,
            "jti": str(jti),
            "grant_id": "g1",
            "scope": "openid",
        }
        claims = Claims.from_dict(data)
        assert claims.sub == sub
        assert claims.jti == jti

    def test_to_dict_roundtrip(self):
        claims = _make_claims()
        data = claims.to_dict()
        restored = Claims.from_dict(data)
        assert claims == restored


class TestClaimsEquality:
    def test_eq_same_values(self):
        sub = uuid4()
        jti = uuid4()
        a = _make_claims(sub=sub, jti=jti)
        b = _make_claims(sub=sub, jti=jti)
        assert a == b

    def test_str_representation(self):
        claims = _make_claims()
        s = str(claims)
        assert "test-issuer" in s


# ============================================================
# RefreshClaims
# ============================================================


class TestRefreshClaimsValidation:
    def test_accepts_valid_refresh_claims(self):
        rc = _make_refresh_claims()
        assert rc.iss == "test-issuer"
        assert rc.client_id == "client-1"

    def test_normalizes_client_id_lowercase(self):
        rc = _make_refresh_claims(client_id="  CLIENT-1  ")
        assert rc.client_id == "client-1"

    def test_rejects_missing_client_id(self):
        with pytest.raises(DomainError, match="client_id.*required"):
            _make_refresh_claims(client_id="")

    def test_rejects_missing_iss(self):
        with pytest.raises(DomainError, match="issuer.*required"):
            _make_refresh_claims(iss=None)

    def test_rejects_missing_sub(self):
        with pytest.raises(DomainError, match="subject.*required"):
            _make_refresh_claims(sub=None)

    def test_rejects_missing_aud(self):
        with pytest.raises(DomainError, match="audience.*required"):
            _make_refresh_claims(aud="")

    def test_rejects_nbf_before_iat(self):
        with pytest.raises(DomainError, match="cannot be earlier than issued at"):
            _make_refresh_claims(iat=2000, nbf=1000)

    def test_rejects_exp_before_iat(self):
        with pytest.raises(DomainError, match="must be after issued at"):
            _make_refresh_claims(iat=5000, nbf=5000, exp=3000)

    def test_rejects_missing_grant_id(self):
        with pytest.raises(DomainError, match="grant_id.*required"):
            _make_refresh_claims(grant_id="")

    def test_rejects_missing_scope(self):
        with pytest.raises(DomainError, match="scope.*required"):
            _make_refresh_claims(scope="")


class TestRefreshClaimsConstructionFromDict:
    def test_from_dict(self):
        sub = uuid4()
        jti = uuid4()
        data = {
            "iss": "issuer",
            "sub": str(sub),
            "aud": "audience",
            "iat": 1000,
            "nbf": 1000,
            "exp": 9999,
            "jti": str(jti),
            "client_id": "c1",
            "grant_id": "g1",
            "scope": "openid",
        }
        rc = RefreshClaims.from_dict(data)
        assert rc.sub == sub
        assert rc.jti == jti
        assert rc.client_id == "c1"

    def test_to_dict_roundtrip(self):
        rc = _make_refresh_claims()
        data = rc.to_dict()
        restored = RefreshClaims.from_dict(data)
        assert rc == restored
