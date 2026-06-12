"""Data recording and retrieval endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_recordings() -> dict:
    """List available recordings."""
    return {"recordings": []}


@router.get("/bands")
async def get_band_definitions() -> dict:
    """Return standard EEG band definitions."""
    return {
        "bands": {
            "delta": {"low": 0.5, "high": 4.0, "description": "Deep sleep, unconscious"},
            "theta": {"low": 4.0, "high": 8.0, "description": "Drowsy, meditative"},
            "alpha": {"low": 8.0, "high": 13.0, "description": "Relaxed, eyes closed"},
            "beta": {"low": 13.0, "high": 30.0, "description": "Alert, focused"},
            "gamma": {"low": 30.0, "high": 100.0, "description": "Higher cognitive, perception"},
        }
    }
