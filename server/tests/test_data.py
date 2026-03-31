"""Tests for data endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from lucid_server.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_get_recordings(client: AsyncClient) -> None:
    response = await client.get("/api/data/")
    assert response.status_code == 200
    assert "recordings" in response.json()


async def test_get_band_definitions(client: AsyncClient) -> None:
    response = await client.get("/api/data/bands")
    assert response.status_code == 200
    bands = response.json()["bands"]
    assert "alpha" in bands
    assert "delta" in bands
    assert bands["alpha"]["low"] == 8.0
    assert bands["alpha"]["high"] == 13.0


async def test_get_protocols(client: AsyncClient) -> None:
    response = await client.get("/api/data/protocols")
    assert response.status_code == 200
    protocols = response.json()["protocols"]
    assert len(protocols) == 3
    names = [p["name"] for p in protocols]
    assert "SMR Training" in names
