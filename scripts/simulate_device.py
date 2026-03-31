#!/usr/bin/env python3
"""Simulate an EEG device sending data through the Lucid WebSocket pipeline.

Generates synthetic EEG with realistic Schumann-band alpha oscillations,
connects to the server WebSocket, and streams binary data at 250 SPS.
The server processes it and returns band powers — verifying the full pipeline.

Usage:
    python scripts/simulate_device.py
    python scripts/simulate_device.py --epochs 100 --alpha-hz 10.0 --alpha-amp 15.0
"""

import argparse
import asyncio
import json
import struct
import sys
import time

import numpy as np
import websockets


def generate_epoch(
    n_channels: int = 8,
    n_samples: int = 250,
    sample_rate: float = 250.0,
    alpha_hz: float = 10.0,
    alpha_amp: float = 15.0,
    noise_amp: float = 2.0,
) -> np.ndarray:
    """Generate one epoch of synthetic EEG.

    Produces a signal with a prominent alpha oscillation plus
    band-limited noise, mimicking real resting-state EEG.

    Returns shape (n_channels, n_samples).
    """
    t = np.arange(n_samples) / sample_rate

    # Alpha oscillation (10 Hz) — dominant rhythm in relaxed, eyes-closed EEG
    alpha = alpha_amp * np.sin(2 * np.pi * alpha_hz * t)

    # Theta component (6 Hz, weaker)
    theta = (alpha_amp * 0.3) * np.sin(2 * np.pi * 6.0 * t)

    # Beta component (20 Hz, weaker)
    beta = (alpha_amp * 0.2) * np.sin(2 * np.pi * 20.0 * t)

    # Per-channel variation
    signal = np.zeros((n_channels, n_samples))
    for ch in range(n_channels):
        phase_offset = ch * 0.3  # slight phase difference per channel
        ch_alpha = alpha_amp * np.sin(2 * np.pi * alpha_hz * t + phase_offset)
        ch_noise = noise_amp * np.random.randn(n_samples)
        signal[ch] = ch_alpha + theta + beta + ch_noise

    return signal


def epoch_to_bytes(data: np.ndarray) -> bytes:
    """Convert numpy array to binary float64 for WebSocket."""
    flat = data.flatten().astype(np.float64)
    return struct.pack(f"<{len(flat)}d", *flat)


async def run_simulation(
    server_url: str = "ws://localhost:3001/ws/eeg",
    n_epochs: int = 50,
    n_channels: int = 8,
    sample_rate: int = 250,
    alpha_hz: float = 10.0,
    alpha_amp: float = 15.0,
    verbose: bool = True,
) -> None:
    """Run the device simulation."""
    print(f"Connecting to {server_url}...")

    async with websockets.connect(server_url) as ws:
        print(f"Connected. Streaming {n_epochs} epochs ({n_channels}ch × {sample_rate}sps)...\n")

        for epoch_num in range(n_epochs):
            # Generate synthetic EEG
            data = generate_epoch(
                n_channels=n_channels,
                n_samples=sample_rate,  # 1 second per epoch
                sample_rate=sample_rate,
                alpha_hz=alpha_hz,
                alpha_amp=alpha_amp,
            )

            # Send as binary
            await ws.send(epoch_to_bytes(data))

            # Receive processed result
            response = await ws.recv()
            result = json.loads(response)

            if verbose and epoch_num % 5 == 0:
                if result.get("status") == "processed":
                    bp = result["band_powers"]
                    # Show channel 0 band powers
                    print(
                        f"Epoch {epoch_num:3d} | "
                        f"δ={bp['delta'][0]:6.1f}  "
                        f"θ={bp['theta'][0]:6.1f}  "
                        f"α={bp['alpha'][0]:6.1f}  "
                        f"β={bp['beta'][0]:6.1f}  "
                        f"γ={bp['gamma'][0]:6.1f}"
                    )
                else:
                    print(f"Epoch {epoch_num:3d} | {result}")

            # Real-time pacing: 1 epoch per second
            await asyncio.sleep(0.1)  # 10 Hz for faster demo

        print(f"\nDone. Streamed {n_epochs} epochs.")


