# Changelog

## [0.1.2] - 2026-03-30

### Added
- EarthSync SR entrainment: live Schumann Resonance data as dynamic neurofeedback target
- EarthSyncClient service: async HTTP client for EarthSync public API
- sr_entrainment.yaml protocol: dynamic bands track live SR fundamental
- NeurofeedbackEngine.update_band_range(): real-time band frequency adjustment
- EEGProcessor.compute_custom_band_power(): arbitrary frequency range power
- httpx dependency for async API calls
- 22 new tests (123 total, was 101)

### Infrastructure
- Python 3.13, FastAPI 0.135, Vite 8, TypeScript 6.0, Vitest 4.1
- pyright type checking, bandit security scanning, vulture dead code detection
- Ruff 0.15 with 30+ rule categories
- GitHub Actions CI (8 jobs)

## [0.1.1] - 2026-03-28
- LSL inlet service: receive data from 60+ EEG devices via Lab Streaming Layer
- LSL REST API: /api/lsl/available, /streams, /status
- EDF+ export: pure Python writer/reader per EDF+ specification (no external deps)
- Configurable device: LUCID_BRAINFLOW_BOARD_ID environment variable
- BrainFlow bridge documents all common board IDs (Muse, OpenBCI, Neurosity, etc.)
- SDK LSL inlet for user-facing data acquisition
- NeuroSky MindWave ThinkGear protocol driver (38 tests, pure Python serial parser)
- Containerized EEG simulator (Docker dev profile, auto-reconnect, configurable parameters)
- WebSocket viewer broadcast: server broadcasts processed data to all connected dashboard clients
- Professional dark theme UI: Tailwind v4, shadcn-inspired, resizable panels, viridis colormap
- Sidebar page navigation: Signals, Neurofeedback, Sessions, Device pages
- Real frequency-resolved spectrogram from PSD data (0-55 Hz, dB scale)
- nginx WebSocket proxy for same-origin browser connections
- BCI protocols integration research (44 KB) + dashboard design research

## [0.1.0] - 2026-03-28

### Added
- Rust DSP core: biquad filters, Hann-windowed FFT/PSD, ASR artifact rejection, CSP, band power extraction (23 tests)
- WASM bindings: 234 KB browser module via wasm-pack (5 exported functions)
- PyO3 bindings: Rust DSP callable from Python, returns numpy arrays via maturin
- Python FastAPI server: real-time WebSocket EEG processing, session management, neurofeedback engine (101 tests, 100% coverage)
- Python SDK: device connection, signal processing, feature extraction, artifact detection (140 tests, 100% coverage)
- React 19 web dashboard: EEG trace, spectrogram, topo map, band power, neurofeedback panel, session manager, device connect (114 tests, 100% coverage)
- ESP32-S3 firmware: compiles with ESP-IDF v5.3.2 (ADS1299 + BLE/WiFi stubs)
- Hardware BOM ($120) and KiCad project placeholders
- Neurofeedback protocols: SMR training, alpha/theta, beta training (YAML)
- Docker compose: server + web containerization
- Integration tests: end-to-end WebSocket pipeline, neurofeedback workflow, REST lifecycle (21 tests)
- 240 KB research literature reviews (BCI landscape, hardware, algorithms, engineering)

### Infrastructure
- Monorepo: pnpm workspaces + Turborepo
- Linting: Biome (TypeScript), Ruff (Python), clippy (Rust)
- Testing: Vitest (web), pytest (server/SDK), cargo test (Rust)
- 378 tests total across 4 languages, 100% coverage on Python + TypeScript
