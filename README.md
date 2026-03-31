# Lucid

Open-source brain-computer interface platform.

Lucid is a complete BCI system — hardware, firmware, real-time signal processing, and web dashboard — built to push the state of the art in six areas:

1. **Active dry electrodes** — through-hair contact with integrated preamplifiers recovering 60 dB CMRR
2. **Real-time artifact rejection** — Artifact Subspace Reconstruction + reference-based adaptive filtering
3. **Cross-subject generalization** — EEG foundation model integration (REVE, NeuroLM)
4. **Evidence-based neurofeedback** — validated protocols grounded in clinical research
5. **Multi-modal fusion** — EEG + EOG + PPG + IMU in one device
6. **EEG-Schumann resonance correlation** — novel research tool with live SR entrainment neurofeedback (with [EarthSync](https://github.com/jeffrmorton/earthsync))
7. **Device Compatibility** — Connects to 50+ devices via BrainFlow (Muse, OpenBCI, Neurosity, g.tec...) and 60+ devices via Lab Streaming Layer
8. **EDF+ Export** — Standard file format for EEG data, compatible with all analysis software

## Hardware (~$120 BOM)

| Component | Part | Purpose | Cost |
|-----------|------|---------|------|
| Biopotential ADC | ADS1299 (8-ch, 24-bit, -110 dB CMRR) | EEG signal acquisition | $25 |
| MCU | ESP32-S3 (WiFi + BLE 5.0, 16MB/8MB) | Wireless streaming + on-device DSP | $8 |
| Electrode preamps | OPA2376 × 5 dual (10 channels) | Active dry electrode amplification | $10 |
| IMU | LSM6DSOX (6-axis) | Head motion reference for artifact rejection | $3 |
| PPG | MAX86150 | Heart rate + cardiac artifact reference | $5 |
| Isolation | ADuM4160 + isolated DC-DC | 5 kV galvanic safety isolation | $12 |
| Power | LiPo 2000mAh + TP4056 USB-C charging | 28+ hr WiFi / 57+ hr BLE | $10 |
| PCB | 4-layer, 50×80mm | Analog/digital ground separation | $30 |
| Electrodes | Spring-loaded pogo pins × 10 clusters | Through-hair dry contact | $12 |

Full BOM: [`hardware/bom.yaml`](hardware/bom.yaml)

## Architecture

```
Electrodes → Active Preamp → ADS1299 → ESP32-S3 → BLE/WiFi/WebTransport
                                                        ↓
                                                  Lucid Server (Python/FastAPI)
                                                ┌───────────────────────┐
                                                │ Artifact rejection    │ ← Rust DSP via PyO3
                                                │ Feature extraction    │
                                                │ Classification (ONNX) │
                                                │ Neurofeedback engine  │
                                                │ Session recording     │
                                                └──────────┬────────────┘
                                                           ↓
                                                    Web Dashboard (React 19)
                                                ┌───────────────────────┐
                                                │ EEG traces (WebGPU)   │
                                                │ Spectrogram           │
                                                │ Topographic map       │
                                                │ Band power            │
                                                │ Neurofeedback UI      │
                                                └───────────────────────┘
```

## Quick Start

```bash
git clone https://github.com/jeffrmorton/lucid.git
cd lucid

# Install dependencies
pnpm install          # Web + monorepo tooling
uv sync               # Python server + SDK

# Start development
pnpm dev              # Starts web dashboard + server

# Connect to a Muse 2 instead of synthetic:
LUCID_BRAINFLOW_BOARD_ID=22 uv run uvicorn lucid_server.main:app
```

## Tech Stack (2026)

| Layer | Technology |
|-------|-----------|
| **Firmware** | ESP-IDF (C/C++), ADS1299 SPI driver |
| **DSP Core** | Rust → WASM (browser) + PyO3 (Python server) |
| **Server** | Python 3.13, FastAPI 0.135, uvicorn, httpx, SQLite/PostgreSQL |
| **Web** | React 19, TypeScript 6.0, Vite 8, Tailwind v4, WebGPU |
| **Streaming** | WebTransport (primary), WebSocket (fallback) |
| **ML** | ONNX Runtime (inference), PyTorch (training) |
| **Testing** | Vitest 4.1, pytest, cargo test, GoogleTest |
| **Linting** | Biome (TS/JS), Ruff 0.15 (Python), clippy (Rust) |
| **Quality** | pyright (type check), bandit (security), vulture (dead code) |
| **Monorepo** | pnpm workspaces, Turborepo |
| **CI** | GitHub Actions (8 jobs) — format, lint, pyright, test, security, dead code |
| **Hardware** | KiCad 8 |
| **Integration** | BrainFlow (50+ devices), LSL (60+ devices), NeuroSky ThinkGear, EDF+ export, [EarthSync](https://github.com/jeffrmorton/earthsync) SR |

## Project Structure

```
lucid/
├── firmware/           # ESP32-S3 + ADS1299 (ESP-IDF, C/C++)
├── hardware/           # KiCad 8 PCB designs + BOM
├── dsp/                # Rust DSP core → WASM + PyO3
├── server/             # Python FastAPI backend
├── web/                # React 19 + TypeScript + Tailwind v4 dashboard
├── sdk/python/         # Python SDK (BrainFlow, LSL, NeuroSky, EDF+ export)
├── simulator/          # Containerized EEG simulator (Docker dev profile)
├── protocols/          # Neurofeedback protocol definitions (YAML, incl. sr_entrainment)
├── models/             # Pre-trained ML models
├── research/           # Literature reviews (280+ KB)
├── scripts/            # Device simulator, utilities
└── docs/               # Documentation
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Hardware Build Guide](docs/HARDWARE_GUIDE.md)
- [Getting Started](docs/GETTING_STARTED.md)
- [Safety](docs/SAFETY.md)
- [API Reference](docs/API_REFERENCE.md)
- [Neurofeedback Guide](docs/NEUROFEEDBACK_GUIDE.md)
- [Contributing](CONTRIBUTING.md)

## Research Foundation

This project is grounded in exhaustive 2025-2026 academic research. See [`research/`](research/) for literature reviews covering hardware design, signal processing algorithms, EEG foundation models, clinical neurofeedback evidence, and system engineering.

Key evidence-based decisions:
- ADS1299 remains the gold-standard biopotential ADC (no successor as of 2026)
- Active dry electrodes with OPA2376 preamps recover ~60 dB CMRR vs passive dry
- ASR is the leading real-time artifact rejection method
- REVE (NeurIPS 2025) foundation model: 60K hours, 92 datasets, open weights
- JAMA Psychiatry 2025 meta-analysis: neurofeedback for ADHD shows limited blinded benefit; stronger evidence for sleep (SMR) and anxiety (alpha/theta)
- JavaScript/Node.js viable for BCI but Python has 10:1 ecosystem advantage
- 8 channels is the practical sweet spot (accuracy flattens beyond)

## License

Code: MIT License. Hardware: CERN-OHL-S v2.
