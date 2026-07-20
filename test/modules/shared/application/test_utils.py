import re

from app.modules.shared.application.utils import BRASILIA_TZ, current_timestamp


class TestCurrentTimestamp:
    def test_returns_iso_format(self):
        ts = current_timestamp()
        assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$", ts)

    def test_ends_with_z(self):
        ts = current_timestamp()
        assert ts.endswith("Z")

    def test_does_not_contain_plus(self):
        ts = current_timestamp()
        assert "+00:00" not in ts


class TestBrasiliaTz:
    def test_is_zone_info(self):
        assert str(BRASILIA_TZ) == "America/Sao_Paulo"
