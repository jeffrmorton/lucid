# Lucid BCI Platform -- Hardware Design Research
**Compiled: 2026-03-26**
**Purpose: Exhaustive academic research for designing a state-of-the-art open-source BCI platform**

---

## 1. ADS1299 Circuit Design -- State of the Art

### 1.1 ADS1299 Core Specifications

The ADS1299 (TI datasheet SBAS499C) remains the gold-standard biopotential ADC for EEG as of 2026. No successor or superior alternative has been released by any manufacturer.

| Parameter | Value | Notes |
|-----------|-------|-------|
| Channels | 4 / 6 / 8 | ADS1299-4, ADS1299-6, ADS1299 |
| Resolution | 24-bit | Delta-sigma topology |
| Data rates | 250, 500, 1000, 2000, 4000, 8000, 16000 SPS | Configurable via CONFIG1 register DR bits |
| Input-referred noise (Gain=24, 250 SPS) | 0.14 uVrms / 1.0 uVpp | 65 Hz -3dB bandwidth at this rate |
| CMRR | -110 dB (datasheet typical) | Up to -143 dB achievable with optimized bias drive (see Section 1.4) |
| PGA gain settings | 1, 2, 4, 6, 8, 12, 24 V/V | Gain of 24 recommended for EEG |
| Input impedance | ~1 GOhm (DC, at PGA input) | But only ~10 MOhm effective with input MUX; external buffering needed for dry electrodes |
| Power consumption | ~6 mW/channel (typical) | AVDD=5V analog, DVDD=1.8-3.3V digital |
| AVDD/AVSS | +5V unipolar or +/-2.5V bipolar | Bipolar supply gives more headroom for electrode DC offset |
| Internal reference | 4.5V (VREFP - VREFN) | Can use external reference for lower noise |
| On-chip oscillator | 2.048 MHz | External clock also supported |
| Package | TQFP-64 | 0.5mm pitch; hand-solderable with care |

**Noise performance at Gain=24 across data rates** (from TI datasheet Table 4 and empirical measurements):

| Data Rate (SPS) | -3dB BW (Hz) | Input Noise (uVrms) | Input Noise (uVpp) |
|-----------------|--------------|---------------------|---------------------|
| 250 | 65 | 0.14 | 1.0 |
| 500 | 131 | 0.21 | 1.5 |
| 1000 | 262 | 0.28 | 1.97 |
| 2000 | 524 | 0.38 | ~2.7 |
| 4000 | 1049 | 0.52 | ~3.6 |
| 8000 | 2097 | 0.70 | ~5.0 |
| 16000 | 4194 | 0.95 | ~6.7 |

Measured OpenBCI Cyton noise: 0.16 uVrms at 250 SPS (Gain=24) -- consistent with datasheet. [An EEG Experimental Study Evaluating the Performance of Texas Instruments ADS1299, Sensors 2018]

### 1.2 Analog Front-End Topology

**DC-coupled (recommended for ADS1299 EEG):**
- OpenBCI Cyton and Cerelog ESP-EEG both use DC coupling.
- The ADS1299 was designed for DC-coupled operation. Its 24-bit resolution provides sufficient dynamic range to handle electrode DC offsets (up to ~300 mV half-cell potential) while still resolving microvolt EEG signals.
- DC coupling preserves very-low-frequency signals (slow cortical potentials, <0.5 Hz) and avoids the high-pass filtering artifacts introduced by coupling capacitors.
- DC offset is removed digitally in post-processing (trivial with 24-bit dynamic range).

**AC-coupled (alternative for high-offset environments):**
- Series coupling capacitors create a high-pass filter: f_c = 1/(2*pi*R*C).
- For EEG (0.5-100 Hz passband): 1 uF capacitor with 1 MOhm input resistance yields f_c ~ 0.16 Hz.
- Use C0G/NP0 ceramic or film capacitors for temperature stability and low leakage.
- Disadvantage: adds component count, creates potential for charge injection artifacts, limits slow-wave recording.
- Use case: when electrode polarization voltages are extreme or unpredictable (e.g., dissimilar electrode metals).

**Input impedance boosting:**
- The ADS1299 internal input impedance is ~1 GOhm at the PGA, but the effective impedance through the input MUX is lower (~10 MOhm).
- For dry electrodes (contact impedance 100-2000 kOhm), this is marginal. Signal attenuation = Z_electrode / (Z_electrode + Z_input).
- Solution: external unity-gain buffer (active electrode) at each electrode site. Op-amp requirements: >10 GOhm input impedance, <10 nV/sqrt(Hz) noise, rail-to-rail output, low input bias current (<1 pA).
- Recommended op-amps: OPA2376 (TI, 10 GOhm input Z, ESD protected), ADA4530 (ADI, 20+ TOhm), OPA378 (TI, zero-drift, 500 fA bias).

[Source: Oreate AI, "ADS1299 Polarization Voltage Improvement Solutions"]

### 1.3 Single-Ended vs. Differential Input Configuration

**Single-ended (referential) montage** -- most common for EEG:
- Each channel measures voltage between one electrode and a shared reference electrode.
- SRB2 pin: can be routed to the positive input of any/all channels as a shared reference.
- SRB1 pin: can be routed to the negative inputs of all channels as an alternate shared reference.
- Typical configuration: signal electrodes on positive inputs (INxP), SRB2 connected to reference electrode (e.g., mastoid/earlobe), negative inputs (INxN) internally routed to SRB2.

**Differential (bipolar) montage:**
- Each channel measures voltage between two electrode sites (INxP - INxN).
- Higher CMRR for the differential pair but fewer independent measurements per channel count.
- Used in EMG, some ECG applications, and specific EEG derivations.

**Recommendation for Lucid**: Support both via firmware/software configuration. Default to referential montage for EEG with SRB2 as reference bus. Expose all INxP and INxN pins to allow differential recording for EMG/EOG auxiliary channels.

### 1.4 Active Bias Drive Circuit (Driven Right Leg)

The ADS1299 has an integrated bias amplifier accessible through the BIAS_OUT, BIAS_IN, BIASREF, and BIASINV pins.

**Standard DRL circuit (TI EEG-FE reference)**:
- BIAS_OUT drives the patient through a 1 MOhm current-limiting resistor (safety).
- BIAS_IN receives the averaged common-mode signal from selected channels.
- Feedback loop: inverted common-mode voltage fed back to patient reduces interference.
- External RC on BIASINV/BIASREF sets loop stability (typical: 1.5 MOhm + 47 nF).

**Optimized 143 dB CMRR configuration** (documented on TI E2E forums):
- Remove RC components on BIASINV and BIASREF pins.
- Place a 1 MOhm series resistor on BIAS_OUT to limit patient current.
- This modification eliminates the phase lag introduced by the external RC, maximizing the bias feedback loop bandwidth and CMRR.
- Result: 143 dB CMRR at gain 24 -- sufficient to reject 50/60 Hz mains without any notch filter.

**Cerelog ESP-EEG implementation:**
- "True closed-loop active bias" that continuously measures common-mode noise, inverts it, and feeds it back through a dedicated bias electrode.
- This is the most modern open-source implementation of the ADS1299 bias drive.

