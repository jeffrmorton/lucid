"""LSL stream management endpoints."""

from fastapi import APIRouter

from lucid_server.services.lsl_inlet import LSLInlet

router = APIRouter()

# Shared LSL inlet instance
_inlet = LSLInlet()


@router.get("/available")
async def lsl_available() -> dict:
    """Check if LSL (pylsl) is available."""
    return {"available": _inlet.is_available}


@router.get("/streams")
async def list_streams() -> dict:
    """List available LSL EEG streams on the network."""
    if not _inlet.is_available:
        return {"streams": [], "error": "pylsl not installed"}
    streams = _inlet.resolve_streams()  # pragma: no cover
    return {"streams": streams}  # pragma: no cover


@router.get("/status")
async def lsl_status() -> dict:
    """Get current LSL connection status."""
    return {
        "connected": _inlet.connected,
        "channel_count": _inlet.get_channel_count(),
        "sample_rate": _inlet.get_sample_rate(),
    }
