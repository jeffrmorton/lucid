# Open-Source BCI & EEG Landscape Research
**Date: 2026-03-26**

---

## 1. Open-Source EEG Hardware

### Tier 1: Research-Grade Open Source

#### OpenBCI Cyton
- **URL**: https://shop.openbci.com / https://github.com/OpenBCI
- **Status**: ACTIVE. The original and most established open-source EEG platform.
- **Channels**: 8 (expandable to 16 with Daisy module)
- **Sample Rate**: 250 SPS (125 SPS with 16-ch Daisy)
- **Bit Depth**: 24-bit
- **ADC**: Texas Instruments ADS1299
- **Electrodes**: Compatible with wet, dry, and active. 3D-printable Ultracortex headset.
- **Form Factor**: Standalone board + 3D-printable Ultracortex Mark IV headset (full cap)
- **Communication**: USB dongle (RFDuino wireless), WiFi shield available
- **Price**: ~$1,249 USD (board only, 2025 pricing -- significant increase from historical ~$500)
- **Community**: OpenBCI_GUI: 892 stars, 297 forks. Active forums. Large ecosystem.
- **Notes**: The ADS1299 is the gold standard ADC for EEG. 24-bit, -110 dB CMRR, 250-16k SPS. On-chip 1-24x programmable gain amplifier. The Cyton is Arduino-compatible (PIC32 MCU). Hardware design files are open source.

#### OpenBCI Ganglion
- **URL**: https://shop.openbci.com/products/ganglion-board
- **Status**: ACTIVE (still listed for sale)
- **Channels**: 4
- **Sample Rate**: 200 SPS
- **Bit Depth**: 24-bit
- **ADC**: Microchip MCP3912 (NOT the ADS1299 -- significantly cheaper but lower performance)
- **Communication**: Bluetooth Low Energy (Simblee/nRF51822)
- **Price**: Historically ~$100-200 (current price not confirmed)
- **Notes**: Uses the Simblee BLE module (based on nRF51822). The MCP3912 has lower CMRR than the ADS1299. Good entry point but limited channels.

#### HackEEG
- **URL**: https://www.crowdsupply.com/starcat/hackeeg / https://github.com/starcat-io/hackeeg-shield
- **Status**: SEMI-ACTIVE. Hardware available, firmware somewhat stale (last push 2021).
- **Channels**: 8 per shield (stackable to 32 channels on one Arduino Due)
- **Sample Rate**: Up to 16,000 SPS (full ADS1299 range)
- **Bit Depth**: 24-bit
- **ADC**: Texas Instruments ADS1299
- **Communication**: USB (Arduino Due, DMA-driven for max throughput)
- **Price**: Was ~$350 on Crowd Supply
- **Community**: 73 stars. Used at Stanford, Harvard Medical School, NIH, Caltech, UCSF, Bayer AG.
- **Notes**: The highest sample rate open-source option by leveraging DMA. Arduino Due shield form factor. Python client + LSL integration. Voltage level shifters for Arduino Mega compatibility. True research-grade performance.

#### FreeEEG32
- **URL**: https://www.crowdsupply.com/neuroidss/freeeeg32 / https://github.com/neuroidss/FreeEEG32-beta
- **Status**: WINDING DOWN. Final shipments completed. No longer manufactured by NeuroIDSS. Open-source design files remain available for self-manufacture.
- **Channels**: 32 (stackable to 64-256+)
- **Sample Rate**: Up to 128 kSPS simultaneous sampling
- **Bit Depth**: 24-bit
- **ADC**: 4x Analog Devices AD7771 (8 channels each)
- **MCU**: STM32H7 ARM Cortex-M7 (1027 DMIPS, 2MB Flash, 1MB SRAM)
- **Noise**: <0.22 uV measured
- **Dynamic Range**: 107 dB @ 32 kSPS
- **Price**: Was $199-250 on Crowd Supply
- **Community**: 153 stars. AGPL license.
- **Notes**: The most channels-per-dollar of any open-source EEG. The AD7771 is a different approach from the ADS1299 -- simultaneous-sampling sigma-delta, not the integrated biopotential SoC. Potentially the best platform for high-density research if someone revives manufacturing.

#### Cerelog ESP-EEG
- **URL**: https://www.cerelog.com / https://github.com/Cerelog-ESP-EEG/ESP-EEG
- **Status**: ACTIVE. New project (appeared late 2025). Growing community.
- **Channels**: 8
- **Sample Rate**: 250-16k SPS (ADS1299 full range)
- **Bit Depth**: 24-bit
- **ADC**: Texas Instruments ADS1299
- **MCU**: ESP32-S3
- **Communication**: USB-C, WiFi (ESP32), planned Bluetooth
- **Price**: $349.99 USD (introductory; MSRP planned $499.99)
- **Community**: 102 stars, 12 forks. Growing fast.
- **Features**: True closed-loop active bias, LiPo charging, BrainFlow integration, forked OpenBCI GUI, LSL streaming
- **Safety Warning**: NOT medically isolated. Must use battery-powered host (laptop on battery or power bank). NOT for use while connected to mains power.
- **Notes**: The most modern ADS1299-based open-source board. ESP32-S3 provides WiFi + future BLE. The active bias pin reduces mains interference at the hardware level. Strong newcomer that could become the new community standard.

### Tier 2: Affordable/Hobbyist Open Source

