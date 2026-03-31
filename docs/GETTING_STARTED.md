# Getting Started

## Prerequisites

- **Rust** (2024 edition) with `wasm-pack` for DSP core
- **Python 3.12+** with `uv` for server and SDK dependency management
- **Node.js 20+** with `pnpm` for web dashboard
- **ESP-IDF 5.x** (only needed for firmware development)

## Install Dependencies

```bash
# Clone the repo
git clone https://github.com/your-org/lucid.git && cd lucid

# Server
cd server && uv sync --all-extras

# Web dashboard
cd ../web && pnpm install

# SDK
cd ../sdk/python && uv sync --all-extras

# DSP core
cd ../../dsp && cargo build
```

## Run Development Servers

```bash
# Terminal 1: Start the FastAPI server
cd server && uv run uvicorn lucid_server.main:app --reload --port 3001

# Terminal 2: Start the Vite dev server (proxies API to :3001)
cd web && pnpm dev
```

Open `http://localhost:3000` in your browser to see the dashboard.

## Run with Docker

```bash
docker compose up
```

This starts both the server and web dashboard with hot-reload enabled.

## Run Tests

```bash
# Rust DSP
cd dsp && cargo test

# Python server (100% coverage required)
cd server && uv run pytest --cov=lucid_server --cov-fail-under=100

# Python SDK
cd sdk/python && PYTHONPATH=. python3 -m pytest tests/ --cov=lucid --cov-fail-under=100

# Web dashboard
cd web && npx vitest run --coverage
```

## Connect a Device

1. Power on the Lucid board (battery or USB with isolation)
2. Ensure BLE or WiFi is enabled on your computer
3. Click "Connect Device" in the dashboard
4. Apply electrodes using the 10-20 montage (see HARDWARE_GUIDE.md)
5. Verify signal quality in the EEG trace view before starting a session

For synthetic data without hardware, the server processes random data sent via the WebSocket test client.

## Connect a Real Device

### Via BrainFlow (recommended)
Set the board ID via environment variable:
```bash
LUCID_BRAINFLOW_BOARD_ID=22   # Muse 2
LUCID_BRAINFLOW_BOARD_ID=0    # OpenBCI Cyton
LUCID_BRAINFLOW_SERIAL_PORT=/dev/ttyUSB0  # for wired boards
```

### Via LSL
Start your device's LSL streaming software, then check:
```bash
curl http://localhost:3001/api/lsl/streams
```

### Export Data
Use the Python SDK to export recordings to EDF+:
```python
from lucid.edf_export import write_edf
write_edf("recording.edf", data, sample_rate=250, channel_names=["Fz","C3","Cz","C4","Pz","PO7","Oz","PO8"])
```
