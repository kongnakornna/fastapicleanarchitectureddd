import pytest
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def authed_client(client):
    """Client with FastAPI session stub."""
    session = client.session
    session["access_token"] = "test-token"
    session["refresh_token"] = "test-refresh"
    session["username"] = "tester"
    session.save()
    return client


@pytest.fixture
def mock_fastapi(mocker):
    """Mock FastAPIClient for unit tests."""
    mocker.patch(
        "apps.shared.infrastructure.fastapi_client.fastapi.request",
        return_value=mocker.Mock(json=lambda: {}, status_code=200),
    )