[Sources: TI E2E Forums; TI SLAU443B EEG Front-End Performance Demonstration Kit User's Guide; Cerelog documentation]

### 1.5 Input Protection and ESD

**Critical design requirement:** EEG electrodes are directly connected to patients. ESD events (human body model: 2-15 kV) can damage the ADS1299 inputs.

**Recommended protection circuit:**
1. Series resistors (4.7-10 kOhm) on each input pin -- limits current during ESD, also forms part of anti-aliasing RC filter.
2. TVS (Transient Voltage Suppressor) diodes or ESD protection diodes (bidirectional, low capacitance) to AVSS/AVDD.
3. Gas discharge tubes (GDTs) for higher-energy protection in clinical environments.
4. Total added capacitance from protection components must be matched between channels to maintain CMRR.

**Anti-aliasing filter:**
- R_input (4.7-10 kOhm) + C_input (1-10 nF) forms a first-order low-pass filter.
- For 250 SPS (65 Hz bandwidth): R=10k, C=1nF gives f_c = 15.9 kHz (adequate, well above Nyquist).
- The ADS1299 internal sinc3 digital filter provides the primary anti-aliasing; the external RC is primarily for EMI/ESD protection.

**Patient current limiting:**
- 1 MOhm resistor in series with BIAS_OUT limits maximum patient current to ~5 uA at 5V supply -- well below the 10 uA limit for Type CF classification.
- For additional safety: add a 100 nF capacitor from BIAS_OUT to AVSS to block any DC component.

### 1.6 Digital Filter Configuration

The ADS1299 uses a third-order sinc3 digital filter with configurable decimation ratio.

**Filter characteristics:**
- Sinc3 provides -3dB bandwidth of approximately 0.262 * f_data (e.g., 65 Hz at 250 SPS).
- First null at the data rate (e.g., 250 Hz at 250 SPS), providing natural rejection of frequencies at multiples of the output data rate.
- Stop-band attenuation: 40 dB for sinc3.

**Optimal settings by application:**

| Application | Recommended Data Rate | -3dB BW | Noise (uVrms) | Notes |
|-------------|----------------------|---------|---------------|-------|
| Neurofeedback | 250 SPS | 65 Hz | 0.14 | Lowest noise. Sufficient for alpha/theta/beta. |
| Motor imagery BCI | 250-500 SPS | 65-131 Hz | 0.14-0.21 | 250 SPS adequate; 500 SPS for gamma access. |
| P300/ERP | 500-1000 SPS | 131-262 Hz | 0.21-0.28 | Higher rate improves temporal resolution for ERP latency measurement. |
| Sleep staging | 250 SPS | 65 Hz | 0.14 | Delta through beta bands sufficient. |
| SSVEP | 250-500 SPS | 65-131 Hz | 0.14-0.21 | Depends on stimulus frequency range. |
| High-gamma research | 1000-2000 SPS | 262-524 Hz | 0.28-0.38 | Rarely needed for scalp EEG. |
| EMG (auxiliary) | 2000-4000 SPS | 524-1049 Hz | 0.38-0.52 | EMG bandwidth extends to ~500 Hz. |

### 1.7 Power Supply Design

**ADS1299 supply rails:**
- AVDD: +5.0V (unipolar) or +2.5V (bipolar, with AVSS at -2.5V)
- DVDD: +1.8V to +3.3V
- VCAP1-4: Internal reference/regulator decoupling (external 1 uF capacitors required)

**Recommended power architecture:**

1. **Battery input** (3.7V LiPo or 2x AA/AAA) -> boost converter to 5V (for AVDD)
2. **AVDD rail**: Low-noise LDO regulator (e.g., TPS7A49, ADP150, LP5907) from 5V boost. PSRR >60 dB at 1 MHz. Output noise <10 uVrms.
3. **DVDD rail**: Separate LDO from battery or from 5V. Standard 3.3V LDO adequate (less noise-sensitive).
4. **Ferrite bead isolation**: Place ferrite beads between AVDD/DVDD supply feeds to block high-frequency digital noise from contaminating the analog supply.
5. **Decoupling**: 100 nF + 1 uF ceramic on every AVDD and DVDD pin, placed as close to the IC as physically possible.

**Ground topology:**
- AGND and DGND should be connected at a single star point directly beneath the ADS1299 IC.
- Route digital traces on opposite side of PCB from analog traces.
- Maintain unbroken ground plane under all analog signal traces.
- Never route analog signals over ground plane gaps or splits.

**Switching noise mitigation:**
- If using a switching boost/buck converter: follow with a low-noise LDO (>40 dB PSRR at switching frequency).
- Keep switching converter physically distant from ADS1299 and analog input traces.
- Use ferrite beads + LC filtering between switcher output and LDO input.

### 1.8 PCB Layout Best Practices

1. **4-layer PCB minimum**: Top (signals), Inner 1 (unbroken ground), Inner 2 (power), Bottom (signals/components).
2. **ADS1299 placement**: Center of board. Keep analog input traces as short as possible.
3. **Star ground**: Single connection point between AGND and DGND under the ADS1299.
4. **Differential input routing**: Route INxP and INxN as parallel pairs. Match trace lengths.
5. **Guard rings/traces**: Active guard driven at the same potential as signal traces to reject capacitive pickup.
6. **Series damping resistors**: 22-100 ohm on all digital output lines (DOUT, DRDY, CLK) to reduce ringing and EMI.
7. **Component placement**: All decoupling capacitors within 3mm of their associated power pins.
8. **No vias under ADS1299**: Thermal pad connects to AGND through multiple vias, but avoid signal vias under the IC.
9. **Input connector placement**: EEG electrode connectors at board edge, with short traces to ADS1299 inputs.

### 1.9 ADS1299 vs. Alternatives Comparison

| Parameter | ADS1299 | ADS1298 | ADS1294 | AD7771 (FreeEEG32) | MCP3912 (Ganglion) |
|-----------|---------|---------|---------|---------------------|---------------------|
| Target application | EEG/biopotential | ECG/biopotential | ECG | General-purpose SAR | General-purpose |
| Channels | 4/6/8 | 4/6/8 | 4 | 8 | 4 |
| Resolution | 24-bit | 24-bit | 24-bit | 24-bit | 24-bit |
| Max PGA gain | 24x | 12x | 12x | 8x (external) | N/A |
| Input noise (best) | 1.0 uVpp | Higher than ADS1299 | Higher | 0.22 uV measured (FreeEEG32) | Significantly higher |
| CMRR | -110 dB | -105 dB | -105 dB | N/A (external) | Lower |
| Built-in bias drive | Yes | Yes | Yes | No | No |
| SRB pins | Yes (SRB1, SRB2) | No | No | No | No |
| Lead-off detection | Yes (AC/DC) | Yes | Yes | No | No |
| Impedance measurement | Yes (internal test signals) | Limited | Limited | No | No |
| Price (qty 1) | ~$30-45 | ~$20-30 | ~$15-20 | ~$15-20 | ~$5-8 |
| Ecosystem for EEG | Extensive | Limited | Limited | Minimal | Minimal |

**Key conclusion**: The ADS1299 remains unmatched for EEG applications. Its SRB pins, built-in bias drive, lead-off detection, impedance measurement, and 24x gain are specifically designed for EEG and have no equivalent in competing parts. No newer alternative has been announced by TI or any competitor as of March 2026.

**2025 design trend** (ACM 2025 conference paper): Modern ADS1299 systems pair the ADC with STM32 microcontrollers using DMA transfer for jitter-free data at all sample rates. The ESP32-S3 (Cerelog) and nRF5340 (BioGAP-Ultra) are also proven modern MCU choices.

---

## 2. Dry Electrode Technology -- Latest Research

### 2.1 Electrode-Skin Impedance: Quantitative Data

| Electrode Type | Typical Impedance Range | Best Achievable | Measurement Frequency |
|---------------|------------------------|----------------|----------------------|
| Wet gel (Ag/AgCl + conductive paste) | 1-10 kOhm | <1 kOhm with skin prep | 10 Hz |
| Semi-dry (saline sponge) | 10-100 kOhm | ~10 kOhm | 10 Hz |
| Semi-dry (conductive hydrogel) | <400 ohm to 100 kOhm | <400 ohm (2025 hydrogel) | 10 Hz |
| Dry contact (metal pins on skin) | 50-300 kOhm (forehead) | ~20 kOhm (SAN/Ir-TiO2) | 10 Hz |
| Dry contact (through hair) | 100-2000 kOhm | ~100 kOhm (multi-pin, good contact) | 10 Hz |
| Dry non-contact (capacitive) | 1-5 MOhm | ~500 kOhm (conductive foam) | 10 Hz |

**Critical threshold:** Contact impedances below 40 kOhm have negligible effects on EEG signal quality in practical applications. Above this, impedance mismatch begins to degrade CMRR.

[Sources: PMC9855417; PMC4168519; AIP Advances 15(4), 2025]

### 2.2 Spring-Loaded Pin Electrodes

**Design parameters from literature:**

| Parameter | Typical Range | Notes |
|-----------|--------------|-------|
| Number of pins | 5-30 per electrode | More pins = lower aggregate impedance |
| Pin diameter | 1-2 mm | Spherical tip for comfort |
| Pin length | 6-10 mm | Must penetrate through hair to scalp |
| Spring force per pin | 0.1-0.5 N | Higher force = lower impedance, but more discomfort |
| Total electrode diameter | 14-20 mm | Circular base with pins in ring formation |
| Pin material | Gold-plated stainless steel, Ag/AgCl coated | Gold is most common for corrosion resistance |
| Pin spacing (center-to-center) | 2-3 mm | Trade-off: closer = more pins but smaller contact area per pin |

**g.tec g.SAHARA:**
- 8 gold-coated pins in circular formation
- Conductive polymer base (proprietary)
- Hybrid design: can be used with or without gel
- Patented design, validated in numerous research publications

**Microneedle arrays (research-grade):**
- 30 needles per electrode array
- Spherical tip diameter: 1 mm
- Height: 6 mm
- Center-to-center spacing: 2.4 mm

[Sources: MDPI Sensors 19(20):4572, 2019; g.tec product documentation; PMC12389868]

### 2.3 Comb/Finger Electrodes for Through-Hair Contact

**3D-printed finger electrodes:**
- Rounded finger-like structures penetrate hair without causing discomfort.
- Typical design: 8 fingers, each 6 mm long and 2 mm diameter, on a 14 mm diameter base.
- Finger tip profile, diameter, and length can be customized per-individual via 3D printing in <90 minutes.
- Two manufacturing approaches:
  1. Intrinsically conductive: Printed from PLA/ABS mixed with carbon-based conductive compound.
  2. Coated: Standard plastic printed, then coated with conductive material (silver paint, electroless plating).

**Conductive hook fabric electrodes:**
- Conductive hook fabric (Velcro-like) with resistance of 1 ohm/sq.
- Pointed hooks establish direct contact with skin through hair.
- Extremely low cost, mechanically robust, washable.
- Published 2023 (PMC10537404).

**Spring-loaded comb designs:**
- Fingers fabricated with integrated springs (stereolithography 3D printing).
- Spring constant determined from contact model between electrode and scalp.
- Flexible fingers conform to scalp curvature, maintaining contact during movement.

[Sources: PMC10255664 (2023); MDPI Sensors 16(10):1635 (2016); PMC10537404 (2023)]

### 2.4 Conductive Polymer Electrodes

**PEDOT:PSS (poly(3,4-ethylenedioxythiophene):poly(styrene sulfonate)):**
- High conductivity (~1000 S/cm achievable), biocompatible, flexible.
- Novel composite: PEDOT:PSS adsorbed on carbon particles achieves low skin-electrode contact impedance through ion exchange properties.
- EEG measurements show correlation >= 0.9 with commercial wet Ag/AgCl electrodes.
- 2025 status: PEDOT:PSS-based bioelectronics for brain monitoring reviewed in Nature Microsystems & Nanoengineering. Active research area.

**PEDOT:PSS/PDMS composite:**
- Surface resistivity of 67.23 ohm/sq on conductive cotton fabric substrate.
- Suitable for wearable, washable electrodes.

**TPU-Ag (Thermoplastic Polyurethane with Silver):**
- 2:1 mass ratio TPU:Ag
- Claw-shaped electrode: impedance approximately 100 ohm
- 3D printable (FDM process)

[Sources: PubMed 38083429; Nature 41467-020-18503-8; PMC12389868]

### 2.5 Carbon Nanotube / Graphene Electrodes

**CNT/aPDMS (Carbon Nanotube / adhesive PDMS):**
- SNR: 3.71 +/- 0.17 dB (vs. 2.79 +/- 0.13 dB without CNTs)
- Motion artifact deviation: only 1.4x higher than wet electrodes (vs. 5x without CNTs)
- Wrinkled surface morphology increases contact area.

**CNT-Graphene hybrid electrodes:**
- SWCNT + reduced graphene oxide (RGO) in PDMS matrix.
- Laser irradiation reduces resistance 13-fold to 8 +/- 2 kOhm.
- Long-term ECG monitoring demonstrated; applicable to EEG.

**Graphene/TiO2 nanotube electrode:**
- Few-layer graphene combined with TiO2 nanotube nanoarchitecture.
- Demonstrated in robot arm control BCI application.
- SAN/Ir-TiO2 flexible electrode: average impedance 19.9 kOhm in hairy regions.

**2025-2026 emerging materials:**
- MXene-polymer composites (2D transition metal carbides/nitrides)
- Self-healing conductive hydrogels
- Ion-conductive biomimetic materials
- All expected to lower contact impedance and enhance long-term stability.

[Sources: PMC12389868; ScienceDirect S0925963525009525; ScienceDirect S0924424723001425]

### 2.6 Active Dry Electrodes (Integrated Preamplifier)

**Operating principle:**
An active electrode incorporates a unity-gain buffer amplifier directly at the electrode site, converting the high-impedance electrode-skin interface to a low-impedance driven signal before it reaches the cable. This architecture:
1. Eliminates cable motion artifacts (cable sees low-impedance source)
2. Rejects capacitive pickup on cables
3. Enables use of high-impedance dry electrodes (100k-2M ohm contact impedance)
4. Enables active shielding of the cable (driven shield at signal potential)

**Circuit topology (Two-Wired Bootstrap):**
- First buffer: picks up signal from skin (high input Z)
- Second buffer: drives active shield/guard and output cable
- Bootstrap topology reduces input capacitance and increases effective input impedance beyond the op-amp's native specification.
- Result: >10 GOhm effective input impedance from an op-amp with 1 GOhm native input Z.

**Recommended op-amps for active electrode buffer:**
| Op-Amp | Input Z | Noise | Bias Current | Notes |
|--------|---------|-------|-------------|-------|
| OPA2376 (TI) | 10 GOhm | Low | <1 pA | Built-in ESD protection. Used in published active EEG electrode designs. |
| ADA4530 (ADI) | >20 TOhm | Very low | <20 fA | Femtoampere-grade. Premium choice. |
| OPA378 (TI) | Very high | Low | 500 fA | Zero-drift for DC accuracy. |
| LMP7702 (TI) | 1 TOhm | Low | <100 fA | Dual, low cost. |

**Commercial implementations:**
- **Cognionics/CGX**: Patented active electrodes with ultra-high impedance amplifiers, active shielding, and noise cancellation. >100 dB CMRR. 24-bit resolution at 1000 SPS. Research-grade dry EEG.
- **g.tec g.Nautilus PRO Flexible (2026)**: Active electrodes, 24-bit resolution, "the best EEG device of 2026" per g.tec's own marketing.
- **BioSemi ActiveTwo**: Gold-standard active wet electrode system for research. Extremely high input impedance.

**Power budget for active electrodes:**
BioGAP-Ultra active electrode system: 2.8 mW total for all active electrodes in 16-channel EEG headband configuration.

[Sources: MDPI Sensors 19(20):4572; PubMed 28113349; PMC5156995; g.tec product page]

### 2.7 Capacitive (Non-Contact) Electrodes

**Feasibility assessment:**
- Capacitive electrodes sense the electric field through a dielectric (air, fabric, hair) without ohmic contact.
- Electrode-skin coupling is purely capacitive: impedance = 1/(2*pi*f*C).
- For typical electrode area (1 cm^2) and 1 mm air gap: C ~ 1 pF, Z ~ 16 GOhm at 10 Hz.
- This requires amplifier input impedance >> 16 GOhm -- achievable with specialized circuits but challenging.

**Current status (2025-2026):**
- Impedance range: 1-5 MOhm (when contact exists through fabric/hair).
- Signal quality: significantly lower than contact electrodes. Suitable for gross brain state (alpha detection) but not for precision EEG.
- Highly sensitive to motion (distance changes modulate capacitance, creating low-frequency artifacts).
- Best results achieved with conductive polymer foam on the electrode surface (reduces effective air gap).
- Some success measuring EEG through hair in hairy occipital/parietal regions using adaptive mechanical design with bandpass filtering.

**Verdict for Lucid:** Capacitive non-contact electrodes are NOT recommended as the primary electrode technology. They may be considered as a secondary option for specialized use cases (e.g., through-pillow sleep EEG). Active dry contact electrodes are the better path.

[Sources: PMC9855417; ScienceDirect S0924424725012026; PMC4168519]

### 2.8 Conductive Hydrogel / Semi-Dry Electrodes (2025 Breakthrough)

**2025 breakthrough: Anti-bacterial semi-dry hydrogel electrode** (Nature Microsystems & Nanoengineering, 2025):
- Material: N-acryloyl glycinamide + hydroxypropyltrimethyl ammonium chloride chitosan.
- Contact impedance: <400 ohm (average) over 12 hours.
- Ionic conductivity: 0.39 mS/cm.
- Compression modulus: 65 kPa.
- Stability: impedance remains below 100 kOhm on scalp for 12 hours; wet electrodes fail after 7-8 hours due to dehydration.
- Anti-bacterial: inhibits both E. coli and S. epidermidis growth.
- Reusable: 21 consecutive days of monitoring with no significant SNR decrease.
- Self-electrolyte: builds ion channels at electrode-skin interface without external gel.

**Comparison vs. wet electrodes:**
- Hydrogel electrode: 12+ hours stable recording. Impedance <100 kOhm throughout.
- Wet gel electrode: signal degradation after 7-8 hours. Requires reapplication.
- This makes hydrogel electrodes SUPERIOR to wet electrodes for long-duration recording.

**Recommendation for Lucid:** Hydrogel semi-dry electrodes represent the most promising electrode technology for 2026. They combine the signal quality approaching wet electrodes with the convenience of dry electrodes and surpass both in long-term stability. Consider designing electrode holders compatible with both dry contact pins AND replaceable hydrogel inserts.

[Sources: Nature 41378-025-00908-4 (2025); Nature 41378-023-00524-0 (2023)]

### 2.9 The Impedance Problem: ADS1299 + Dry Electrodes

**The fundamental challenge:**
- Dry electrode impedance: 50-2000 kOhm.
- ADS1299 effective input impedance: ~10 MOhm (through input MUX).
- Signal attenuation at worst case: Z_elec/(Z_elec + Z_input) = 2000k/(2000k + 10000k) = 17% signal loss.
- More critically: impedance MISMATCH between electrodes converts common-mode interference to differential signal.

**CMRR degradation formula:**
- Effective CMRR = Amplifier_CMRR - 20*log10(delta_Z_electrode / Z_input)
- If two dry electrodes have 100 kOhm and 200 kOhm impedance (100 kOhm mismatch):
  - With ADS1299 direct (10 MOhm): CMRR degradation = 20*log10(100k/10M) = -40 dB
  - With active electrodes (10 GOhm buffer): CMRR degradation = 20*log10(100k/10G) = -100 dB
  - This means active electrodes recover ~60 dB of CMRR compared to passive dry electrodes.

**Practical impact on 50/60 Hz rejection:**
- Mains common-mode voltage on body: ~1-10 mV.
- Required differential rejection to reach <1 uV residual: >60 dB.
- ADS1299 native CMRR (-110 dB) minus impedance mismatch penalty must exceed 60 dB.
- With passive dry electrodes (40 dB penalty): 110 - 40 = 70 dB net -- marginal.
- With active dry electrodes (100 dB penalty offset): 110 - 10 = 100 dB net -- excellent.

**Conclusion for Lucid:** Active electrodes are ESSENTIAL for reliable dry electrode operation. Passive dry electrodes connected directly to ADS1299 inputs will produce degraded CMRR and unreliable 50/60 Hz rejection.

### 2.10 Commercial Dry Electrode Systems Comparison

| System | Electrode Type | Impedance Approach | Input Z | CMRR | Price |
|--------|---------------|-------------------|---------|------|-------|
| Cognionics Quick-20 | Dry active comb | Ultra-high Z active preamp | "Patented" (likely >47 GOhm) | >100 dB | Research pricing |
| Cognionics HD-72 | Dry active flexible | Ultra-high Z active preamp | Same | >100 dB | Research pricing |
| g.tec g.SAHARA Hybrid | 8-pin gold + polymer | Hybrid gel/dry | Standard g.tec | Standard | Included with g.tec systems |
| g.tec g.Nautilus PRO | Active dry | Active electrode | High | High | EUR ~10,000+ |
| Emotiv EPOC X | Semi-dry felt (saline) | Wet/saline soak | Standard | Standard | $999 |
| Muse 2 / Muse S Athena | Dry metal (forehead), conductive (ear) | Forehead = hairless, low Z | Standard | Standard | $250-475 |
| Neurosity Crown | Dry Ag/AgCl | 8 positions, no hair region | Standard | Standard | ~$1000 |

---

## 3. Multi-Modal Physiological Sensing

### 3.1 EEG + fNIRS (Functional Near-Infrared Spectroscopy)

**How fNIRS works:**
- Near-infrared light (600-1000 nm) passes through skull and brain tissue.
- Oxygenated hemoglobin (HbO2) and deoxygenated hemoglobin (HHb) absorb different wavelengths.
- Dual-wavelength measurement (typically ~750 nm and ~850 nm) allows computing relative concentrations via the modified Beer-Lambert law.
- Provides hemodynamic/metabolic information complementary to EEG's electrical information.
- Temporal resolution: 1-10 Hz (hemodynamic response is slow, ~5-8 second delay from neural activity).
- Spatial resolution: 2.3-3.3 cm (with high-density DOT).
- Penetration depth: ~1.5-2.5 cm from scalp surface (cortical surface only).

**Low-cost implementation (2025-2026):**

| System | Channels | Cost | LEDs | Photodiode | Sampling | Open Source |
|--------|----------|------|------|------------|----------|-------------|
| OpenNIRScap (2025) | 24 detector + 8 emitter | $419 | 660 nm + 940 nm | VBPW34S (Vishay) | 1 kHz / 12-bit | Yes |
| DIY-fNIRS Headband | 4 | $215 | Dual wavelength | Standard | 10 Hz / 12-bit | Yes |
| biosignalsplux fNIRS | 1 | $789 | Dual wavelength | Standard | 500 Hz / 16-bit | No |
| Muse S Athena (consumer) | 5-optode bilateral | $475 | 730nm + 850nm + 660nm (PPG) | Integrated | 64 Hz / 20-bit | No |
| NIRx WINGS2 (research) | High-density | >$50,000 | Multiple | Multiple | Variable | No |

**OpenNIRScap specifications (May 2025, arXiv:2505.20509):**
- Total cost: $419 for complete system.
- 24 custom sensor boards with dual-wavelength LED emitters and photodiode detectors.
- Photodiode: VBPW34S (Vishay), spectral range 440-1100 nm, dark current 2 nA.
- Amplification: two-stage (transimpedance + non-inverting AC gain) using AD8618 op-amp (10 nV/sqrt(Hz) noise, 23-60 uV offset).
- SNR: 52.3 dB average (range 50.3-53.8 dB).
- MCU: STM32L476.
- USB isolation: ADuM4160.
- Battery runtime: >5 hours.
- Sensor spacing: 35 mm center-to-center.

**EEG-fNIRS mobile combined system (February 2026, MDPI Sensors 26(4):1342):**
- EEG: ADS1299-based, 8 channels.
- fNIRS: dual-wavelength LEDs (750/850 nm) + OPT101 photodiode/transimpedance amplifier.
- Digitally controlled constant-current LED drivers.
- Photodetector responsivity: 0.3-0.6 A/W across 750-850 nm.
- Wireless operation for ambulatory brain research.

**Can it be done cheaply?** YES. The OpenNIRScap proves a 24-channel fNIRS system can be built for $419 using off-the-shelf components. A combined EEG+fNIRS Lucid module is feasible at the $100-200 incremental cost level.

**Synchronization requirement:** EEG and fNIRS data need NOT be precisely synchronized at the sample level because the hemodynamic response is inherently slow (seconds). However, event markers must be synchronized to <10 ms for proper ERP-hemodynamic correlation. LSL provides sub-millisecond synchronization which is more than adequate.

[Sources: arXiv:2505.20509v1; MDPI Sensors 26(4):1342; PMC12592382; PMC8469799]

### 3.2 EEG + EMG (Electromyography)

**Same ADC, different electrode placement:**
- EMG signals: 0.1-5 mV amplitude (10-100x larger than EEG), bandwidth 20-500 Hz.
- The ADS1299 can record both EEG and EMG simultaneously on different channels.
- EMG channels benefit from higher sample rates (2000-4000 SPS) and lower PGA gain (1-6x).
- Challenge: ADS1299 has a single global data rate setting for all channels. If mixing EEG (250 SPS) and EMG (2000 SPS), must use the higher rate for all channels and digitally filter/downsample the EEG channels.

**BioGAP-Ultra implementation:**
- 16-channel ADS1298 (dual IC) records both EEG and EMG.
- EMG sleeve form factor: 12 forearm + 4 upper arm channels in 6x4 array.
- EEG headband: 16 dry electrode channels.
- Single unified data acquisition framework for both.

**Practical for Lucid:** Dedicate 2-4 of the 8 ADS1299 channels to EMG (facial muscles for jaw clench detection, neck muscles for head movement). Run at 500-1000 SPS as compromise rate. Use differential recording for EMG channels.

### 3.3 EEG + EOG (Electrooculography)

**Eye movement as reference + input:**
- VEOG (Vertical EOG): electrodes above and below one eye. Detects blinks and vertical eye movements.
- HEOG (Horizontal EOG): electrodes at outer canthi of both eyes. Detects saccades.
- EOG signals: 50-3500 uV amplitude (much larger than EEG).
- Bandwidth: 0-100 Hz.

**Dual purpose:**
1. **Artifact removal**: EOG channels serve as reference signals for regression-based or ICA-based ocular artifact removal from EEG channels.
2. **Eye-tracking input**: EOG provides low-resolution gaze direction data usable as a BCI input modality.

**Integration with ADS1299:**
- EOG can be recorded on 2-4 dedicated ADS1299 channels with lower gain (1-6x due to high amplitude).
- Challenge: ADS1299 has global PGA gain setting. Either use a gain that works for both (gain=6-12) or use separate ADS1299 ICs for EEG and EOG/EMG.
- Alternative: external voltage divider on EOG channels to attenuate signal before PGA.

**Artifact removal methods:**
- Traditional: regression subtracts scaled EOG from EEG (requires dedicated EOG reference channels).
- Modern: ICA (Independent Component Analysis) identifies and removes ocular components without requiring explicit EOG channels (but works better with them).
- Most effective: combined EOG reference + ICA.

### 3.4 EEG + PPG (Photoplethysmography)

**Heart rate from optical sensor:**
- PPG uses LED (green: 525 nm for wrist, or IR: 850 nm for ear/forehead) and photodiode.
- Measures blood volume pulse from reflected/transmitted light changes.
- Provides: heart rate, heart rate variability (HRV), SpO2 (with dual wavelength), respiratory rate.
- Sampling rate: 25-100 Hz adequate.
- Can be integrated into ear clip or forehead band alongside EEG electrodes.

**Combined implementations:**
- Muse S Athena: EEG + fNIRS + PPG in single headband. PPG uses triple wavelength (660, 730, 850 nm).
- BioGAP-Ultra: EEG-PPG headband (PPG on earlobe) at 32.8 mW total power.
- IronBCI: Includes pulse oximetry among its sensor suite.

**Value for Lucid:**
- Heart rate as physiological state indicator (stress, relaxation, arousal).
- HRV provides window into autonomic nervous system (parasympathetic/sympathetic balance).
- Cardiac artifact removal: PPG provides precise heartbeat timing for ECG artifact subtraction from EEG.
- Implementation cost: ~$2-5 for MAX30102 or MAX86150 PPG sensor module.

### 3.5 EEG + EDA/GSR (Electrodermal Activity)

**Stress/arousal indicator:**
- EDA measures skin conductance changes due to sweat gland activity (sympathetic nervous system).
- Electrode placement: typically fingers or palm (highest sweat gland density). Can also be measured at wrist.
- Measurement: apply small DC voltage (0.5V) across two electrodes, measure current (skin conductance 1-20 uS range).
- Sampling rate: 10-100 Hz adequate (EDA signals are very slow, <1 Hz for tonic, <5 Hz for phasic).

**Integration approach:**
- EDA requires separate measurement circuit (DC excitation, not AC like EEG).
- Cannot share ADS1299 channels (wrong measurement topology).
- Simple implementation: dedicated EDA ADC (e.g., ADS1115 16-bit, $2) with voltage divider circuit.
- More integrated: use one ADS1299 channel with external DC excitation circuit, measuring voltage drop across skin.

**Multi-modal platforms supporting EDA:**
- NIRx WINGS2: includes EDA/GSR sensor.
- iMotions Lab: software platform synchronizing EEG + EDA from Shimmer, BIOPAC, or PLUX hardware.
- Shimmer3R GSR+: dedicated wearable EDA sensor with Bluetooth.

### 3.6 EEG + IMU (Inertial Measurement Unit)

**Motion reference for artifact rejection:**

This is one of the most impactful multi-modal additions for mobile/wearable EEG.

**How it works:**
- 6-axis IMU (3-axis accelerometer + 3-axis gyroscope) or 9-axis (+ 3-axis magnetometer).
- IMU data serves as reference signal for adaptive artifact rejection algorithms.
- Key insight from research: motion artifacts correlate better with VELOCITY (integrated acceleration) than raw acceleration.
- Adaptive filtering: LMS (Least Mean Squares) algorithm with IMU-derived velocity as reference input.
- 2025 breakthrough: "IMU-Enhanced EEG Motion Artifact Removal with Fine-Tuned Large Brain Models" (arXiv:2509.01073) -- deep learning model uses spatial channel relationships in IMU data to identify motion artifacts.

**Implementation:**
- IMU chip: LSM6DSOX (ST, 6-axis, $3), ICM-42688-P (TDK, 6-axis, $4), or BMI270 (Bosch, 6-axis, $3).
- Communication: SPI or I2C to main MCU.
- Sampling rate: 100-400 Hz (must be >= EEG sampling rate for effective adaptive filtering).
- Power consumption: 0.5-3 mW.
- BioGAP-Ultra uses LIS2DUXS12 (ST) integrated IMU.

**Artifact removal performance:**
- Multi-channel IMU + adaptive filtering achieves significant EEG artifact reduction during walking and other motion.
- ARX (autoregressive exogenous) input models using 9-DOF IMU data provide mathematical estimation of movement artifacts.
- Combined with ICA: IMU reference identifies motion-related ICA components for removal.

### 3.7 Temporal Synchronization Requirements

| Modality Pair | Required Sync Accuracy | Reasoning |
|--------------|----------------------|-----------|
| EEG channels (inter-channel) | <10 us | Simultaneous sampling for spatial analysis. ADS1299 provides this natively. |
| EEG + EMG | <1 ms | Cortico-muscular coherence analysis. |
| EEG + EOG | <1 ms | Artifact removal regression requires temporal alignment. |
| EEG + IMU | <5 ms | Adaptive artifact filtering reference. |
| EEG + PPG | <10 ms | Cardiac artifact removal. |
| EEG + EDA | <100 ms | EDA is very slow; rough synchronization sufficient. |
| EEG + fNIRS | <10 ms (event markers) | Hemodynamic response is slow but event timing must be precise. |

**Lab Streaming Layer (LSL):**
- Provides sub-millisecond synchronization across all modalities on a common LAN.
- Empirically validated: <0.5 ms offset between EEG and EMG streams on standard laptop hardware.
- Microsecond-precision timestamping with automatic jitter compensation.
- The de facto standard for multi-modal neurophysiology synchronization.
- 2025 reference paper published: "The lab streaming layer for synchronized multimodal recording" (Imaging Neuroscience, MIT Press).

[Sources: PMC12434378; BioRxiv 2024.02.13.580071]

### 3.8 BrainFusion Framework

**BrainFusion** is a software framework (NOT hardware), published in Advanced Science (2025).

**What it does:**
- Low-code Python framework for multimodal BCI and brain-body interaction research.
- Standardized data structures and automated preprocessing pipelines.
- Cross-modal feature engineering and integrated ML/DL modules.
- Currently supports: EEG, fNIRS, EMG, ECG.
- Planned: expansion to additional physiological modalities.

**Performance results:**
- EEG-fNIRS motor imagery classification: 95.5% accuracy (within-subject, ensemble modeling).
- EEG-ECG sleep staging: 80.2% accuracy (deep learning).
- Application generator can transform workflows into deployable executables.

**Relevance for Lucid:** BrainFusion provides the software data analysis layer for multi-modal data collected by Lucid hardware. Consider targeting BrainFusion compatibility as a software integration goal.

### 3.9 BioGAP-Ultra Platform (2025)

BioGAP-Ultra from ETH Zurich is the most relevant existing open-source multi-modal biosensing platform.

**Complete specifications:**

| Component | Specification |
|-----------|--------------|
| ExG AFE | 2x ADS1298, 16 channels, 24-bit, 250-32k SPS, gain 1-12x |
| ExG noise | 0.47 uVrms (0.5-100 Hz), IFCN clinical EEG compliant |
| PPG sensor | MAX86150, 100 Hz sampling |
| IMU | LIS2DUXS12, 400 Hz accelerometer |
| Microphone | T5838 PDM digital |
| Main processor | GAP9 PULP SoC: 370 MHz, 32.2 GMACs ML, 15.6 GOPs DSP |
| Control SoC | nRF5340 dual-core Cortex-M33, BLE 5.4 |
| Flash | 512 Mbit Octal-SPI |
| RAM | 512 Mbit PSRAM (3.2 Gbit/s) + 128 Mbit QSPI |
| Wireless | BLE 5.4 at 1.4 Mbit/s |
| Power (headband) | 32.8 mW total, 16.9 hours battery life |
| Power (EMG sleeve) | 26.7 mW, 20.8 hours |
| Power (chestband) | 9.3 mW, 59.7 hours |
| License | Open source (permissive) |
| Form factors | Headband (EEG+PPG), sleeve (EMG), chestband (ECG+PPG) |

**Key difference from Lucid concept:** BioGAP-Ultra uses ADS1298 (12x max gain) instead of ADS1299 (24x max gain). The ADS1298 is adequate for EMG/ECG but suboptimal for low-amplitude EEG. Lucid should use ADS1299 for superior EEG noise performance.

[Sources: arXiv:2508.13728; IEEE Xplore 11346484]

---

## 4. Electrical Safety in EEG Design

### 4.1 IEC 60601-1 Requirements

IEC 60601-1 Edition 3.2 is the current international safety standard for medical electrical equipment. Edition 4.0 is in development with draft expected mid-2025.

**Classification types for patient-connected devices:**

| Type | Description | Normal Leakage | Single Fault | Isolation |
|------|-------------|---------------|--------------|-----------|
| Type B | Body contact, not isolated | 500 uA (earth), 100 uA (patient) | 500 uA (patient) | Input-to-output: 1,500 VAC |
| Type BF | Body Floating (EEG applicable) | 100 uA (patient) | 500 uA (patient) | Input-to-output: 4,000 VAC; Output-to-ground: 1,500 VAC |
| Type CF | Cardiac Floating (cardiac direct) | 10 uA (patient) | 50 uA (patient) | Input-to-output: 4,000 VAC; Output-to-ground: 1,500 VAC |

**EEG classification:** Type BF (Body Floating) is the applicable classification for EEG devices. EEG electrodes are applied-parts that contact the patient's head.

**Means of Protection (MOP):**
- Two MOP required between patient-applied parts and any accessible part.
- Each MOP is categorized as MOOP (Means of Operator Protection) or MOPP (Means of Patient Protection).
- For Type BF: 2x MOPP required.
- Each MOPP requires a basic insulation + supplementary insulation, or reinforced insulation.

### 4.2 Galvanic Isolation Approaches

**For USB-connected EEG devices, isolation must be placed between the patient-connected analog front-end and the USB-connected digital interface.**

| Technology | Product Examples | Isolation Rating | Bandwidth | Pros | Cons |
|-----------|-----------------|-----------------|-----------|------|------|
| Capacitive (iCoupler) | ADuM4160 (USB), ADuM3160 | 5,000 Vrms (1 min) | Full/Low-speed USB | High reliability, low EMI, small size | USB speed limited to full/low speed |
| Magnetic (transformer) | ISO7741, ISO7742 (TI) | 4,243 Vpk | SPI up to 100 Mbps | Higher data rate, robust | Larger, more EMI |
| Optical (optocoupler) | IL300, HCNR200 | Varies | Limited by LED/phototransistor speed | Proven technology | Slowest, highest power, aging |
| DC-DC isolated power | SN6505, R1SE-0505 | 5,000 Vrms | N/A (power only) | Provides isolated power supply | Leakage current adds to total |

**Recommended isolation architecture for Lucid:**
1. **ADuM4160** for USB data isolation (5 kV, proven in medical devices, used by OpenNIRScap).
2. **Isolated DC-DC converter** (e.g., SN6505-based push-pull driver + transformer) to power the analog side from USB. Leakage current: <4 uA (compliant with Type CF even).
3. **Total isolation barrier**: digital ground (connected to USB/computer) is completely separated from analog ground (connected to patient through electrodes).

### 4.3 How Open-Source EEG Handles Safety

| Project | Isolation | Safety Approach | Notes |
|---------|-----------|----------------|-------|
| OpenBCI Cyton | NONE | Battery-powered only. Warning: never connect to mains. | Relies entirely on battery operation. |
| Cerelog ESP-EEG | NONE | Battery or USB power bank. Explicit warning: NOT medical, NOT isolated. | "NOT for use while connected to mains power." |
| PiEEG | NONE | Raspberry Pi powered. No isolation from Pi's USB power. | Highest risk if Pi is mains-powered. |
| HackEEG | NONE | Arduino Due USB. No isolation. | Research use only warning. |
| OpenHardwareExG | 5 kV reinforced isolation | ADuM-based USB isolation + isolated DC-DC. Only open-source EEG with proper isolation. | ADS1299 + Arduino Due. The model for Lucid. |
| VolksEEG | Planned (targeting FDA) | Designed for IEC 60601 compliance. Project slow/semi-abandoned. | Ambitious but incomplete. |
| BioGAP-Ultra | Isolated BLE | Wireless-only operation provides inherent isolation. | BLE 5.4 means no galvanic path to any computer. |

**OpenHardwareExG is the only existing open-source EEG with 5 kV reinforced isolation and should serve as the safety reference design for Lucid.**

### 4.4 When Connected to Mains-Powered Computer

**The danger scenario:** EEG board connected via USB to a laptop that is plugged into mains power.

- Mains leakage through laptop power supply: typically 100-500 uA (varies by manufacturer).
- This leakage flows through: mains -> laptop PSU -> USB cable -> EEG board -> patient electrodes -> patient -> earth.
- Without isolation: patient receives the full leakage current through scalp electrodes.
- With Type BF isolation: leakage is limited to <100 uA normal, <500 uA single fault.
- With Type CF isolation: leakage is limited to <10 uA normal, <50 uA single fault.

**Risk assessment:**
- Scalp electrodes are NOT directly on the heart, so cardiac fibrillation risk is low.
- But discomfort, burns (from DC leakage), and secondary injury (from startle) are possible.
- A ground fault in the mains supply could expose the patient to lethal voltages without isolation.

**Recommendation for Lucid:**
1. Include 5 kV galvanic isolation (ADuM4160 + isolated DC-DC) as a standard feature, not an option.
2. Wireless (BLE 5.x) primary data path provides inherent isolation.
3. USB used only for firmware update and bench testing (with isolation).
4. Include a physical isolation indicator LED that confirms isolation barrier is intact.

### 4.5 Leakage Current Budget

For Type BF compliance (normal condition, 100 uA limit):

| Source | Typical Leakage | Notes |
|--------|----------------|-------|
| Isolated DC-DC converter | 1-4 uA | Primary source. Choose <4 uA rated part. |
| ADuM4160 isolation capacitance | <1 uA | Very low coupling capacitance. |
| PCB parasitic capacitance | <0.5 uA | Depends on layout. Maximize creepage distance. |
| Total | ~5-6 uA | Well within 100 uA Type BF limit. Even within 10 uA Type CF. |

---

## 5. EEG Signal Characteristics -- Quantitative

### 5.1 Amplitude of Each EEG Band at Scalp

| Band | Frequency Range | Typical Amplitude (scalp) | Peak Amplitude | Associated State | Clinical Significance |
|------|----------------|--------------------------|----------------|-----------------|----------------------|
| Delta | 0.5-4 Hz | 20-200 uV | Up to 200 uV | Deep sleep (NREM stage 3/4) | Highest amplitude band. Should NOT be present in awake adults. Pathological if present during wakefulness. |
| Theta | 4-8 Hz | 5-100 uV | Up to 100 uV | Drowsiness, light sleep, meditation, memory encoding | More prominent in children. Associated with memory consolidation and creative states. |
| Alpha | 8-13 Hz | 10-50 uV | Up to 50 uV | Relaxed wakefulness, eyes closed | Hallmark of the awake adult brain. Posterior dominant (occipital). Blocks (desynchronizes) with eye opening ("alpha blocking"). |
| Beta | 13-30 Hz | 5-30 uV | Up to 30 uV | Active thinking, focus, anxiety, motor planning | Often contaminated by frontal muscle (EMG) artifact. Low amplitude, hard to measure. |
| Gamma | 30-100+ Hz | 1-10 uV | Up to 10 uV | Higher cognitive processing, binding, attention | Very difficult to measure with scalp EEG. Almost always contaminated by muscle artifact. Not reliably seen on scalp recordings. |

**Key design implication:** The weakest signals of interest (gamma, 1-10 uV) require a system noise floor of <0.5 uV to achieve even 6 dB SNR. The ADS1299 at 250 SPS (0.14 uVrms noise) provides adequate margin. For alpha/theta neurofeedback (10-50 uV signals), the noise margin is comfortable (>30 dB SNR).

### 5.2 Noise Floor of ADS1299-Based Systems

| System | Measured Noise Floor | Conditions | Source |
|--------|---------------------|-----------|--------|
| ADS1299 datasheet (theoretical) | 0.14 uVrms | Gain=24, 250 SPS, shorted inputs | TI SBAS499C |
| OpenBCI Cyton (measured) | 0.16 uVrms | Gain=24, 250 SPS, shorted inputs | EEG Hacker blog, 2013 |
| ADS1299 prototype (academic) | 8.85 uVrms | Gain=24, 250 SPS, electrodes on subject (includes biological noise) | PMC6263632, 2018 |
| FreeEEG32 (AD7771) | <0.22 uV | Internal noise measurement | Crowd Supply specs |
| BioGAP-Ultra (ADS1298) | 0.47 uVrms | 0.5-100 Hz bandwidth | arXiv:2508.13728, 2025 |
| Neurosity Crown (claimed) | 0.25 uVrms | Proprietary implementation | Neurosity specs |

**Note:** The ~9 uVrms measured with electrodes on a subject includes biological noise (ongoing EEG activity, EMG, EOG, etc.) -- the actual electronics noise floor is the 0.14-0.16 uVrms figure.

### 5.3 Electrode Impedance Ranges by Type

| Electrode Technology | Impedance Range (at 10 Hz) | Prep Time | Comfort | Duration | Reusable |
|---------------------|--------------------------|-----------|---------|----------|----------|
| Wet gel (Ag/AgCl + Ten20 paste) | 1-10 kOhm | 20-45 min (full cap) | Low (messy) | 2-4 hours (gel dries) | Electrodes yes, gel no |
| Wet gel (pre-gelled disposable) | 2-15 kOhm | 5-15 min | Medium | 4-8 hours | No |
| Saline sponge (Emotiv-style) | 10-100 kOhm | 2-5 min | Medium | 2-6 hours (evaporates) | Sponges replaceable |
| Semi-dry hydrogel (2025) | 0.4-100 kOhm | <1 min | High | 12+ hours | Yes (21+ uses) |
| Dry contact metal (forehead/ear) | 20-100 kOhm | Instant | High | Unlimited | Yes |
| Dry pin (through hair) | 50-300 kOhm | Instant | Medium-Low | Unlimited | Yes |
| Dry comb/finger (through hair) | 100-2000 kOhm | Instant | Medium | Unlimited | Yes |
| Active dry (Cognionics-style) | 100-2000 kOhm (contact) but buffered to <1 kOhm (output) | Instant | Medium | Unlimited | Yes |
| Capacitive non-contact | 1-5 MOhm | Instant | High | Unlimited | Yes |

### 5.4 CMRR Requirements

| Scenario | Required Net CMRR | Notes |
|---------|-------------------|-------|
| Minimal (shielded room, wet electrodes) | >60 dB | Controlled environment, matched impedances |
| Standard (lab, wet electrodes) | >80 dB | Some mains pickup, well-matched electrodes |
| Good (office, wet electrodes, DRL) | >100 dB | ADS1299 native CMRR sufficient |
| Required (office, dry electrodes, no DRL) | >110 dB | Need active electrodes to maintain CMRR |
| Required (field, dry electrodes, movement) | >120 dB | Active electrodes + optimized bias drive essential |
| Achieved (ADS1299 with optimized bias) | 143 dB | Documented with modified bias circuit |

**Rule of thumb:** Every 10 kOhm of impedance mismatch between two electrodes degrades CMRR by approximately 20*log10(delta_Z/Z_input) dB. With 10 MOhm input impedance and 10 kOhm mismatch: 20*log10(10k/10M) = -60 dB degradation.

### 5.5 Minimum Channels by Application

| Application | Minimum | Recommended | Notes |
|------------|---------|-------------|-------|
| Basic neurofeedback (alpha/theta training) | 1 | 2-4 | Single channel at Cz, Oz, or Pz sufficient for alpha/theta. 2-4 allows frontal+posterior. |
| Motor imagery BCI (2-class) | 2 | 3-8 | C3 and C4 (over motor cortex). 3-8 channels gives 83-84% accuracy; more channels add diminishing returns. |
| Motor imagery BCI (4-class) | 4 | 8-16 | More classes require more spatial information. |
| P300 speller | 4 | 8-16 | Parietal electrodes (Pz, P3, P4, Cz). 4 channels achieves comparable bit rate to 32. Optimal subset: Fz, Cz, Pz + 1-5 others. |
| SSVEP BCI | 1 | 4-8 | Occipital electrodes (O1, O2, Oz). Single channel works but multi-channel improves ITR. |
| Sleep staging | 1 | 2-4 | Single-channel (Fpz-Cz or Fpz-Oz) achieves 83-88% accuracy with deep learning (2025). Clinical PSG uses 6+ EEG channels. |
| Full 10-20 system | 19 | 21 (19 + 2 ref) | Standard clinical/research placement. 19 active + 2 reference electrodes. |
| High-density research | 64 | 128-256 | Source localization, connectivity studies. |
| Emotion detection | 4 | 14-32 | Frontal asymmetry (F3/F4) + broader coverage. |

**2025 channel reduction research finding:** A study using Binary Grey Wolf Optimization achieved 93.18% motor imagery accuracy with optimized channel selection from 22 channels, suggesting that smart channel selection can match or exceed brute-force high-density recordings. Another study showed that 6 channels (3 EEG + 3 EOG) achieved 83% accuracy -- nearly identical to all 22 EEG channels (84%).

### 5.6 Sampling Rate Requirements by Application

| Application | Minimum | Recommended | Maximum Useful | Notes |
|------------|---------|-------------|---------------|-------|
| Neurofeedback | 128 Hz | 250 Hz | 256 Hz | 128 Hz provides 6+ samples per 40 Hz waveform. 256 Hz is standard in all modern neurofeedback systems. |
| Motor imagery BCI | 128 Hz | 250-500 Hz | 500 Hz | Mu rhythm (8-12 Hz) and beta (13-30 Hz). 250 Hz is standard. |
| P300/ERP | 256 Hz | 512 Hz | 1000 Hz | ERP temporal resolution benefits from higher rate. 512 Hz standard in research. |
| SSVEP | 250 Hz | 500 Hz | 1000 Hz | Depends on stimulus frequency. Must be >2x max stimulus frequency. |
| Sleep staging | 128 Hz | 256 Hz | 500 Hz | Delta through sigma bands. 256 Hz is standard for PSG. |
| High-gamma research | 500 Hz | 1000-2000 Hz | 4000 Hz | Gamma >30 Hz needs >60 Hz Nyquist minimum, but oversampling improves SNR. |
| EMG (auxiliary) | 500 Hz | 2000 Hz | 4000 Hz | EMG bandwidth extends to ~500 Hz. |
| Clinical EEG | 256 Hz | 512 Hz | 1000 Hz | ACNS recommends minimum 256 Hz, 512 Hz preferred for digital EEG. |

### 5.7 Signal Quality Metrics Comparison

| Metric | Wet Gel Electrodes | Semi-dry | Dry Contact | Dry Active | Source |
|--------|--------------------|----------|-------------|------------|--------|
| SNR (typical) | ~24.9 dB | ~24.4 dB | 10-20 dB | 18-24 dB | BCI_EEG_LANDSCAPE.md; PMC12389868 |
| Correlation with reference | 1.0 (is the reference) | 0.95-0.99 | 0.7-0.9 | 0.85-0.95 | Multiple sources |
| 50/60 Hz artifact power | Baseline | 1.1x | 1.3-1.4x | 1.1-1.2x | PMC12389868 |
| Motion artifact susceptibility | Low | Low-Medium | High | Medium | Multiple sources |
| Cross-subject accuracy penalty | Baseline | ~2-5% | 10-15% | 5-10% | PMC12389868 |

---

## 6. Design Recommendations for Lucid Platform

Based on this research, the following architecture is recommended for the Lucid BCI platform:

### 6.1 Core ADC
- **ADS1299** (8-channel). No substitute exists with equivalent EEG-specific features.
- Support daisy-chain of 2x ADS1299 for 16-channel configuration.
- Default data rate: 500 SPS (compromise between noise performance and bandwidth for all applications).

### 6.2 Electrode Strategy
- **Primary: Active dry electrodes** with OPA2376 or equivalent unity-gain buffer at each electrode site.
- **Secondary: Semi-dry hydrogel inserts** for electrode holders (highest signal quality, 12+ hour stability).
- **Electrode holder: 3D-printable** comb/finger design with spring compliance, compatible with both dry and hydrogel inserts.
- Target impedance: <100 kOhm with active buffering to maintain >100 dB effective CMRR.

### 6.3 Multi-Modal Sensors
- **PPG**: MAX86150 or MAX30102 on earlobe clip ($2-5 BOM).
- **IMU**: LSM6DSOX or BMI270 6-axis ($3) for motion artifact reference.
- **fNIRS**: Optional expansion board using OpenNIRScap-inspired design (dual-wavelength LED + VBPW34S photodiode, $15-20/channel).
- **EDA**: Optional ADS1115 + excitation circuit on auxiliary board ($5).

### 6.4 Safety
- **5 kV galvanic isolation** using ADuM4160 (USB) + isolated DC-DC converter. Non-negotiable.
- **Wireless primary**: ESP32-S3 or nRF5340 BLE 5.x for inherent isolation during normal operation.
- **1 MOhm current-limiting** on BIAS_OUT.
- Target: Type BF compliance (<100 uA patient leakage).

### 6.5 Software Compatibility
- **LSL** (Lab Streaming Layer) native output for multi-modal synchronization.
- **BrainFlow** board driver for broad software ecosystem compatibility.
- **BrainFusion** compatible data format for multi-modal analysis.

---

## Sources

### Section 1: ADS1299 Circuit Design
- [ADS1299 Datasheet (TI SBAS499C)](https://www.ti.com/lit/ds/symlink/ads1299.pdf)
- [Design and Implementation of an ADS1299-Based Electrophysiological Signal Acquisition System (ACM 2025)](https://dl.acm.org/doi/10.1145/3788112.3788119)
- [ADS1299 140dB CMRR analog front-end design (TI E2E Forums)](https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/546300/ads1299-140db-cmrr-analog-front-end-schematics-design)
- [EEG Front-End Performance Demonstration Kit User's Guide (TI SLAU443B)](https://www.ti.com/lit/ug/slau443b/slau443b.pdf)
- [ADS1299 SRB, BIAS and reference (TI E2E)](https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/551341/ads1299-srb-bias-and-reference)
- [ADS1298 vs ADS1299 (TI E2E)](https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/231604/ads1298-vs-ads1299)
- [ADS1299 Polarization Voltage Improvement Solutions (Oreate AI)](https://www.oreateai.com/blog/ads1299-polarization-voltage-improvement-solutions-and-technical-analysis/c15d0b020688ded408120745f28631ec)
- [An EEG Experimental Study Evaluating the Performance of Texas Instruments ADS1299 (Sensors 2018)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6263632/)
- [OpenBCI Self-Noise Measurement (EEG Hacker)](http://eeghacker.blogspot.com/2013/12/self-noise-of-openbci.html)
- [ADS1299 PCB Design Questions (TI E2E)](https://e2e.ti.com/support/data-converters-group/data-converters/f/data-converters-forum/1093452/ads1299-some-questions-about-pcb-design)
- [Development of a Modular Board for EEG Signal Acquisition (PMC6068481)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6068481/)

### Section 2: Dry Electrode Technology
- [Recent Advances in Portable Dry Electrode EEG (Sensors 2025)](https://www.mdpi.com/1424-8220/25/16/5215)
- [Advancements in dry and semi-dry EEG electrodes (AIP Advances 2025)](https://pubs.aip.org/aip/adv/article/15/4/040703/3345166/Advancements-in-dry-and-semi-dry-EEG-electrodes)
- [A comprehensive review of EEG electrode technologies (2025)](https://www.sciencedirect.com/science/article/abs/pii/S0924424725012026)
- [Two-Wired Active Spring-Loaded Dry Electrodes (Sensors 2019)](https://www.mdpi.com/1424-8220/19/20/4572)
- [Fully 3D-Printed Dry EEG Electrodes (Sensors 2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10255664/)
- [3D Printed Dry EEG Electrodes (Sensors 2016)](https://www.mdpi.com/1424-8220/16/10/1635)
- [The Feature, Performance, and Prospect of Advanced Electrodes for EEG (Biosensors 2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9855417/)
- [Dry EEG Electrodes (Sensors 2014, foundational)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4168519/)
- [A tough semi-dry hydrogel electrode (Nature Microsystems & Nanoengineering 2025)](https://www.nature.com/articles/s41378-025-00908-4)
- [Hydrogel electrodes with conductive and substrate-adhesive layers (Nature 2023)](https://www.nature.com/articles/s41378-023-00524-0)
- [PEDOT:PSS-based bioelectronics for brain monitoring (Nature 2025)](https://www.nature.com/articles/s41378-025-00948-w)
- [Novel dry EEG electrode with PEDOT:PSS and carbon particles (PubMed 2023)](https://pubmed.ncbi.nlm.nih.gov/38083429/)
- [Carbon-Based Nanocomposite Electrodes for EEG (PMC 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11991328/)
- [Active Electrodes for Wearable EEG: Review and Design Methodology (IEEE 2017)](https://ieeexplore.ieee.org/document/7828037/)
- [Impedance and Noise of Passive and Active Dry EEG Electrodes: A Review (IEEE 2020)](https://ieeexplore.ieee.org/document/9149885/)
- [g.SAHARA Hybrid (g.tec)](https://www.gtec.at/product/g-sahara-hybrid/)
- [CGX/Cognionics Dry EEG Technology](https://www.cgxsystems.com/technology)
- [Emotiv EPOC X Technical Specifications](https://emotiv.gitbook.io/epoc-x-user-manual/introduction/technical-specifications)
- [g.Nautilus PRO Flexible -- Best EEG Device of 2026 (g.tec)](https://www.gtec.at/2025/12/11/guide-to-the-best-eeg-device-of-2026-g-nautilus-pro-flexible/)
- [Hook Fabric EEG Electrode (PMC 2023)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10537404/)

### Section 3: Multi-Modal Sensing
- [BioGAP-Ultra: A Modular Edge-AI Platform (arXiv/IEEE 2025)](https://arxiv.org/html/2508.13728v1)
- [OpenNIRScap: Open-Source Low-Cost fNIRS (arXiv 2025)](https://arxiv.org/html/2505.20509v1)
- [Mobile EEG/fNIRS Multi-Modal Device (Sensors 2026)](https://www.mdpi.com/1424-8220/26/4/1342)
- [Multimodal fNIRS-EEG sensor fusion: Review (PMC 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12592382/)
- [BrainFusion: Low-Code Multimodal BCI Framework (Advanced Science 2025)](https://advanced.onlinelibrary.wiley.com/doi/full/10.1002/advs.202417408)
- [The Lab Streaming Layer for Synchronized Multimodal Recording (Imaging Neuroscience 2025)](https://direct.mit.edu/imag/article/doi/10.1162/IMAG.a.136/132678/The-lab-streaming-layer-for-synchronized)
- [OpenEarable ExG (arXiv 2024)](https://arxiv.org/html/2410.06533v1)
- [Muse S Athena Specifications](https://intl.choosemuse.com/products/muse-s-athena)
- [How The Muse S Athena Works For EEG & fNIRS Neurofeedback](https://www.diygenius.com/how-the-muse-s-athena-eeg-and-fnirs-neurofeedback-device-works/)
- [IMU-Enhanced EEG Motion Artifact Removal (arXiv 2025)](https://arxiv.org/abs/2509.01073)
- [Motion artifact removal using multichannel IMUs (PMC 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8450177/)
- [Motion Artifact Removal Techniques for Wearable EEG and PPG (Frontiers 2021)](https://www.frontiersin.org/journals/electronics/articles/10.3389/felec.2021.685513/full)
- [Wearable, Integrated EEG-fNIRS Technologies: A Review (PMC 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8469799/)

### Section 4: Electrical Safety
- [IEC 60601-1 (Wikipedia)](https://en.wikipedia.org/wiki/IEC_60601)
- [IEC 60601-1 Safety Guide (Wall Industries)](https://www.wallindustries.com/your-guide-to-iec-60601-1/)
- [Safety Requirements: BF and CF Classifications (Advanced Energy)](https://www.advancedenergy.com/en-us/about/news/blog/safety-requirements-in-medical-equipment-designing-for-bf-and-cf-classifications/)
- [IEC 60601-1 Insulation Requirements (Medical Device HQ)](https://medicaldevicehq.com/articles/identify-iec-60601-1-standard-insulation-requirements-for-electrical-medical-devices/)
- [ADuM4160 Full/Low Speed 5 kV USB Digital Isolator (Analog Devices)](https://www.analog.com/en/products/adum4160.html)
- [Galvanic Isolation Guidelines for MP Research Systems (BIOPAC)](https://www.biopac.com/knowledge-base/galvanic-isolation-guidelines-for-the-mp150-system/)
- [OpenHardwareExG (GitHub)](https://github.com/openelectronicslab/OpenHardwareExG)
- [VolksEEG: Open Source EEG Project](https://volkseeg.org/)
- [Cerelog ESP-EEG](https://www.cerelog.com/)

### Section 5: EEG Signal Characteristics
- [Normal EEG Waveforms (StatPearls/NCBI)](https://www.ncbi.nlm.nih.gov/books/NBK539805/)
- [EEG Terminology and Waveforms (LearningEEG)](https://www.learningeeg.com/terminology-and-waveforms)
- [Electroencephalography (Wikipedia)](https://en.wikipedia.org/wiki/Electroencephalography)
- [CMRR and Electrode Impedance Mismatch (PMC4168519)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4168519/)
- [Effects of Electrode Impedance on Data Quality in ERP (PMC 2010)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2902592/)
- [Deep Learning in Automatic Sleep Staging With Single Channel EEG (PMC 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7965953/)
- [Channel Reduction in Motor Imagery BCI (PMC 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12578340/)
- [Performance Improvement with Reduced Channels in MI BCI (PMC 2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11723053/)
- [Optimal EEG Electrode Configuration for P300 (PMC 2015)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4377128/)
- [Sampling Rate (Brain-Trainer)](https://brain-trainer.com/answer/sampling-rate/)
