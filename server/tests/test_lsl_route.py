"""Tests for LSL route endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from lucid_server.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_lsl_available(client: AsyncClient) -> None:
    response = await client.get("/api/lsl/available")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert isinstance(data["available"], bool)


async def test_lsl_streams_without_pylsl(client: AsyncClient) -> None:
    response = await client.get("/api/lsl/streams")
    assert response.status_code == 200
    data = response.json()
    assert "streams" in data
    assert isinstance(data["streams"], list)


async def test_lsl_status(client: AsyncClient) -> None:
    response = await client.get("/api/lsl/status")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data
    assert data["connected"] is False
    assert "channel_count" in data
    assert data["channel_count"] == 0
    assert "sample_rate" in data
    assert data["sample_rate"] == 0.0