#### PiEEG
- **URL**: https://pieeg.com / https://github.com/pieeg-club/PiEEG-16
- **Status**: ACTIVE. Expanding product line.
- **Channels**: 8 (original), 16 (PiEEG-16)
- **Sample Rate**: 250-16k SPS
- **Bit Depth**: 24-bit
- **ADC**: Texas Instruments ADS1299
- **Form Factor**: Raspberry Pi HAT (40-pin GPIO, SPI interface)
- **Price**: $250 (4-ch) / $350 (8-ch) / $1,120 (full kit with Pi 5, display, electrodes, course)
- **Community**: IronBCI (related project): 589 stars. PiEEG-16: 53 stars.
- **Notes**: Unique approach -- integrates with the Raspberry Pi ecosystem directly. Good for embedded/portable applications. The same team also built IronBCI (wearable BLE version with ADS1299 + STM32).

#### IronBCI
- **URL**: https://github.com/pieeg-club/ironbci
- **Status**: ACTIVE.
- **Channels**: 8
- **Sample Rate**: 250 SPS
- **Bit Depth**: 24-bit
- **ADC**: ADS1299
- **MCU**: STM32
- **Communication**: Bluetooth Low Energy 5
- **Electrodes**: 8 dry Ag/AgCl at F7, Fz, F8, C3, C4, T5, Pz, T6
- **Noise**: <1 uV internal noise level
- **Additional Sensors**: Gyroscope, accelerometer, CO2, temperature, humidity, ambient sound, pulse oximetry
- **Community**: 589 stars, 56 forks
- **Notes**: The most integrated wearable open-source BCI. The additional environmental sensors make it uniquely useful for context-aware BCI research.

#### Olimex EEG-SMT (OpenEEG)
- **URL**: https://www.olimex.com/Products/EEG/OpenEEG/EEG-SMT/
- **Status**: ACTIVE (still manufactured and sold by Olimex). Based on the legacy OpenEEG project.
- **Channels**: 2 (bipolar)
- **Sample Rate**: 256 Hz
- **Bit Depth**: 10-bit (likely, based on old ADC design)
- **Communication**: USB (mini-USB, self-powered)
- **Price**: 99 EUR (~$107 USD)
- **Notes**: The cheapest complete, assembled, off-the-shelf open-source EEG. Based on the ModularEEG project. Only 2 channels and relatively low resolution. Good for basic neurofeedback experiments but not serious research. Original OpenEEG project dates to early 2000s.

#### BioAmp EXG Pill (Upside Down Labs)
- **URL**: https://github.com/upsidedownlabs/BioAmp-EXG-Pill
- **Status**: ACTIVE.
- **Channels**: 1
- **ADC**: None built-in -- uses external MCU ADC (Arduino, ESP32, Raspberry Pi Pico, etc.)
- **Amplifier**: TL074 quad low-noise JFET op-amp
- **Size**: 25.4 x 10 mm
- **Price**: ~$10-20 USD
- **Community**: 372 stars, 88 forks
- **License**: CERN-OHL-S-2.0 + MIT
- **Notes**: Not a complete EEG system -- it is a tiny analog front-end module. Configurable for EEG/ECG/EMG/EOG via solder bridges. Resolution depends entirely on the external ADC. Publication-grade signals claimed without dedicated hardware filters. Extremely low cost for experimentation. Designed in KiCad, fully open hardware files.

#### Creamino
- **URL**: https://github.com/ArcesUnibo/creamino
- **Status**: SEMI-ACTIVE (academic project from University of Bologna).
- **Channels**: Multiple (configurable)
- **Form Factor**: Arduino Due shield
- **Communication**: USB (SPI to Arduino, Arduino to PC)
- **Features**: Compatible with BCI2000, OpenViBE, Simulink
- **Notes**: Academic project focused on educational use. Java-based acquisition software. Good documentation for a teaching platform.

#### Elata EEG
- **URL**: https://github.com/Elata-Biosciences/elata-eeg / https://www.elata.bio
- **Status**: ACTIVE but early stage. DAO-governed (decentralized autonomous organization).
- **Channels**: 8 (initial), 32-channel version in development
- **ADC**: ADS1299
- **MCU**: Raspberry Pi 5
- **Price**: "Hundreds of dollars" (not precisely specified)
- **Community**: 16 stars (very new)
- **Notes**: Unusual model -- blockchain/DAO-funded open-source neuroscience. Focus on precision psychiatry. Held EEG-controlled Pong tournament at Token2049. Has its own data protocol (ZORP). Early stage but well-funded through DeSci model.

### Tier 3: Legacy/Abandoned

#### OpenEEG (original project)
- **URL**: https://openeeg.sourceforge.net
- **Status**: ABANDONED. Last meaningful updates years ago.
- **Notes**: The pioneer of open-source EEG. Spawned the Olimex EEG-SMT. SourceForge-era project. Historical significance but no longer relevant for new builds.

#### VolksEEG
- **URL**: https://github.com/VolksEEG/VolksEEG
- **Status**: SLOW/SEMI-ABANDONED. Ambitious goals but limited recent activity.
- **Goal**: FDA-clearable, CE-marked, fully open-source clinical EEG.
- **Community**: 74 stars.
- **Notes**: Noble goal of creating a truly clinical-grade open-source EEG. The regulatory pathway (FDA, CE) makes this extremely challenging for an open-source project.

---

## 2. Open-Source EEG Software

### Data Acquisition & Streaming