async def run_neurofeedback_simulation(
    server_url: str = "ws://localhost:3001/ws/neurofeedback",
    protocol: str = "smr_training",
    n_channels: int = 8,
    sample_rate: int = 250,
    verbose: bool = True,
) -> None:
    """Run a neurofeedback session simulation."""
    print(f"Connecting to {server_url}...")

    async with websockets.connect(server_url) as ws:
        # Send protocol selection
        await ws.send(json.dumps({"protocol": protocol}))
        init_response = json.loads(await ws.recv())
        print(f"Init: {init_response}")

        if "error" in init_response:
            print(f"Error: {init_response['error']}")
            return

        # Calibration phase
        if init_response.get("phase") == "calibration":
            cal_duration = init_response.get("duration_s", 30)
            cal_epochs = cal_duration  # 1 epoch per second at sample_rate samples
            print(f"Calibration: sending {cal_epochs} epochs...")

            for i in range(cal_epochs):
                data = generate_epoch(n_channels=n_channels, n_samples=sample_rate, alpha_amp=10.0)
                await ws.send(epoch_to_bytes(data))

            # Receive calibration complete
            cal_result = json.loads(await ws.recv())
            print(f"Calibration result: {cal_result}")

        # Training phase
        print("\nTraining phase — sending epochs with varying alpha...")
        for epoch_num in range(20):
            # Vary alpha amplitude to simulate training
            alpha = 5.0 + epoch_num * 1.0  # Gradually increase
            data = generate_epoch(n_channels=n_channels, n_samples=sample_rate, alpha_amp=alpha)
            await ws.send(epoch_to_bytes(data))

            response = json.loads(await ws.recv())
            if verbose:
                reward = "✓ REWARD" if response.get("reward") else "  —    "
                inhibit = "⚠ INHIBIT" if response.get("inhibit") else "         "
                print(
                    f"Epoch {epoch_num:3d} | α_amp={alpha:5.1f} | "
                    f"{reward} {inhibit} | "
                    f"reward_val={response.get('reward_value', 0):.2f}"
                )

            await asyncio.sleep(0.1)

        print("\nNeurofeedback session complete.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate EEG device for Lucid")
    parser.add_argument("--server", default="ws://localhost:3001/ws/eeg", help="WebSocket URL")
    parser.add_argument("--epochs", type=int, default=50, help="Number of epochs to send")
    parser.add_argument("--channels", type=int, default=8, help="Number of EEG channels")
    parser.add_argument("--rate", type=int, default=250, help="Sample rate (SPS)")
    parser.add_argument("--alpha-hz", type=float, default=10.0, help="Alpha oscillation frequency")
    parser.add_argument("--alpha-amp", type=float, default=15.0, help="Alpha amplitude")
    parser.add_argument("--mode", choices=["eeg", "nfb"], default="eeg", help="Mode: eeg or neurofeedback")
    parser.add_argument("--protocol", default="smr_training", help="Neurofeedback protocol name")
    parser.add_argument("-q", "--quiet", action="store_true", help="Less output")

    args = parser.parse_args()

    if args.mode == "nfb":
        asyncio.run(
            run_neurofeedback_simulation(
                server_url=args.server.replace("/ws/eeg", "/ws/neurofeedback"),
                protocol=args.protocol,
                n_channels=args.channels,
                sample_rate=args.rate,
                verbose=not args.quiet,
            )
        )
    else:
        asyncio.run(
            run_simulation(
                server_url=args.server,
                n_epochs=args.epochs,
                n_channels=args.channels,
                sample_rate=args.rate,
                alpha_hz=args.alpha_hz,
                alpha_amp=args.alpha_amp,
                verbose=not args.quiet,
            )
        )


if __name__ == "__main__":
    main()
