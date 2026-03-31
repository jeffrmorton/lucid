"""Session management endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory session store (replace with SQLite via SQLModel later)
_sessions: dict[str, dict] = {}
_session_counter = 0


class SessionCreate(BaseModel):
    name: str = "Untitled Session"
    protocol: str | None = None


class SessionResponse(BaseModel):
    id: str
    name: str
    protocol: str | None
    created_at: str
    status: str


@router.get("/")
async def list_sessions() -> list[SessionResponse]:
    """List all recording sessions."""
    return [SessionResponse(**s) for s in _sessions.values()]


@router.post("/")
async def create_session(body: SessionCreate | None = None) -> SessionResponse:
    """Create a new recording session."""
    global _session_counter  # noqa: PLW0603
    _session_counter += 1
    session_id = f"session_{_session_counter}"
    name = body.name if body else "Untitled Session"
    protocol = body.protocol if body else None

    session = {
        "id": session_id,
        "name": name,
        "protocol": protocol,
        "created_at": datetime.now(UTC).isoformat(),
        "status": "created",
    }
    _sessions[session_id] = session
    return SessionResponse(**session)


@router.get("/{session_id}")
async def get_session(session_id: str) -> SessionResponse | dict:
    """Get a specific session."""
    if session_id in _sessions:
        return SessionResponse(**_sessions[session_id])
    return {"error": "Session not found"}


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> dict:
    """Delete a session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return {"status": "deleted"}
    return {"error": "Session not found"}
