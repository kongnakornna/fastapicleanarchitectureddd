# config/tests/test_config.py
"""
Tests — ทดสอบ invariants ของ config
"""

from __future__ import annotations

import pytest
from dataclasses import replace

from ..domain.entities import ConfigEntry
from ..domain.exceptions import DomainError
from ..domain.enums import ConfigScope, ConfigType


# ---------- test_override_precedence ----------
async def test_override_precedence(fake_repo):
    """Property: USER > TENANT > GLOBAL เสมอ"""
    # GLOBAL
    await fake_repo.save(ConfigEntry(
        key="app.theme", value="light",
        scope=ConfigScope.GLOBAL.value, scope_id="GLOBAL",
    ))
    # TENANT
    await fake_repo.save(ConfigEntry(
        key="app.theme", value="dark",
        scope=ConfigScope.TENANT.value, scope_id="t1",
    ))
    # USER
    await fake_repo.save(ConfigEntry(
        key="app.theme", value="blue",
        scope=ConfigScope.USER.value, scope_id="u1",
    ))

    # USER > TENANT > GLOBAL
    assert (await fake_repo.get_effective("app.theme", "t1", "u1")).value == "blue"
    assert (await fake_repo.get_effective("app.theme", "t1", None)).value == "dark"
    assert (await fake_repo.get_effective("app.theme", "t2", None)).value == "light"


# ---------- test_secret_encrypted_at_rest ----------
async def test_secret_encrypted_at_rest(fake_repo, cipher):
    """Secret ต้องถูก encrypt ก่อนเก็บ"""
    plain = "my-secret-value"
    ciphertext = cipher.encrypt(plain)
    assert ciphertext != plain
    entry = ConfigEntry(
        key="db.password", value=ciphertext,
        value_type=ConfigType.SECRET.value, is_secret=True,
        scope=ConfigScope.TENANT.value, scope_id="t1",
    )
    saved = await fake_repo.save(entry)
    assert saved.value != plain
    assert cipher.decrypt(saved.value) == plain


# ---------- test_secret_masked_in_api ----------
def test_secret_masked_in_api():
    """Secret ต้องถูก mask เป็น '***' ก่อนส่ง API"""
    entry = ConfigEntry(
        key="db.password", value="plain",
        value_type=ConfigType.SECRET.value, is_secret=True,
    )
    masked = entry.mask()
    assert masked.value == "***"
    assert masked.is_secret is True

    # non-secret ต้องไม่ถูก mask
    normal = ConfigEntry(key="app.theme", value="dark", is_secret=False)
    assert normal.mask().value == "dark"


# ---------- test_invalid_key_format_raises ----------
def test_invalid_key_format_raises():
    """Key format ผิดต้อง raise DomainError"""
    with pytest.raises(DomainError):
        ConfigEntry(key="Invalid-Key", value="x")
    with pytest.raises(DomainError):
        ConfigEntry(key="1starts_with_digit", value="x")
    with pytest.raises(DomainError):
        ConfigEntry(key="", value="x")
    # valid
    ConfigEntry(key="app.theme.color", value="blue")


# ---------- test_property_override_order ----------
@pytest.mark.parametrize("scopes,expected", [
    (["GLOBAL", "TENANT", "USER"], "USER"),
    (["GLOBAL", "TENANT"], "TENANT"),
    (["GLOBAL"], "GLOBAL"),
    (["TENANT", "USER"], "USER"),
])
async def test_property_override_order(fake_repo, scopes, expected):
    """Property: user > tenant > global เสมอ"""
    for scope in scopes:
        sid = {"GLOBAL": "GLOBAL", "TENANT": "t1", "USER": "u1"}[scope]
        await fake_repo.save(ConfigEntry(
            key="app.theme", value=scope,
            scope=scope, scope_id=sid,
        ))
    result = await fake_repo.get_effective("app.theme", "t1", "u1")
    assert result.value == expected