"""Health check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Return server health status."""
    return {"status": "ok", "version": "0.2.0"}
