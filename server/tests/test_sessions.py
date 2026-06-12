"""Tests for session endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from lucid_server.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_list_sessions_empty(client: AsyncClient) -> None:
    response = await client.get("/api/sessions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_create_session(client: AsyncClient) -> None:
    response = await client.post("/api/sessions/", json={"name": "Test Session"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Session"
    assert data["status"] == "created"


async def test_create_session_default_name(client: AsyncClient) -> None:
    response = await client.post("/api/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Untitled Session"


async def test_get_session(client: AsyncClient) -> None:
    # Create then get
    create_resp = await client.post("/api/sessions/", json={"name": "Get Test"})
    session_id = create_resp.json()["id"]
    response = await client.get(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Get Test"


async def test_get_session_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/sessions/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


async def test_delete_session(client: AsyncClient) -> None:
    create_resp = await client.post("/api/sessions/", json={"name": "Delete Test"})
    session_id = create_resp.json()["id"]
    response = await client.delete(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


async def test_delete_session_not_found(client: AsyncClient) -> None:
    response = await client.delete("/api/sessions/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
