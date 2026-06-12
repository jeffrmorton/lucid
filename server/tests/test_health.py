"""Tests for health endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from lucid_server.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


async def test_health_returns_version(client: AsyncClient) -> None:
    import lucid_server

    response = await client.get("/health")
    assert response.json()["version"] == lucid_server.__version__
