"""Neurofeedback protocol management endpoints."""

import re
from pathlib import Path

import structlog
from fastapi import APIRouter, HTTPException, status

from lucid_server.services.neurofeedback import load_protocol

router = APIRouter()
logger = structlog.get_logger(__name__)

PROTOCOLS_DIR = Path(__file__).parent.parent.parent.parent / "protocols"
_PROTOCOL_NAME_RE = re.compile(r"^[a-z0-9_-]+$")


@router.get("/")
async def list_protocols() -> list[dict]:
    """List available neurofeedback protocols."""
    protocols = []
    if PROTOCOLS_DIR.exists():
        for f in sorted(PROTOCOLS_DIR.glob("*.yaml")):
            try:
                p = load_protocol(f)
            except Exception:
                logger.warning("protocol_load_failed", file=f.name, exc_info=True)
                continue
            protocols.append(
                {
                    "name": p.name,
                    "file": f.name,
                    "evidence_level": p.evidence_level,
                    "electrode": p.electrode,
                    "description": p.description[:200] if p.description else "",
                }
            )
    return protocols


@router.get("/{protocol_name}")
async def get_protocol(protocol_name: str) -> dict:
    """Get a specific protocol's full details."""
    if not _PROTOCOL_NAME_RE.match(protocol_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protocol '{protocol_name}' not found",
        )
    path = PROTOCOLS_DIR / f"{protocol_name}.yaml"
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protocol '{protocol_name}' not found",
        )
    p = load_protocol(path)
    return {
        "name": p.name,
        "description": p.description,
        "evidence_level": p.evidence_level,
        "electrode": p.electrode,
        "reference": p.reference,
        "bands": [
            {"name": b.name, "low_hz": b.low_hz, "high_hz": b.high_hz, "target": b.target}
            for b in p.bands
        ],
        "session_duration_s": p.session_duration_s,
        "baseline_duration_s": p.baseline_duration_s,
    }
