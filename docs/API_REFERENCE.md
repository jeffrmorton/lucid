# API Reference

## REST Endpoints

All REST endpoints are served by the FastAPI server on port 3001 by default.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server health check. Returns `{"status": "ok", "version": "<lucid_server.__version__>"}`. |
| GET | `/api/sessions/` | List all recording sessions. |
| POST | `/api/sessions/` | Create a new session. Body: `{"name": "...", "protocol": "..."}`. |
| GET | `/api/sessions/{id}` | Get a specific session by ID. Returns **404** `{"detail": "Session not found"}` if absent. |
| DELETE | `/api/sessions/{id}` | Delete a session by ID. Returns **404** if absent. |
| GET | `/api/data/` | List available recordings. |
| GET | `/api/data/bands` | Get standard EEG band definitions (delta through gamma). |
| GET | `/api/protocols/` | List protocols from YAML files with evidence levels (canonical protocol listing). |
| GET | `/api/protocols/{name}` | Get full protocol details. Returns **404** for a missing or non-allowlisted (`[a-z0-9_-]+`) name. |
| GET | `/api/lsl/available` | Check if LSL (pylsl) is installed. |
| GET | `/api/lsl/streams` | List available EEG streams on network. |
| GET | `/api/lsl/status` | LSL connection status. |

> The former `/api/data/protocols` (a stale static list) was removed; use `/api/protocols/`.

## WebSocket: EEG Streaming (`/ws/eeg`)

Real-time bidirectional EEG data streaming.

**Client sends**: Binary frames containing raw EEG samples as little-endian float64 values. Data is interpreted as `(n_channels, n_samples)` where `n_channels` is configured server-side (default 8).

**Server responds**: JSON frames with processed results:

```json
{
  "type": "processed",
  "status": "processed",
  "n_samples": 250,
  "band_powers": {
    "delta": [0.5, 0.6, ...],
    "theta": [1.2, 1.1, ...],
    "alpha": [3.5, 3.2, ...],
    "beta": [0.8, 0.9, ...],
    "gamma": [0.1, 0.2, ...]
  },
  "psd_shape": [8, 126]
}
```

Each band power array has one value per channel. Error responses use `{"type": "error", "error": "message"}`.

**Message envelope**: every outbound message carries a uniform `type` discriminator (`processed` / `phase` / `feedback` / `error`); the legacy `status`/`phase`/`error` keys are retained for backward compatibility.

**Connection hardening** (all WS endpoints): the `Origin` header is checked against the configured CORS origins — a cross-site browser origin is closed with code 1008 (a missing Origin, i.e. a native client, is allowed). Frames larger than 8 MB are rejected; misaligned binary frames are sliced to an 8-byte boundary rather than crashing the connection. `/ws/viewer` caps concurrent viewers at 64.

## WebSocket: Neurofeedback (`/ws/neurofeedback`)

Two-phase neurofeedback training protocol.

**Phase 1 -- Protocol Selection**: Client sends JSON to select a protocol:
```json
{"protocol": "smr_training"}
```

Server responds with calibration instructions:
```json
{"type": "phase", "phase": "calibration", "duration_s": 120}
```

For the SR-entrainment protocol, the calibration message also carries an `earthsync` block (`station_id`, `sr_frequency`, `sr_amplitude`, `degraded`).

**Phase 2 -- Calibration**: Client sends binary EEG data (same format as `/ws/eeg`). Server accumulates baseline statistics. When complete it reports the real calibration state:
```json
{"type": "phase", "phase": "training", "calibrated": true}
```

**Phase 3 -- Training**: Client continues sending binary EEG. Server responds with real-time feedback:
```json
{
  "type": "feedback",
  "status": "feedback",
  "reward": true,
  "inhibit": false,
  "reward_value": 1.2,
  "inhibit_value": 0.3,
  "band_powers": {"alpha": [...], "smr": [...], "sr": [...], ...},
  "sr": {"frequency": 7.84, "station_id": "simulator1", "degraded": false}
}
```

`band_powers` now includes **every protocol band** (e.g. `smr`, `low beta`, `high beta`, `sr`) computed over its own frequency range, not just the 5 standard bands — so custom reward/inhibit bands actually drive feedback. The `sr` field is present only when EarthSync entrainment is active.
