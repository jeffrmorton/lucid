# Safety

## Electrical Isolation Requirements

Galvanic isolation between patient-connected circuits and mains-powered equipment is **mandatory and non-negotiable**. The Lucid hardware uses an ADuM4160 USB isolator rated for 5 kV isolation. All analog circuits (ADS1299, electrode preamps, electrode connectors) must be powered by battery only and physically separated from the digital section.

- Maximum patient auxiliary current: 10 uA DC, 100 uA AC (per IEC 60601-1 Type BF)
- All electrode leads must have series current-limiting resistors (10 kOhm minimum)
- The isolation barrier must never be bridged by wires, probes, or conductive paths
- Test isolation integrity before every session using an isolation tester (>2 kV withstand)

## Contraindications

Do **not** use Lucid EEG with:

- Persons with implanted electrical devices (pacemakers, cochlear implants, deep brain stimulators)
- Persons with a history of photosensitive epilepsy (neurofeedback visual stimuli may trigger seizures)
- Open wounds or skin lesions at electrode sites
- During electrical storms (lightning risk to equipment)

Consult a physician before using EEG-based neurofeedback for any clinical application.

## Emergency Procedures

1. **If the user reports tingling, pain, or discomfort**: Immediately disconnect all electrodes. Do not touch the user and equipment simultaneously.
2. **If equipment becomes wet**: Power off immediately. Do not reconnect until fully dried and isolation is verified.
3. **If the isolation barrier is suspected compromised**: Stop all use. Test with an isolation tester before resuming.
4. **If a seizure occurs during neurofeedback**: Stop the session. Remove electrodes. Place the person in the recovery position. Call emergency services.

## Regulatory Notice

Lucid is an open-source research tool. It has not been cleared or approved by the FDA, CE, or any regulatory body for clinical diagnostic or therapeutic use. Use at your own risk and only for research purposes.
