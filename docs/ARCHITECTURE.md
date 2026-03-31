# Architecture

## System Overview

Lucid is a modular brain-computer interface platform organized into five layers: hardware, firmware, DSP core, server, and web dashboard. Each layer communicates through well-defined interfaces, allowing independent development and testing.

## Data Flow

```
Data Sources (choose one):
  ├─ BrainFlow board (50+ devices: Muse, OpenBCI, Neurosity...)
  ├─ LSL stream (60+ devices: Brain Products, BioSemi, ANT Neuro...)
  └─ Direct WebSocket (binary float64)
    ↓
Server Pipeline: bandpass → notch → PSD → band powers
    ↓
Electrodes -> ADS1299 (24-bit ADC, 250 SPS)
           -> ESP32-S3 (SPI @ 20 MHz)
           -> BLE/WiFi streaming
           -> FastAPI Server (WebSocket)
           -> EEG Processing Pipeline
              -> Bandpass filter (0.5-100 Hz, 4th order Butterworth)
              -> Notch filter (50/60 Hz, IIR)
              -> Artifact rejection (threshold-based ASR)
              -> Welch PSD estimation
              -> Band power extraction (delta/theta/alpha/beta/gamma)
           -> JSON response via WebSocket
           -> React Web Dashboard (real-time visualization)
```

## Component Boundaries

**Firmware** (ESP-IDF/C): Owns hardware communication. Reads raw ADC samples via SPI, buffers them, and streams over BLE or WiFi. No signal processing occurs on-device beyond basic sample buffering.

**DSP Core** (Rust): Stateless signal processing library compiled to both WASM (for browser-side processing) and PyO3 (for server-side Python bindings). Implements filters, FFT, artifact subspace reconstruction, and common spatial patterns.

**Server** (Python/FastAPI): Orchestrates the processing pipeline. Receives binary EEG data over WebSocket, runs it through the filter chain, computes spectral features, and manages neurofeedback training sessions. Exposes REST endpoints for session management and protocol configuration.

**Web Dashboard** (React 19/TypeScript): Renders real-time EEG traces, spectrograms, topographic maps, and band power charts. Manages device connection state and neurofeedback training UI. Uses Canvas 2D for visualization with planned WebGPU migration.

**SDK** (Python): Client library for programmatic device access, offline analysis, and BrainFlow integration for third-party hardware.

## Key Design Decisions

- **Galvanic isolation is mandatory.** The ADuM4160 USB isolator ensures patient safety. All analog circuits are battery-powered and electrically isolated from mains-connected equipment.
- **Stateful filters with per-chunk processing.** The server maintains filter state (IIR zi vectors) across WebSocket messages, enabling continuous streaming without boundary artifacts.
- **YAML-based neurofeedback protocols.** Protocol definitions are declarative, specifying target bands, threshold percentiles, and electrode montages. The engine evaluates band powers against calibrated baselines.
- **Canvas 2D over WebGL for initial visualization.** Simpler debugging and broader compatibility. WebGPU planned for spectrogram rendering when browser support stabilizes.
- **ONNX Runtime for ML inference.** Enables training models in PyTorch and deploying via a lightweight runtime without framework dependencies in production.