| Project | Language | Stars | Status | Description |
|---------|----------|-------|--------|-------------|
| **BrainFlow** | C++/Python/Java/C#/Julia/MATLAB/R/Rust/TypeScript | 1,639 | VERY ACTIVE (v5.21.0, Feb 2026) | Universal data acquisition API. Supports 20+ boards: OpenBCI, Muse, Emotiv, g.tec, PiEEG, Neurosity, and more. The de facto standard for hardware-agnostic EEG acquisition. |
| **Lab Streaming Layer (LSL)** | C/C++/Python/MATLAB/Java/C#/JS/Rust/Julia | 724 | VERY ACTIVE | Real-time data streaming protocol. Sub-millisecond synchronization. Supports 150+ device classes. The de facto standard for multi-device synchronization in neuroscience. |
| **OpenBCI GUI** | Processing/Java | 892 | ACTIVE | Cross-platform visualization and recording for OpenBCI hardware. Also works with Cerelog ESP-EEG (forked version). |

### Offline Analysis & Processing

| Project | Language | Stars | Status | Description |
|---------|----------|-------|--------|-------------|
| **MNE-Python** | Python | 3,328 | VERY ACTIVE (v1.11.0) | The gold standard for EEG/MEG analysis in Python. Preprocessing, source localization, time-frequency analysis, connectivity, statistics, machine learning. Tightly integrated with NumPy/SciPy/scikit-learn. |
| **EEGLAB** | MATLAB | 747 | VERY ACTIVE (v2025.1.0) | The gold standard for EEG analysis in MATLAB. ICA, time-frequency, extensible plugin architecture. 34th annual workshop in 2025. |
| **FieldTrip** | MATLAB | 961 | VERY ACTIVE (v20251201) | Advanced MEG/EEG/iEEG analysis. Source reconstruction, beamformers, statistics. From Donders Institute, Radboud University. |
| **MOABB** | Python | 958 | VERY ACTIVE | Mother of All BCI Benchmarks. 36 public datasets, 30 ML pipelines, standardized evaluation across motor imagery (14), P300 (15), SSVEP (7) paradigms. |

### Real-Time Processing & BCI Platforms

| Project | Language | Stars | Status | Description |
|---------|----------|-------|--------|-------------|
| **OpenViBE** | C++ | N/A | ACTIVE (v3.7.0) | Visual programming BCI platform from INRIA. P300, motor imagery paradigms built in. No programming required for basic experiments. Windows/Linux. |
| **BCI2000** | C++ | N/A | ACTIVE | General-purpose BCI platform from Wadsworth Center. Supports diverse brain signals, output devices, operating protocols. Used in hundreds of research papers. Free for research/education. |
| **MetaBCI** | Python | 514 | ACTIVE | China's first open-source BCI platform (Tianjin University). 376 classes/functions, 14 public datasets, 16 analysis methods, 53 decoding models. MI, P300, SSVEP paradigms. |
| **BciPy** | Python | 145 | ACTIVE | RSVP Keyboard / P300 speller platform. Uses LSL for acquisition, PsychoPy for stimulus presentation. BSD-3 license. |
| **Timeflux** | Python | 187 | SEMI-ACTIVE (last push Dec 2024) | YAML-defined processing pipelines. Modular plugin architecture. Built on SciPy/Pandas/scikit-learn. Good design but documentation needs work. |
| **NeuroPype** | Python | N/A | ACTIVE (commercial + open components) | Real-time pipeline with visual drag-and-drop designer. Real-time artifact rejection. LSL integration. Pipeline Designer is open source; full suite is commercial. |
| **BrainBay** | C/C++ | 194 | ACTIVE | Open-source bio/neurofeedback. Windows-focused. Supports OpenBCI, OpenEEG, and other hardware. |

### Specialized Tools

| Project | Language | Stars/Status | Description |
|---------|----------|-------------|-------------|
| **EEGUnity** | Python | 55 / ACTIVE | Large-scale EEG dataset management. Intelligent data structure inference, cleaning, unification. Addresses the dataset heterogeneity problem. |
| **DISCOVER-EEG** | Python | ACTIVE | Fully automated resting-state EEG pipeline. Preprocessing, analysis, visualization with minimal user intervention. |
| **EEGsynth** | Python | ACTIVE | Brain-to-music/art performance platform. Converts neural signals to sound/image control. Used in live performances. |
| **amused-py** | Python | 55 / ACTIVE | First open-source BLE protocol implementation for Muse S. Stream raw EEG from Muse headsets. |

---

## 3. Open-Source BCI Applications

### Motor Imagery (Cursor/Wheelchair/Prosthetic Control)

- **OpenViBE Motor Imagery**: Built-in MI classification scenarios. CSP (Common Spatial Pattern) + LDA classifier. The most accessible entry point.
- **MetaBCI MI Module**: Multiple MI decoding models including CSP, FBCSP, EEGNet, and deep learning approaches.
- **MOABB MI Benchmarks**: 14 MI datasets with 30 standardized pipelines for comparison.
- **BCI2000 Cursor Control**: Classic mu-rhythm based cursor control paradigm.
- **OpenBCI Motor Imagery**: Community tutorials and example code for CSP-based classification.
- **EEG-Controlled Wheelchair**: Multiple open-source implementations using OpenBCI + ensemble ML. One system achieves real-time goal selection using 16-channel EEG.
- **CognitiveArm (2025)**: Real-time EEG-controlled prosthetic arm using BrainFlow + embedded deep learning. Recent breakthrough enabling individual finger-level robotic hand control from EEG.

### SSVEP (Steady-State Visual Evoked Potential)

- **MetaBCI SSVEP Module**: 7 SSVEP datasets, multiple classification algorithms.
- **TRCA-SSVEP**: Task-Related Component Analysis for SSVEP detection. 147 GitHub stars. Widely cited reference implementation.
- **Deep-SSVEP-BCI**: Deep neural network for SSVEP classification. 80 stars.
- **Hybrid P300-SSVEP Speller**: 94.29% accuracy, 28.64 bit/min information transfer rate in online tests.

