# BQRC Digital Engineering Platform

## System Requirements Specification

**Project:** BQRC-01 — Bharatiya Quantum Research Cube  
**Document:** System Requirements Specification (SRS)  
**Status:** Initial Development Baseline  
**Parent Documents:** `PROJECT_BASELINE.md`, `SYSTEM_ARCHITECTURE.md`  
**Requirement Prefix:** `BQRC`

---

# 1. Purpose

This document defines the engineering requirements for the BQRC Digital Engineering Platform.

It converts the BQRC project baseline and system architecture into explicit, implementable and verifiable engineering requirements.

Each requirement shall eventually be connected to:

```text
Mission / Research Objective
        ↓
Requirement
        ↓
Architecture
        ↓
Implementation
        ↓
Test
        ↓
Verification Result
        ↓
Evidence
```

A feature shall not be considered scientifically or technically verified merely because it appears to work in the web application.

---

# 2. Requirement Status

Requirements may use the following states:

- **PROPOSED** — identified but not yet accepted into implementation.
- **BASELINED** — accepted as part of the current project architecture.
- **IMPLEMENTED** — implemented but not fully verified.
- **VERIFIED** — implementation has passed the defined verification.
- **DEFERRED** — intentionally postponed.
- **RETIRED** — no longer applicable but preserved for traceability.

Unless otherwise stated, requirements in this initial document are considered **BASELINED architectural requirements**.

Numerical performance requirements shall be refined as supporting literature, datasets, hardware specifications and experimental evidence become available.

---

# 3. Requirement Priority

Requirements may be classified as:

| Priority | Meaning |
|---|---|
| Critical | Necessary for architectural/scientific integrity |
| High | Required for the intended BQRC platform |
| Medium | Important but may follow the first implementation |
| Low | Enhancement or longer-term capability |

---

# 4. Verification Methods

Requirements may be verified using:

| Method | Meaning |
|---|---|
| Test | Execute software/hardware and evaluate the result |
| Analysis | Mathematical, statistical or scientific evaluation |
| Inspection | Review code, configuration, documentation or records |
| Demonstration | Show correct functional operation |
| Comparison | Compare against reference model/data/hardware |
| Calibration | Verify using known reference inputs |

---

# 5. Requirement Identifier

Requirements shall use:

`BQRC-[DOMAIN]-[NUMBER]`

Examples:

```text
BQRC-CORE-001
BQRC-SIM-001
BQRC-NV-001
BQRC-DATA-001
```

Requirement identifiers shall remain stable once baselined.

---

# 6. Requirement Domains

| Code | Domain |
|---|---|
| CORE | Digital Engineering Core |
| SIM | Simulation Engine |
| TIME | Time and Scheduling |
| ORB | Orbit and Position |
| FRM | Reference Frames and Attitude |
| ENV | Space Environment |
| MAG | Magnetic Environment |
| MGR | Microgravity and Vibration |
| THM | Thermal Environment |
| RAD | Radiation Environment |
| NV | NV-Center Quantum Sensing |
| ODMR | ODMR Acquisition and Processing |
| IMU | Conventional Inertial Sensors |
| HW | Hardware Digital Twin |
| ELEC | Electronics and Acquisition |
| DATA | Dataset and Data Management |
| CAL | Calibration |
| UNC | Uncertainty and Quality |
| ALG | Algorithms and Estimation |
| FUS | Sensor Fusion |
| MSN | Mission Software |
| TLM | Telemetry and Communication |
| FLT | Fault Injection and Handling |
| ANA | Scientific Analysis |
| APP | Applications |
| NAV | Navigation Research |
| ML | AI / ML / DL |
| API | Backend and API |
| UI | Web Interface and Visualization |
| KNW | Knowledge, Documentation and Evidence |
| VER | Verification and Validation |
| HIL | Hardware-in-the-Loop |
| PERF | Performance and Scalability |
| SEC | Software and Data Integrity |

---

# 7. Requirement Writing Rules

BQRC requirements shall:

1. Use **shall** for mandatory requirements.
2. Be testable or otherwise verifiable.
3. Avoid unsupported numerical precision.
4. Specify units for numerical physical quantities.
5. Distinguish measured, simulated and assumed information.
6. Distinguish current implementation from future research.
7. Avoid claiming unsupported flight performance.
8. Preserve scientific traceability.
9. Identify assumptions when authoritative information is unavailable.
10. Be updated when stronger evidence becomes available.

---

# 8. Digital Engineering Core Requirements

### BQRC-CORE-001 — Modular Architecture

The platform shall use a modular architecture separating simulation, hardware abstraction, algorithms, datasets, mission software, backend services, frontend visualization and documentation.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-CORE-002 — Scientific Separation

The platform shall separate physical truth, simulated measurement, processed measurement and final engineering result.

**Priority:** Critical  
**Verification:** Inspection + Test

### BQRC-CORE-003 — Truth Isolation

Estimation algorithms shall not directly access hidden simulation ground-truth quantities unless explicitly operating in a verification context.

**Priority:** Critical  
**Verification:** Test + Inspection

### BQRC-CORE-004 — Common Data Structures

The platform shall define common data structures for measurements, configuration, quality, uncertainty and provenance.

**Priority:** High  
**Verification:** Inspection

### BQRC-CORE-005 — Unit Consistency

Scientific calculations shall use explicitly documented physical units.

**Priority:** Critical  
**Verification:** Test + Inspection

### BQRC-CORE-006 — Configuration-Driven Operation

Scientific models shall be configurable without requiring source-code modification wherever practical.

**Priority:** High  
**Verification:** Demonstration

### BQRC-CORE-007 — Model Version Identification

Important scientific models shall expose version information.

**Priority:** High  
**Verification:** Inspection

### BQRC-CORE-008 — Model Maturity

Important models shall carry a maturity classification.

**Priority:** High  
**Verification:** Inspection

### BQRC-CORE-009 — Reproducibility

Deterministic simulations executed with identical configuration, model versions, initial conditions and random seed shall reproduce equivalent results within defined numerical tolerances.

**Priority:** Critical  
**Verification:** Test

### BQRC-CORE-010 — Extensibility

New sensors, hardware profiles, models, algorithms and applications shall be addable without redesigning unrelated platform components.

**Priority:** High  
**Verification:** Inspection + Demonstration

---

# 9. Simulation Requirements

### BQRC-SIM-001 — Simulation Orchestrator

The platform shall provide a simulation orchestrator responsible for coordinating simulation modules.

**Priority:** Critical  
**Verification:** Test

### BQRC-SIM-002 — Scenario Execution

The simulator shall execute defined engineering scenarios.

