"""Neurofeedback protocol management endpoints."""

from pathlib import Path

from fastapi import APIRouter

from lucid_server.services.neurofeedback import load_protocol

router = APIRouter()

PROTOCOLS_DIR = Path(__file__).parent.parent.parent.parent / "protocols"


@router.get("/")
async def list_protocols() -> list[dict]:
    """List available neurofeedback protocols."""
    protocols = []
    if PROTOCOLS_DIR.exists():
        for f in sorted(PROTOCOLS_DIR.glob("*.yaml")):
            try:
                p = load_protocol(f)
                protocols.append(
                    {
                        "name": p.name,
                        "file": f.name,
                        "evidence_level": p.evidence_level,
                        "electrode": p.electrode,
                        "description": p.description[:200] if p.description else "",
                    }
                )
            except Exception:  # noqa: S112
                continue
    return protocols


@router.get("/{protocol_name}")
async def get_protocol(protocol_name: str) -> dict:
    """Get a specific protocol's full details."""
    path = PROTOCOLS_DIR / f"{protocol_name}.yaml"
    if not path.exists():
        return {"error": f"Protocol '{protocol_name}' not found"}
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