### P300 Speller

- **BciPy RSVP Keyboard**: Full P300 speller with rapid serial visual presentation. LSL + PsychoPy integration.
- **OpenViBE P300 Speller**: Built-in P300 paradigm with visual programming interface.
- **BCI2000 P300**: Classic P300 speller matrix paradigm.
- **P300 Speller + LLM (2025)**: Recent research connecting P300 speller output to large language models for enhanced text prediction.
- **uniBrain Speller** (Tsinghua): One-stop open-source speller supporting multiple paradigms.

### Neurofeedback & Meditation

- **eeg_neurofeedback**: Open-source neurofeedback for meditation. Works with all popular EEG headsets. Adaptive fitting to brain patterns. Real-time sound feedback.
- **CortEX**: Meditation tool reading EEG + ECG in real time. Focus, relaxation, and heart rhythm analysis with session reports.
- **BrainBay**: Full neurofeedback application supporting multiple protocols and hardware.
- **OpenNFT**: Open Neurofeedback Training framework (originally fMRI, now extending to EEG).
- **Muse-based projects**: Multiple open-source meditation apps using Muse headsets via Bluetooth hacks (uvicMuse, BlueMuse, Mind Monitor).

### Sleep Staging

- **SIESTA**: Open-source Python toolkit for automated sleep stage detection using supervised training algorithms.
- **UTSN-L**: Open-source real-time sleep stage classification. 90% accuracy. GUI + closed feedback loop.
- **swa-matlab**: Sleep Wave Analysis toolbox for MATLAB.
- **Various deep learning models**: CNN, LSTM, and hybrid architectures achieving 87-90% accuracy on standard sleep datasets (Sleep-EDF, SVUH-UCD).

### Emotion Detection

- **EEG-Driven Emotion Detection**: Open-source classifier using ML techniques.
- **Public datasets**: SEED (15 subjects, 62 channels, positive/negative/neutral), DEAP (multimodal), SEED-IV (happy/sad/neutral/fear).
- **Methods**: Differential entropy features, multi-scale CNN, gated transformers. Alpha activity correlates with relaxation; beta with concentration/arousal.

### Music & Art Generation

- **EEGsynth**: Performance platform converting neural signals to sound/image control. Active in live art performances (2025 shows in Copenhagen).
- **Brain2Music** (Google Research): Reconstructs music from brain activity.
- **neural-art**: Generate images similar to MidJourney from brain data. 14 stars.
- **Scale-free brainwave music**: EEG amplitude to pitch, period to duration, power to intensity.
- **Real-time AI art from EEG**: TouchDesigner + Stable Diffusion pipeline driven by EEG data.

---

## 4. Commercial BCI Products (Comparison)

### Invasive

| Company | Product | Channels | Status | Price | Notes |
|---------|---------|----------|--------|-------|-------|
| **Neuralink** | N1 Implant | 1,024 electrodes | CLINICAL TRIALS | N/A | 12 patients as of Sept 2025. FDA Breakthrough Device Designation for speech restoration. $650M Series E (2025), ~$9B valuation. Plans for high-volume production and automated surgery in 2026. Blindsight (vision restoration) trials planned 2026. |
| **Paradromics** | Connexus | High-density | DEVELOPMENT | N/A | Competing with Neuralink on implantable BCIs. |

### Non-Invasive Consumer/Research

| Company | Product | Channels | Sample Rate | Electrodes | Price | Notes |
|---------|---------|----------|-------------|------------|-------|-------|
| **Emotiv** | EPOC X | 14 | 256 Hz | Semi-dry felt | $999 | Professional-grade. 9hr battery. Neuromarketing, research. |
| **Emotiv** | Insight | 5 | 128 Hz | Semi-dry polymer | $499 | Consumer/education. 20hr battery. |
| **Emotiv** | MN8 | 2 | 128 Hz | In-ear | $399 | Earbud form factor. Focus/attention tracking. 6hr battery. |
| **InteraXon** | Muse 2 | 4 EEG + 2 aux | 256 Hz | Dry (forehead + ear) | $249.99 | TP9, AF7, AF8, TP10. PPG, accelerometer. Meditation focused. |
| **InteraXon** | Muse S Athena | 4 EEG + fNIRS | 256 Hz | Dry fabric | $474.99 | First consumer EEG + fNIRS hybrid. Sleep tracking. Launched March 2025. |
| **NeuroSky** | MindWave Mobile 2 | 1 | 512 Hz | Dry (forehead) | $129.99 | FP1 position. 12-bit. 8hr battery. Cheapest commercial EEG. On-chip FFT. |
| **Neurosity** | Crown | 8 | 256 Hz | Dry Ag/AgCl | ~$1,000+ | CP3, C3, F5, PO3, PO4, F6, C4, CP4. On-device quad-core processor. Native AI app integration (Claude, ChatGPT). WiFi + BLE. |
| **g.tec** | Unicorn Hybrid Black | 8 | 250 Hz (24-bit) | Hybrid dry/wet | EUR 1,089 | 56 grams. 3hr battery. Unicorn Suite software. Validated in peer-reviewed research. |
| **CGX/Cognionics** | Quick-20 | 20 | 1,000 Hz (24-bit) | Dry | Research pricing | >100 dB CMRR. Ultra-high impedance (>47 GOhm). Research-grade dry electrode technology. |
| **CGX/Cognionics** | HD-72 | 64 | 1,000 Hz (24-bit) | Dry | Research pricing | Wireless. Flexible dry sensors through hair. Gold standard for mobile dry EEG. |
| **NextMind** | (discontinued) | Visual cortex | N/A | Dry | N/A | Acquired by Snap (2022). Visual cortex BCI for AR interfaces. Technology being integrated into Spectacles AR glasses. |
| **OpenBCI** | Cyton | 8 | 250 Hz (24-bit) | Any (open) | $1,249 | ADS1299. Open source hardware + software. 3D-printable headset. |