**Priority:** High  
**Verification:** Demonstration

### BQRC-SIM-003 — Initial Conditions

Simulation scenarios shall support explicit initial conditions.

**Priority:** High  
**Verification:** Test

### BQRC-SIM-004 — Deterministic Random Seed

Stochastic simulations shall support user-defined or automatically recorded random seeds.

**Priority:** Critical  
**Verification:** Test

### BQRC-SIM-005 — Simulation Modes

The simulator shall support nominal and configurable degraded operating scenarios.

**Priority:** High  
**Verification:** Demonstration

### BQRC-SIM-006 — Parameter Propagation

A parameter change shall propagate through all scientifically dependent downstream models.

**Priority:** Critical  
**Verification:** Integration Test

### BQRC-SIM-007 — No Decorative Simulation Values

Values presented as simulation outputs shall originate from defined models, datasets, calculations or explicitly identified assumptions.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-SIM-008 — State Preservation

The simulator shall maintain the state required by stateful models between simulation steps.

**Priority:** High  
**Verification:** Test

---

# 10. Time and Scheduling Requirements

### BQRC-TIME-001 — Master Clock

The platform shall maintain a common master simulation clock.

**Priority:** Critical  
**Verification:** Test

### BQRC-TIME-002 — Pause and Resume

The simulation clock shall support pause and resume.

**Priority:** High  
**Verification:** Demonstration

### BQRC-TIME-003 — Step Execution

The simulation shall support controlled step execution.

**Priority:** High  
**Verification:** Test

### BQRC-TIME-004 — Time Acceleration

The architecture shall support simulation execution faster than real time where model constraints permit.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-TIME-005 — Multi-Rate Execution

The scheduler shall support models operating at different update frequencies.

**Priority:** Critical  
**Verification:** Test

### BQRC-TIME-006 — Timestamping

Generated measurements shall contain simulation or acquisition timestamps.

**Priority:** Critical  
**Verification:** Test

### BQRC-TIME-007 — Timing Error Models

The architecture shall support modelling timestamp uncertainty, clock drift, jitter and synchronization errors where applicable.

**Priority:** Medium  
**Verification:** Test

---

# 11. Orbit and Position Requirements

### BQRC-ORB-001 — Position State

The platform shall provide position information required by environmental models.

**Priority:** Critical  
**Verification:** Test

### BQRC-ORB-002 — Velocity State

The orbital model shall provide velocity when required by downstream models.

**Priority:** High  
**Verification:** Test

### BQRC-ORB-003 — Geographic Representation

The platform shall support representation of latitude, longitude and altitude where applicable.

**Priority:** High  
**Verification:** Test

### BQRC-ORB-004 — Time Dependence

Orbital state shall evolve with simulation time when an orbital propagation model is active.

**Priority:** Critical  
**Verification:** Test

### BQRC-ORB-005 — Manual Position

The platform shall permit manual position input for controlled experiments.

**Priority:** High  
**Verification:** Demonstration

### BQRC-ORB-006 — Orbit Model Replacement

The architecture shall allow progressively higher-fidelity orbital propagation models without requiring redesign of dependent modules.

**Priority:** High  
**Verification:** Inspection

### BQRC-ORB-007 — Orbit Model Traceability

Each experiment shall identify the orbital model or position source used.

**Priority:** High  
**Verification:** Inspection

---

# 12. Reference Frame and Attitude Requirements

### BQRC-FRM-001 — Multiple Frames

The platform shall support multiple reference frames required by BQRC models.

**Priority:** Critical  
**Verification:** Test

### BQRC-FRM-002 — Frame Transformations

The platform shall provide explicit transformations between supported frames.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-FRM-003 — BQRC Body Frame

The platform shall represent a BQRC payload body frame.

**Priority:** High  
**Verification:** Inspection

### BQRC-FRM-004 — Sensor Frames

Individual sensors shall be capable of having their own defined orientation relative to the BQRC body frame.

**Priority:** High  
**Verification:** Test

### BQRC-FRM-005 — Attitude Dependence

Orientation-dependent sensor outputs shall change consistently with simulated attitude.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-FRM-006 — Numerical Robustness

Attitude representation shall use a numerically appropriate representation such as quaternions where required.

**Priority:** High  
**Verification:** Inspection + Test

---

# 13. Space Environment Requirements

### BQRC-ENV-001 — Modular Environment

Space-environment models shall be modular.

**Priority:** High  
**Verification:** Inspection

### BQRC-ENV-002 — Coupled Environment

Environmental quantities shall be capable of influencing sensor and hardware models.

**Priority:** Critical  
**Verification:** Integration Test

### BQRC-ENV-003 — Configurable Environment

Environmental conditions shall support scenario-based configuration.

**Priority:** High  
**Verification:** Demonstration

### BQRC-ENV-004 — Environment Provenance

Environment-model parameters shall identify their source or assumption status.

**Priority:** High  
**Verification:** Inspection

### BQRC-ENV-005 — Unknown Environment Handling

Unavailable BAS-specific environmental information shall be represented as explicit assumptions or configurable ranges rather than fabricated authoritative values.

**Priority:** Critical  
**Verification:** Inspection

---

# 14. Magnetic Environment Requirements

### BQRC-MAG-001 — Geomagnetic Reference

The platform shall provide a time- and position-dependent geomagnetic reference model.

**Priority:** Critical  
**Verification:** Scientific Comparison

### BQRC-MAG-002 — Vector Magnetic Field

The magnetic environment shall represent magnetic field as a vector where required.

**Priority:** Critical  
**Verification:** Test

### BQRC-MAG-003 — Frame Transformation

Magnetic vectors shall be transformable into the BQRC and sensor reference frames.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-MAG-004 — Local Magnetic Disturbance

The architecture shall support additional local magnetic disturbances.

**Priority:** High  
**Verification:** Test

### BQRC-MAG-005 — Electrical Equipment Effects

The magnetic model shall support configurable disturbances representing electrical equipment and current-carrying systems where scientifically justified.

**Priority:** High  
**Verification:** Demonstration

### BQRC-MAG-006 — BQRC Self-Contamination

The architecture shall support modelling magnetic contamination generated by BQRC hardware.

**Priority:** High  
**Verification:** Analysis + Test

### BQRC-MAG-007 — Disturbance Superposition

Multiple magnetic contributions shall be combinable according to the selected physical model.

**Priority:** High  
**Verification:** Test

### BQRC-MAG-008 — Magnetic Mapping

The platform shall support associating magnetic estimates with position, time, orientation, uncertainty and quality information.

**Priority:** High  
**Verification:** Demonstration

