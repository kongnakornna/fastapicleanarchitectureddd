from app.modules.health.application.enums import HealthType
from app.modules.health.domain.entities import Health


class TestHealthConstruction:
    def test_defaults(self):
        h = Health()
        assert h.alembic_version is None
        assert h.user is None

    def test_status_always_ok(self):
        h = Health()
        assert h.status == HealthType.OK

    def test_with_alembic_version(self):
        h = Health(alembic_version="abc123")
        assert h.alembic_version == "abc123"

    def test_status_ok_with_alembic_version(self):
        h = Health(alembic_version="v1")
        assert h.status == HealthType.OK
