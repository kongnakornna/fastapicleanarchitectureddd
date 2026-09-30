"""Property tests for authentication invariants"""
from __future__ import annotations
import uuid

import pytest
from hypothesis import given, settings, strategies as st

from app.modules.authentication.domain.value_objects import Claims

pytestmark = pytest.mark.property


@settings(max_examples=50)
@given(
    sub=st.integers(min_value=1, max_value=10**12),
    scope=st.sampled_from(["user", "admin", "moderator"]),
)
def test_claims_sub_always_string(sub: int, scope: str) -> None:
    c = Claims(
        iss="erp-api", sub=str(sub), aud="erp-client",
        iat=1700000000, nbf=1700000000, exp=1700003600,
        jti=uuid.uuid4(), grant_id=str(sub), scope=scope,
    )
    assert isinstance(c.sub, str)
    assert c.sub == str(sub)