### BQRC-MAG-009 — Update Rate Integrity

A selected simulation or display update rate shall not be represented as equivalent to physical sensor bandwidth or independent information rate.

**Priority:** Critical  
**Verification:** Inspection

---

# 15. Microgravity and Vibration Requirements

### BQRC-MGR-001 — Residual Acceleration

The platform shall support modelling non-zero residual acceleration in microgravity scenarios.

**Priority:** Critical  
**Verification:** Test

### BQRC-MGR-002 — G-Jitter

The architecture shall support configurable g-jitter models.

**Priority:** High  
**Verification:** Test

### BQRC-MGR-003 — Vibration

The architecture shall support vibration disturbances.

**Priority:** High  
**Verification:** Test

### BQRC-MGR-004 — Transient Events

The microgravity environment shall support transient acceleration events.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-MGR-005 — Frequency Analysis

Microgravity measurements shall be usable for time- and frequency-domain analysis.

**Priority:** High  
**Verification:** Demonstration

### BQRC-MGR-006 — Source Traceability

Disturbance models shall identify whether they originate from measured data, literature, physical modelling or engineering assumptions.

**Priority:** Critical  
**Verification:** Inspection

---

# 16. Thermal Requirements

### BQRC-THM-001 — Temperature State

The platform shall maintain temperature information required by temperature-sensitive models.

**Priority:** Critical  
**Verification:** Test

### BQRC-THM-002 — Component Heat

The architecture shall support component-generated heat.

**Priority:** High  
**Verification:** Analysis

### BQRC-THM-003 — Power-Thermal Coupling

Component power consumption shall be capable of influencing thermal behaviour where applicable.

**Priority:** High  
**Verification:** Integration Test

### BQRC-THM-004 — Sensor Thermal Effects

Temperature shall be capable of affecting temperature-sensitive sensor parameters.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-THM-005 — Manual Temperature

Users shall be able to define controlled temperature scenarios.

**Priority:** High  
**Verification:** Demonstration

---

# 17. Radiation Requirements

### BQRC-RAD-001 — Radiation Measurement

The platform shall support radiation measurements or simulated radiation quantities.

**Priority:** High  
**Verification:** Demonstration

### BQRC-RAD-002 — Radiation Scenarios

The simulator shall support configurable radiation scenarios.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-RAD-003 — Radiation Events

The architecture shall support transient radiation events where justified.

**Priority:** Medium  
**Verification:** Test

### BQRC-RAD-004 — Radiation Hardware Effects

Radiation-induced hardware effects may be introduced only where a scientifically supported model or explicit engineering assumption exists.

**Priority:** High  
**Verification:** Inspection

---

# 18. NV-Center Quantum Sensor Requirements

### BQRC-NV-001 — NV Physics Model

The platform shall provide an NV-center sensing model suitable for the selected BQRC quantum-sensing experiment.

**Priority:** Critical  
**Verification:** Scientific Comparison

### BQRC-NV-002 — Magnetic Dependence

The NV model shall respond to magnetic-field input.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-NV-003 — Temperature Dependence

The NV model shall support temperature-dependent behaviour where required by the implemented physical model.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-NV-004 — Orientation Dependence

The NV model shall support orientation-dependent magnetic response.

**Priority:** High  
**Verification:** Scientific Test

### BQRC-NV-005 — Research Maturity

NV gyroscope and future NV accelerometer capabilities shall be explicitly labelled according to their research maturity.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-NV-006 — No Unsupported Flight Claim

Simulated NV performance shall not be represented as demonstrated BQRC flight performance.

**Priority:** Critical  
**Verification:** Inspection

---

# 19. ODMR Requirements

### BQRC-ODMR-001 — Spectrum Generation

The simulator shall generate an ODMR response from the selected NV physical model rather than directly outputting only the final magnetic estimate.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-ODMR-002 — Microwave Sweep

The architecture shall support configurable microwave excitation/sweep parameters required by the selected ODMR model.

**Priority:** High  
**Verification:** Test

### BQRC-ODMR-003 — Fluorescence Response

The model shall represent an optical fluorescence response associated with ODMR behaviour.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-ODMR-004 — Raw Spectrum Preservation

Raw generated or measured ODMR spectra shall be preservable before fitting.

**Priority:** Critical  
**Verification:** Test

### BQRC-ODMR-005 — Resonance Detection

The processing system shall support resonance detection.

**Priority:** Critical  
**Verification:** Test

### BQRC-ODMR-006 — Lineshape Fitting

The processing system shall support a scientifically justified classical resonance-fitting method.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-ODMR-007 — Magnetic Estimation

The magnetic estimate shall be derived from processed ODMR information according to the implemented physical model.

**Priority:** Critical  
**Verification:** Scientific Test

### BQRC-ODMR-008 — Temperature Compensation

The architecture shall support temperature compensation where required by the selected ODMR measurement method.

**Priority:** High  
**Verification:** Test

### BQRC-ODMR-009 — Fit Quality

ODMR processing shall expose an appropriate fit or estimation quality metric where applicable.

**Priority:** High  
**Verification:** Test

---

# 20. Conventional IMU Requirements

### BQRC-IMU-001 — Three-Axis Acceleration

The platform shall support three-axis acceleration measurements.

**Priority:** Critical  
**Verification:** Test

### BQRC-IMU-002 — Three-Axis Angular Rate

The platform shall support three-axis gyroscope measurements.

**Priority:** Critical  
**Verification:** Test

### BQRC-IMU-003 — Bias

The IMU model shall support configurable sensor bias.

**Priority:** Critical  
**Verification:** Test

### BQRC-IMU-004 — White Noise

The IMU model shall support white measurement noise.

**Priority:** Critical  
**Verification:** Statistical Test

### BQRC-IMU-005 — Random Walk

The architecture shall support random-walk-type error processes where justified by the hardware model.

**Priority:** High  
**Verification:** Statistical Test

### BQRC-IMU-006 — Scale Factor

The IMU model shall support scale-factor error.

**Priority:** High  
**Verification:** Test

### BQRC-IMU-007 — Misalignment

The IMU model shall support sensor-axis misalignment.

**Priority:** High  
**Verification:** Test

### BQRC-IMU-008 — Cross-Axis Effects

The architecture shall support cross-axis coupling where required by the selected hardware model.

**Priority:** Medium  
**Verification:** Test

### BQRC-IMU-009 — Saturation

The IMU model shall support sensor saturation according to the configured hardware profile.

**Priority:** High  
**Verification:** Test

### BQRC-IMU-010 — Quantization

The IMU model shall support finite measurement resolution where applicable.

**Priority:** High  
**Verification:** Test

