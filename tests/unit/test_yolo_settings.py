"""Unit tests for settings"""
from __future__ import annotations
import uuid
import pytest
from app.modules.yolo.domain.settings import PlatformSettings, SettingsPatch

pytestmark = pytest.mark.unit


def test_default_settings_valid():
    s = PlatformSettings(tenant_id=uuid.uuid4())
    assert s.validate() == []


def test_invalid_conf():
    s = PlatformSettings(tenant_id=uuid.uuid4(), conf_threshold=1.5)
    errs = s.validate()
    assert any("conf_threshold" in e for e in errs)


def test_patch_apply():
    s = PlatformSettings(tenant_id=uuid.uuid4())
    p = SettingsPatch(conf_threshold=0.5, device="cpu")
    s2 = p.apply_to(s)
    assert s2.conf_threshold == 0.5
    assert s2.device == "cpu"