---

## 5. Key Technical Challenges

### Noise Rejection (50/60 Hz Mains Hum)

**The core problem**: Mains power produces a substantial peak in the EEG power spectrum at 50 Hz (Europe/Asia) or 60 Hz (Americas). This is directly in the gamma band and can overwhelm actual brain signals.

**Hardware approaches**:
- Driven Right Leg (DRL) circuit: Feeds inverted common-mode signal back to the patient, achieving >110 dB common-mode rejection. The ADS1299 has a built-in bias drive output for this purpose.
- Improved DgRL (Driving ground Reference Leg): Achieves 70+ dB additional rejection over standard patient grounding, 30 dB better than traditional DRL.
- Active electrodes: Front-end amplification on the electrode itself minimizes sensitivity to cable movement and common-mode interference.
- Shielded cables: Reduce capacitive coupling from mains.
- Active shielding: Guard traces driven at the same potential as the signal trace.

**Software approaches**:
- Notch filter at 50/60 Hz (most common, but removes real brain signal too)
- Spectrum interpolation: Replaces corrupted spectral bins with interpolated values
- Adaptive filtering: Multi-channel adaptive filters that track and subtract the interference
- CleanLine algorithm (EEGLAB plugin): More sophisticated spectral approach

**Parallel to EarthSync/Schumann**: The mains interference problem in EEG is fundamentally the same as in Schumann resonance measurement -- extracting microVolt-level signals in the presence of milliVolt-level 50/60 Hz interference. The first five Schumann resonance modes (0-35 Hz) directly overlap with EEG delta/theta/alpha/beta bands. The measurement challenges are nearly identical: both require high CMRR, careful grounding, and sophisticated digital filtering.

### Electrode-Skin Impedance

- Wet (gel) electrodes: 1-5 kOhm. Gold standard for signal quality. Messy, time-consuming setup.
- Dry electrodes: 10 kOhm to 2+ MOhm. Convenient but noisier. Requires ultra-high impedance amplifier inputs.
- Semi-dry electrodes: Moderate impedance. Compromise approach.
- Impedance mismatches between electrodes convert common-mode interference to differential (measurable) noise.
- Skin preparation (abrasion, cleaning) reduces impedance but is impractical for consumer applications.
- Active electrodes with on-board amplification (>47 GOhm input impedance, as in Cognionics) can handle high contact impedance.

### Motion Artifacts

- Electrode movement relative to skin causes impedance changes, generating large artifacts (mostly <20 Hz -- overlapping with delta/theta/alpha bands).
- Particularly problematic for wearable/mobile EEG.
- Solutions: Adaptive filtering using accelerometer reference, ICA decomposition, band-pass filtering, artifact rejection algorithms.
- IronBCI's integrated accelerometer/gyroscope is specifically designed to enable motion artifact removal.

### Reference & Ground Electrode Placement

- All EEG is measured differentially -- voltage at electrode X minus voltage at reference.
- Common reference positions: mastoids (behind ears), earlobes, linked ears, average reference.
- Ground/bias electrode: Typically forehead (FPz) or earlobe.
- Reference choice significantly affects signal morphology and interpretation.
- Average reference (computed) requires many channels (ideally 32+).

### ADC Requirements

| Parameter | Minimum for EEG | Ideal | Notes |
|-----------|-----------------|-------|-------|
| Resolution | 16-bit | 24-bit | EEG signals are 10-100 uV on top of DC offsets up to 300 mV |
| Sample Rate | 250 SPS | 500-1000 SPS | Must satisfy Nyquist for gamma (100 Hz). 250 SPS barely sufficient. |
| CMRR | >80 dB | >110 dB | ADS1299 achieves -110 dB. Critical for mains rejection. |
| Input Noise | <1 uV RMS | <0.25 uV RMS | Neurosity Crown achieves 0.25 uVrms. Must be below EEG amplitude. |
| PGA Gain | 1-12x | 1-24x | ADS1299 provides 1-24x. Needed to match signal to ADC input range. |
| Input Impedance | >100 MOhm | >1 GOhm | Higher is better, especially for dry electrodes. |

### Safety (Electrical Isolation)

**IEC 60601-1 requirements for patient-contact medical devices**:
- Type BF (Body Floating, applicable to EEG): Max 100 uA patient leakage (normal), 500 uA (single fault)
- Minimum input-to-output isolation: 4,000 VAC
- Minimum output-to-ground isolation: 1,500 VAC (Type BF)
- Most open-source EEG boards (OpenBCI, Cerelog, PiEEG) are NOT medically isolated
- **Critical safety practice**: Always operate open-source EEG on battery power. NEVER connect the host computer to mains while electrodes are on a person.
- VolksEEG is the only project explicitly targeting FDA/CE clearance.

---

## 6. EEG Signal Characteristics

### Frequency Bands