### BQRC-IMU-011 — Temperature Dependence

The IMU model shall support temperature-dependent errors where supported by evidence.

**Priority:** High  
**Verification:** Test

---

# 21. Hardware Digital Twin Requirements

### BQRC-HW-001 — Hardware Profiles

Important BQRC components shall be representable through hardware profiles.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-HW-002 — Manufacturer Information

Hardware profiles shall support manufacturer and model information when known.

**Priority:** High  
**Verification:** Inspection

### BQRC-HW-003 — Datasheet Provenance

Datasheet-derived parameters shall reference their source.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-HW-004 — Candidate Hardware

Candidate hardware shall be explicitly distinguishable from selected hardware.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-HW-005 — Hardware Swapping

Users shall be able to execute equivalent scenarios using different compatible hardware profiles.

**Priority:** High  
**Verification:** Demonstration

### BQRC-HW-006 — Hardware Impact

Changing a hardware profile shall affect relevant model behaviour rather than only changing displayed metadata.

**Priority:** Critical  
**Verification:** Integration Test

### BQRC-HW-007 — Model Maturity

Hardware profiles shall identify whether characteristics are literature-based, datasheet-based, laboratory-calibrated or otherwise validated.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-HW-008 — Custom Hardware

The architecture shall support future user-defined hardware profiles.

**Priority:** Medium  
**Verification:** Demonstration

---

# 22. Electronics and Acquisition Requirements

### BQRC-ELEC-001 — Acquisition Chain

The NV sensor simulation shall support an acquisition chain between physical sensor response and digital raw data.

**Priority:** Critical  
**Verification:** Inspection + Test

### BQRC-ELEC-002 — Detector Model

The architecture shall support APD/photodetector characteristics relevant to the selected design.

**Priority:** High  
**Verification:** Test

### BQRC-ELEC-003 — Analog Noise

The acquisition model shall support configurable electronics noise.

**Priority:** High  
**Verification:** Statistical Test

### BQRC-ELEC-004 — ADC Resolution

The architecture shall support finite ADC resolution.

**Priority:** High  
**Verification:** Test

### BQRC-ELEC-005 — ADC Range

The acquisition model shall support ADC input range and saturation where applicable.

**Priority:** High  
**Verification:** Test

### BQRC-ELEC-006 — Power-Supply Effects

The architecture shall permit power-supply-related disturbances where scientifically supported.

**Priority:** Medium  
**Verification:** Test

---

# 23. Dataset Requirements

### BQRC-DATA-001 — Dataset Classification

Datasets shall be classified as measured, generated, hybrid, replay or other explicitly defined origin.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-DATA-002 — No Synthetic Misrepresentation

Generated datasets shall not be represented as measured data.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-DATA-003 — Real Data Preference

Suitable real measured data shall be preferred when it exists and is scientifically applicable.

**Priority:** High  
**Verification:** Inspection

### BQRC-DATA-004 — Synthetic Gap Filling

Synthetic data may be generated to fill scientifically justified data gaps.

**Priority:** High  
**Verification:** Inspection

### BQRC-DATA-005 — Extreme Cases

The dataset system shall support controlled best-case, nominal, degraded, worst-credible and research-extreme scenarios where justified.

**Priority:** High  
**Verification:** Demonstration

### BQRC-DATA-006 — Dataset Metadata

Important datasets shall include provenance metadata.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-DATA-007 — Units

Dataset variables shall document units.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-DATA-008 — Sampling Information

Time-series datasets shall document sampling information when available.

**Priority:** High  
**Verification:** Inspection

### BQRC-DATA-009 — Generation Reproducibility

Generated datasets shall record sufficient information for reproduction where practical.

**Priority:** Critical  
**Verification:** Test + Inspection

### BQRC-DATA-010 — Dataset Versioning

Datasets used in important experiments shall be version identifiable.

**Priority:** High  
**Verification:** Inspection

### BQRC-DATA-011 — Raw Data Preservation

Original raw data shall be preserved separately from processed derivatives where practical.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-DATA-012 — Dataset Validation

Synthetic and augmented datasets shall be compared against physical expectations, reference models or measured data where possible.

**Priority:** Critical  
**Verification:** Analysis

---

# 24. Calibration Requirements

### BQRC-CAL-001 — Calibration Support

The platform shall support sensor calibration workflows.

**Priority:** Critical  
**Verification:** Demonstration

### BQRC-CAL-002 — Calibration Version

Calibration parameters shall be version identifiable.

**Priority:** High  
**Verification:** Inspection

### BQRC-CAL-003 — Calibration Provenance

Calibration parameters shall identify their source.

**Priority:** High  
**Verification:** Inspection

### BQRC-CAL-004 — Calibration Validity

Calibration information should document its applicable range where known.

**Priority:** High  
**Verification:** Inspection

### BQRC-CAL-005 — Raw Data Preservation

Calibration shall not destroy the original raw measurement.

**Priority:** Critical  
**Verification:** Test

---

# 25. Uncertainty and Quality Requirements

### BQRC-UNC-001 — Measurement Uncertainty

Important estimated quantities shall support uncertainty information where scientifically meaningful.

**Priority:** High  
**Verification:** Inspection + Test

### BQRC-UNC-002 — Quality Flags

Measurements shall support quality-state information.

**Priority:** High  
**Verification:** Test

### BQRC-UNC-003 — Invalid Data

The platform shall distinguish invalid or missing measurements from valid zero-valued measurements.

**Priority:** Critical  
**Verification:** Test

### BQRC-UNC-004 — Saturation Flag

Saturated measurements shall be identifiable.

**Priority:** High  
**Verification:** Test

### BQRC-UNC-005 — Extrapolation Warning

The platform shall support identifying results produced outside a model's validated range.

**Priority:** Critical  
**Verification:** Test

### BQRC-UNC-006 — Uncertainty Propagation

The architecture shall support propagation of important uncertainties through derived quantities.

**Priority:** High  
**Verification:** Analysis

---

# 26. Algorithm Requirements

### BQRC-ALG-001 — Algorithm Separation

Estimation algorithms shall remain separable from the physical simulator.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-ALG-002 — Dataset Compatibility

Algorithms shall be capable of operating on compatible simulated, replayed or measured data.

**Priority:** High  
**Verification:** Integration Test

### BQRC-ALG-003 — Algorithm Versioning

Important algorithms shall be version identifiable.

**Priority:** High  
**Verification:** Inspection

### BQRC-ALG-004 — Input Validation

Algorithms shall validate critical input structure and units where practical.

**Priority:** High  
**Verification:** Test

### BQRC-ALG-005 — Failure Handling

