# Hardware Guide

## Bill of Materials (Summary)

| Component | Part | Key Spec |
|-----------|------|----------|
| ADC | ADS1299 | 8-ch, 24-bit, 250 SPS, -110 dB CMRR |
| MCU | ESP32-S3-WROOM-1 | Dual-core, WiFi + BLE 5.0 |
| Isolation | ADuM4160 | USB 2.0 galvanic isolator |
| Preamp | OPA2376 | Unity gain buffer, >10 GOhm input Z |
| Power | LiPo 3.7V 2000mAh | Battery-powered analog section |

Full BOM with Digikey/Mouser part numbers is in `hardware/bom.yaml`.

## Circuit Design

The design uses a two-board architecture: an isolated analog front-end (ADS1299 + active electrode preamps) and a digital controller (ESP32-S3). The ADuM4160 isolator sits between them, providing 5 kV galvanic isolation.

Schematics and PCB layout are in `hardware/lucid-board/` (KiCad 8 format). Active electrode designs are in `hardware/active-electrode/`. See `hardware/DESIGN_NOTES.md` for detailed design rationale.

## Assembly

1. Solder the analog board first (ADS1299, OPA2376 preamps, passive components)
2. Solder the digital board (ESP32-S3, ADuM4160, USB-C connector)
3. Connect boards via the isolated SPI ribbon cable
4. Flash firmware: `cd firmware && idf.py flash monitor`
5. Verify SPI communication by checking the ADS1299 device ID register

## Safety

All patient-connected circuits must be galvanically isolated from mains power. See `docs/SAFETY.md` for mandatory safety requirements before connecting electrodes to any person. Never bypass the isolation barrier.

## Using Existing Hardware

Lucid supports 50+ commercial EEG devices via BrainFlow and 60+ via LSL. You don't need to build custom hardware to use Lucid.

See the [Getting Started](GETTING_STARTED.md) guide for device configuration.
