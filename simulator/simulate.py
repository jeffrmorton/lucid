#!/usr/bin/env python3
"""Lucid EEG device simulator — runs as a Docker service.

Generates synthetic EEG with configurable parameters and streams
to the Lucid server via WebSocket. Designed to run as a container
alongside the server in development mode.

Environment variables:
    SERVER_URL: WebSocket URL (default ws://server:3001/ws/eeg)
    SAMPLE_RATE: Samples per second (default 250)
    N_CHANNELS: Number of EEG channels (default 8)
    ALPHA_HZ: Alpha oscillation frequency (default 10.0)
    ALPHA_AMP: Alpha amplitude (default 15.0)
    THETA_AMP: Theta amplitude (default 5.0)
    BETA_AMP: Beta amplitude (default 3.0)
    NOISE_AMP: Noise amplitude (default 2.0)
    EPOCH_INTERVAL: Seconds between epochs (default 1.0)
    LOG_LEVEL: Logging verbosity (default info)
"""

import asyncio
import json
import logging
import os
import struct
import sys
import time

import numpy as np

# Configuration from environment
SERVER_URL = os.environ.get("SERVER_URL", "ws://server:3001/ws/eeg")
SAMPLE_RATE = int(os.environ.get("SAMPLE_RATE", "250"))
N_CHANNELS = int(os.environ.get("N_CHANNELS", "8"))
ALPHA_HZ = float(os.environ.get("ALPHA_HZ", "10.0"))
ALPHA_AMP = float(os.environ.get("ALPHA_AMP", "15.0"))
THETA_AMP = float(os.environ.get("THETA_AMP", "5.0"))
BETA_AMP = float(os.environ.get("BETA_AMP", "3.0"))
NOISE_AMP = float(os.environ.get("NOISE_AMP", "2.0"))
EPOCH_INTERVAL = float(os.environ.get("EPOCH_INTERVAL", "1.0"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("lucid-simulator")


def generate_epoch() -> np.ndarray:
    """Generate one epoch of synthetic EEG. Shape: (N_CHANNELS, SAMPLE_RATE)."""
    t = np.arange(SAMPLE_RATE) / SAMPLE_RATE
    signal = np.zeros((N_CHANNELS, SAMPLE_RATE))

    for ch in range(N_CHANNELS):
        phase = ch * 0.3  # slight per-channel phase offset
        alpha = ALPHA_AMP * np.sin(2 * np.pi * ALPHA_HZ * t + phase)
        theta = THETA_AMP * np.sin(2 * np.pi * 6.0 * t + phase * 0.5)
        beta = BETA_AMP * np.sin(2 * np.pi * 20.0 * t + phase * 1.5)
        noise = NOISE_AMP * np.random.randn(SAMPLE_RATE)
        signal[ch] = alpha + theta + beta + noise

    return signal


async def run() -> None:
    """Main simulation loop with reconnection."""
    import websockets

    epoch_count = 0

    while True:
        try:
            log.info("Connecting to %s", SERVER_URL)
            async with websockets.connect(SERVER_URL) as ws:
                log.info(
                    "Connected. Streaming %dch × %d SPS, α=%.1f Hz @ %.1f, interval=%.1fs",
                    N_CHANNELS, SAMPLE_RATE, ALPHA_HZ, ALPHA_AMP, EPOCH_INTERVAL,
                )

                while True:
                    data = generate_epoch()
                    raw = struct.pack(f"<{N_CHANNELS * SAMPLE_RATE}d", *data.flatten())
                    await ws.send(raw)

                    response = json.loads(await ws.recv())
                    epoch_count += 1

                    if epoch_count % 10 == 0:
                        bp = response.get("band_powers", {})
                        log.info(
                            "Epoch %d | δ=%.1f θ=%.1f α=%.1f β=%.1f γ=%.1f",
                            epoch_count,
                            bp.get("delta", [0])[0],
                            bp.get("theta", [0])[0],
                            bp.get("alpha", [0])[0],
                            bp.get("beta", [0])[0],
                            bp.get("gamma", [0])[0],
                        )

                    await asyncio.sleep(EPOCH_INTERVAL)

        except Exception as e:
            log.warning("Connection lost: %s. Reconnecting in 3s...", e)
            await asyncio.sleep(3)


if __name__ == "__main__":
    log.info("Lucid EEG Simulator starting")
    asyncio.run(run())