Algorithms shall not silently return apparently valid engineering values when required inputs are invalid.

**Priority:** Critical  
**Verification:** Test

---

# 27. Sensor Fusion Requirements

### BQRC-FUS-001 — Classical Baseline

The platform shall support at least one classical sensor-fusion approach before advanced ML fusion is treated as a research comparison.

**Priority:** High  
**Verification:** Demonstration

### BQRC-FUS-002 — Measurement Quality

Fusion algorithms shall be capable of considering measurement quality where applicable.

**Priority:** High  
**Verification:** Test

### BQRC-FUS-003 — Measurement Uncertainty

Fusion algorithms should use measurement uncertainty/covariance where supported by the selected method.

**Priority:** High  
**Verification:** Scientific Test

### BQRC-FUS-004 — Outlier Handling

The architecture shall support outlier detection or gating for appropriate fusion algorithms.

**Priority:** High  
**Verification:** Test

---

# 28. Mission Software Requirements

### BQRC-MSN-001 — Mission States

The mission emulator shall support defined operational states.

**Priority:** High  
**Verification:** Test

### BQRC-MSN-002 — State-Dependent Hardware

Mission state shall influence subsystem operation.

**Priority:** Critical  
**Verification:** Integration Test

### BQRC-MSN-003 — Boot State

The architecture shall support a boot/initialization sequence.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-MSN-004 — Calibration State

The architecture shall support a calibration mode or workflow.

**Priority:** High  
**Verification:** Demonstration

### BQRC-MSN-005 — Science State

The architecture shall support a science-data-acquisition mode.

**Priority:** Critical  
**Verification:** Demonstration

### BQRC-MSN-006 — Safe State

The architecture shall support a safe state for selected simulated fault conditions.

**Priority:** High  
**Verification:** Test

---

# 29. Telemetry Requirements

### BQRC-TLM-001 — Telemetry Generation

The platform shall support generation of payload telemetry from measurements and health information.

**Priority:** High  
**Verification:** Test

### BQRC-TLM-002 — Timestamp

Telemetry records shall include time information.

**Priority:** Critical  
**Verification:** Test

### BQRC-TLM-003 — Packet Simulation

The architecture shall support packetized telemetry simulation.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-TLM-004 — Packet Loss

The simulator shall support configurable packet loss.

**Priority:** Medium  
**Verification:** Test

### BQRC-TLM-005 — Corruption

The architecture shall support controlled telemetry corruption for fault studies.

**Priority:** Medium  
**Verification:** Test

### BQRC-TLM-006 — Storage Constraints

The architecture shall support modelling onboard data-storage constraints.

**Priority:** Medium  
**Verification:** Analysis

### BQRC-TLM-007 — BAS Interface Assumptions

Unavailable BAS interface details shall be explicitly identified as assumptions until authoritative information becomes available.

**Priority:** Critical  
**Verification:** Inspection

---

# 30. Fault Requirements

### BQRC-FLT-001 — Fault Injection

The platform shall support controlled fault injection.

**Priority:** High  
**Verification:** Demonstration

### BQRC-FLT-002 — Layer-Correct Injection

Faults shall be injected at the appropriate physical, hardware, data or software layer rather than modifying only final displayed results.

**Priority:** Critical  
**Verification:** Inspection + Test

### BQRC-FLT-003 — Reproducible Faults

Fault scenarios shall be reproducible where practical.

**Priority:** High  
**Verification:** Test

### BQRC-FLT-004 — Sensor Dropout

The simulator shall support sensor-data dropout.

**Priority:** High  
**Verification:** Test

### BQRC-FLT-005 — Bias Fault

The simulator shall support controlled sensor-bias faults.

**Priority:** High  
**Verification:** Test

### BQRC-FLT-006 — NV Chain Faults

The architecture shall support representative faults in the NV sensing chain such as laser, microwave or detector anomalies.

**Priority:** High  
**Verification:** Demonstration

---

# 31. Analysis Requirements

### BQRC-ANA-001 — Time-Series Analysis

The platform shall support time-series visualization and analysis.

**Priority:** High  
**Verification:** Demonstration

### BQRC-ANA-002 — Residual Analysis

The platform shall support comparison of estimates against appropriate references or simulation truth.

**Priority:** Critical  
**Verification:** Test

### BQRC-ANA-003 — Error Metrics

The platform shall support relevant quantitative error metrics.

**Priority:** High  
**Verification:** Test

### BQRC-ANA-004 — Frequency Analysis

The architecture shall support frequency-domain analysis for applicable signals.

**Priority:** High  
**Verification:** Demonstration

### BQRC-ANA-005 — Stability Analysis

The platform shall support appropriate long-duration sensor-stability analysis.

**Priority:** High  
**Verification:** Demonstration

### BQRC-ANA-006 — Correlation

The platform shall support correlation analysis between relevant environmental and sensor channels.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-ANA-007 — Export

Analysis results shall be exportable in a documented format.

**Priority:** High  
**Verification:** Demonstration

---

# 32. Application Requirements

### BQRC-APP-001 — Real Pipeline Outputs

Applications shall consume outputs from the actual simulation/data-processing pipeline rather than unrelated demonstration values.

**Priority:** Critical  
**Verification:** Integration Test

### BQRC-APP-002 — Quantum Magnetometry

The platform shall provide an application demonstrating NV-based magnetic-field estimation.

**Priority:** Critical  
**Verification:** Demonstration

### BQRC-APP-003 — Magnetic Mapping

The platform shall support magnetic-field mapping research using position, time, orientation and magnetic estimates.

**Priority:** High  
**Verification:** Demonstration

### BQRC-APP-004 — Microgravity Characterization

The platform shall provide a residual-microgravity characterization application.

**Priority:** High  
**Verification:** Demonstration

### BQRC-APP-005 — Thermal Characterization

The platform shall support thermal-environment analysis.

**Priority:** High  
**Verification:** Demonstration

### BQRC-APP-006 — Radiation Characterization

The platform shall support radiation-environment analysis.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-APP-007 — Sensor Comparison

The platform shall support quantum-versus-classical sensor comparison where scientifically meaningful.

**Priority:** High  
**Verification:** Demonstration

### BQRC-APP-008 — Payload Health

The platform shall support payload-health visualization.

**Priority:** High  
**Verification:** Demonstration

---

# 33. Navigation Research Requirements

### BQRC-NAV-001 — Research Classification

Navigation functionality shall initially be identified as research functionality rather than demonstrated flight capability.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-NAV-002 — State Estimation

The architecture shall support future estimation of navigation states using compatible sensor measurements.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-NAV-003 — Magnetic Ambiguity

