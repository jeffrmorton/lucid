# API Reference

## REST Endpoints

All REST endpoints are served by the FastAPI server on port 3001 by default.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server health check. Returns `{"status": "ok", "version": "0.1.2"}`. |
| GET | `/api/sessions/` | List all recording sessions. |
| POST | `/api/sessions/` | Create a new session. Body: `{"name": "...", "protocol": "..."}`. |
| GET | `/api/sessions/{id}` | Get a specific session by ID. |
| DELETE | `/api/sessions/{id}` | Delete a session by ID. |
| GET | `/api/data/` | List available recordings. |
| GET | `/api/data/bands` | Get standard EEG band definitions (delta through gamma). |
| GET | `/api/data/protocols` | List available neurofeedback protocols (static list). |
| GET | `/api/protocols/` | List protocols from YAML files with evidence levels. |
| GET | `/api/protocols/{name}` | Get full protocol details including bands and session parameters. |
| GET | `/api/lsl/available` | Check if LSL (pylsl) is installed. |
| GET | `/api/lsl/streams` | List available EEG streams on network. |
| GET | `/api/lsl/status` | LSL connection status. |

## WebSocket: EEG Streaming (`/ws/eeg`)

Real-time bidirectional EEG data streaming.

**Client sends**: Binary frames containing raw EEG samples as little-endian float64 values. Data is interpreted as `(n_channels, n_samples)` where `n_channels` is configured server-side (default 8).

**Server responds**: JSON frames with processed results:

```json
{
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

Each band power array has one value per channel. Error responses use `{"error": "message"}`.

## WebSocket: Neurofeedback (`/ws/neurofeedback`)

Two-phase neurofeedback training protocol.

**Phase 1 -- Protocol Selection**: Client sends JSON to select a protocol:
```json
{"protocol": "smr_training"}
```

Server responds with calibration instructions:
```json
{"phase": "calibration", "duration_s": 120}
```

**Phase 2 -- Calibration**: Client sends binary EEG data (same format as `/ws/eeg`). Server accumulates baseline statistics. When complete:
```json
{"phase": "training", "calibrated": true}
```

**Phase 3 -- Training**: Client continues sending binary EEG. Server responds with real-time feedback:
```json
{
  "status": "feedback",
  "reward": true,
  "inhibit": false,
  "reward_value": 1.2,
  "inhibit_value": 0.3,
  "band_powers": {"alpha": [...], ...}
}
```
