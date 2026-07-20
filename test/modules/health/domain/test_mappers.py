import pytest

from app.modules.health.domain.entities import Health
from app.modules.health.domain.mappers import (
    alembic_entity_mapper,
    health_mapper,
    model_entity_mapper,
)
from app.modules.health.infrastructure.models import AlembicModel
from app.modules.user.domain.entities import User
from app.modules.user.domain.value_objects import Name


def _make_user():
    return User(
        name=Name(first_name="Admin", last_name="User"),
        username="admin",
        email="admin@localhost.com",
        password="secret",
    )


class TestHealthMapper:
    @pytest.mark.asyncio
    async def test_maps_health_to_response(self):
        h = Health(alembic_version="abc123")
        result = await health_mapper(h)
        assert result.status.value == "ok"


class TestAlembicEntityMapper:
    @pytest.mark.asyncio
    async def test_user_to_health(self):
        user = _make_user()
        result = await alembic_entity_mapper(user)
        assert isinstance(result, Health)
        assert result.user == user

    @pytest.mark.asyncio
    async def test_health_to_alembic_response(self):
        h = Health(alembic_version="v1")
        result = await alembic_entity_mapper(h)
        assert result.version == "v1"


class TestModelEntityMapper:
    @pytest.mark.asyncio
    async def test_alembic_model_to_health(self):
        model = AlembicModel(version_num="abc123")
        result = await model_entity_mapper(model)
        assert isinstance(result, Health)
        assert result.alembic_version == "abc123"