Magnetic measurements shall not be assumed to uniquely determine position.

**Priority:** Critical  
**Verification:** Inspection + Scientific Test

### BQRC-NAV-004 — Truth Comparison

Navigation simulations shall support comparison against simulated true trajectory.

**Priority:** High  
**Verification:** Test

### BQRC-NAV-005 — Inertial Drift

The navigation research environment shall support investigation of inertial drift.

**Priority:** High  
**Verification:** Demonstration

### BQRC-NAV-006 — Future Astronaut Assistance

The architecture shall permit future astronaut-assist navigation research without coupling it to the initial BQRC flight-payload claim.

**Priority:** Medium  
**Verification:** Inspection

---

# 34. AI / ML / DL Requirements

### BQRC-ML-001 — Supporting Role

AI/ML/DL shall be treated as supporting research capability rather than a replacement for validated physical models.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-ML-002 — Classical Baseline

ML-based approaches shall be compared against an appropriate classical baseline where one exists.

**Priority:** Critical  
**Verification:** Analysis

### BQRC-ML-003 — Dataset Provenance

Training and evaluation datasets shall preserve provenance.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-ML-004 — Train/Test Separation

ML evaluation shall use scientifically appropriate separation between training and evaluation data.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-ML-005 — Anomaly Detection

The architecture shall support future telemetry anomaly-detection research.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-ML-006 — Fault Classification

The architecture shall support future fault/event classification research.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-ML-007 — ODMR Research

The platform shall permit comparison between classical ODMR processing and ML-based ODMR estimation.

**Priority:** Medium  
**Verification:** Analysis

### BQRC-ML-008 — No Unsupported Generalization

ML performance shall not be claimed outside validated data domains without explicit qualification.

**Priority:** Critical  
**Verification:** Inspection

---

# 35. Backend/API Requirements

### BQRC-API-001 — Scientific Backend

Core scientific calculations shall execute outside the frontend presentation layer.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-API-002 — Simulation Control

The backend shall expose interfaces required to control simulations.

**Priority:** High  
**Verification:** Integration Test

### BQRC-API-003 — Configuration Access

The backend shall support access to approved configuration data.

**Priority:** High  
**Verification:** Test

### BQRC-API-004 — Experiment Management

The architecture shall support creation and retrieval of experiment records.

**Priority:** High  
**Verification:** Test

### BQRC-API-005 — Dataset Access

The backend shall support controlled dataset access.

**Priority:** High  
**Verification:** Test

### BQRC-API-006 — Hardware Profiles

The backend shall expose relevant hardware-profile information to applications.

**Priority:** High  
**Verification:** Test

---

# 36. Web Interface Requirements

### BQRC-UI-001 — Engineering Interface

The web application shall act as an interface to actual BQRC engineering models and data.

**Priority:** Critical  
**Verification:** Integration Test

### BQRC-UI-002 — Simulation Control

The interface shall provide simulation control appropriate to the current implementation.

**Priority:** High  
**Verification:** Demonstration

### BQRC-UI-003 — Parameter Controls

The interface shall support user-adjustable parameters for approved configurable quantities.

**Priority:** High  
**Verification:** Demonstration

### BQRC-UI-004 — Manual Override Visibility

The interface shall clearly identify manually overridden parameters.

**Priority:** Critical  
**Verification:** Demonstration

### BQRC-UI-005 — Source Visibility

The interface shall eventually allow users to inspect important parameter/model sources.

**Priority:** High  
**Verification:** Demonstration

### BQRC-UI-006 — Model Maturity Visibility

The interface shall expose model maturity where relevant.

**Priority:** High  
**Verification:** Demonstration

### BQRC-UI-007 — Uncertainty Display

Important engineering results shall display uncertainty where available and meaningful.

**Priority:** High  
**Verification:** Demonstration

### BQRC-UI-008 — Quality Display

The interface shall display measurement quality information where applicable.

**Priority:** High  
**Verification:** Demonstration

### BQRC-UI-009 — No False Precision

The interface shall not display numerical precision unsupported by the underlying model or measurement.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-UI-010 — Actual-State Animation

Animations representing engineering state shall be driven by actual simulation state wherever practical.

**Priority:** High  
**Verification:** Integration Test

---

# 37. Knowledge, Documentation and Evidence Requirements

### BQRC-KNW-001 — Mission Guide

The platform shall contain a comprehensive explanation of the BQRC mission and platform.

**Priority:** High  
**Verification:** Inspection

### BQRC-KNW-002 — Beginner Documentation

The knowledge system shall provide beginner-level explanations.

**Priority:** High  
**Verification:** Inspection

### BQRC-KNW-003 — Engineering Documentation

The knowledge system shall provide engineering-level documentation.

**Priority:** High  
**Verification:** Inspection

### BQRC-KNW-004 — Research Documentation

The knowledge system shall support research-level sources and detailed model information.

**Priority:** High  
**Verification:** Inspection

### BQRC-KNW-005 — Formula Library

Important scientific formulas shall be documented.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-KNW-006 — Formula Sources

Important formulas shall reference appropriate scientific sources.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-KNW-007 — Dataset Sources

Dataset entries shall reference their source where applicable.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-KNW-008 — Hardware Sources

Important hardware parameters shall link to supporting datasheets or characterization evidence.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-KNW-009 — Assumption Register

The project shall maintain an explicit assumption register.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-KNW-010 — Limitation Documentation

Important models and applications shall document known limitations.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-KNW-011 — User Guide

The web application shall eventually provide instructions explaining how to use its major engineering functions.

**Priority:** High  
**Verification:** Demonstration

---

# 38. Verification and Validation Requirements

### BQRC-VER-001 — Requirement Traceability

Important implementation features shall be traceable to requirements.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-VER-002 — Verification Record

Verified requirements shall retain verification evidence.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-VER-003 — Unit Tests

Core scientific and engineering functions shall have unit tests where appropriate.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-VER-004 — Integration Tests

Important subsystem interactions shall have integration tests.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-VER-005 — Scientific Tests

Scientific models shall be compared against known equations, reference values, literature results or appropriate datasets where possible.

**Priority:** Critical  
**Verification:** Analysis

### BQRC-VER-006 — Golden Cases

The project shall maintain deterministic scientific golden test cases.

**Priority:** High  
**Verification:** Test

### BQRC-VER-007 — Regression Testing

Changes shall be testable against established behaviour to identify unintended regressions.

**Priority:** High  
**Verification:** Test

### BQRC-VER-008 — Simulation Limitation

Simulation verification shall not be presented as physical flight qualification.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-VER-009 — Model-to-Reality Validation