| Band | Frequency | Amplitude (scalp) | Associated State | Notes |
|------|-----------|-------------------|-----------------|-------|
| **Delta** | 0.5 - 4 Hz | 20-200 uV | Deep sleep (stage 3/4) | Should NOT be present in awake adults. Highest amplitude band. |
| **Theta** | 4 - 8 Hz | 5-100 uV | Drowsiness, light sleep, meditation | More prominent in children. Memory encoding. |
| **Alpha** | 8 - 13 Hz | 10-50 uV | Relaxed wakefulness, eyes closed | Hallmark of the awake adult brain. Posterior dominant. Blocks with eye opening. |
| **Beta** | 13 - 30 Hz | 5-30 uV | Active thinking, focus, anxiety | Often contaminated by frontal muscle artifact. |
| **Gamma** | 30 - 100+ Hz | 1-10 uV | Higher cognitive processing | Very difficult to measure with scalp EEG. Often contaminated by muscle artifact. Not reliably seen on scalp recordings. |

### Signal Characteristics

- **Typical scalp amplitude**: 10-100 uV (mostly 10-50 uV range)
- **Recording sensitivity**: Typically 5 uV/mm
- **Filter settings**: Standard clinical recording at 0.3-35 Hz. Research may extend to 0.1-100 Hz.
- **SNR**: Typical 3-25 dB for surface electrodes. Wet gel: ~24.9 dB. Semi-dry: ~24.4 dB. Dry: lower, highly variable.
- **Useful bandwidth**: Most clinical EEG activity is within 0.5-25 Hz

### Comparison to Schumann Resonance Measurement

| Parameter | EEG | Schumann Resonance |
|-----------|-----|-------------------|
| **Signal amplitude** | 10-100 uV (scalp) | ~1 pT (magnetic), ~0.5 mV/m (electric) |
| **Frequency range** | 0.5-100 Hz | 7.83, 14.3, 20.8, 27.3, 33.8 Hz (and harmonics) |
| **Key bands overlap** | Alpha (8-13 Hz) = SR1 (7.83 Hz); Beta low (13-16 Hz) = SR2 (14.3 Hz) | First 5 modes fall within EEG delta-beta range |
| **Noise floor challenge** | uV signals in mV interference | pT/fT signals in environmental noise |
| **50/60 Hz problem** | YES -- directly in gamma band | YES -- directly corrupts higher harmonics |
| **Key processing** | Bandpass, ICA, notch, CSP, wavelet | Bandpass, spectral averaging, notch |
| **Sensor challenge** | Electrode-skin impedance | Magnetic induction coil sensitivity |

**The overlap is striking**: Both require extracting extremely weak signals from the same frequency range (0.5-35 Hz) in the presence of the same dominant interference (50/60 Hz mains). Both require high-resolution ADCs, careful analog front-end design, and sophisticated digital signal processing. The Schumann resonance fundamental at 7.83 Hz falls squarely in the alpha/theta boundary -- the same frequency range most important for meditation/relaxation neurofeedback.

### Key Signal Processing Techniques

1. **Bandpass filtering**: Butterworth (2nd-4th order) for isolating frequency bands. Same as Schumann.
2. **FFT / STFT / Welch's method**: Spectral decomposition. Same techniques used in Schumann analysis.
3. **Independent Component Analysis (ICA)**: Blind source separation for artifact removal. EEG-specific.
4. **Common Spatial Patterns (CSP)**: Spatial filtering for motor imagery classification.
5. **Wavelet decomposition**: Time-frequency analysis with variable resolution.
6. **Artifact rejection**: Threshold-based, ICA-based, regression-based.
7. **Adaptive filtering**: Real-time noise cancellation using reference channels.
8. **Event-Related Potentials (ERP)**: Averaging time-locked to stimulus events (P300, N400, etc.).
9. **Coherence / connectivity analysis**: Phase coupling between channels.
10. **Deep learning**: EEGNet, CNNs, transformers for classification tasks.

---

## 7. EEG Foundation Models & Emerging Trends (2025-2026)

### EEG Foundation Models

A new paradigm is emerging: large-scale self-supervised EEG encoders (EEG-FMs) pre-trained on heterogeneous, unlabeled EEG data. These use transformer architectures with masking and quantization strategies. The goal is transferable neural representations that generalize across subjects, tasks, and hardware.

- **NeuroLM**: First multi-task foundation model treating EEG as a "foreign language" for LLMs.
- **EEG-GPT** (Neurosity): Foundational model for the Neurosity Crown.
- **EEGUnity**: Open-source tool for unifying diverse EEG datasets to feed foundation model training.
- **BrainFusion**: Open-source Python platform for multimodal physiological analysis.

### Key Challenges for Foundation Models
- EEG datasets are small, heterogeneous, and variable in quality
- No standardization across hardware, electrode configurations, experimental protocols
- EEG signals are inherently noisy and highly variable between individuals
- Lack of unified evaluation protocols

---

## 8. Gap Analysis & Opportunities

### What is the cheapest functional open-source EEG?

1. **BioAmp EXG Pill**: ~$10-20 for a single-channel analog front end. Needs external ADC/MCU. Not a complete system.
2. **Olimex EEG-SMT**: ~$107 for a complete 2-channel assembled board with USB.
3. **Creamino**: Low cost (academic BOM, Arduino Due based) but requires self-assembly.
4. **FreeEEG32**: Was $199 for 32 channels. Best value ever offered, but manufacturing wound down.
5. **PiEEG (4-ch)**: $250 if you already have a Raspberry Pi.

### What is the best documented?

