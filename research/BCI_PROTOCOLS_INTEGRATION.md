# BCI Communication Protocols and Hardware Integration Research

Comprehensive survey of communication protocols, data formats, and integration paths for connecting the Lucid platform to existing commercial and open-source EEG/BCI hardware.

**Research date:** 2026-03-26

---

## Table of Contents

1. [BrainFlow Universal Abstraction Layer](#1-brainflow-universal-abstraction-layer)
2. [Lab Streaming Layer (LSL)](#2-lab-streaming-layer-lsl)
3. [Bluetooth Low Energy (BLE) for EEG](#3-bluetooth-low-energy-ble-for-eeg)
4. [Open Standards and Data Formats](#4-open-standards-and-data-formats)
5. [Commercial Device Protocol Reference](#5-commercial-device-protocol-reference)
6. [Practical Integration Path for Lucid](#6-practical-integration-path-for-lucid)

---

## 1. BrainFlow Universal Abstraction Layer

### 1.1 Overview

**Repository:** https://github.com/brainflow-dev/brainflow
**Stars:** ~1,700 | **License:** MIT | **Latest:** v5.21.0 (Jan 2026)
**Languages:** C++ core with bindings for Python, Java, C#, Julia, MATLAB, R, Rust, TypeScript/Node.js (9 languages)

BrainFlow is the de facto standard for hardware-agnostic EEG/biosignal acquisition. It provides a single API (`BoardShim`) that abstracts over 39+ board configurations. All boards inherit from a C++ `Board` base class. Language bindings call the same underlying C/C++ code through FFI, meaning adding a new board requires zero changes to any language binding.

### 1.2 Three Core Modules

1. **BoardShim** -- Data acquisition abstraction. Board discovery, connection, configuration, streaming. Board-agnostic API.
2. **DataFilter** -- Signal processing. FFT, bandpass/bandstop/lowpass/highpass (Butterworth, Chebyshev, Bessel), wavelet transform, denoising, downsampling, CSP, PSD.
3. **MLModel** -- ONNX model inference (replaced built-in classifiers in v5.x).

### 1.3 Complete Board List with IDs and Protocols

| Board ID | Enum Name | Device | Manufacturer | Protocol |
|----------|-----------|--------|-------------|----------|
| -3 | PLAYBACK_FILE_BOARD | Playback (recorded data) | BrainFlow | File I/O |
| -2 | STREAMING_BOARD | Streaming Board | BrainFlow | Multicast UDP |
| -1 | SYNTHETIC_BOARD | Synthetic Board (testing) | BrainFlow | Software-generated |
| 0 | CYTON_BOARD | Cyton | OpenBCI | Serial (115200 baud via RFDuino USB dongle) |
| 1 | GANGLION_BOARD | Ganglion | OpenBCI | Serial (via BLED112 BLE dongle) |
| 2 | CYTON_DAISY_BOARD | Cyton + Daisy (16-ch) | OpenBCI | Serial (115200 baud) |
| 3 | GALEA_BOARD | Galea | OpenBCI | Socket/USB |
| 4 | GANGLION_WIFI_BOARD | Ganglion + WiFi Shield | OpenBCI | WiFi (TCP) |
| 5 | CYTON_WIFI_BOARD | Cyton + WiFi Shield | OpenBCI | WiFi (TCP) |
| 6 | CYTON_DAISY_WIFI_BOARD | CytonDaisy + WiFi Shield | OpenBCI | WiFi (TCP) |
| 7 | BRAINBIT_BOARD | BrainBit | NeuroMD | BLE (via libneurosdk) |
| 8 | UNICORN_BOARD | Unicorn Hybrid Black | g.tec | BLE (via Unicorn API) |
| 9 | CALLIBRI_EEG_BOARD | Callibri EEG | NeuroMD | BLE (via libneurosdk) |
| 10 | CALLIBRI_EMG_BOARD | Callibri EMG | NeuroMD | BLE (via libneurosdk) |
| 11 | CALLIBRI_ECG_BOARD | Callibri ECG | NeuroMD | BLE (via libneurosdk) |
| 13 | NOTION_1_BOARD | Notion 1 | Neurosity | WiFi/Cloud (WebSocket) |
| 14 | NOTION_2_BOARD | Notion 2 | Neurosity | WiFi/Cloud (WebSocket) |
| 16 | GFORCE_PRO_BOARD | gForcePro ArmBand | OYMotion | BLE |
| 17 | FREEEEG32_BOARD | FreeEEG32 | NeuroIDSS | USB Serial (921600 baud) |
| 18 | BRAINBIT_BLED_BOARD | BrainBit (BLED) | NeuroMD | BLE (native, no dongle) |
| 19 | GFORCE_DUAL_BOARD | gForceDual ArmBand | OYMotion | BLE |
| 21 | MUSE_S_BLED_BOARD | Muse S | InteraXon | BLE GATT (native, no dongle) |
| 22 | MUSE_2_BLED_BOARD | Muse 2 | InteraXon | BLE GATT (native, no dongle) |
| 23 | CROWN_BOARD | Crown | Neurosity | WiFi/Cloud (WebSocket) |
| 24 | ANT_NEURO_EE_410_BOARD | eego mylab 410 | ANT Neuro | USB (via vendor SDK) |
| 25 | ANT_NEURO_EE_411_BOARD | eego mylab 411 | ANT Neuro | USB (via vendor SDK) |
| 26 | ANT_NEURO_EE_430_BOARD | eego sports 430 | ANT Neuro | USB (via vendor SDK) |
| 27 | ANT_NEURO_EE_211_BOARD | eego 211 | ANT Neuro | USB (via vendor SDK) |
| 28 | ANT_NEURO_EE_212_BOARD | eego 212 | ANT Neuro | USB (via vendor SDK) |
| 29 | ANT_NEURO_EE_213_BOARD | eego 213 | ANT Neuro | USB (via vendor SDK) |
| 30 | ANT_NEURO_EE_214_BOARD | eego 214 | ANT Neuro | USB (via vendor SDK) |
| 31 | ANT_NEURO_EE_215_BOARD | eego 215 | ANT Neuro | USB (via vendor SDK) |
| 32 | ANT_NEURO_EE_221_BOARD | eego 221 | ANT Neuro | USB (via vendor SDK) |
| 33 | ANT_NEURO_EE_222_BOARD | eego 222 | ANT Neuro | USB (via vendor SDK) |
| 34 | ANT_NEURO_EE_223_BOARD | eego 223 | ANT Neuro | USB (via vendor SDK) |
| 35 | ANT_NEURO_EE_224_BOARD | eego 224 | ANT Neuro | USB (via vendor SDK) |
| 36 | ANT_NEURO_EE_225_BOARD | eego 225 | ANT Neuro | USB (via vendor SDK) |
| 37 | ENOPHONE_BOARD | Enophone | Enophone | BLE |
| 38 | MUSE_2016_BOARD | Muse 2016 (original) | InteraXon | BLE (via BLED112 dongle) |
| 39 | MUSE_2016_BLED_BOARD | Muse 2016 BLED | InteraXon | BLE GATT (native) |
| 40 | PIEEG_BOARD | PiEEG | HackerBCI | SPI (GPIO on Raspberry Pi) |
| 41 | BRAINALIVE_BOARD | BrainAlive | BrainAlive | BLE |
| 42 | MUSE_S_BOARD | Muse S | InteraXon | BLE (via BLED112 dongle) |
| 43 | MUSE_2_BOARD | Muse 2 | InteraXon | BLE (via BLED112 dongle) |
| 44 | EXPLORE_4_BOARD | Explore 4-ch | Mentalab | BLE |
| 45 | EXPLORE_8_BOARD | Explore 8-ch | Mentalab | BLE |
| 46 | EMOTIBIT_BOARD | EmotiBit | EmotiBit | WiFi (UDP) |
| 47 | KNIGHT_BOARD | Knight | NeuroPawn | Serial |
| 48 | KNIGHT_IMU_BOARD | Knight IMU | NeuroPawn | Serial |
| 49 | BIOLISTENER_BOARD | BioListener | BioListener | Serial |
| 50 | IRONBCI32_BOARD | IronBCI 32 | IronBCI | USB Serial |

**Note on Muse variants:** Muse has two connection modes in BrainFlow. The `_BLED_BOARD` variants use native BLE (no dongle required) and are the recommended path. The non-BLED variants require a Silicon Labs BLED112 USB BLE dongle.

### 1.4 BrainFlow Python Usage Pattern

```python
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

params = BrainFlowInputParams()
params.serial_port = "/dev/ttyUSB0"  # device-specific

board = BoardShim(BoardIds.CYTON_BOARD, params)
board.prepare_session()
board.start_stream()

# ... collect data ...

data = board.get_board_data()  # returns 2D numpy array, removes from buffer
# OR
data = board.get_current_board_data(256)  # last 256 samples, non-destructive

board.stop_stream()
board.release_session()

# Channel discovery
eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_BOARD)
sampling_rate = BoardShim.get_sampling_rate(BoardIds.CYTON_BOARD)
```

### 1.5 Adding a New Board to BrainFlow

**Effort:** 1-3 days for experienced C++ developer. Steps:

1. Add board ID to `BoardIds` enum in C and all language bindings
2. Add object creation to `board_controller.cpp` `prepare_session` factory switch
3. Add board metadata to `brainflow_boards.cpp` (channel descriptions, sample rate, etc.)
4. Inherit from `Board` class, implement pure virtual methods
5. Store data in `DataBuffer`, reuse utilities from `utils/` folder
6. Add source files to `build.cmake`
7. Optionally develop a device emulator for CI testing

Helper base classes: `DynLibBoard` (for SDK-based boards), `BLELibBoard` (for BLE devices).

**Key insight:** Device abstraction at C/C++ level keeps FFI interface stable. Adding a new board requires zero changes to language bindings.

---

## 2. Lab Streaming Layer (LSL)

### 2.1 Overview

**Repository:** https://github.com/sccn/labstreaminglayer
**Stars:** ~750 | **License:** MIT | **Core library:** liblsl (C++)
**Reference paper:** Kothe et al. (2025) "The lab streaming layer for synchronized multimodal recording" (Imaging Neuroscience, MIT Press)

LSL is the standard protocol for real-time synchronized multimodal biosignal streaming in research environments. It provides:

- **Network-transparent data transport** over TCP/UDP on LAN
- **Sub-millisecond time synchronization** across machines (NTP-style clock correction)
- **Automatic service discovery** via UDP multicast
- **Stream metadata** (channel count, sample rate, channel format, channel labels)

### 2.2 Architecture

```
Data Source (Outlet)                    Data Consumer (Inlet)
+---------------------+                +---------------------+
| EEG Device Driver   |   TCP/UDP      | Recording Software  |
| creates StreamOutlet| ----LAN----->  | creates StreamInlet |
| pushes samples      |                | pulls samples       |
+---------------------+                +---------------------+
         |                                       |
         +--- UDP multicast service discovery ----+
```

**Core components:**
- **liblsl** -- C++ library implementing the protocol
- **Outlets** -- Data publishers (one per stream, e.g., one per EEG device)
- **Inlets** -- Data consumers (one per stream being received)
- **LabRecorder** -- Application for recording all LSL streams to XDF files

### 2.3 Time Synchronization Protocol

LSL implements a simplified NTP algorithm:

1. Peer A sends packet with local timestamp t0
2. Peer B records receive time t1, then sends response with t1 and send time t2
3. Peer A records final receive time t3
4. Round-trip time (RTT) = (t3 - t0) - (t2 - t1)
5. Clock offset (OFS) = ((t1 - t0) + (t2 - t3)) / 2
6. Multiple exchanges (~10 over 200 ms), lowest-RTT pair selected
7. Re-synchronization every ~5 seconds

**Accuracy:** Sub-millisecond on standard LAN. Sufficient for EEG (4 ms resolution at 250 SPS).

### 2.4 LSL Python Usage Pattern (pylsl)

```python
from pylsl import StreamInlet, resolve_stream

# Resolve an EEG stream on the network
streams = resolve_stream('type', 'EEG')
inlet = StreamInlet(streams[0])

# Receive samples
while True:
    sample, timestamp = inlet.pull_sample()
    # sample is a list of floats (one per channel)
    # timestamp is in LSL's unified clock
```

For higher throughput: `inlet.pull_chunk()` returns multiple samples at once.

**MNE-LSL (modern API):** The `mne-lsl` package replaces the older `mne-realtime` and `pylsl`, providing tighter MNE-Python integration with `RtEpochs` for real-time epoching with artifact rejection.

### 2.5 Complete LSL-Supported Device List

#### EEG/Biosignal Hardware with Native (Manufacturer-Provided) LSL Support

| Manufacturer | Device | Signal Type |
|-------------|--------|-------------|
| ANT Neuro | eego mylab, eego sports | EEG |
| Bitbrain | EEG & Biosignals platform | EEG/Bio |
| Bittium | NeurOne Tesla | EEG |
| BrainAccess | All devices (default protocol) | EEG |
| Brain Products | actiCHamp, actiCHamp Plus, BrainAmp series, LiveAmp | EEG |
| Cognionics | All headsets | EEG |
| EB Neuro | BE Plus LTM | EEG |
| Emotiv | EPOC (via EmotivPRO) | EEG |
| IDUN | Guardian | EEG |
| mBrainTrain | SMARTING | EEG |
| Mentalab | Explore 4-ch, 8-ch | EEG |
| Neuracle | NeuroHub | EEG |
| neuroelectrics | Enobio, StarStim (via NIC2) | EEG/tDCS |
| Neurosity | Notion (Crown not confirmed) | EEG |
| OpenBCI | All headsets (Cyton, Ganglion, Daisy) | EEG |
| Starcat | HackEEG Shield | EEG |
| TMSi | APEX, SAGA | EEG/EMG |
| Foc.us | EEG Dev Kit | EEG |
| Cerelog | ESP-EEG | EEG |

#### EEG/Biosignal Hardware with Third-Party LSL Adapters

| Manufacturer | Device | Adapter |
|-------------|--------|---------|
| ABM | B-Alert X4/X10/X24 | LSL distribution app |
| BioSemi | Active II Mk1/Mk2 | LSL distribution app |
| Blackrock | Cerebus/NSP | LSL distribution app |
| Cognionics | dry/wireless | LSL distribution app |
| EGI | AmpServer | LSL distribution app |
| g.tec | g.USBamp, g.HIamp, g.Nautilus | g.NEEDaccess LSL app |
| g.tec | Unicorn Hybrid Black | UnicornLSL app |
| InteraXon | Muse 2016, Muse 2, Muse S | muse-lsl / BlueMuse |
| Neuroscan | Synamp II, Synamp Wireless | LSL distribution app |
| Wearable Sensing | All devices | LSL distribution app |

#### Non-EEG Hardware with LSL Support

- **fNIRS:** Artinis (Brite, PortaLite, PortaMon, OxyMon), Cortivision PHOTON CAP, GowerLabs LUMO, NIRx (NIRScout, NIRSport 2)
- **ECG/EMG:** bitalino, CGX AIM, Polar H10, Shimmer, TMSi SPIRE
- **Eye tracking:** 7invensun, EyeLogic, EyeTech, Pupil-Labs, SMI, SR Research Eyelink, Tobii (Pro, Glasses 3, consumer)
- **Motion capture:** PhaseSpace, Microsoft Kinect, OptiTrack, OpenVR, Qualisys, Xsens, Leap Motion
- **Input devices:** Keyboards, joysticks, gamepads, Wiimote
- **Stimulation:** PsychoPy, PsychToolbox, Presentation, E-Prime 3.0, Unity, Unreal Engine

#### Software Platforms with LSL Integration

BCI2000, OpenViBE (via Acquisition Server), NeuroPype, MNE-Python (via mne-lsl), BCILAB, Open Ephys, FieldTrip, Timeflux, iMotions, EventIDE.

### 2.6 LSL vs BrainFlow

| Aspect | BrainFlow | LSL |
|--------|-----------|-----|
| **Primary purpose** | Hardware abstraction + data acquisition | Multi-stream synchronization + network transport |
| **Protocol** | Direct device connection | TCP/UDP over LAN |
| **Time sync** | Per-device timestamps | Cross-device NTP-style sync |
| **Device support** | ~50 board configs (built into library) | 60+ devices (via separate apps) |
| **Data processing** | Built-in (FFT, filters, CSP, ONNX) | None (separate concern) |
| **Recording** | Custom (user code) | LabRecorder to XDF |
| **Language bindings** | 9 languages | C, C++, Python, Java, C#, MATLAB |
| **Best for** | Single-device BCI apps | Multi-device research setups |
| **Complementary** | Yes -- BrainFlow can push to LSL | Yes -- LSL can feed BrainFlow |

**Key insight for Lucid:** These are not competing -- they are complementary. BrainFlow provides device connection; LSL provides multi-stream synchronization. Lucid should support both.

---

## 3. Bluetooth Low Energy (BLE) for EEG

### 3.1 No Standard BLE Profile for EEG

**There is no Bluetooth SIG-adopted GATT profile for EEG or biopotential signals.** Every manufacturer uses proprietary BLE services and characteristics. The Bluetooth SIG has adopted profiles for heart rate (0x180D), blood pressure (0x1810), and generic health sensors, but nothing for EEG/biopotential.

The closest standard is IEEE 11073-10101 (Health Informatics -- Nomenclature), which includes neurology-related codes in its nomenclature, and IEEE 11073-20601 which defines an optimized exchange protocol used by the Bluetooth SIG's Generic Health Sensor profile. However, no manufacturer has implemented EEG over the Generic Health Sensor profile. Every consumer EEG device uses custom BLE GATT services.

### 3.2 Muse (InteraXon) BLE Protocol

**Devices:** Muse 2016, Muse 2, Muse S, Muse S Athena
**Protocol status:** Reverse-engineered, community-documented, functional open-source implementations exist

#### BLE GATT Service and Characteristics

| Element | UUID |
|---------|------|
| **Service** | `0xfe8d` |
| **Control** | `273e0001-4c4d-454d-96be-f03bac821358` |
| **EEG Ch 1 (TP9)** | `273e0003-4c4d-454d-96be-f03bac821358` |
| **EEG Ch 2 (AF7)** | `273e0004-4c4d-454d-96be-f03bac821358` |
| **EEG Ch 3 (AF8)** | `273e0005-4c4d-454d-96be-f03bac821358` |
| **EEG Ch 4 (TP10)** | `273e0006-4c4d-454d-96be-f03bac821358` |
| **EEG Ch 5 (AUX)** | `273e0007-4c4d-454d-96be-f03bac821358` |
| **Gyroscope** | `273e0009-4c4d-454d-96be-f03bac821358` |
| **Accelerometer** | `273e000a-4c4d-454d-96be-f03bac821358` |
| **Telemetry** | `273e000b-4c4d-454d-96be-f03bac821358` |
| **PPG Ch 1 (ambient)** | `273e000f-4c4d-454d-96be-f03bac821358` |
| **PPG Ch 2 (infrared)** | `273e0010-4c4d-454d-96be-f03bac821358` |
| **PPG Ch 3 (red)** | `273e0011-4c4d-454d-96be-f03bac821358` |

#### Command Protocol

Commands sent as encoded strings to Control characteristic:
- `p21` -- Standard EEG preset
- `p20` -- EEG with auxiliary channels
- `p50` -- PPG enabled mode
- `p1035` -- Full sensor mode (Muse S, all sensors)
- `h` -- Halt/pause streaming
- `d` -- Resume streaming
- `s` -- Start stream
- `v1` -- Request firmware version

**Critical quirk (Muse S):** The `dc001` command must be sent TWICE to start streaming -- undocumented behavior discovered by reverse engineering (amused-py project).

#### Sampling Rates

- EEG: 256 Hz (12 samples per BLE notification)
- PPG: 64 Hz (6 samples per notification)
- Accelerometer/Gyroscope: 52 Hz

#### Open-Source Implementations

| Project | Language | Status | Notes |
|---------|----------|--------|-------|
| muse-js | TypeScript | Active | Web Bluetooth API, Muse 1/2/S |
| muse-lsl | Python | Active | pylsl + bleak backend, streams to LSL |
| BlueMuse | C# (UWP) | Active | Windows 10 UWP, streams to LSL |
| amused-py | Python | Active (2024) | First Muse S full protocol implementation |
| BrainFlow | C++ | Active | Board IDs 21-22 (BLED), 38-39 (dongle), 42-43 (dongle) |

### 3.3 OpenBCI Ganglion BLE Protocol

**Device:** OpenBCI Ganglion (4-channel, MCP3912 ADC)
**Protocol status:** Fully documented by manufacturer (open source)

#### BLE GATT Service and Characteristics

| Element | UUID |
|---------|------|
| **Service** | `fe84` |
| **Receive (RX)** | `2d30c082-f39f-4ce6-923f-3484ea480596` |
| **Send (TX)** | `2d30c083-f39f-4ce6-923f-3484ea480596` |
| **Disconnect** | `2d30c084-f39f-4ce6-923f-3484ea480596` |

#### Packet Format (20 bytes total)

- **Byte 0:** Packet ID (determines data type)
- **Bytes 1-19:** Data payload

**Packet ID ranges:**
| ID Range | Type | Description |
|----------|------|-------------|
| 0-99 | 18-bit samples | Accelerometer/aux data enabled (1 byte for accel) |
| 100-199 | 19-bit samples | Full resolution, no aux data |
| 200 | Uncompressed | Raw 24-bit (4 channels, 1 sample) |
| 201-205 | Impedance | Channel 1-4 + reference impedance values |
| 206 | ASCII (partial) | Multi-packet text message |
| 207 | ASCII (final) | End of text message |

**Delta compression:** 18-bit and 19-bit modes transmit the most significant bits of 24-bit samples. Worst-case precision loss: 64 counts (0.12 uV), negligible vs environmental noise.

**Scale factor:** 0.001869917138805 uV per count. ADC range: +/-15,686 uV.

#### Commands

- `b` -- Start binary streaming (ASCII character)
- `s` -- Stop streaming
- `n` / `N` -- Enable/disable accelerometer
- `z` / `Z` -- Start/stop impedance testing

**Sampling rate:** 200 Hz internal, 100 Hz BLE transmission limit (20-byte BLE packet constraint).

### 3.4 OpenBCI Cyton Protocol (NOT BLE)

**Device:** OpenBCI Cyton (8-channel, ADS1299)
**Protocol:** Serial at 115200 baud (8-N-1) via RFDuino USB dongle. The RFDuino does NOT use standard BLE GATT -- it uses a proprietary Nordic Gazelle radio link.

#### Binary Packet Format (33 bytes)

| Byte(s) | Content | Encoding |
|---------|---------|----------|
| 1 | Start byte | `0xA0` |
| 2 | Sample number | 0-255 (unsigned 8-bit) |
| 3-26 | 8 EEG channels | 24-bit signed two's complement, MSB first, 3 bytes each |
| 27-32 | Auxiliary data | Format determined by stop byte |
| 33 | Stop byte | `0xCX` (X = 0-F, determines aux format) |

**Stop byte interpretation:**
- `0xC0` -- Accelerometer data (AX1,AX0, AY1,AY0, AZ1,AZ0)
- `0xC1` -- Raw auxiliary
- `0xC3`/`0xC4` -- Timestamped + accelerometer
- `0xC5`/`0xC6` -- Timestamped + raw auxiliary

**Scale factor:** `4.5V / gain / (2^23 - 1)`. At default 24x gain: **0.02235 uV/count**.
**Accelerometer scale:** `0.002 / 2^4` (assumes 4G range).

**Commands:** `b` (start), `s` (stop), `v` (initialize/identify).
**Sample rate:** 250 Hz default.

### 3.5 Emotiv Protocol (Encrypted)

**Devices:** EPOC, EPOC+, EPOC X, Insight, MN8
**Protocol status:** Encrypted. Reverse-engineered for older models (pre-2016). Newer models require Cortex API.

#### Encryption Details (EPOC/EPOC+, pre-2016)

- **Method:** AES-128 in ECB mode (significant weakness -- ECB provides no diffusion)
- **Key derivation:** 128-bit key derived from the 16-character USB dongle serial number (format: `SNxxxxxxxxYYYY`). Only the last 4 characters are used. Different byte ordering for consumer vs research models.
- **USB HID:** Dongle encrypts incoming wireless data before emitting as 32-byte HID reports at 128 Hz.
- **Packet format:** 32 bytes (256 bits):
  - Bits 0-7: Counter/battery (high bit = battery packet)
  - 14 EEG channels at 14-bit resolution: F3, FC5, AF3, F7, T7, P7, O1, O2, P8, T8, F8, AF4, FC6, F4
  - 8-bit gyroscope X and Y
  - Rotating contact quality data
- **Open-source driver:** emokit (https://github.com/openyou/emokit) -- supports EPOC/EPOC+ pre-2016 only

#### Cortex API (Official, Current)

- **Protocol:** WebSocket + JSON
- **Authentication:** Requires registered App ID and OAuth-style token flow
- **Available streams:** eeg, mot (motion), dev (device info), eq (EEG quality), pow (band power), met (performance metrics), com (mental commands), fac (facial expressions), sys (system events)
- **Raw EEG access:** Requires paid Developer API license for professional devices (EPOC X, EPOC Flex). Consumer devices (Insight, MN8) include raw EEG access.
- **BrainFlow support:** Board ID not in the standard BrainFlow list. Emotiv's own ecosystem is walled.
- **LSL support:** Via EmotivPRO application (vendor-provided)

**Legal note:** Emotiv has historically been hostile to reverse engineering. The emokit project received legal pressure. Official API is the only sanctioned path for newer devices.

### 3.6 NeuroSky ThinkGear Protocol

**Devices:** MindWave, MindWave Mobile 2, and any device using TGAM/TGAT chip (including Macrotellect BrainLink Lite)
**Protocol status:** Fully documented by manufacturer

#### Connection

- **Transport:** Classic Bluetooth SPP (Serial Port Profile) at 57600 baud, NOT BLE
- **On-chip processing:** TGAM ASIC performs all EEG processing on-chip (FFT, eSense algorithms)

#### ThinkGear Packet Format

```
[0xAA] [0xAA] [PLENGTH] [PAYLOAD...] [CHECKSUM]
```

- **Sync bytes:** `0xAA 0xAA`
- **Payload length:** 1 byte (0-169)
- **Checksum:** `~(sum of payload bytes) & 0xFF`

**DataRow format within payload:**
```
[EXCODE...] [CODE] ([VLENGTH]) [VALUE...]
```

**Key data codes:**

| Code | Type | Size | Description |
|------|------|------|-------------|
| 0x02 | POOR_SIGNAL | 1 byte | Signal quality (0=good, 200=no contact) |
| 0x04 | ATTENTION | 1 byte | eSense attention meter (0-100) |
| 0x05 | MEDITATION | 1 byte | eSense meditation meter (0-100) |
| 0x80 | RAW_WAVE | 2 bytes | Signed 16-bit raw EEG at 512 Hz |
| 0x83 | ASIC_EEG_POWER | 24 bytes | 8 band powers (3 bytes unsigned each) |

**EEG power bands (in order):** delta (0.5-2.75 Hz), theta (3.5-6.75 Hz), low-alpha (7.5-9.25 Hz), high-alpha (10-11.75 Hz), low-beta (13-16.75 Hz), high-beta (18-29.75 Hz), low-gamma (31-39.75 Hz), mid-gamma (41-49.75 Hz).

**Baud rate requirements:** Raw 16-bit wave needs minimum 57600 baud. On-chip processed data works at 9600 baud.

**BrainFlow support:** Not directly listed. NeuroSky devices are simple enough to connect via serial.
**LSL support:** Not listed (no vendor or third-party adapter found).

### 3.7 Neurosity Crown Protocol

**Device:** Crown (8-channel, 256 Hz, dry Ag/AgCl electrodes)
**Protocol status:** Proprietary but with official SDK

#### Connection

- **Primary:** WiFi via Neurosity cloud servers (default)
- **Secondary:** Bluetooth (Web and React Native only, available since Neurosity OS v16)
- **OSC output:** Supported for raw EEG at 256 Hz via `startPerformMode()`

#### SDK Access

- **JavaScript SDK:** Web and React Native (official)
- **Python SDK:** Beta (official)
- **Data streams:** Raw brainwaves, signal quality, focus, calm, kinesis (WiFi only), haptics
- **Streaming strategies:** `wifi-only`, `wifi-with-bluetooth-fallback`, `bluetooth-with-wifi-fallback`

**BrainFlow support:** Board IDs 13 (Notion 1), 14 (Notion 2), 23 (Crown). Connects via WiFi/Cloud.
**LSL support:** Neurosity Notion listed as native LSL support. OSC can bridge to LSL.

**Limitation:** All WiFi streaming goes through Neurosity cloud servers. No direct local connection documented for WiFi mode. Bluetooth mode allows offline/local use.

### 3.8 Other Notable Devices

#### g.tec Unicorn Hybrid Black
- **Channels:** 8 EEG + 3 accel + 3 gyro | **Sample rate:** 250 Hz, 24-bit
- **Connection:** BLE (with included Bluetooth dongle)
- **SDK:** Unicorn C API, .NET API, Python API (Windows-only software suite)
- **BrainFlow:** Board ID 8 (UNICORN_BOARD)
- **LSL:** Via UnicornLSL application (vendor-provided)
- **Price:** ~$650

#### BrainBit (NeuroMD)
- **Channels:** 4 EEG (O1, O2, T3, T4) | **Sample rate:** 250 Hz
- **Connection:** BLE
- **SDK:** NeuroMD SDK (free, multi-platform)
- **BrainFlow:** Board IDs 7 (BRAINBIT_BOARD), 18 (BRAINBIT_BLED_BOARD)
- **LSL:** Not directly listed

#### Mentalab Explore
- **Channels:** 4 or 8 | **Sample rate:** Up to 1000 Hz
- **Connection:** Bluetooth Classic
- **SDK:** explorepy (open source Python API), pushes to LSL natively
- **BrainFlow:** Board IDs 44 (4-ch), 45 (8-ch)
- **LSL:** Native via explorepy

#### PiEEG (HackerBCI)
- **Channels:** 8 (ADS1299) | **Sample rate:** 250-16000 SPS
- **Connection:** SPI over Raspberry Pi 40-pin GPIO header
- **SDK:** Open source Python, C, C++ drivers (GPL v3.0)
- **BrainFlow:** Board ID 40 (PIEEG_BOARD)
- **LSL:** Not directly listed
- **Compatibility:** Raspberry Pi 3, 4, 5

#### FreeEEG32 (NeuroIDSS)
- **Channels:** 32 (4x AD7771) | **Sample rate:** Up to 128 kSPS
- **Connection:** USB Serial at 921600 baud (STM32H7 Cortex-M7)
- **Data format:** Mimics OpenBCI stacked output format, scaled for 32 channels
- **BrainFlow:** Board ID 17 (FREEEEG32_BOARD)
- **LSL:** Via OpenViBE integration
- **License:** AGPL
- **Status:** Final shipment completed, project winding down

#### Macrotellect BrainLink
- **Chip:** NeuroSky TGAM (same as MindWave)
- **BrainLink Lite:** Compatible with NeuroSky ThinkGear protocol, third-party software works
- **BrainLink Pro:** NOT compatible with NeuroSky/third-party software (different protocol)
- **BrainFlow:** Not listed
- **LSL:** Not listed

---

## 4. Open Standards and Data Formats

### 4.1 IEEE 11073 (Health Device Communication)

IEEE 11073-10101 defines nomenclature for point-of-care medical device communication. It includes neurology-related measurement codes in its taxonomy. However:

- **No BLE profile for EEG exists** in the Bluetooth SIG specifications
- **No EEG-specific Personal Health Device (PHD) standard** has been adopted
- IEEE 11073-20601 defines a transport protocol used by BLE's Generic Health Sensor profile, but no EEG device implements it
- The standard is oriented toward vital signs (ECG, SpO2, blood pressure), not EEG

**Bottom line:** IEEE 11073 is not relevant to consumer EEG integration today. Every device uses proprietary protocols.

### 4.2 EDF/EDF+ (European Data Format)

**Specification:** https://www.edfplus.info/specs/edf.html
**Status:** De facto standard for EEG file storage. Universally supported.

**Structure:**
- **Header record:** 256 + (ns * 256) bytes. Contains patient ID, recording date, signal descriptions, sampling rates, physical/digital min/max, number of signals.
- **Data records:** Fixed-duration blocks. Each signal stored as consecutive 16-bit signed integers.
- **EDF+ extension (2003):** Adds discontinuous recording support, UTF-8 annotations, event markers.

**Key fields per signal:**
- Physical minimum/maximum (e.g., -500 to 500 uV)
- Digital minimum/maximum (e.g., -32768 to 32767)
- Scale factor derived from physical/digital range mapping

**Supported by:** MNE-Python, EEGLAB, FieldTrip, BrainVision, virtually all EEG software.
**Limitation:** 16-bit resolution per sample. BDF+ variant provides 24-bit.

### 4.3 GDF (General Data Format)

**Specification:** Schloegl (2006), https://arxiv.org/pdf/cs/0608052
**Purpose:** Designed to overcome EDF limitations and unify biosignal formats.

**Improvements over EDF:**
- Supports multiple data types (float, int8-64, etc.)
- Built-in event/marker table
- Better handling of multi-rate signals
- Single-pass readable
- Used extensively in BCI research (BCI Competition datasets)

**Supported by:** BioSig (MATLAB/Octave), MNE-Python, BCI2000.

### 4.4 XDF (Extensible Data Format)

**Specification:** https://github.com/sccn/xdf/wiki/Specifications
**Purpose:** LSL's native recording format. Designed for synchronized multimodal data.

**File structure:**

```
[XDF:] magic bytes (4 bytes)
[Chunk] [Chunk] [Chunk] ...
```

**Chunk types:**

| Tag | Type | Purpose |
|-----|------|---------|
| 1 | FileHeader | Required first chunk. XML with version. |
| 2 | StreamHeader | One per stream. StreamID + XML metadata (channel count, sample rate, format). |
| 3 | Samples | Data samples. StreamID + array of timestamped multi-channel samples. |
| 4 | ClockOffset | Time sync. StreamID + collection time + offset in seconds. |
| 5 | Boundary | Seek markers (fixed 16-byte UUID). |
| 6 | StreamFooter | Stream closure. StreamID + computed stats. |

**Binary encoding:** Little-endian. Variable-length integers (1, 4, or 8 bytes). Timestamps as 8-byte doubles. Strings as UTF-8.

**Supported channel formats:** int8, int16, int32, int64, float32, double64, string.

**Key advantage:** Natively multimodal. A single XDF file can contain time-synchronized EEG + eye tracking + motion capture + event markers from different devices.

### 4.5 BIDS (Brain Imaging Data Structure) for EEG

**Specification:** https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html
**Paper:** Pernet et al. (2019) "EEG-BIDS, an extension to the brain imaging data structure for electroencephalography" (Scientific Data)

BIDS is not a data format -- it is a **directory structure and metadata convention** for organizing neuroscience datasets.

**Required data formats for EEG-BIDS:**
- EDF (recommended)
- BrainVision (.vhdr/.vmrk/.eeg) (recommended)
- EEGLAB (.set/.fdt) (accepted)
- BDF (.bdf) (accepted)

**Required metadata files:**
- `*_eeg.json` -- Recording parameters, hardware info, filter settings
- `*_channels.tsv` -- Channel names, types, units, status
- `*_electrodes.tsv` -- 3D electrode positions
- `*_coordsystem.json` -- Coordinate frame specification
- `*_events.tsv` -- Event markers with onset, duration, type

**BIDS directory structure:**
```
dataset/
  sub-01/
    ses-01/
      eeg/
        sub-01_ses-01_task-rest_eeg.edf
        sub-01_ses-01_task-rest_eeg.json
        sub-01_ses-01_task-rest_channels.tsv
        sub-01_ses-01_task-rest_electrodes.tsv
        sub-01_ses-01_task-rest_events.tsv
```

**Relevance to Lucid:** BIDS compliance makes Lucid session data immediately shareable and usable by the research community. MNE-Python has built-in BIDS read/write via `mne-bids`.

### 4.6 Emerging Standards for Real-Time BCI Streaming

No formal standard exists for real-time BCI data streaming. The closest candidates:

1. **LSL** -- The de facto standard for real-time synchronized streaming in research. Not formally standardized by any standards body.
2. **BrainFlow data format** -- 2D array with standardized row indices (timestamp, EEG channels, accel, gyro, etc.). Not a formal standard.
3. **WebTransport/WebSocket** -- For browser-based BCI. No EEG-specific standard.
4. **OSC (Open Sound Control)** -- Used by Neurosity and some neurofeedback tools. UDP-based, low-latency, but no EEG-specific schema.

---

## 5. Commercial Device Protocol Reference

### 5.1 Device Accessibility Summary

| Device | Price | Channels | Protocol | Documented? | BrainFlow? | LSL? | Third-Party Access |
|--------|-------|----------|----------|-------------|------------|------|-------------------|
| **Muse 2** | $250 | 4 EEG + PPG + IMU | BLE GATT (proprietary) | Reverse-engineered, well-documented | Yes (ID 22) | Yes (muse-lsl, BlueMuse) | Excellent -- multiple open-source libs |
| **Muse S** | $400 | 4 EEG + PPG + IMU | BLE GATT (proprietary) | Reverse-engineered | Yes (ID 21) | Yes (muse-lsl, BlueMuse) | Excellent -- amused-py for full protocol |
| **Muse S Athena** | $475 | 4 EEG + fNIRS + PPG | BLE GATT (proprietary) | Partially reverse-engineered | Likely (via Muse S) | Via muse-lsl | Good but fNIRS may be locked |
| **OpenBCI Cyton** | $1,249 | 8 (16 w/Daisy) | Serial via RFDuino dongle | Fully documented (open source) | Yes (ID 0) | Yes (native) | Excellent -- fully open |
| **OpenBCI Ganglion** | ~$200 | 4 | BLE GATT (open) | Fully documented (open source) | Yes (ID 1) | Yes (native) | Excellent -- fully open |
| **Emotiv Insight** | $499 | 5 | Encrypted wireless | Cortex API documented | No (not in BrainFlow) | Yes (via EmotivPRO) | Restricted -- API requires registration, raw EEG included for consumer devices |
| **Emotiv EPOC X** | $999 | 14 | Encrypted wireless | Cortex API documented | No (not in BrainFlow) | Yes (via EmotivPRO) | Restricted -- raw EEG requires paid license |
| **Emotiv MN8** | $399 | 2 | Encrypted wireless | Cortex API documented | No | Yes (via EmotivPRO) | Restricted |
| **NeuroSky MindWave** | $130 | 1 | Bluetooth SPP (ThinkGear) | Fully documented | No (simple serial) | No adapter found | Good -- open protocol, trivial to implement |
| **Neurosity Crown** | ~$1,000 | 8 | WiFi (cloud) + BLE | SDK documented | Yes (ID 23) | Yes (via Neurosity software) | Good -- official SDK, but cloud-dependent on WiFi |
| **g.tec Unicorn** | ~$650 | 8 | BLE (dongle) | SDK documented | Yes (ID 8) | Yes (UnicornLSL) | Good -- vendor SDKs, Windows-centric |
| **BrainBit** | ~$300 | 4 | BLE | SDK documented | Yes (ID 7, 18) | Not directly | Good -- free SDK |
| **Mentalab Explore** | ~$1,500 | 4-8 | Bluetooth Classic | SDK documented | Yes (ID 44, 45) | Yes (native via explorepy) | Excellent -- open source API |
| **FreeEEG32** | ~$300 | 32 | USB Serial | Open source firmware | Yes (ID 17) | Via OpenViBE | Good -- fully open, but project winding down |
| **PiEEG** | ~$350 | 8 | SPI (Raspberry Pi GPIO) | Open source drivers | Yes (ID 40) | Not directly | Excellent -- fully open (GPL) |
| **Macrotellect BrainLink Lite** | ~$100 | 1 | Bluetooth SPP (ThinkGear) | Documented (uses TGAM) | No | No | Good (Lite only) -- uses NeuroSky protocol |
| **Macrotellect BrainLink Pro** | ~$200 | 1 | Proprietary Bluetooth | Not documented | No | No | Poor -- incompatible with third-party software |

### 5.2 Legal and Licensing Considerations

**Fully open (no restrictions):**
- OpenBCI (all products) -- MIT/open-source hardware
- PiEEG -- GPL v3.0
- FreeEEG32 -- AGPL
- BrainBit -- Free SDK

**Community reverse-engineered (gray area):**
- Muse -- InteraXon does not officially support third-party access but has not enforced against community tools (muse-lsl, BlueMuse, BrainFlow). Wide academic use. Effectively tolerated.
- NeuroSky -- Protocol is officially documented by manufacturer. Third-party use explicitly supported.

**Restricted/licensed:**
- Emotiv -- Official Cortex API requires app registration. Raw EEG for EPOC X/Flex requires paid Developer license. Historical legal pressure against emokit project. Older EPOC/EPOC+ encryption broken (emokit) but Emotiv disapproves.
- Neurosity -- Cloud-mediated access. Requires Neurosity account and device ownership. BrainFlow integration exists but routes through cloud.
- g.tec -- Vendor SDK is provided with device purchase. No independent reverse engineering needed.

---

## 6. Practical Integration Path for Lucid

### 6.1 Recommended Architecture

```
                    +-----------------------+
                    |    Lucid Server        |
                    |    (FastAPI/Python)    |
                    +-----------+-----------+
                                |
                    +-----------+-----------+
                    |  Device Abstraction   |
                    |       Layer           |
                    +--+------+------+-----+
                       |      |      |
              +--------+  +---+---+  +--------+
              |BrainFlow|  |  LSL  |  | Direct |
              | Bridge  |  | Bridge|  |  BLE   |
              +----+----+  +---+---+  +----+---+
                   |           |           |
              Any BrainFlow  Any LSL    Muse 2/S
              device (50+)   stream     (via bleak)
```

**Three integration tiers:**

1. **BrainFlow bridge** -- Covers 50+ device configurations out of the box. Fastest path to broad compatibility.
2. **LSL bridge** -- Covers 60+ devices including research-grade systems. Enables multi-device synchronization.
3. **Direct BLE** -- For Muse 2/S, the most popular consumer device. Avoids external dependencies.

### 6.2 Priority Device Integration Order

Based on installed base, price, protocol openness, and BrainFlow/LSL support:

**Tier 1 -- Integrate immediately (largest user base, lowest barrier):**

1. **Muse 2 / Muse S** -- Most popular consumer EEG. BrainFlow Board IDs 21-22 (native BLE, no dongle). Also accessible via muse-lsl/BlueMuse. Direct BLE via bleak is well-documented. ~$250-400.
2. **OpenBCI Cyton/Ganglion** -- Most popular open-source EEG. BrainFlow Board IDs 0-6. Fully documented open protocol. ~$200-1,249.
3. **Synthetic Board** -- BrainFlow Board ID -1. Zero hardware needed. Essential for development and testing.

**Tier 2 -- Add via BrainFlow (broad coverage, single integration):**

4. **BrainFlow generic integration** -- A single BrainFlow bridge covers Neurosity Crown (ID 23), g.tec Unicorn (ID 8), BrainBit (ID 7/18), Mentalab Explore (ID 44/45), PiEEG (ID 40), FreeEEG32 (ID 17), EmotiBit (ID 46), and all OpenBCI variants.

**Tier 3 -- Add via LSL (research compatibility):**

5. **LSL inlet** -- A single LSL bridge covers everything in Tier 2 plus Brain Products, ANT Neuro, BioSemi, Cognionics, Emotiv (via EmotivPRO), and all other research-grade systems.

**Tier 4 -- Device-specific (if demand warrants):**

6. **NeuroSky MindWave** -- Simple serial protocol, trivial to implement directly if BrainFlow support is not added. The ThinkGear protocol is ~200 lines of code to parse.
7. **Emotiv Cortex API** -- WebSocket + JSON. Only needed if Lucid users specifically need Emotiv and cannot use EmotivPRO's LSL output.

### 6.3 Minimum Implementation Plan

**Phase 1: BrainFlow integration (covers 50+ devices immediately)**

```python
# server/lucid_server/services/acquisition.py
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

class BrainFlowAcquisition:
    def __init__(self, board_id: int, params: dict):
        self.params = BrainFlowInputParams()
        for key, value in params.items():
            setattr(self.params, key, value)
        self.board = BoardShim(board_id, self.params)

    async def start(self):
        self.board.prepare_session()
        self.board.start_stream()

    async def get_data(self, num_samples: int = 256):
        return self.board.get_current_board_data(num_samples)

    async def stop(self):
        self.board.stop_stream()
        self.board.release_session()
```

**Phase 2: LSL inlet (covers research devices)**

```python
# server/lucid_server/services/lsl_acquisition.py
from pylsl import StreamInlet, resolve_stream

class LSLAcquisition:
    def __init__(self, stream_type: str = "EEG"):
        streams = resolve_stream("type", stream_type)
        self.inlet = StreamInlet(streams[0])

    async def get_data(self):
        chunk, timestamps = self.inlet.pull_chunk()
        return chunk, timestamps
```

**Phase 3: Direct Muse BLE (for best consumer experience)**

Use the `bleak` Python library to connect directly to Muse 2/S via BLE GATT using the UUIDs documented in Section 3.2. This removes the BrainFlow/LSL dependency for the most common consumer device.

### 6.4 Data Format Strategy

**Recording:** Save to EDF+ (universal compatibility) and optionally XDF (for LSL multi-stream sessions).

**Export:** Support BIDS-compliant directory structure for research users (via `mne-bids`).

**Internal streaming:** Use the existing Lucid WebTransport/WebSocket protocol. Normalize all incoming data (BrainFlow, LSL, direct BLE) to a common internal format before pipeline processing.

### 6.5 Key Dependencies

| Package | Purpose | License |
|---------|---------|---------|
| `brainflow` | Device abstraction (50+ devices) | MIT |
| `pylsl` or `mne-lsl` | LSL stream ingestion | MIT |
| `bleak` | Direct BLE for Muse | MIT |
| `pyedflib` | EDF/EDF+ read/write | BSD |
| `mne-bids` | BIDS-compliant export | BSD-3 |
| `pyxdf` | XDF file reading | BSD |

All MIT/BSD licensed -- no copyleft contamination of Lucid's MIT license.

---

## Sources

### BrainFlow
- [BrainFlow Supported Boards](https://brainflow.readthedocs.io/en/stable/SupportedBoards.html)
- [BrainFlow Developer Docs](https://brainflow.readthedocs.io/en/stable/BrainFlowDev.html)
- [BrainFlow Adding New Boards Guide](https://brainflow.org/2022-11-01-adding-new-boards/)
- [BrainFlow GitHub](https://github.com/brainflow-dev/brainflow)
- [BrainFlow Code Examples](https://brainflow.readthedocs.io/en/stable/Examples.html)

### Lab Streaming Layer
- [LSL Introduction](https://labstreaminglayer.readthedocs.io/info/intro.html)
- [LSL Supported Devices](https://labstreaminglayer.readthedocs.io/info/supported_devices.html)
- [LSL Reference Paper (Kothe et al. 2025)](https://direct.mit.edu/imag/article/doi/10.1162/IMAG.a.136/132678/)
- [XDF Specification](https://github.com/sccn/xdf/wiki/Specifications)
- [LabRecorder](https://github.com/labstreaminglayer/App-LabRecorder)
- [MNE-LSL](https://mne.tools/mne-lsl/stable/)

### Muse Protocol
- [muse-js (Web Bluetooth)](https://github.com/urish/muse-js)
- [muse-lsl](https://github.com/alexandrebarachant/muse-lsl)
- [BlueMuse (Windows LSL)](https://github.com/kowalej/BlueMuse)
- [amused-py (Muse S BLE protocol)](https://github.com/Amused-EEG/amused-py)
- [Muse BLE Protocol Reverse Engineering](https://alexandre.barachant.org/blog/2017/01/27/reverse-engineering-muse-eeg-headband-bluetooth-protocol.html)

### OpenBCI Protocol
- [Cyton Data Format](https://docs.openbci.com/Cyton/CytonDataFormat/)
- [Cyton SDK Commands](https://docs.openbci.com/Cyton/CytonSDK/)
- [Ganglion Data Format](https://docs.openbci.com/Ganglion/GanglionDataFormat/)
- [Ganglion SDK Commands](https://docs.openbci.com/Ganglion/GanglionSDK/)

### Emotiv Protocol
- [Emotiv Cortex API](https://emotiv.gitbook.io/cortex-api)
- [Emotiv Data Subscription](https://emotiv.gitbook.io/cortex-api/data-subscription)
- [emokit Protocol Documentation](https://github.com/openyou/emokit/blob/master/doc/emotiv_protocol.asciidoc)
- [Emotiv Developer Portal](https://www.emotiv.com/pages/developer)
- [Emotiv EPOC+ Reverse Engineering](https://mindgardenai.com/blog/2024-12-12-emotiv-data-reader/)

### NeuroSky Protocol
- [ThinkGear Communications Protocol](https://developer.neurosky.com/docs/doku.php?id=thinkgear_communications_protocol)
- [ThinkGear Serial Stream Guide](https://cdn.hackaday.io/files/11146476870464/ThinkGearSerialStreamGuide.pdf)
- [TGAM Datasheet](https://cdn.hackaday.io/files/11146476870464/TGAM%20Datasheet.pdf)

### Neurosity
- [Neurosity SDK Overview](https://docs.neurosity.co/docs/overview/)
- [Neurosity Streaming (WiFi/BLE)](https://docs.neurosity.co/docs/api/streaming/)
- [Neurosity OSC Support](https://docs.neurosity.co/docs/api/osc/)
- [Neurosity Python SDK](https://github.com/neurosity/neurosity-sdk-python)

### Other Devices
- [g.tec Unicorn Hybrid Black](https://www.gtec.at/product/unicorn-hybrid-black/)
- [BrainBit Store/SDK](https://store.brainbit.com/products/brainbit-sdk)
- [Mentalab Explore BrainFlow Integration](https://wiki.mentalab.com/integrations/interfaces/brainflow/)
- [PiEEG Crowd Supply](https://www.crowdsupply.com/hackerbci/pieeg)
- [FreeEEG32](https://www.crowdsupply.com/neuroidss/freeeeg32)

### Data Formats and Standards
- [EDF Specification](https://www.edfplus.info/specs/edf.html)
- [GDF Specification (Schloegl)](https://arxiv.org/pdf/cs/0608052)
- [BIDS EEG Specification](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html)
- [EEG-BIDS Paper (Pernet et al. 2019)](https://www.nature.com/articles/s41597-019-0104-8)
- [IEEE 11073-10101 Nomenclature](https://standards.ieee.org/ieee/11073-10101/5034/)