When laboratory hardware becomes available, corresponding digital models shall be compared against physical measurements.

**Priority:** High  
**Verification:** Comparison

---

# 39. Hardware-in-the-Loop Requirements

### BQRC-HIL-001 — Common Sensor Interface

Simulated and physical sensors should use compatible abstraction interfaces wherever practical.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-HIL-002 — Driver Replacement

The architecture shall permit simulated sensor drivers to be replaced with real hardware drivers without redesigning unrelated downstream algorithms.

**Priority:** Critical  
**Verification:** Integration Test

### BQRC-HIL-003 — Dataset Replay

The architecture shall support dataset replay as an intermediate stage between simulation and physical hardware.

**Priority:** High  
**Verification:** Demonstration

### BQRC-HIL-004 — Hardware Timestamping

Future physical hardware measurements shall support timing information compatible with the BQRC data pipeline.

**Priority:** High  
**Verification:** Test

### BQRC-HIL-005 — Model Calibration

Physical measurements shall be usable to calibrate digital hardware models.

**Priority:** High  
**Verification:** Comparison

---

# 40. Performance Requirements

### BQRC-PERF-001 — Performance Measurement

Simulation execution performance shall be measurable.

**Priority:** Medium  
**Verification:** Test

### BQRC-PERF-002 — Scientific Priority

Scientific correctness and traceability shall take priority over unnecessary graphical update rate.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-PERF-003 — Configurable Fidelity

The architecture should permit different simulation fidelity/performance configurations where appropriate.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-PERF-004 — Large Experiment Support

The architecture shall support future batch and Monte Carlo execution without requiring the web interface to remain open.

**Priority:** Medium  
**Verification:** Demonstration

---

# 41. Software and Data Integrity Requirements

### BQRC-SEC-001 — Input Validation

User-provided configuration values shall be validated before use.

**Priority:** Critical  
**Verification:** Test

### BQRC-SEC-002 — Invalid Range Warning

The platform shall identify values outside supported model ranges where such ranges are known.

**Priority:** Critical  
**Verification:** Test

### BQRC-SEC-003 — Experiment Integrity

Stored experiment metadata shall preserve the configuration needed to interpret results.

**Priority:** High  
**Verification:** Inspection

### BQRC-SEC-004 — Source Data Protection

Raw reference datasets shall not be silently modified during processing.

**Priority:** Critical  
**Verification:** Test

### BQRC-SEC-005 — Configuration Validation

Configuration files shall be checked for required fields and incompatible values where practical.

**Priority:** High  
**Verification:** Test

---

# 42. Manual Override Requirements

### BQRC-CORE-011 — Parameter Sources

Important configurable quantities shall support explicit identification of their source.

Possible sources include:

```text
MODEL
DATASET
MANUAL
HARDWARE
```

**Priority:** Critical  
**Verification:** Test

### BQRC-CORE-012 — Override Operation

The platform shall support manual override for approved parameters.

**Priority:** High  
**Verification:** Demonstration

### BQRC-CORE-013 — Offset Operation

The platform should support controlled offsets for suitable parameters.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-CORE-014 — Scale Operation

The platform should support controlled scaling for suitable parameters.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-CORE-015 — Override Traceability

Manual overrides used during an experiment shall be recorded.

**Priority:** Critical  
**Verification:** Test

### BQRC-CORE-016 — Physical Propagation

Manual changes shall propagate through dependent models rather than altering only frontend values.

**Priority:** Critical  
**Verification:** Integration Test

---

# 43. Experiment Requirements

### BQRC-CORE-017 — Experiment Identifier

Important simulation runs shall support a unique experiment identifier.

**Priority:** High  
**Verification:** Test

### BQRC-CORE-018 — Experiment Configuration

Experiment records shall identify the configuration used.

**Priority:** Critical  
**Verification:** Inspection

### BQRC-CORE-019 — Experiment Models

Experiment records shall identify important model versions.

**Priority:** High  
**Verification:** Inspection

### BQRC-CORE-020 — Experiment Dataset

Experiment records shall identify important datasets used.

**Priority:** High  
**Verification:** Inspection

### BQRC-CORE-021 — Experiment Hardware

Experiment records shall identify relevant hardware profiles.

**Priority:** High  
**Verification:** Inspection

### BQRC-CORE-022 — Experiment Seed

Stochastic experiment records shall preserve the random seed where required for reproducibility.

**Priority:** Critical  
**Verification:** Test

---

# 44. Monte Carlo Requirements

### BQRC-SIM-009 — Monte Carlo Execution

The platform shall support repeated simulation using controlled parameter variation.

**Priority:** High  
**Verification:** Demonstration

### BQRC-SIM-010 — Parameter Distributions

Monte Carlo parameters shall support explicitly defined distributions or sampling rules.

**Priority:** High  
**Verification:** Inspection

### BQRC-SIM-011 — Monte Carlo Reproducibility

Monte Carlo studies shall support reproducible random seeds.

**Priority:** Critical  
**Verification:** Test

### BQRC-SIM-012 — Statistical Output

Monte Carlo results shall support statistical analysis.

**Priority:** High  
**Verification:** Demonstration

---

# 45. Hardware Trade-Study Requirements

### BQRC-HW-009 — Comparable Scenario

Candidate hardware comparisons shall support execution under equivalent scenarios.

**Priority:** Critical  
**Verification:** Test

### BQRC-HW-010 — Engineering Metrics

Hardware comparisons shall support relevant engineering metrics such as performance, power, mass, bandwidth, data rate and environmental behaviour when information is available.

**Priority:** High  
**Verification:** Demonstration

### BQRC-HW-011 — Evidence-Based Comparison

Trade-study values shall remain traceable to models, measurements, datasheets or assumptions.

**Priority:** Critical  
**Verification:** Inspection

---

# 46. Power and Data Budget Requirements

### BQRC-HW-012 — Component Power

Hardware profiles shall support component power information where available.

**Priority:** High  
**Verification:** Inspection

### BQRC-HW-013 — Mission-Mode Power

The platform shall support calculation of payload power according to active mission mode.

**Priority:** High  
**Verification:** Analysis

### BQRC-DATA-013 — Data Generation Rate

The platform shall support estimation of generated data rate.

**Priority:** High  
**Verification:** Analysis

### BQRC-DATA-014 — Storage Estimate

The platform shall support estimation of storage consumption over experiment duration.

**Priority:** High  
**Verification:** Analysis

### BQRC-DATA-015 — Downlink Estimate

The architecture shall support future estimation of downlink data requirements.

**Priority:** Medium  
**Verification:** Analysis

---