1. **OpenBCI**: Best overall documentation. Extensive docs site, active forums, tutorials, GUI.
2. **MNE-Python**: Excellent API documentation and tutorials for software analysis.
3. **EEGLAB**: Decades of workshops, textbooks, and tutorial materials.
4. **BrainFlow**: Good API docs across 9 programming languages.
5. **BCI2000**: Extensive wiki and forum with 6,000+ posts.

### What is MISSING from the open-source ecosystem?

1. **Affordable, well-documented, CURRENTLY AVAILABLE hardware in the $100-300 range**. The FreeEEG32 wound down. The Ganglion's MCP3912 is inferior to the ADS1299. The Cerelog ESP-EEG at $350 is the closest but still pricey. There is a huge gap between the $107 Olimex (2-channel, antiquated) and the $350+ ADS1299-based boards.

2. **Integrated, plug-and-play BCI system for non-programmers**. Most open-source BCI requires significant technical skill. There is no "install this app, put on this headset, and control your computer" open-source solution.

3. **Medical-grade electrical isolation in open-source hardware**. Almost no open-source EEG board includes proper galvanic isolation. This is a serious safety gap.

4. **Standardized dry electrode system**. Dry electrodes remain the biggest hardware challenge. No open-source project has cracked affordable, reliable, through-hair dry electrodes. Most use wet gel or cheap dry contacts that work poorly.

5. **Unified real-time processing pipeline**. The ecosystem is fragmented: BrainFlow for acquisition, LSL for streaming, MNE for analysis, OpenViBE for BCI -- but no single, coherent, modern pipeline from electrode to application. Timeflux tried but has limited adoption.

6. **Consumer-quality mobile app for open-source hardware**. Commercial devices (Muse, Emotiv) have polished mobile apps. Open-source hardware has command-line tools and desktop GUIs.

7. **EEG-optimized analog front end reference design with modern components**. The ADS1299 is a decade-old chip. TI has newer parts. AD7771 offers alternatives. But no well-documented reference design compares options and provides a modern, optimized design.

8. **Behind-the-ear / in-ear form factor**. Commercial devices (Emotiv MN8 earbuds, Muse) are moving to discreet wearable form factors. Open-source hardware is still boards-and-wires.

### Where are the opportunities for a new project?

1. **"The ESP32-S3 EEG" -- Sub-$100, 4-8 channel, ADS1299-based board with WiFi/BLE**
   - The Cerelog ESP-EEG proves the concept but at $350. A stripped-down version targeting $75-150 with excellent documentation could fill the massive gap between the $107 Olimex and $350+ boards.
   - ESP32-S3 provides WiFi + BLE + sufficient processing power.
   - BrainFlow already supports custom boards.
   - This is the most obvious hardware opportunity.

