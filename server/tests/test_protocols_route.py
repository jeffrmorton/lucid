"""Tests for protocols route."""

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from lucid_server.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_list_protocols(client: AsyncClient) -> None:
    response = await client.get("/api/protocols/")
    assert response.status_code == 200
    protocols = response.json()
    assert isinstance(protocols, list)
    # Should find at least one protocol from the protocols/ directory
    assert len(protocols) > 0
    for p in protocols:
        assert "name" in p
        assert "evidence_level" in p


async def test_get_protocol(client: AsyncClient) -> None:
    response = await client.get("/api/protocols/smr_training")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "bands" in data
    assert data["name"] == "SMR Training"


async def test_get_nonexistent_protocol(client: AsyncClient) -> None:
    response = await client.get("/api/protocols/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


async def test_get_protocol_rejects_invalid_name(client: AsyncClient) -> None:
    """A protocol name failing the allowlist (e.g. uppercase/dots) is rejected with 404."""
    response = await client.get("/api/protocols/Bad.Name")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


async def test_list_protocols_handles_parse_error(client: AsyncClient) -> None:
    """When a protocol YAML fails to parse, it is skipped."""
    with patch(
        "lucid_server.routes.protocols.load_protocol",
        side_effect=RuntimeError("bad yaml"),
    ):
        response = await client.get("/api/protocols/")
        assert response.status_code == 200
        # All protocols fail to parse, returns empty list
        assert response.json() == []
