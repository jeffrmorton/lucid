"""Health check endpoints."""

from fastapi import APIRouter

from lucid_server import __version__

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Return server health status."""
    return {"status": "ok", "version": __version__}
