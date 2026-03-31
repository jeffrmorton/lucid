# Hardware Design Notes

## ADS1299 Selection Rationale

The Texas Instruments ADS1299 is the industry standard analog front-end for research-grade EEG. Key reasons for selection:

- 24-bit resolution at 250 SPS per channel with integrated PGA (1x-24x gain)
- 8 differential input channels with built-in bias drive (SRB) and lead-off detection
- Input-referred noise of 1 uVpp — sufficient for resolving low-amplitude EEG rhythms
- Widely used in OpenBCI and academic BCI systems, well-documented

The ADS1299-6 variant is used (6-channel base, expandable to 8 via daisy-chain or single 8-channel ADS1299-8 if cost allows in later revisions).

## Active Electrode Preamp Design (OPA2376)

Active electrodes place a preamp at the electrode site to minimize cable artifact and noise pickup:

- OPA2376 selected for 7.5 nV/rtHz input noise, rail-to-rail output, low quiescent current (760 uA)
- Unity-gain buffer topology — high impedance input, low impedance output
- Dual op-amp package (SOT-23-8) keeps per-channel footprint small
- 3-wire cable from each active electrode: signal, power, ground

## Galvanic Isolation (ADuM4160)

Patient safety requires galvanic isolation between the EEG analog section and the host computer:

- ADuM4160 provides USB 2.0 isolation. Combined with an isolated DC-DC converter, the design achieves 5 kV peak galvanic isolation.
- Placed between ESP32-S3 USB PHY and the host USB-C connector
- Isolation barrier also separates analog and digital ground planes on the PCB
- Meets IEC 60601-1 requirements for Type BF applied parts

## Power Supply Topology

Dual-rail analog supply is required for the ADS1299 and active electrode preamps:

- Single Li-Po cell (3.7V nominal) feeds TPS63001 buck-boost for 3.3V digital rail
- TPS7A49 positive LDO: 3.3V digital -> clean AVDD1 (positive analog)
- TPS7A30 negative LDO: charge pump generates negative rail -> AVDD1N
- Separate analog and digital ground planes, connected at a single star point under the ADS1299
- Estimated battery life: ~28 hr WiFi / ~57 hr BLE continuous acquisition from 2000 mAh cell

## PCB Layout Guidelines

- 4-layer stackup: Top (signal) / Ground / Power / Bottom (signal)
- ADS1299 placed centrally with symmetric routing to electrode connectors
- Analog ground plane unbroken under ADS1299 and LDO regulators
- Digital and analog ground planes joined at single star point
- Guard rings around high-impedance analog inputs
- Isolation barrier clearly demarcated with keepout zone (min 2.5 mm creepage)
- Decoupling: 100 nF + 10 uF on each power pin, placed within 5 mm of pin