2. **Open-source active dry electrode system**
   - The electrode is the weakest link in DIY EEG. An open-source active electrode with ultra-high impedance amplifier (like Cognionics' approach) would be transformative.
   - Could pair with any ADS1299-based board.
   - 3D-printable mounting system for different head positions.

3. **Unified EEG application framework**
   - A modern Python framework that combines acquisition (BrainFlow), streaming (LSL), processing (MNE), and application (neurofeedback, BCI) in one coherent package.
   - With a web-based UI (React/TypeScript) instead of desktop-only.
   - Real-time visualization, recording, playback, and BCI in the browser.

4. **EEG + Schumann resonance correlation tool**
   - Research shows real-time coherence between EEG spectral power and Schumann resonance frequencies.
   - A tool that simultaneously measures/correlates both would be unique and scientifically interesting.
   - Could share analog front-end expertise between the two domains.

5. **Medically isolated open-source front end**
   - An isolated analog front-end reference design (optocoupler or capacitive isolation) that any open-source EEG can use.
   - Addresses the safety gap without requiring each board to redesign.

### What could someone with EarthSync/Murmur-level analog front-end expertise bring?

The overlap between EarthSync (Schumann resonance measurement) and EEG is profound:

1. **Identical frequency range**: Both operate at 0.5-100 Hz. The signal processing toolchain is essentially the same.

2. **Identical noise challenges**: 50/60 Hz mains rejection is THE dominant challenge in both fields. Experience with notch filtering, adaptive filtering, and spectral techniques transfers directly.

3. **Analog front-end design**: High-gain, low-noise amplification of uV-level signals with high CMRR. The instrumentation amplifier + ADC pipeline is the same fundamental architecture.

4. **ADC expertise**: Understanding of sigma-delta ADCs, oversampling, decimation filtering, and noise shaping applies to both.

5. **Murmur's signal processing**: Passive radar signal extraction from noise is analogous to EEG artifact rejection -- both involve separating weak desired signals from strong interferers.

6. **Specific technical contributions possible**:
   - Better analog front-end reference design (the open-source EEG world lacks clean, well-documented AFE designs)
   - Novel mains rejection approaches (adaptive algorithms from Schumann work)
   - DRL/driven ground circuit optimization
   - Active electrode design with proper shielding
   - Low-cost isolated power supply design
   - Combined EEG + Schumann correlation system

---

## Summary Table: Hardware at a Glance

| Project | Channels | ADC | Sample Rate | Bit Depth | Price | Status | Form |
|---------|----------|-----|------------|-----------|-------|--------|------|
| OpenBCI Cyton | 8 (16 w/Daisy) | ADS1299 | 250 (125 w/Daisy) | 24 | $1,249 | Active | Board+headset |
| OpenBCI Ganglion | 4 | MCP3912 | 200 | 24 | ~$200 | Active | Board |
| HackEEG | 8 (32 stacked) | ADS1299 | 16,000 max | 24 | ~$350 | Semi-active | Arduino shield |
| FreeEEG32 | 32 (stackable) | 4x AD7771 | 128,000 | 24 | Was $199 | Wound down | Board |
| Cerelog ESP-EEG | 8 | ADS1299 | 250-16k | 24 | $350 | Active | Board |
| PiEEG | 8/16 | ADS1299 | 250-16k | 24 | $250-350 | Active | RPi HAT |
| IronBCI | 8 | ADS1299 | 250 | 24 | DIY | Active | Wearable |
| Olimex EEG-SMT | 2 | Legacy | 256 | ~10 | $107 | Active | Board |
| BioAmp EXG Pill | 1 | External | Varies | Varies | $10-20 | Active | Tiny AFE |
| Creamino | Multi | Varies | Varies | Varies | Low DIY | Semi-active | Arduino shield |
| Elata EEG | 8-32 | ADS1299 | Varies | 24 | ~$200-500 | Early | Board+RPi |

---

## Key Takeaways

1. **The ADS1299 dominates**: Nearly every serious open-source EEG uses the TI ADS1299. It is the single most important component in the ecosystem. Understanding this chip is understanding open-source EEG.

2. **BrainFlow is the universal translator**: Supporting 20+ boards across 9 languages, BrainFlow has become the HAL (hardware abstraction layer) of the EEG world. Any new hardware should target BrainFlow compatibility.

3. **The $100-300 hardware gap is real**: There is no good, currently-available, well-documented, ADS1299-based open-source EEG board under $300. This is the single biggest opportunity.

4. **Software is ahead of hardware**: MNE-Python, BrainFlow, and MOABB are genuinely excellent. The bottleneck is affordable, reliable hardware with good electrodes.

5. **Dry electrodes remain unsolved for open source**: Commercial companies (Cognionics, Emotiv, Neurosity) have proprietary dry electrode technology. No open-source equivalent exists at comparable quality.

6. **Foundation models are coming**: EEG-FMs will transform the field by enabling transfer learning across subjects and tasks, but they need standardized data pipelines -- another opportunity.

7. **The EarthSync/Schumann analog expertise transfers directly**: Both domains share the same frequency range, the same noise challenges, and the same fundamental measurement architecture. Cross-pollination is natural and would be genuinely novel.

---

Sources:
- [OpenBCI Shop](https://shop.openbci.com)
- [OpenBCI Documentation](https://docs.openbci.com)
- [BrainFlow](https://brainflow.org)
- [BrainFlow GitHub](https://github.com/brainflow-dev/brainflow)
- [MNE-Python](https://mne.tools)
- [MNE-Python GitHub](https://github.com/mne-tools/mne-python)
- [EEGLAB](https://sccn.ucsd.edu/eeglab)
- [FieldTrip](https://www.fieldtriptoolbox.org)
- [OpenViBE](https://openvibe.inria.fr)
- [Lab Streaming Layer](https://labstreaminglayer.org)
- [LSL GitHub](https://github.com/sccn/labstreaminglayer)
- [BCI2000](https://www.bci2000.org)
- [FreeEEG32 Crowd Supply](https://www.crowdsupply.com/neuroidss/freeeeg32)
- [HackEEG Crowd Supply](https://www.crowdsupply.com/starcat/hackeeg)
- [PiEEG](https://pieeg.com)
- [IronBCI GitHub](https://github.com/pieeg-club/ironbci)
- [Cerelog ESP-EEG](https://www.cerelog.com)
- [Cerelog GitHub](https://github.com/Cerelog-ESP-EEG/ESP-EEG)
- [Elata Biosciences](https://www.elata.bio)
- [BioAmp EXG Pill GitHub](https://github.com/upsidedownlabs/BioAmp-EXG-Pill)
- [Olimex OpenEEG](https://www.olimex.com/Products/EEG/OpenEEG/)
- [Creamino GitHub](https://github.com/ArcesUnibo/creamino)
- [VolksEEG GitHub](https://github.com/VolksEEG/VolksEEG)
- [Emotiv](https://www.emotiv.com)
- [Muse / InteraXon](https://choosemuse.com)
- [NeuroSky](https://store.neurosky.com)
- [Neurosity Crown](https://neurosity.co)
- [g.tec Unicorn](https://www.gtec.at)
- [CGX / Cognionics](https://www.cgxsystems.com)
- [Neuralink](https://neuralink.com)
- [MetaBCI GitHub](https://github.com/TBC-TJU/MetaBCI)
- [BciPy GitHub](https://github.com/CAMBI-tech/BciPy)
- [MOABB GitHub](https://github.com/NeuroTechX/moabb)
- [Timeflux](https://timeflux.io)
- [NeuroPype](https://www.neuropype.io)
- [BrainBay GitHub](https://github.com/ChrisVeigl/BrainBay)
- [EEGsynth](https://www.eegsynth.org)
- [TRCA-SSVEP GitHub](https://github.com/mnakanishi/TRCA-SSVEP)
- [Muse-LSL / amused-py](https://github.com/Amused-EEG/amused-py)
- [EEGUnity GitHub](https://github.com/Baizhige/EEGUnity)
- [ADS1299 Datasheet](https://www.ti.com/product/ADS1299)
- [IEC 60601-1 Guide](https://www.wallindustries.com/your-guide-to-iec-60601-1/)
- [Neuralink Milestones 2025](https://www.cerebralink.com/post/neuralink-s-milestones-in-2025-and-its-promising-future-in-2026)
- [EEG Foundation Models Survey](https://arxiv.org/abs/2507.11783)
- [EEG-FM Benchmark](https://github.com/Dingkun0817/EEG-FM-Benchmark)
