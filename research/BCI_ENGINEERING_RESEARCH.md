# Lucid BCI Platform -- Engineering Research Report
**Date: 2026-03-26**

This document covers system engineering, platform architecture, and practical aspects of building a complete brain-computer interface system for the Lucid open-source BCI platform. It complements `BCI_EEG_LANDSCAPE.md` (which covers the hardware/software ecosystem) with deep technical details on implementation.

---

## 1. BCI System Architecture -- Best Practices

### 1.1 End-to-End Pipeline

The canonical BCI data flow is:

```
Electrodes -> Analog Front End (ADS1299) -> SPI -> MCU (ESP32-S3)
  -> Wireless (WiFi/BLE) -> Host Computer -> Processing Pipeline
  -> Application (Neurofeedback / BCI Control / Visualization)
```

Each stage introduces latency, noise, and potential failure modes. The system design must budget and minimize delay at every stage.

**Key references:**
- Chen (2025), "Brain-computer interfaces in 2023-2024," *Brain-X*, Wiley -- comprehensive BCI review covering non-invasive and invasive approaches (https://onlinelibrary.wiley.com/doi/full/10.1002/brx2.70024)
- PMC "Advancing Brain-Computer Interface Closed-Loop Systems for Neurorehabilitation" (2025) -- systematic review of AI/ML in BCI (https://pmc.ncbi.nlm.nih.gov/articles/PMC12588595/)
- Springer Nature (2025), "Non-Invasive Brain-Computer Interfaces: Converging Frontiers" (https://link.springer.com/article/10.1007/s40820-025-02042-2)

### 1.2 Latency Budget Allocation

Based on the NeuroBand engineering course and BCI literature, here is a representative latency budget for a 1-second analysis window system:

| Pipeline Stage | Time Budget | Notes |
|---|---|---|
| Signal Acquisition + Buffer Fill | 1000 ms | Dominant component. Determined by analysis window length. |
| Preprocessing (Filters, ICA) | 50 ms | Bandpass, notch, artifact rejection |
| Spatial Filtering (CSP) | 20 ms | Common Spatial Patterns for motor imagery |
| Feature Classification (EEGNet/ML) | 100 ms | Neural network inference or SVM/LDA |
| Command Execution / Feedback | 30 ms | Application-layer response |
| **Total End-to-End** | **~1200 ms** | |

**Critical thresholds:**
- Users perceive latency differences as small as 50-100 ms in direct control tasks
- 85% of test subjects report diminished interest when latency exceeds 500 ms
- Chinese researchers achieved sub-100 ms system delay for invasive BCIs (2025)
- For non-invasive EEG BCIs, 1-2 seconds end-to-end is the practical minimum for most paradigms

**Optimization strategy -- Sliding Window:**
Instead of waiting for a full 1-second window before processing, use overlapping windows: analyze 1-second windows every 250 ms, generating 4 predictions/second. This reduces perceived latency from 1200 ms to ~450 ms.

**Information Transfer Rate (ITR)** is the key metric: bits/second combining accuracy and speed. A 99% accurate system taking 10 seconds per decision is worse than an 80% system taking 1 second.

**Sources:**
- NeuroBand BCI latency course (https://oboe.com/learn/engineering-neuroband-implementing-low-cost-bci-solutions-1d6cfnm/latency-and-performance-4)
- PMC, "A Procedure for Measuring Latencies in Brain-Computer Interfaces" (https://pmc.ncbi.nlm.nih.gov/articles/PMC3161621/)
- Frontiers, "Low-latency multi-threaded processing for BCIs" (https://www.frontiersin.org/journals/neuroengineering/articles/10.3389/fneng.2014.00001/full)

### 1.3 Buffering Strategies for Real-Time Processing

**Ring Buffer (Circular Buffer):**
The standard approach for continuous EEG streaming. The FieldTrip buffer is the canonical implementation -- a network-transparent TCP server that allows acquisition clients to stream data per-sample or in small blocks while processing clients read simultaneously. BrainFlow uses an internal `DataBuffer` ring buffer in C++ for the same purpose.

**Key design principles:**
- Acquisition and processing run on separate threads/processes
- A shared ring buffer decouples the two: acquisition writes at the head, processing reads from the tail
- Buffer size must accommodate the worst-case processing latency without data loss
- For 8 channels at 250 SPS x 24-bit: data rate = 48 kbps = 6 KB/s. A 10-second ring buffer = 60 KB -- trivial for any modern system.
- For 8 channels at 1000 SPS: data rate = 192 kbps = 24 KB/s. 10-second buffer = 240 KB.

**Sliding Window with Overlap:**
For spectral analysis (FFT/Welch), use overlapping windows (e.g., 1-second Hann window with 50% overlap). This provides smoother spectral estimates and more frequent updates without requiring longer data collection periods.

**Double/Triple Buffering:**
For latency-critical applications, use double buffering: while one buffer is being processed, the other is being filled. Eliminates the processing gap.

**Sources:**
- FieldTrip real-time buffer architecture (https://www.fieldtriptoolbox.org/development/realtime/buffer/)
- FieldTrip BCI getting started (https://www.fieldtriptoolbox.org/getting_started/realtime/)
- DSP Guide, Circular Buffering (http://www.dspguide.com/ch28/2.htm)

### 1.4 BrainFlow Architecture (Internal Design)

**Repository:** https://github.com/brainflow-dev/brainflow (1,600 stars, 384 forks, MIT license)

**Core architecture:**
- Written in C++ (46.6% of codebase) with C (13.5%) forming the signal processing engine
- Board abstraction: All boards inherit from a `Board` base class and implement pure virtual methods
- Data is stored in a `DataBuffer` ring buffer object
- All board data returned as a 2D array where each row represents a data channel type (timestamps, EEG, EMG, accelerometer, etc.)
- Channel layout is statically defined in `brainflow_boards.cpp` (JSON-like configuration)

**Three main modules:**
1. **BoardShim** -- Data acquisition abstraction. Handles board discovery, connection, configuration, and streaming. Board-agnostic API.
2. **DataFilter** -- Signal processing. FFT, inverse FFT, bandpass/bandstop/lowpass/highpass filters, wavelet transforms, denoising, downsampling, CSP (Common Spatial Patterns), PSD computation.
3. **MLModel** -- Machine learning. Now supports ONNX model loading directly (moved away from built-in classifiers). CSP feature vectors + ONNX inference.

**Language bindings (9 languages):**
- Python (`python_package/`), Java (`java_package/`), C++ (`cpp_package/`), C# (`csharp_package/`), MATLAB (`matlab_package/`), Julia (`julia_package/`), R (`r_package/`), Rust (`rust_package/`), Node.js/TypeScript (`nodejs_package/`)
- All bindings call the same underlying C/C++ code through FFI

**Adding a new board (integration steps):**
1. Add board ID to `BoardIds` enum in C and all language bindings
2. Add object creation to `board_controller.cpp` `prepare_session` method (factory switch)
3. Add board metadata to `brainflow_boards.cpp` (channel descriptions, sample rate, etc.)
4. Inherit from `Board` class, implement pure virtual methods
5. Store data in `DataBuffer`, reuse utilities from `utils/` folder
6. Add source files to `build.cmake`
7. Optionally develop a device emulator for CI testing
- Helpers exist for common patterns: `DynLibBoard`, `BLELibBoard` for BLE devices

**Key design insight:** Device abstraction at the C/C++ level keeps the FFI interface stable. Adding a new board requires zero changes to language bindings -- only C++ code changes.

**Sources:**
- BrainFlow developer docs (https://brainflow.readthedocs.io/en/stable/BrainFlowDev.html)
- BrainFlow adding new boards guide (https://brainflow.org/2022-11-01-adding-new-boards/)
- BrainFlow history (https://brainflow.org/2021-07-30-history/)

### 1.5 Lab Streaming Layer (LSL) Time Synchronization

**Repository:** https://github.com/sccn/labstreaminglayer (724 stars)
**Reference paper (2024):** "The lab streaming layer for synchronized multimodal recording" (https://direct.mit.edu/imag/article/doi/10.1162/IMAG.a.136/132678/)

**How LSL time synchronization works:**

LSL implements a simplified version of the NTP (Network Time Protocol) clock synchronization algorithm. The process:

1. **Timestamp assignment:** Each sample gets a timestamp from `std::chrono::steady_clock` (monotonic, high-resolution) on the sending machine.

2. **Clock offset measurement protocol:**
   - Peer A sends packet with local timestamp t0
   - Peer B records receive time t1, then sends response with t1 and send time t2
   - Peer A records final receive time t3
   - Round-trip time (RTT) = (t3 - t0) - (t2 - t1)
   - Clock offset (OFS) = ((t1 - t0) + (t2 - t3)) / 2
   - This cancels symmetric network delays

3. **NTP clock filter:** Multiple packet exchanges (e.g., 10 exchanges over 200 ms) produce a set of OFS/RTT pairs. The OFS with the lowest RTT is selected as the minimum-noise estimate.

4. **Periodic re-synchronization:** Clocks drift, so the process repeats every ~5 seconds by default.

5. **Jitter removal:** The time correction values provided by LSL allow the consumer to remap timestamps to a common clock. Jitter in the transmission is filtered out by the NTP algorithm.

**Accuracy achieved:** Sub-millisecond on a standard LAN. The timestamp resolution is at minimum 1 ms, typically better. This is more than sufficient for EEG (where temporal resolution is limited by sample rate -- 4 ms at 250 SPS).

**Architecture components:**
- **liblsl** -- Core C++ library implementing the protocol
- **Outlets** -- Data publishers (e.g., EEG device driver)
- **Inlets** -- Data consumers (e.g., recording software)
- Service discovery via UDP multicast for automatic device detection

### 1.6 RTOS vs Standard OS for BCI

**On-device (MCU firmware):**
The ESP32-S3 runs FreeRTOS natively through ESP-IDF. This provides deterministic task scheduling critical for maintaining consistent SPI communication with the ADS1299. Key advantages:
- Guaranteed task execution timing (hard real-time)
- Small memory footprint (ESP32-S3 has 512 KB SRAM)
- Priority-based preemptive scheduling
- Built-in semaphores, queues, and mutexes for inter-task communication
- The ESP32-S3's dual-core architecture allows dedicating one core to SPI/acquisition and the other to WiFi/BLE transmission

**On the host (processing computer):**
Standard Linux/macOS/Windows is sufficient for BCI processing. The reasons:
- EEG sample rates (250-1000 SPS) generate modest data rates (6-24 KB/s for 8 channels)
- Processing latency budgets are 50-100 ms -- well within standard OS scheduling granularity
- Linux with PREEMPT_RT patches can achieve sub-100 us latency if needed
- The bottleneck is the analysis window length (1000 ms), not OS scheduling

**Bottom line:** Use FreeRTOS on the MCU for deterministic acquisition; use standard OS on the host for processing and visualization. No need for RTOS on the host.

**Sources:**
- FreeRTOS fundamentals (https://www.freertos.org/Documentation/01-FreeRTOS-quick-start/01-Beginners-guide/01-RTOS-fundamentals)
- ByteSnap, FreeRTOS vs Linux comparison (https://www.bytesnap.com/news-blog/freertos-vs-linux-embedded-systems/)

### 1.7 Edge Processing vs Host vs Cloud

**Edge (on-device, ESP32-S3):**
- Pros: Lowest latency, no network dependency, privacy (data never leaves device)
- Cons: Limited compute (240 MHz dual-core, 512 KB SRAM), limited DSP library
- Suitable for: Real-time filtering (bandpass, notch), simple feature extraction (band power), data compression before wireless transmission
- ESP-DSP library provides hardware-accelerated FFT, IIR/FIR filters optimized for ESP32-S3

**Host (laptop/desktop):**
- Pros: Full compute power, rich software ecosystem (Python/MNE/BrainFlow), real-time visualization
- Cons: Requires physical proximity or reliable network to device
- Suitable for: All standard BCI processing, source localization, ICA, machine learning inference

**Cloud:**
- Pros: Unlimited compute, foundation model inference, multi-user analytics
- Cons: Latency (100+ ms network round-trip), privacy concerns, internet dependency
- Suitable for: EEG foundation model inference (LaBraM, NeuroLM), batch analysis, citizen science data aggregation, training ML models on pooled data
- NOT suitable for: Real-time feedback loops (neurofeedback, motor imagery BCI)

**Hybrid approach for Lucid:**
- Edge: Real-time filtering, impedance checking, data quality monitoring, compression
- Host: Real-time visualization, neurofeedback, BCI paradigm execution, artifact rejection
- Cloud (optional): Foundation model inference, dataset aggregation, community analytics

**Sources:**
- ArXiv, "Low-Latency Neural Inference on an Edge Device" (https://arxiv.org/pdf/2510.19832)
- ACM, "LSTM and CNN Performance in EEG Motor Imagery for Edge Computing BCI" (https://dl.acm.org/doi/10.1145/3707292.3707376)
- BrainAccess, "EEG Foundation Models" (https://www.brainaccess.ai/eeg-foundation-models-unlocking-the-next-generation-of-neurotechnology/)

---

## 2. ESP32-S3 for EEG -- Technical Feasibility

### 2.1 SPI Interface Capabilities

**ESP32-S3 SPI specifications** (from Espressif official documentation):

| Parameter | Value | Notes |
|---|---|---|
| SPI peripherals | SPI2 (HSPI), SPI3 (VSPI) | SPI0/SPI1 reserved for flash |
| Max clock (IOMUX pins) | 80 MHz | Direct hardware routing, no GPIO matrix overhead |
| Max clock (GPIO matrix) | 26 MHz | Through GPIO matrix, adds propagation delay |
| DMA channels | 5 TX + 5 RX (GDMA) | Both SPI2 and SPI3 support DMA |
| Max DMA transfer | 4092 bytes | Per transaction with DMA enabled |
| Max non-DMA transfer | 64 bytes | Without DMA, limited by SPI buffer registers |
| Transaction overhead | ~20 us (interrupt mode) | Plus 8n/Fspi[MHz] us for n bytes |
| DMA setup time | ~2 us per transaction | Linked-list DMA descriptor setup |

**ADS1299 SPI requirements:**
| Parameter | Value |
|---|---|
| Max SCLK | 20 MHz (at DVDD 2.7-3.6V) |
| SCLK idle polarity | CPOL=0, CPHA=1 (SPI Mode 1) |
| Data ready signal | DRDY pin goes low when new data available |
| Data packet size | 27 bytes per sample (3-byte status + 8 x 3-byte channels) |
| Command wait time | 4 * t_CLK (~2 us at 2.048 MHz master clock) after SDATAC |

**Feasibility assessment:**

At **250 SPS**: Each sample = 27 bytes via SPI. At 4 MHz SPI clock (conservative), transfer time = 27*8/4MHz = 54 us per sample. Sample period = 4 ms. SPI utilization = 1.35%. **Trivially feasible.** The Cerelog ESP-EEG already does this.

At **1000 SPS**: Sample period = 1 ms. SPI transfer at 4 MHz = 54 us. Utilization = 5.4%. **Easily feasible.** Even at 2 MHz SPI, it uses only ~10% of the available time.

At **16,000 SPS** (max ADS1299 rate): Sample period = 62.5 us. SPI transfer at 16 MHz = ~14 us. Utilization = 22%. **Feasible but requires careful DMA management and higher SPI clock.**

**Practical SPI clock selection:**
- Cerelog uses 16 MHz during streaming, 2 MHz for configuration (register read/write)
- IOMUX pins recommended for best signal integrity at higher speeds
- DMA essential for sustained high-rate operation (avoids CPU blocking)

**Sources:**
- ESP-IDF SPI Master documentation (https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/spi_master.html)
- ADS1299 datasheet, TI (https://www.ti.com/lit/gpn/ADS1299)
- TI E2E forum, ADS1299 clock requirements (https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/421438/clock-required-for-ads1299)

### 2.2 WiFi Streaming Performance

**ESP32-S3 WiFi characteristics for real-time EEG streaming:**

| Parameter | Value | Notes |
|---|---|---|
| WiFi standard | 802.11 b/g/n | 2.4 GHz, up to 150 Mbps PHY |
| Typical UDP latency | 1-5 ms (LAN) | Can spike to 60-200 ms under contention |
| UDP jitter | < 10 us (optimized) | Worst case: 250 ms outliers observed |
| TCP latency | 5-20 ms typical | Higher due to ACK overhead |
| Bandwidth required (8ch/250 SPS) | 48 kbps (6 KB/s) | Negligible fraction of WiFi capacity |
| Bandwidth required (8ch/1000 SPS) | 192 kbps (24 KB/s) | Still negligible |

**Key findings from ESP32 community:**
- The LWIP network stack introduces most of the jitter, not the WiFi radio itself
- UDP packets sometimes arrive in clusters (3 packets at once, then 200 ms gap) -- buffering on receiver side is essential
- With optimized zero-copy DMA paths, jitter can be reduced to < 10 us
- NTP synchronization over WiFi achieves < 1 ms accuracy using ESP32's built-in WiFi

**Practical recommendation:** Use UDP for data streaming with a sequence number and timestamp in each packet. The receiver reconstructs timing using LSL-style clock correction. WiFi is more than adequate for EEG data rates. Buffer 100-200 ms on the receiver to smooth jitter.

**Sources:**
- ESP32 Forum, "Real-time data streaming over WiFi" (https://www.esp32.com/viewtopic.php?t=13420)
- ESP-IDF GitHub, "Making UDP send latency more predictable" (https://github.com/espressif/esp-idf/issues/15345)
- Electric UI, "Benchmarking latency across wireless links" (https://electricui.com/blog/latency-comparison)

### 2.3 BLE 5.0 Throughput

| Parameter | Value |
|---|---|
| BLE 5.0 1M PHY throughput | ~700 Kbps (~90 KB/s) |
| BLE 5.0 2M PHY throughput | ~1.4 Mbps (~170 KB/s) |
| Coded PHY (long range) | 125 Kbps / 500 Kbps |
| Typical MTU | 247 bytes |
| Connection interval (min) | 7.5 ms |

**EEG bandwidth requirement:** 8 channels x 24 bits x 250 SPS = 48 kbps (6 KB/s). This is well within BLE 5.0 1M PHY capacity (700 Kbps). At 1000 SPS, the 192 kbps requirement is still comfortably within range.

**Practical considerations:**
- BLE has inherent latency from connection intervals (7.5-4000 ms configurable)
- At minimum connection interval (7.5 ms), BLE adds ~7.5 ms average latency
- BLE is more power-efficient than WiFi for continuous streaming
- BLE range: typically 10-30 meters indoors; Coded PHY extends to 240 meters at reduced throughput
- BLE is better suited for mobile/tablet host devices; WiFi better for desktop hosts

**Sources:**
- Espressif ESP32-S3 product page (https://www.espressif.com/en/products/socs/esp32-s3)
- Espressif BLE FAQ (https://docs.espressif.com/projects/esp-faq/en/latest/software-framework/bt/ble.html)
- Circuit Labs, BLE performance optimization (https://circuitlabs.net/ble-performance-optimization/)

### 2.4 Power Consumption and Battery Life

**Component power draw estimates:**

| Component | Active Mode | Sleep/Idle |
|---|---|---|
| ADS1299 (8-ch, 250 SPS) | ~6 mW (1.2 mA @ 5V) | < 1 mW (power-down) |
| ESP32-S3 (WiFi active, 240 MHz) | ~250 mW (~50 mA @ 5V) | Deep sleep: 5-10 uA |
| ESP32-S3 (BLE active, 240 MHz) | ~120 mW (~24 mA @ 5V) | Modem sleep: ~3 mA |
| ESP32-S3 (80 MHz, WiFi periodic) | ~80 mW | Reduced freq helps |
| Total (WiFi streaming) | ~260 mW | |
| Total (BLE streaming) | ~130 mW | |

**Battery life estimates (2000 mAh LiPo at 3.7V = 7.4 Wh):**
- WiFi continuous streaming: ~28 hours
- BLE continuous streaming: ~57 hours
- With optimized power management (lower CPU freq, batched WiFi transmission): 40+ hours

**Power optimization strategies:**
1. Lower CPU frequency to 80 MHz (sufficient for SPI + networking)
2. Use BLE instead of WiFi when mobile
3. Batch data and use WiFi modem sleep between transmissions
4. Disable unused peripherals and GPIOs
5. Use LDO regulators with low quiescent current

**Sources:**
- Hubble Network, "ESP32 Power Consumption: Datasheet vs Reality" (https://community.hubble.com/guides/esp32-power-consumption-datasheet-vs-reality/)
- GetZenQuery ESP32 power calculator (https://www.getzenquery.com/tools/esp32-power-consumption-calculator/)

### 2.5 Existing ESP32 + ADS1299 Projects

| Project | MCU | Status | Notes |
|---|---|---|---|
| **Cerelog ESP-EEG** | ESP32-WROOM-DA | ACTIVE (2025+) | 8-ch, ADS1299, $349.99. BrainFlow + LSL. Open source firmware + hardware. True closed-loop active bias. |
| **Meower** | ESP32-C3 | ACTIVE | Dual ADS1299 (16-ch). Real-time streaming firmware. github.com/nikki-uwu/Meower |
| **ESP32 EEG (Hackaday)** | ESP32 | Community project | Basic ADS1299 + ESP32 integration. hackaday.io/project/178007-esp32-eeg |
| **OpenBCI Forum ESP32 ports** | ESP32 | Various | Multiple community members have ported OpenBCI Ganglion firmware to ESP32 |
| **TI E2E examples** | ESP32 | Reference | Programming examples for ADS1299 + ESP32 SPI (https://e2e.ti.com/support/logic-group/logic/f/logic-forum/923651/) |

**Note:** Cerelog uses ESP32-WROOM-DA (not the S3 specifically). The S3 variant adds vector DSP instructions and more PSRAM options, making it superior for on-device processing.

**Sources:**
- Cerelog ESP-EEG (https://github.com/Cerelog-ESP-EEG/ESP-EEG)
- Hackster.io coverage (https://www.hackster.io/news/this-open-source-eeg-board-brings-real-brain-computer-interfaces-home-019e8c40e628)
- HN discussion (https://news.ycombinator.com/item?id=46502051)

### 2.6 ESP32-S3 On-Device DSP

**ESP-DSP Library** (https://github.com/espressif/esp-dsp):

Espressif's official DSP library provides hardware-accelerated signal processing:

| Capability | Details |
|---|---|
| FFT | Real and complex FFT, hardware-accelerated on ESP32-S3 |
| IIR filters | Biquad cascades (bandpass, notch, lowpass, highpass) |
| FIR filters | Arbitrary-length FIR filter |
| Dot product | SIMD-optimized vector operations |
| Matrix operations | Optimized matrix multiplication |
| Kalman filter | State estimation |
| Data types | 32-bit float, 16-bit signed integer |

**ESP32-S3 specific advantages over base ESP32:**
- Hardware vector instructions for DSP (PIE -- Processor Instruction Extension)
- Significantly faster FFT and filter execution than generic C implementations
- Assembly-optimized implementations for critical paths

**Feasibility for real-time EEG filtering:**
- At 250 SPS, the processing budget per sample is 4 ms (4,000 us)
- A 256-point FFT on ESP32-S3 takes < 100 us with esp-dsp
- An 8-channel biquad IIR filter (bandpass + notch) takes < 10 us per sample
- Conclusion: **ESP32-S3 can easily perform real-time filtering on all 8 channels before transmission**

**Practical on-device processing pipeline:**
1. Read ADS1299 via SPI (DMA)
2. Apply notch filter (50/60 Hz rejection)
3. Apply bandpass filter (0.5-100 Hz)
4. Compute impedance check (if requested)
5. Pack data into WiFi/BLE packet with timestamp
6. Transmit

**Sources:**
- ESP-DSP library (https://github.com/espressif/esp-dsp)
- ESP-DSP API reference (https://docs.espressif.com/projects/esp-dsp/en/latest/esp32/index.html)
- ESP-DSP examples (https://docs.espressif.com/projects/esp-dsp/en/latest/esp32/esp-dsp-examples.html)

### 2.7 Flash/RAM Requirements

**ESP32-S3 memory options:**

| Memory Type | Size | Notes |
|---|---|---|
| Internal SRAM | 512 KB | Shared between IRAM (instruction) and DRAM (data) |
| External PSRAM | 2-8 MB typical | Quad or Octal SPI, ~10-40 MHz effective |
| Flash | 4-16 MB typical | Code storage, SPIFFS/LittleFS |

**Firmware size estimates:**
- ESP-IDF base framework: ~200 KB flash, ~50 KB RAM
- WiFi stack: ~100 KB flash, ~40 KB RAM
- BLE stack: ~200 KB flash, ~60 KB RAM
- SPI driver + ADS1299 code: ~20 KB flash, ~5 KB RAM
- ESP-DSP filters: ~30 KB flash, ~10 KB RAM
- Ring buffer (10s @ 8ch @ 1000 SPS): ~240 KB RAM
- Total estimate: ~550 KB flash, ~165 KB RAM (WiFi mode)

**Conclusion:** An ESP32-S3 module with 4 MB flash and 2 MB PSRAM is more than sufficient. A module with 8 MB PSRAM would allow larger ring buffers and potential ML inference on-device.

**Sources:**
- ESP-IDF memory types documentation (https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/memory-types.html)
- ESP32-S3 datasheet (https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)

### 2.8 Arduino Framework vs ESP-IDF

| Aspect | Arduino Framework | ESP-IDF (Native) |
|---|---|---|
| Ease of development | High -- familiar API, vast library ecosystem | Medium -- steeper learning curve, richer API |
| Performance | Good for most uses | Up to 40% smaller binaries, potentially faster |
| FreeRTOS access | Limited (single-loop abstraction) | Full native FreeRTOS with task priorities, queues |
| SPI DMA control | Through libraries (limited) | Full DMA configuration control |
| WiFi/BLE control | Simplified API | Full control over PHY, connection parameters |
| DSP library | Can use esp-dsp as component | Native esp-dsp integration |
| Build system | PlatformIO or Arduino IDE | CMake-based, professional toolchain |
| BrainFlow firmware examples | Arduino style exists | More common for production firmware |
| OTA updates | Supported | Full partition table control |

**Recommendation for Lucid:** Start with **ESP-IDF**. The EEG acquisition firmware needs:
- Precise DMA-driven SPI timing
- FreeRTOS task prioritization (SPI acquisition on core 0, WiFi/BLE on core 1)
- Fine-grained WiFi/BLE parameter control for latency optimization
- esp-dsp integration for on-device filtering

Arduino is acceptable for rapid prototyping but ESP-IDF is the right choice for production firmware. PlatformIO can bridge the gap by using ESP-IDF framework with Arduino-compatible libraries.

**Sources:**
- Arduino Forum, "ESP-IDF vs Arduino framework performance" (https://forum.arduino.cc/t/espidf-vs-arduino-framework-performance/1137510)
- espboards.dev comparison (https://www.espboards.dev/blog/esp-idf-vs-arduino-core/)

---

## 3. Web-Based EEG Visualization -- Existing Work

### 3.1 Existing Web EEG Libraries and Projects

| Project | Technology | Stars | Status | Description |
|---|---|---|---|---|
| **muse-js** | TypeScript | Active (2024) | Web Bluetooth API to stream raw EEG from Muse 2016 headset directly in browser |
| **eegpwa** | JS/WebWorkers | Community | Progressive Web App for browser-based EEG processing. GPU.js FFT with web workers for real-time DSP. |
| **EEG-101** | React Native | NeuroTechX | Interactive neuroscience tutorial using Muse. Includes real-time visualization and binary classifier. |
| **angular-muse** | Angular/RxJS | Community | EEG data visualization + head orientation from Muse headset |
| **OpenEXP** | JS/Browser | Research | Open-source browser-based experiment runner for collecting EEG data with OpenBCI |
| **eeg-brainwave-tutorial-demo** | Web | Community | Real-time animated EEG visualization with accurate waveform rendering for 5 brainwave types |
| **BrainWave** | Vue.js/Flask | Community | EEG visualizer + predictor with web frontend (github.com/malikshahzaib7238/BrainWave) |

**Key insight:** There is NO comprehensive, production-quality, React/TypeScript-based EEG dashboard that handles real-time multi-channel visualization, FFT, and BCI features. This is a major gap.

**Sources:**
- GitHub EEG topics (https://github.com/topics/eeg?l=javascript)
- NeuroJS organization (https://github.com/NeuroJS)
- muse-js (https://github.com/joshbrew/eegpwa)

### 3.2 Real-Time Charting Libraries -- Performance Comparison

| Library | Technology | Max Data Points | FPS | Cost | EEG Suitability |
|---|---|---|---|---|---|
| **LightningChart JS** | WebGL | 8 billion (tested) | 60 FPS @ 400 channels | Commercial ($790+) | Best performance. Handles 400 EEG channels at 1000 Hz. |
| **webgl-plot** | WebGL (native) | Canvas-width limited | 60 FPS | Free (MIT) | Good for oscilloscope-style display. 656 stars. Used in Arduino/FPGA UIs. Thick lines 6x slower. |
| **Plotly.js** | SVG/Canvas/WebGL | Millions (scattergl) | 20 Hz max stream rate | Free (MIT) | Already used in EarthSync. Supports WebGL traces (scattergl, heatmapgl). 50 ms minimum update interval for streaming. |
| **D3.js** | SVG/Canvas | Thousands (SVG), more with Canvas | Variable | Free (BSD) | Highly customizable but requires manual performance optimization for high-frequency updates |
| **Chart.js** | Canvas | Thousands | 60 FPS for small datasets | Free (MIT) | Too slow for multi-channel real-time EEG |
| **uPlot** | Canvas | Millions | 60 FPS | Free (MIT) | Very fast, lightweight. Good for time series but less feature-rich. |

**WebGL vs Canvas benchmarks (2025):**
- Canvas: 60 FPS for small datasets, drops to 22 FPS at 50K scatter points
- WebGL: Maintains 58 FPS at 50K points after warm-up
- WebGL handles hundreds of thousands to millions of data points interactively
- For EEG: 8 channels x 250 SPS x 10 seconds visible = 20,000 points. WebGL is preferred.

**Recommendation for Lucid:**
- Use **webgl-plot** or **Plotly.js with scattergl** for real-time multi-channel EEG waveforms
- webgl-plot is purpose-built for oscilloscope-style display and is MIT licensed
- Plotly.js is already proven in EarthSync and provides richer interactivity (zoom, hover, annotations)
- For maximum performance: consider LightningChart JS if budget allows, or build custom WebGL renderer

**Sources:**
- LightningChart performance comparison (https://github.com/Lightning-Chart/javascript-charts-performance-comparison)
- webgl-plot (https://github.com/danchitnis/webgl-plot)
- Dev3lop, WebGL vs Canvas benchmarks (https://dev3lop.com/real-time-dashboard-performance-webgl-vs-canvas-rendering-benchmarks/)
- Plotly.js streaming (https://plotly.com/javascript/streaming/)

### 3.3 WebSocket Streaming and Browser-Side DSP

**Bandwidth requirements:**

| Configuration | Raw Data Rate | With JSON overhead (~2x) |
|---|---|---|
| 8 ch x 250 SPS x 24-bit | 48 kbps (6 KB/s) | ~12 KB/s |
| 8 ch x 1000 SPS x 24-bit | 192 kbps (24 KB/s) | ~48 KB/s |
| 32 ch x 250 SPS x 24-bit | 192 kbps (24 KB/s) | ~48 KB/s |

All configurations are well within WebSocket capacity. Even on mobile networks.

**Binary protocol optimization:** Use ArrayBuffer/DataView instead of JSON for 2-3x bandwidth reduction. Pack 24-bit samples as 3 bytes each. Include timestamp and sequence number in a fixed header.

**Browser-side FFT options:**

| Library | Technology | Size | Performance |
|---|---|---|---|
| **fft.js** | Pure JavaScript | 5 KB | Good for small FFTs. Already used in EarthSync. |
| **pffft.wasm** | WebAssembly (C compiled) | 33 KB + 27 KB support | Faster than JS, especially for large FFTs |
| **KissFFT.wasm** | WebAssembly | Similar | Comparable to pffft.wasm |
| **Web Audio API** | Built-in browser | 0 KB | AnalyserNode provides built-in FFT, but limited configuration |
| **Superpowered Web Audio SDK** | WebAssembly | Larger | Commercial-grade performance |

**WASM FFT is 2-5x faster than pure JS** for large transforms but adds ~60 KB to bundle. For 256-point FFTs at 250 SPS (4 per second), pure JS is sufficient. For 1024-point FFTs at higher rates, WASM is recommended.

**Sources:**
- pffft.wasm (https://github.com/JorenSix/pffft.wasm)
- KISS FFT vs fft.js benchmark (https://toughengineer.github.io/demo/dsp/fft-perf/)

### 3.4 OpenBCI GUI Technology Stack

The OpenBCI GUI is built with **Processing 4** (Java-based creative coding framework).

- **GUI v5.0+** uses **BrainFlow-Java** for hardware communication (replacing the previous Node.js Electron middleware)
- Prior to v5.0, it used a Node.js Electron app as middleware for TCP/IP communication
- Built as a Processing sketch, can run as standalone application
- Cross-platform (Windows, macOS, Linux)
- Repository: https://github.com/OpenBCI/OpenBCI_GUI (892 stars)

**Limitations of Processing-based approach:** Processing is not modern web technology. It's a desktop-only Java application with a custom rendering pipeline. Not easily embedded in web apps. This is why many researchers use BrainFlow + Python instead.

### 3.5 Timeflux Web Interface

Timeflux includes a web-based monitoring interface:
- The **timeflux_ui** plugin provides a framework for web applications that interface with Timeflux
- Built-in browser-based signal monitoring
- Real-time data stream visualization in the browser
- Can send events from the web UI back to Timeflux
- Uses WebSocket for communication between Timeflux backend and browser frontend
- Repository: https://github.com/timeflux/timeflux_ui

**Why Timeflux hasn't gained more traction:**
- Documentation is "a bit coarse" and "some parts of the code need polishing" (per their own assessment)
- YAML-based graph definitions are hard to debug and unit-test
- Static DAG graphs struggle with dynamic execution patterns
- Small team (187 stars, 31 forks, 5 contributors)
- Competes with BrainFlow (1600 stars) and MNE-Python (3300 stars) which have larger communities
- No enterprise backing or visible sponsorship

---

## 4. Electrode Montage Standards

### 4.1 International 10-20 System

The 10-20 system is the internationally standardized method for scalp electrode placement, defined by measuring distances as percentages of skull landmarks:

**Landmarks:**
- **Nasion**: Bridge of the nose between the eyes
- **Inion**: Bony prominence at the back of the skull
- **Preauricular points**: In front of each ear

**Naming convention:**
- Letters indicate brain region: F (frontal), C (central), T (temporal), P (parietal), O (occipital)
- Odd numbers = left hemisphere, even numbers = right hemisphere
- "z" suffix = midline (Fz, Cz, Pz, Oz)
- Lower numbers = closer to midline

**Standard 21-electrode positions:**
Fp1, Fp2, F7, F3, Fz, F4, F8, T3, C3, Cz, C4, T4, T5, P3, Pz, P4, T6, O1, Oz, O2, and reference (A1/A2)

**Extended systems:**
- **10-10 system**: 81 positions (adds intermediate sites between 10-20 positions)
- **10-5 system**: 345 positions (highest density standard nomenclature)

**Sources:**
- Wikipedia, "10-20 system (EEG)" (https://en.wikipedia.org/wiki/10%E2%80%9320_system_(EEG))
- ACNS electrode nomenclature guidelines (https://www.acns.org/UserFiles/file/EEGGuideline2Electrodenomenclature_final_v1.pdf)
- TMSi, "What Is the 10-20 System for EEG?" (https://www.tmsi.artinis.com/blog/the-10-20-system-for-eeg)

### 4.2 Application-Specific Minimum Electrode Sets

#### Motor Imagery BCI

| Configuration | Electrodes | Accuracy Notes |
|---|---|---|
| Minimum (3 ch) | C3, Cz, C4 | Core sensorimotor area. Single-channel (C4 alone) achieves 71-88% |
| Standard (8 ch) | FC3, FC4, C3, Cz, C4, CP3, CP4, CPz | Extended sensorimotor coverage |
| Optimal | Subject-specific subset selected by algorithm | CSP-based channel selection often outperforms all-channel or fixed subsets |

**Key finding:** Channel selection methods achieve significantly higher classification accuracy (p < 0.001) than using all channels OR the conventional C3/C4/Cz minimum.

**Sources:**
- Springer, "A novel channel selection method for optimal classification in MI BCI" (https://link.springer.com/article/10.1186/s12938-015-0087-4)
- PMC, "Performance Improvement with Reduced Number of Channels in MI BCI" (https://pmc.ncbi.nlm.nih.gov/articles/PMC11723053/)

#### P300 Speller

| Configuration | Electrodes | Notes |
|---|---|---|
| Standard (8 ch) | Fz, Cz, Pz, Oz, P3, P4, PO7, PO8 | Most common setup in literature |
| Minimum (4 ch) | PO8, PO7, POz, CPz | Clinically effective, per electrode subset studies |
| Minimum (6 ch) | Subset of standard | Performance equivalent to larger sets |

**Key finding:** Posterior/occipital electrodes (PO7, PO8, Oz) are more discriminable than the traditional midline P300 sites (Fz, Cz, Pz). An 8-electrode system with posterior coverage is optimal.

**Sources:**
- PMC, "Channel Selection Methods for the P300 Speller" (https://pmc.ncbi.nlm.nih.gov/articles/PMC4106671/)
- PMC, "Method for Optimizing EEG Electrode Number in P300" (https://pmc.ncbi.nlm.nih.gov/articles/PMC4377128/)

#### SSVEP

| Configuration | Electrodes | Notes |
|---|---|---|
| Minimum (1 ch) | Oz | Single most important electrode. Performance degrades significantly if Oz is replaced by O1 or O2. |
| Standard (3 ch) | O1, Oz, O2 | Standard occipital coverage |
| Extended (6 ch) | PO3, POz, PO4, O1, Oz, O2 | Adds parieto-occipital coverage for better signal |
| Optimal bipolar | POz-Oz | Best single bipolar derivation |

**Sources:**
- Frontiers, "Influence of Number of Channels on SSVEP BCI Performance" (https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2021.750839/full)
- Frontiers, "Portable EEG and limited-electrode channel classification for SSVEP" (https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2024.1502560/full)

#### Neurofeedback Protocols

| Protocol | Electrodes | Frequency Target | Application |
|---|---|---|---|
| SMR training | Cz | 12-15 Hz (up), theta down, high-beta down | ADHD, focus, attention |
| Alpha training | Pz or Oz | 8-13 Hz (up) | Relaxation, sleep quality |
| Alpha/theta | Pz | Alpha (up) then theta crossover | Addiction, PTSD, deep relaxation |
| Frontal asymmetry | F3, F4 (ref: Cz) | Alpha asymmetry (reduce left > right alpha) | Depression |
| Beta training | F3 or F4 | 15-18 Hz (up) | Cognitive enhancement |
| Theta/beta ratio | Cz or Fz | Theta/beta ratio (decrease) | ADHD |

**Sources:**
- Myndlift, "Common Neurofeedback Protocols" (https://www.myndlift.com/post/what-are-common-neurofeedback-protocols)
- PMC, "Neurofeedback: A Comprehensive Review" (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4892319/)

#### Sleep Staging (AASM Standard)

**Recommended montage:** F4-M1, C4-M1, O2-M1 (referential to contralateral mastoid)
**Acceptable montage:** Fz-Cz, Cz-Oz (bipolar), C4-M1 (referential)
**EOG:** E1 (1 cm below left outer canthus), E2 (1 cm above right outer canthus)
**Chin EMG:** 3 electrodes (2 active + 1 backup)

**Full AASM sleep staging requires:** 3 EEG channels + 2 EOG channels + 1 EMG channel = minimum 6 channels from the EEG amplifier (plus dedicated EOG/EMG amplification if separate).

**Impedance requirements:** < 5 kOhm for EEG/ECG/EOG, < 10 kOhm for EMG.

**Sources:**
- PMC, "The 2007 AASM Recommendations for EEG Electrode Placement" (https://pmc.ncbi.nlm.nih.gov/articles/PMC3001799/)
- AASM Scoring Manual (https://aasm.org/clinical-resources/scoring-manual/)

### 4.3 Optimal 8-Channel Configuration for Lucid

Given 8 channels, the goal is to cover the maximum number of use cases. Based on the analysis above:

**Recommended default montage:**

| Channel | Position | Covers |
|---|---|---|
| 1 | Fz | P300 (midline), neurofeedback (theta/beta) |
| 2 | C3 | Motor imagery (left hand), sleep staging |
| 3 | Cz | Motor imagery (feet), SMR neurofeedback, P300 |
| 4 | C4 | Motor imagery (right hand), sleep staging |
| 5 | Pz | P300, alpha neurofeedback, alpha/theta training |
| 6 | PO7 | P300 (posterior), SSVEP support |
| 7 | Oz | SSVEP (primary), P300, sleep staging |
| 8 | PO8 | P300 (posterior), SSVEP support |
| REF | M1 (left mastoid) | Contralateral reference |
| GND | M2 (right mastoid) or AFz | Ground/bias electrode |

This matches the published 8-channel configuration from PMC research and provides:
- Motor imagery: C3, Cz, C4 (core sensorimotor area)
- SSVEP: PO7, Oz, PO8 (full occipital coverage)
- P300: Fz, Cz, Pz, Oz, PO7, PO8 (6 of 8 standard channels)
- Neurofeedback: Cz (SMR), Pz (alpha), Fz (theta/beta)
- Sleep staging: C3, C4, Oz (with Fz if Cz used as reference alternative)

**Sources:**
- PMC, "Quantitative and Qualitative Representation of EEG Concepts: Different Setups" (https://pmc.ncbi.nlm.nih.gov/articles/PMC10426816/)
- ResearchGate, "8 channel 10-20 EEG electrode placement system" (https://www.researchgate.net/figure/channel-10-20-EEG-electrode-placement-system_fig3_342933365)

### 4.4 Reference and Ground Electrode Options

| Reference Type | Location | Pros | Cons |
|---|---|---|---|
| Single mastoid (M1 or M2) | Behind ear | Easy to attach, stable contact, little cortical activity | Hemispheric bias |
| Linked mastoids | Both M1 + M2 (averaged) | Symmetric, no hemispheric bias | Can attenuate laterality effects |
| Single earlobe (A1 or A2) | Earlobe clip | Easy attachment, minimal cortical activity | More movement artifact than mastoid |
| Average of mastoid + contralateral active | M1 ref, M2 as active channel | "Average mastoid" -- growing standard | Requires post-processing |
| Cz (vertex) | Top of head | Easy to secure, stable | Picks up significant cortical activity, not ideal for many paradigms |
| AFz or Fpz | Forehead midline | Common for ground/bias electrode | Reference Electrode Standardization Technique (REST) shows better error profile |
| Average reference | Computed from all channels | Theoretically ideal if coverage is dense | Requires 64+ electrodes for acceptable bias |

**Recommendation for Lucid (8-channel):** Use M1 (left mastoid) as reference, M2 (right mastoid) or AFz as ground/bias. Record M2 as an active channel if possible (using the bias output pin of ADS1299) to allow offline re-referencing to average mastoid.

**Sources:**
- CMU Memory Lab, "The need for a ground electrode" (https://www.cmu.edu/dietrich/psychology/memorylab/EEG/REF.html)
- PMC, "Which Reference Should We Use for EEG and ERP practice?" (https://pmc.ncbi.nlm.nih.gov/articles/PMC6592976/)
- EEGLAB Wiki, Re-referencing (https://eeglab.org/tutorials/ConceptsGuide/rereferencing_background.html)

---

## 5. Open Source BCI Software Frameworks -- Deep Dive

### 5.1 BrainFlow

**Repository:** https://github.com/brainflow-dev/brainflow
**Stars:** 1,600 | **Forks:** 384 | **License:** MIT | **Latest:** v5.21.0

**Architecture:**
```
brainflow/
  src/
    board_controller/     # C++ board abstraction layer
      board.h/cpp         # Base Board class (pure virtual)
      board_controller.cpp  # Factory (prepare_session switch)
      brainflow_boards.cpp  # JSON board metadata
      openbci/            # OpenBCI board implementations
      synthetic/          # Synthetic board (testing)
      ...
    data_handler/         # Signal processing (C++)
      data_handler.cpp    # FFT, filters, wavelets, CSP, PSD
    ml_module/            # ML inference (ONNX)
  python_package/         # Python bindings
  java_package/           # Java bindings
  cpp_package/            # C++ bindings + examples
  csharp_package/         # C# bindings
  matlab_package/         # MATLAB bindings
  julia_package/          # Julia bindings
  r_package/              # R bindings
  rust_package/           # Rust bindings
  nodejs_package/         # TypeScript/Node bindings
  emulator/               # Device emulators for CI
  cmake/                  # Build configuration
  docs/                   # Sphinx documentation
```

**Signal processing capabilities (DataFilter):**
- FFT and inverse FFT
- Bandpass, bandstop, lowpass, highpass filters (Butterworth, Chebyshev, Bessel)
- Wavelet transform and denoising
- Common Spatial Patterns (CSP) via `get_csp()`
- Power Spectral Density (PSD) computation
- Downsampling
- Detrending
- ONNX model inference (replaced built-in classifiers in v5.x)

**Supported boards (20+):** OpenBCI Cyton, Ganglion, Daisy; Muse 2, Muse S; Neurosity Crown; Emotiv; g.tec Unicorn; BrainAlive; Enophone; PiEEG; ANT Neuro; BrainBit; Callibri; synthetic board; and more.

**Integration effort for new board:** Moderate (1-3 days for an experienced C++ developer). Steps documented above in Section 1.4. The `synthetic_board` provides a complete reference implementation.

### 5.2 MNE-Python

**Repository:** https://github.com/mne-tools/mne-python
**Stars:** 3,300 | **Forks:** 1,500 | **License:** BSD-3 | **Latest:** v1.11.0

**Architecture:**
```
mne-python/
  mne/                    # Core package (99.3% Python)
    io/                   # Data I/O (EDF, BDF, BrainVision, FIF, etc.)
    preprocessing/        # Filtering, ICA, SSP, ASR (via asrpy)
    time_frequency/       # Morlet wavelets, multitaper, STFT
    inverse/              # Source localization (MNE, dSPM, sLORETA, eLORETA, LCMV beamformer)
    connectivity/         # Functional connectivity measures
    stats/                # Cluster permutation tests, ANOVA
    viz/                  # 3D brain visualization (PySurface, PyVista)
    decoding/             # ML wrappers (sklearn pipeline integration)
  doc/                    # Sphinx documentation
  examples/               # Usage examples
  tutorials/              # Step-by-step tutorials
```

**Real-time capabilities (mne-lsl):**
- `mne-lsl` replaces the older `mne-realtime` and `pylsl`
- Provides improved Python bindings for liblsl
- `RtEpochs` for real-time epoching with artifact rejection
- Can receive from any LSL-compatible device
- Supports peak-to-peak rejection thresholds per channel
- TCP-based, works wirelessly across LAN

**Artifact rejection tools:**
- **ICA (Independent Component Analysis):** FastICA, Infomax, Picard algorithms. Automatic component labeling (ICLabel integration). The primary method for removing eye blinks, cardiac artifacts, and muscle activity.
- **SSP (Signal Space Projection):** Projects out artifact subspace vectors. Lower computational cost than ICA. Good for known artifact topographies.
- **ASR (Artifact Subspace Reconstruction):** Available via `asrpy` package (https://github.com/DiGyt/asrpy). Sliding-window PCA-based artifact interpolation. Works in real-time. Identifies contaminated channels per window and interpolates using clean channels. Increasingly popular for mobile/wearable EEG.
- **Threshold rejection:** Simple peak-to-peak amplitude rejection per epoch per channel.

**Source localization methods:**
- MNE (Minimum Norm Estimate)
- dSPM (dynamic Statistical Parametric Mapping)
- sLORETA (standardized Low Resolution Electromagnetic Tomography)
- eLORETA (exact LORETA)
- LCMV beamformer
- Equivalent current dipole (ECD) fitting
- Requires: Forward model (from BEM/sphere head model), noise covariance, inverse operator

**Sources:**
- MNE documentation (https://mne.tools/stable/)
- mne-lsl (https://github.com/mne-tools/mne-lsl)
- ASRpy (https://github.com/DiGyt/asrpy)

### 5.3 OpenViBE

**URL:** https://openvibe.inria.fr/ | **License:** AGPLv3 | **Language:** C++

**Architecture:**
- Visual programming environment ("Designer") for building BCI processing pipelines
- Processing units are "boxes" (plugins) connected by edges in a directed graph
- Each box has inputs, outputs, and configurable settings
- Boxes are C++ plugins with header + implementation files
- Kernel handles scheduling: boxes notified on clock ticks and input data arrival
- Scenarios saved as XML files

**Built-in BCI paradigm implementations:**
- **Motor imagery:** CSP spatial filter + LDA classifier. Multiple pre-built scenarios in `bci-examples/motor-imagery-CSP/`. Virtual ball control, spaceship control.
- **P300 speller:** Full row-column flash matrix paradigm with xDAWN spatial filter
- **SSVEP:** Frequency detection using CCA (Canonical Correlation Analysis) and CSP filters

**Signal processing boxes include:**
- Temporal filters (IIR, FIR)
- Spatial filters (CSP, xDAWN, surface Laplacian)
- Spectral analysis (FFT, PSD)
- Feature extraction (band power, CSP features, log-variance)
- Classifiers (LDA, SVM through integration)
- Stimulus presentation (visual, auditory)

**Python scripting support** via scripting boxes that can call Python code within OpenViBE scenarios.

**Limitations:** Windows/Linux only (no macOS). AGPLv3 license restricts commercial use. Desktop-only (no web interface). Documentation is adequate but dated.

**Sources:**
- OpenViBE software architecture (https://openvibe.inria.fr/software-architecture/)
- OpenViBE signal processing tutorial (https://openvibe.inria.fr/tutorial-1-implementing-a-signal-processing-box/)

### 5.4 Timeflux

**Repository:** https://github.com/timeflux/timeflux
**Stars:** 187 | **Forks:** 31 | **License:** MIT | **Latest:** v0.17.2

**Architecture:**
- Graph-based processing defined in **YAML** files
- Each processing step is a **node** (Python class)
- Nodes connected by edges forming a **directed acyclic graph (DAG)**
- Graphs can be distributed across CPU cores, threads, and hosts automatically
- Built on SciPy, Pandas, Xarray, scikit-learn
- Plugin system: any Python package can be a plugin by inheriting base node class

**Plugin ecosystem:**
- `timeflux_lsl` -- LSL integration
- `timeflux_ui` -- Web-based monitoring interface
- `timeflux_ml` -- Machine learning integration
- `timeflux_dsp` -- Digital signal processing nodes

**Real-time capabilities:**
- LSL integration for device input
- ZeroMQ for inter-process communication
- OSC (Open Sound Control) for creative applications
- HDF5 file handling for recording and replay

**Why limited adoption (analysis):**
1. **Documentation gap:** Self-described as "a bit coarse"
2. **YAML graph limitations:** Hard to debug, hard to unit-test, no IDE support
3. **Competition:** BrainFlow has 8.5x more stars, MNE-Python has 17.6x more
4. **Small team:** 5 contributors, no visible corporate backing
5. **Niche positioning:** Tries to be everything (acquisition + processing + ML + UI) without excelling at any one thing
6. **No killer feature:** BrainFlow has board abstraction, MNE has analysis depth, OpenViBE has visual programming -- Timeflux's YAML graphs are not compelling enough

---

## 6. Neurofeedback Software -- Existing Open Source

### 6.1 NFBLab

**Repository:** https://github.com/nikolaims/nfb
**Paper:** Smetanin et al. (2018), Frontiers in Neuroinformatics (https://pmc.ncbi.nlm.nih.gov/articles/PMC6311652/)

**Features:**
- Written in Python (PyQt GUI)
- XML-based protocol language for experimental blocks and sequences
- Interactive signal processing tract configuration (spatial + temporal filters)
- Randomization of experimental blocks
- Direct MNE-Python integration for source-space neurofeedback (individual inverse solvers)
- LSL integration for device input (supports most EEG vendors)
- Session management with data recording

**Protocols supported:** Alpha, theta, SMR, beta training, custom frequency band training. Supports individualized spatial filtering using head models.

### 6.2 OpenNFT

**Repository:** https://github.com/OpenNFT/OpenNFT and https://github.com/OpenNFT/pyOpenNFT
**URL:** https://opennft.org/

**Overview:**
- Originally designed for real-time **fMRI** neurofeedback (not EEG)
- Multi-processing architecture: Python GUI + Matlab computation modules
- The newer **pyOpenNFT** (2025) is fully Python-based with FastAPI backend
- Now extending to EEG-fMRI integration via LSL
- Supports ML-based prediction server for fMRI neurofeedback signal from EEG
- MICCAI 2025 paper published on the framework

**Architecture:** Separate processes for GUI (Python), data processing (Matlab/Python), and ML inference. FastAPI RESTful interface for interoperability.

### 6.3 BrainBay

**Repository:** https://github.com/ChrisVeigl/BrainBay (194 stars)
**License:** GPL

**Features:**
- Visual programming interface (120+ built-in processing elements)
- Bio/neurofeedback application
- Supports OpenBCI, OpenEEG, and other hardware
- MIDI, video, and computer control output
- Alpha threshold triggering, frequency band power computation
- OSC sender for data transfer to external applications
- Can process up to 1 kHz on modest hardware
- Windows only
- No programming required for basic use

### 6.4 BioEra

**URL:** https://bioera.net/
**Status:** Proprietary (NOT open source)

- Visual designer for biofeedback
- 120+ built-in processing elements
- Windows and Android only (Mac/Linux via VirtualBox)
- Trial version available; full version is commercial
- Can filter EEG frequency bands and trigger MIDI/video/tasks at thresholds
- Compatible with OpenBCI via OpenBCI documentation page

### 6.5 Other Open-Source Neurofeedback Tools

| Tool | Type | Status | Notes |
|---|---|---|---|
| **eeg_neurofeedback** | Meditation | Active | Works with all popular headsets. Adaptive fitting. Real-time sound feedback. |
| **CortEX** | Meditation | Active | EEG + ECG. Focus, relaxation, heart rhythm analysis. Session reports. |
| **OpenNFB (strfry)** | Programmable | Maintained | "Neurofeedback Software for Programmers." Python. Minimal GUI. (https://github.com/strfry/OpenNFB) |
| **NeuroPype** | Commercial + open | Active | Visual pipeline designer (open source). Full suite is commercial. Real-time artifact rejection. |

### 6.6 Clinical vs Consumer Neurofeedback -- Regulatory Differences

**Clinical neurofeedback:**
- Requires medical-grade equipment (IEC 60601-1 compliance)
- Practitioner oversight (typically requires certification: BCIA, QEEG-certified)
- Protocol selection based on quantitative EEG (qEEG) assessment
- Session records must be maintained
- FDA considers neurofeedback devices "Class II" when marketed for clinical use
- Requires 510(k) clearance in the US for medical claims

**Consumer neurofeedback:**
- No regulatory requirements when marketed as "wellness" (not medical)
- Colorado and Minnesota (2024) are first US states with specific neural data protections
- Consumer devices (Muse, Emotiv Insight) explicitly avoid medical claims
- No practitioner required
- Limited protocol options (typically just relaxation/meditation feedback)

---

## 7. Citizen Science EEG -- Prior Attempts

### 7.1 Muse Labs (InteraXon)

**URL:** https://choosemuse.com/pages/muse-labs

The most successful citizen science EEG program to date:
- Community members participate in research studies by wearing Muse headband
- Studies cover: sleep, mood, lucid dreaming, focus, breathwork effects
- Over **6 million hours** of meditation EEG data collected
- Over **200 peer-reviewed studies** using Muse data
- Participants download the Muse app and opt into studies
- The world's largest EEG data collection

**Limitation:** Data is proprietary to InteraXon. Not openly shared with the research community.

### 7.2 OpenBCI Community Research

**URL:** https://openbci.com/community/

- Active community forum with research project discussions
- **Neurotech Challenge Series (NTCS):** Collaboration between OpenBCI, NeuroTechX, and CAMH. Participants record brain data using visual/auditory experiments and upload to a portal for aggregation and open-access release.
- **EEG Notebooks:** NeuroTechX + OpenBCI collaboration democratizing cognitive neuroscience. Classic EEG experiments in Python 3 + Jupyter notebooks.
- **OpenEXP:** Browser-based experiment runner for EEG data collection with OpenBCI
- **OpenBCI Meets the Web (2024):** ACM UbiComp paper on scalable, customizable web-based EEG data collection platform

### 7.3 Open EEG Datasets

**Major repositories:**

| Repository | Datasets | Format | Access |
|---|---|---|---|
| **TUH EEG Corpus** | 26,846 clinical recordings, 29.1 years of data, 572 GB | EDF | Free registration (www.nedcdata.org). Physical USB mail for full download. |
| **OpenNeuro** | Growing collection of BIDS-formatted EEG/MEG | BIDS (EDF/BDF) | Free, CC0 license. https://openneuro.org/ |
| **MOABB** | 36 BCI datasets (14 MI, 15 P300, 7 SSVEP) | Various | Free via Python API. https://moabb.neurotechx.com/ |
| **PhysioNet** | Multiple EEG datasets including motor imagery | EDF | Free. https://physionet.org/ |
| **NEMAR** | EEG/MEG data + analysis tools | BIDS | Free, via OpenNeuro. https://nemar.org/ |
| **HBN-EEG** | 2,600+ child participants | BIDS | Free, CC-BY-SA 4.0. Healthy Brain Network. |
| **GitHub openlists/ElectrophysiologyData** | Curated list of 100+ EEG/MEG datasets | Various | Meta-list. https://github.com/openlists/ElectrophysiologyData |

**MOABB dataset details (complete):**

*Motor Imagery (14 datasets, ~900+ subjects):*
AlexMI (8 subj, 16 ch), BNCI2014_001 (9 subj, 22 ch), BNCI2014_002 (14 subj, 15 ch), BNCI2014_004 (9 subj, 3 ch), BNCI2015_001 (12 subj, 13 ch), BNCI2015_004 (9 subj, 30 ch), Cho2017 (52 subj, 64 ch), Lee2019_MI (54 subj, 62 ch), GrosseWentrup2009 (10 subj, 128 ch), PhysionetMI (109 subj, 64 ch), Schirrmeister2017 (14 subj, 128 ch), Shin2017A (29 subj, 30 ch), Weibo2014 (10 subj, 60 ch), Zhou2016 (4 subj, 14 ch)

*P300/ERP (15 datasets):*
BI2012 (25 subj), BI2013a (24 subj), BI2014a (64 subj), BI2014b (37 subj), BI2015a (43 subj), BI2015b (44 subj), BNCI2014_008 (8 subj), BNCI2014_009 (10 subj), BNCI2015_003 (10 subj), EPFLP300 (8 subj), Huebner2017 (13 subj), Huebner2018 (12 subj), Lee2019_ERP (54 subj), Sosulski2019 (13 subj), Cattan2019_VR (21 subj)

*SSVEP (7 datasets):*
Lee2019_SSVEP (54 subj), MAMEM1 (10 subj, 256 ch), MAMEM2 (10 subj, 256 ch), MAMEM3 (10 subj, 14 ch), Nakanishi2015 (9 subj), Kalunga2016 (12 subj), Wang2016 (34 subj)

**Sources:**
- MOABB benchmark paper (https://arxiv.org/abs/2404.15319)
- TUH EEG Corpus (https://isip.piconepress.com/projects/tuh_eeg/)
- OpenNeuro (https://openneuro.org/)
- BIDS standard (https://bids.neuroimaging.io/)

### 7.4 Privacy and Neuroethics Considerations

**Key concerns:**

1. **Neural data sensitivity:** A 2024 US survey found the majority of Americans consider brain data as sensitive as or more sensitive than genetic or financial data. EEG signals capture real-time internal states including emotions, cognitive processes, and potentially thought content.

2. **Re-identification risk:** Machine learning on publicly available EEG datasets predicted alcohol use disorder with 96% precision. Brain data can serve as a biometric identifier. De-identification may not be sufficient -- EEG signals contain subject-specific patterns.

3. **Regulatory landscape (2024-2025):**
   - UNESCO drafted "Recommendation on the ethics of Neurotechnology" (first draft 2024)
   - Colorado and Minnesota (May 2024) enacted specific neural data protection laws
   - Minnesota: civil and criminal penalties for neural data rights violations
   - No federal US framework yet for brain data

4. **Foundation model concerns:** Neural data used to train foundation models (LaBraM, NeuroLM) raises issues of large-scale repurposing and cross-context stitching. The foundation model paradigm subjects brain data to practices outside clinical/research governance frameworks.

5. **Informed consent for citizen science:** Participants must understand what their brain data reveals and how it could be used. "Coercive optimism" is a risk -- people with disabilities may feel BCIs are their only hope, compromising voluntariness.

6. **Best practices for Lucid:**
   - Process all data locally by default (no cloud upload without explicit consent)
   - Strip personally identifying information before any aggregation
   - Provide clear, plain-language consent forms
   - Allow data deletion at any time
   - Use differential privacy for aggregated datasets
   - Open-source all data processing code for auditability

**Sources:**
- PMC, "Addressing privacy risk in neuroscience data" (https://pmc.ncbi.nlm.nih.gov/articles/PMC9444136/)
- PMC, "US public perceptions of brain data sensitivity" (https://pmc.ncbi.nlm.nih.gov/articles/PMC10800024/)
- ArXiv, "Training Data Governance for Brain Foundation Models" (https://www.arxiv.org/pdf/2602.02511)
- PMC, "Ethical imperatives in BCI commercialization" (https://pmc.ncbi.nlm.nih.gov/articles/PMC12553070/)
- PMC, "Regulating neural data processing in the age of BCIs" (https://pmc.ncbi.nlm.nih.gov/articles/PMC11951885/)

---

## 8. Project Structure for a BCI Platform

### 8.1 How Major Projects Are Organized

**BrainFlow (monorepo, multi-language):**
```
brainflow/
  src/                    # C++ core (board_controller, data_handler, ml_module)
  python_package/         # Python bindings
  java_package/           # Java bindings
  cpp_package/            # C++ bindings + examples
  csharp_package/         # C# bindings
  matlab_package/         # MATLAB bindings
  julia_package/          # Julia bindings
  r_package/              # R bindings
  rust_package/           # Rust bindings
  nodejs_package/         # TypeScript/Node bindings
  emulator/               # Device emulators for CI testing
  cmake/                  # Build system
  docs/                   # Sphinx -> ReadTheDocs
  third_party/            # Vendored dependencies
```
**Pattern:** Monorepo. C++ core + language-specific binding directories.

**OpenBCI (multi-repo, separate hardware/firmware/software):**
```
OpenBCI/                          # GitHub organization (16+ repos)
  OpenBCI_GUI/                    # Processing/Java GUI application
  OpenBCI_Cyton_Library/          # Arduino firmware library for Cyton
  OpenBCI_Ganglion_Library/       # Firmware for Ganglion
  V3_Hardware_Design_Files/       # PCB schematics (Design Spark format)
  Ganglion_Hardware_Design_Files/ # PCB schematics (KiCad format)
  Docs/                           # Documentation site source
  OpenBCI_WIFI/                   # WiFi shield firmware
  OpenBCI_NodeJS_Cyton/           # Node.js SDK for Cyton
  OpenBCI_Hub/                    # Electron app (deprecated, replaced by BrainFlow)
```
**Pattern:** Multi-repo. Separate repos for each hardware variant, firmware, and software tool.

**MNE-Python (monorepo, Python-only):**
```
mne-python/
  mne/                   # Core package (all Python)
    io/                  # File format readers
    preprocessing/       # Filters, ICA, SSP
    time_frequency/      # TF analysis
    inverse/             # Source localization
    connectivity/        # Connectivity measures
    stats/               # Statistical testing
    viz/                 # Visualization
    decoding/            # ML integration
  doc/                   # Sphinx documentation
  examples/              # Example scripts
  tutorials/             # Step-by-step tutorials
```
**Pattern:** Monorepo. Single Python package with submodules.

### 8.2 Languages by Component

| Component | Typical Language | Rationale |
|---|---|---|
| MCU firmware | C/C++ (ESP-IDF, Arduino) | Hardware control, real-time constraints, small memory |
| Device drivers / core library | C/C++ | Performance, FFI to all languages |
| Language bindings | Python, Java, C#, etc. | Thin wrappers over C/C++ core |
| Signal processing (offline) | Python (NumPy/SciPy/MNE) | Rich ecosystem, rapid development |
| Signal processing (real-time) | C/C++ or Rust | Low latency, deterministic |
| Web visualization | TypeScript/JavaScript (React) | Browser ecosystem, real-time WebSocket |
| Mobile app | React Native or Flutter | Cross-platform |
| Desktop app | Python (PyQt) or Electron | Cross-platform |
| ML/AI models | Python (PyTorch/TensorFlow) | Training. ONNX for deployment. |
| Hardware design | KiCad (open source) | Free, widely supported, version-controllable |

### 8.3 Monorepo vs Multi-Repo

| Aspect | Monorepo (BrainFlow style) | Multi-Repo (OpenBCI style) |
|---|---|---|
| Coordination | Single PR for cross-cutting changes | Requires coordinating PRs across repos |
| CI/CD | Single pipeline tests everything | Separate pipelines per repo |
| Versioning | Single version number | Version matrix across repos |
| Discoverability | Everything in one place | Harder to find components |
| Build complexity | More complex build system | Simpler per-repo builds |
| Contributor experience | Easier to understand full system | Lower barrier for single-component contributions |

**Recommendation for Lucid:** **Monorepo** with clear directory separation. This is the BrainFlow/MNE pattern and works well for a platform where firmware, host library, and web UI must evolve together.

### 8.4 Proposed Lucid Repository Structure

```
lucid/
  firmware/                         # ESP32-S3 + ADS1299 firmware (C/C++, ESP-IDF)
    main/                           # Main firmware application
    components/
      ads1299/                      # ADS1299 SPI driver
      streaming/                    # WiFi/BLE streaming protocol
      dsp/                          # On-device filtering (esp-dsp)
    test/                           # Firmware unit tests
    sdkconfig                       # ESP-IDF configuration

  hardware/                         # PCB design files (KiCad)
    pcb/                            # Schematic + layout
    bom/                            # Bill of materials
    gerber/                         # Manufacturing files
    3d/                             # 3D printable enclosure/headset
    docs/                           # Hardware assembly guide

  sdk/                              # Host-side library (Python)
    lucid/
      acquisition/                  # Device communication (BrainFlow wrapper or custom)
      processing/                   # Real-time processing pipeline
      neurofeedback/                # Neurofeedback protocol engine
      bci/                          # BCI paradigm implementations (MI, P300, SSVEP)
      io/                           # File I/O (BIDS, EDF, CSV)
      ml/                           # ML model management (ONNX inference)
    tests/

  web/                              # Web dashboard (TypeScript/React)
    src/
      components/
        EEGDisplay/                 # Multi-channel waveform (WebGL)
        SpectralView/               # FFT / spectrogram
        TopographicMap/             # 2D head map
        NeurofeedbackPanel/         # Real-time feedback UI
        SessionManager/             # Recording, playback
        BCIControls/                # BCI paradigm controls
      hooks/
        useWebSocket.ts             # Device data streaming
        useEEGProcessing.ts         # Browser-side DSP
      services/
        brainflow.ts                # BrainFlow integration
        lsl.ts                      # LSL integration

  server/                           # Backend API (Python/FastAPI or Node.js)
    api/                            # REST endpoints
    streaming/                      # WebSocket relay
    storage/                        # Session database
    citizen_science/                # Data aggregation, anonymization

  docs/                             # Documentation (Docusaurus or Sphinx)
    getting-started/
    hardware-guide/
    api-reference/
    tutorials/
    research/

  datasets/                         # Sample data and MOABB integration
  docker/                           # Docker configurations
  .github/workflows/                # CI/CD
```

### 8.5 Hardware Design Storage

**Tool recommendation: KiCad**
- Open source (GPL), free
- Version-controllable (text-based file formats)
- Used by OpenBCI Ganglion, BioAmp EXG Pill, many others
- Active development, large component libraries
- Export to Gerber for manufacturing
- 3D viewer for PCB visualization
- Supports hierarchical schematics

**Alternatives:** Eagle (Autodesk, freemium), Altium (commercial, expensive), Design Spark (free, used by OpenBCI Cyton -- not recommended, proprietary format)

**Best practice:** Store schematics, PCB layouts, BOM, and Gerber files in the `hardware/` directory. Include 3D-printable case/headset files in STL format.

### 8.6 Documentation Approaches

| Tool | Used By | Best For |
|---|---|---|
| **Sphinx + ReadTheDocs** | BrainFlow, MNE-Python, LSL | Python projects. Auto-generates from docstrings. Free hosting. Versioning. |
| **Docusaurus** | Modern JS/React projects | Mixed language projects. React component support. Beautiful out of box. i18n. |
| **MkDocs + Material** | Many open-source projects | Simple Markdown-based docs. Material theme is polished. |
| **GitHub Wiki** | Simple projects | Quick start. Limited formatting. No versioning. |
| **OpenBCI Docs** | OpenBCI | Custom Docusaurus-based docs site (docs.openbci.com) |

**Recommendation for Lucid:** **Docusaurus** for the main documentation site (hardware guides, tutorials, getting started). It handles multi-language projects well and has a modern look. Use inline docstrings + auto-generated API docs for the Python SDK (via Sphinx or pdoc).

**Sources:**
- ReadTheDocs documentation tools (https://docs.readthedocs.com/platform/stable/intro/doctools.html)
- DeepDocs, "Best Tools for Technical Documentation" (https://deepdocs.dev/best-tools-for-technical-documentation/)

---

## 9. EEG Foundation Models (Cloud Processing Use Case)

This is the primary use case for cloud processing in a BCI platform.

### 9.1 Key Models (2024-2025)

| Model | Architecture | Pre-training Data | Key Innovation |
|---|---|---|---|
| **LaBraM** | Neural Transformer | ~2,500 hours EEG, 20 datasets | Vector-quantized neural spectrum prediction. Tokenizes EEG channel patches into neural codes. ICLR 2024 spotlight. |
| **NeuroLM** | LLM-integrated | Multi-task EEG | Treats EEG as "foreign language" for LLMs. Cross-modal contrastive alignment of EEG and text embeddings. |
| **Large Cognition Model (LCM)** | Dual attention Transformer | Raw EEG | Combines temporal + spectral attention. Captures time dynamics and frequency patterns from raw data. |

**How cloud inference would work for Lucid:**
1. Local device streams EEG to host computer
2. Host performs real-time processing (filtering, artifact rejection, feature extraction)
3. Periodically (or on request), host sends feature vectors or raw segments to cloud API
4. Cloud runs foundation model inference (classification, anomaly detection, biomarker extraction)
5. Results returned to host for display/annotation

**This is NOT for real-time feedback loops** -- cloud round-trip latency (100+ ms) makes it unsuitable for neurofeedback or BCI control. It IS suitable for:
- Post-session analysis and insights
- Automated sleep staging from overnight recordings
- Emotion/cognitive state classification
- Anomaly detection (seizure screening)
- Citizen science aggregate analysis

**Sources:**
- LaBraM (https://github.com/935963004/LaBraM, https://arxiv.org/abs/2405.18765)
- Brain Foundation Models survey (https://arxiv.org/html/2503.00580v1)
- PMC, "Bridging neuroscience and AI: LLMs for neurological signal interpretation" (https://pmc.ncbi.nlm.nih.gov/articles/PMC12213581/)

---

## Summary of Key Technical Decisions for Lucid

| Decision | Recommendation | Rationale |
|---|---|---|
| ADC | ADS1299 | Gold standard, 24-bit, -110 dB CMRR, proven in 5+ open-source projects |
| MCU | ESP32-S3 (N16R8) | WiFi + BLE, dual-core 240 MHz, DSP extensions, 16 MB flash, 8 MB PSRAM, FreeRTOS |
| Firmware framework | ESP-IDF | Full FreeRTOS control, DMA-driven SPI, esp-dsp integration |
| Wireless protocol | WiFi (primary), BLE (low-power mode) | WiFi for desktop, BLE for mobile |
| Streaming protocol | Custom UDP with LSL-style timestamps | Low latency, jitter-tolerant with receiver buffering |
| Host SDK language | Python | BrainFlow + MNE ecosystem, ML/AI tooling |
| Web visualization | TypeScript/React + WebGL (webgl-plot or Plotly scattergl) | Real-time multi-channel display, existing EarthSync expertise |
| BCI framework integration | BrainFlow (acquisition) + MNE (processing) | Largest communities, most mature |
| Default montage | Fz, C3, Cz, C4, Pz, PO7, Oz, PO8 (ref: M1, gnd: M2/AFz) | Covers MI, P300, SSVEP, NFB, sleep |
| Repository structure | Monorepo | Firmware + SDK + web evolve together |
| Hardware design tool | KiCad | Open source, version-controllable, widely used |
| Documentation | Docusaurus (main site) + Sphinx (Python API) | Modern, multi-language support |
| Data format | BIDS-compatible EDF for storage | Interoperable with OpenNeuro, MNE, EEGLAB |
| Citizen science data | Local-first, opt-in aggregation with anonymization | Privacy by design |