# 47. Magnetic Cleanliness Requirements

### BQRC-MAG-010 — Magnetic Source Model

The architecture shall permit local magnetic contamination sources to be represented individually.

**Priority:** High  
**Verification:** Test

### BQRC-MAG-011 — Source Position

Magnetic source models should support spatial relationship to the NV sensor where required by the selected physical model.

**Priority:** High  
**Verification:** Test

### BQRC-MAG-012 — Hardware Placement Research

The platform shall permit future magnetic-cleanliness placement studies.

**Priority:** Medium  
**Verification:** Demonstration

### BQRC-MAG-013 — Unknown Station Sources

Unknown station magnetic sources shall not be represented as known BAS characteristics without evidence.

**Priority:** Critical  
**Verification:** Inspection

---

# 48. Initial V1 Requirements

The first implementation shall focus on a complete scientific vertical slice.

### BQRC-V1-001 — Master Clock

V1 shall implement a working master simulation clock.

### BQRC-V1-002 — Position Input

V1 shall support at least manual position input or a basic orbital-position source.

### BQRC-V1-003 — Geomagnetic Reference

V1 shall implement a scientifically sourced geomagnetic reference model suitable for the initial simulation.

### BQRC-V1-004 — Magnetic Truth

V1 shall maintain magnetic ground truth separately from sensor estimate.

### BQRC-V1-005 — Frame Transformation

V1 shall implement the frame transformation required for the initial magnetic experiment.

### BQRC-V1-006 — Local Disturbance

V1 shall support at least one configurable local magnetic disturbance.

### BQRC-V1-007 — NV Physics

V1 shall implement an evidence-based NV magnetometry model.

### BQRC-V1-008 — ODMR Generation

V1 shall generate a simulated ODMR spectrum.

### BQRC-V1-009 — Noise

V1 shall include at least one scientifically justified detector/electronics noise model.

### BQRC-V1-010 — ODMR Estimation

V1 shall estimate resonance information from the generated noisy spectrum.

### BQRC-V1-011 — Magnetic Estimate

V1 shall calculate an estimated magnetic quantity from processed ODMR data.

### BQRC-V1-012 — Truth Comparison

V1 shall compare the estimated result with simulation truth.

### BQRC-V1-013 — Quality

V1 shall expose a basic quality or fit metric.

### BQRC-V1-014 — Uncertainty

V1 shall support an initial uncertainty estimate where scientifically justified.

### BQRC-V1-015 — IMU Channel

V1 shall include a basic conventional IMU simulation channel.

### BQRC-V1-016 — Backend

V1 shall expose simulation outputs through a backend interface.

### BQRC-V1-017 — Web Visualization

V1 shall visualize actual simulation outputs through the web application.

### BQRC-V1-018 — Manual Parameters

V1 shall provide selected manual parameter controls.

### BQRC-V1-019 — Source Information

V1 shall expose the scientific source or model information for major implemented models.

### BQRC-V1-020 — Experiment Export

V1 shall support export of important experiment results and configuration.

---

# 49. Scientific Integrity Requirements

The following requirements apply across the entire project.

### BQRC-SCI-001

The platform shall never intentionally represent simulated data as measured data.

### BQRC-SCI-002

The platform shall never intentionally represent an engineering assumption as established scientific fact.

### BQRC-SCI-003

Candidate hardware shall not be represented as selected flight hardware unless formally selected.

### BQRC-SCI-004

Literature-based models shall not be represented as flight-validated models.

### BQRC-SCI-005

Raw data shall be preserved where scientifically practical.

### BQRC-SCI-006

Important parameter provenance shall be preserved.

### BQRC-SCI-007

Known limitations shall be documented.

### BQRC-SCI-008

Model validity ranges shall be documented when known.

### BQRC-SCI-009

Simulation results shall not be described as hardware qualification evidence.

### BQRC-SCI-010

When stronger measured or authoritative evidence becomes available, unsupported assumptions shall be reviewed and replaced where appropriate.

---

# 50. Requirement Traceability Matrix

The detailed traceability matrix will be maintained as implementation begins.

Initial structure:

| Requirement | Design | Implementation | Test | Evidence | Status |
|---|---|---|---|---|---|
| BQRC-CORE-001 | TBD | TBD | TBD | TBD | BASELINED |
| BQRC-SIM-001 | TBD | TBD | TBD | TBD | BASELINED |
| BQRC-TIME-001 | TBD | TBD | TBD | TBD | BASELINED |
| BQRC-MAG-001 | TBD | TBD | TBD | TBD | BASELINED |
| BQRC-NV-001 | TBD | TBD | TBD | TBD | BASELINED |
| BQRC-ODMR-001 | TBD | TBD | TBD | TBD | BASELINED |
| BQRC-IMU-001 | TBD | TBD | TBD | TBD | BASELINED |
| BQRC-DATA-001 | TBD | TBD | TBD | TBD | BASELINED |
| BQRC-VER-001 | TBD | TBD | TBD | TBD | BASELINED |

The matrix shall expand during development.

---

# 51. Requirement Refinement Policy

Some requirements intentionally do not yet specify numerical thresholds.

This is because numerical engineering requirements shall not be invented simply to make the specification appear complete.

Values such as:

- magnetic sensitivity
- magnetic accuracy
- ODMR linewidth
- sampling frequency
- laser power
- microwave power
- accelerometer noise
- gyroscope drift
- thermal range
- radiation range
- payload power
- mass
- storage
- telemetry rate
- processing latency

shall be progressively baselined using:

```text
Mission Need
      +
Scientific Literature
      +
Hardware Datasheets
      +
Real Datasets
      +
Laboratory Measurements
      +
System Trade Studies
      ↓
Defensible Engineering Requirement
```

Once a value becomes sufficiently supported, the associated requirement shall be updated with:

- numerical threshold
- units
- tolerance
- operating conditions
- source
- verification method

---

# 52. Final Requirement Principle

The BQRC requirements system exists to ensure that development does not become:

```text
Idea
↓
Code
↓
Pretty Dashboard
```

Instead, development shall follow:

```text
MISSION OBJECTIVE
        ↓
SCIENTIFIC EVIDENCE
        ↓
REQUIREMENT
        ↓
ARCHITECTURE
        ↓
MODEL / HARDWARE / DATASET
        ↓
IMPLEMENTATION
        ↓
TEST
        ↓
VERIFICATION
        ↓
EVIDENCE
        ↓
APPLICATION
```

The purpose of this document is therefore not merely project documentation.

It is the engineering contract connecting the original BQRC mission concept to the software, simulations, datasets, hardware models, experiments and future physical payload.