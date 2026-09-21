from unittest.mock import AsyncMock, Mock

import pytest

from app.modules.health.application.use_cases import HealthUseCases
from app.modules.health.domain.entities import Health
from app.modules.user.domain.entities import User
from app.modules.user.domain.value_objects import Name


def _make_user():
    return User(
        name=Name(first_name="Admin", last_name="User"),
        username="admin",
        email="admin@localhost.com",
        password="secret",
    )


def _make_health_uc():
    repo = Mock()
    return HealthUseCases(repository=repo), repo


class TestHealth:
    @pytest.mark.asyncio
    async def test_returns_health_with_ok_status(self):
        result = await HealthUseCases.health()
        assert isinstance(result, Health)
        assert result.status.value == "ok"


class TestAlembicVersion:
    @pytest.mark.asyncio
    async def test_sets_alembic_version(self):
        uc, repo = _make_health_uc()
        user = _make_user()
        health = Health(user=user)
        repo.get_alembic_version = AsyncMock(return_value=Health(alembic_version="abc123"))
        result = await uc.alembic_version(health)
        assert result.alembic_version == "abc123"

    @pytest.mark.asyncio
    async def test_returns_health_object(self):
        uc, repo = _make_health_uc()
        user = _make_user()
        health = Health(user=user)
        repo.get_alembic_version = AsyncMock(return_value=Health(alembic_version="v1"))
        result = await uc.alembic_version(health)
        assert isinstance(result, Health)
