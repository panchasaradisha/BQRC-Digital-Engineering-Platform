# BQRC Digital Engineering Platform

## Assumptions, Unknowns and Evidence Register

**Project:** BQRC-01 — Bharatiya Quantum Research Cube  
**Document:** Assumptions, Unknowns and Evidence Register  
**Status:** Initial Development Baseline  
**Parent Documents:** `PROJECT_BASELINE.md`, `SYSTEM_ARCHITECTURE.md`, `REQUIREMENTS.md`

---

# 1. Purpose

This document records assumptions, unknowns, provisional engineering values, evidence gaps and unresolved technical decisions used during development of the BQRC Digital Engineering Platform.

The purpose is to prevent:

- assumptions from being treated as facts
- simulated values from being treated as measurements
- candidate hardware from being treated as selected hardware
- literature predictions from being treated as demonstrated BQRC performance
- unavailable BAS information from being invented
- provisional values from becoming permanent without review

The governing principle is:

```text
IF WE KNOW IT
→ cite the evidence.

IF WE DERIVE IT
→ show the derivation.

IF WE MEASURE IT
→ preserve the measurement.

IF WE SIMULATE IT
→ identify the model.

IF WE ASSUME IT
→ record the assumption.

IF WE DO NOT KNOW IT
→ mark it UNKNOWN / TBD.
```

---

# 2. Information Classification

Every important BQRC engineering value should eventually belong to one of the following categories.

| Code | Classification | Meaning |
|---|---|---|
| FACT | Established information | Supported by authoritative or scientific evidence |
| SOURCE | Sourced parameter | Obtained from paper, datasheet, standard or dataset |
| DERIVED | Derived value | Calculated from sourced or measured information |
| MEASURED | Measured value | Obtained from laboratory or future hardware |
| MODEL | Model output | Produced by an identified physical or mathematical model |
| SIMULATED | Simulation result | Generated during a BQRC simulation |
| ASSUMPTION | Engineering assumption | Temporary value/condition used because evidence is unavailable |
| ESTIMATE | Engineering estimate | Approximate value based on incomplete evidence |
| CANDIDATE | Candidate selection | Possible hardware/model/design not yet selected |
| UNKNOWN | Unknown | Information currently unavailable |
| TBD | To Be Determined | Decision/value intentionally pending |
| TBC | To Be Confirmed | Existing information requiring confirmation |

---

# 3. Evidence Hierarchy

When multiple sources exist, evidence should generally be evaluated according to relevance and quality rather than simply selecting the first available value.

A useful hierarchy is:

```text
BQRC Laboratory Measurement
        ↓
Applicable Mission / Agency Documentation
        ↓
Peer-Reviewed Experimental Research
        ↓
Manufacturer Datasheet
        ↓
Validated Public Dataset
        ↓
Peer-Reviewed Theoretical Model
        ↓
Technical Report / Thesis
        ↓
Engineering Derivation
        ↓
Engineering Estimate
        ↓
Explicit Assumption
```

This hierarchy is guidance rather than an absolute rule.

A manufacturer datasheet, for example, may be more appropriate than a research paper when modelling a specific commercial component.

---

# 4. Assumption Identifier

Assumptions shall use:

`BQRC-ASM-[DOMAIN]-[NUMBER]`

Examples:

```text
BQRC-ASM-MAG-001
BQRC-ASM-NV-001
BQRC-ASM-HW-001
BQRC-ASM-BAS-001
```

Unknowns may use:

`BQRC-UNK-[DOMAIN]-[NUMBER]`

Examples:

```text
BQRC-UNK-BAS-001
BQRC-UNK-HW-001
```

Important pending decisions may use:

`BQRC-TBD-[DOMAIN]-[NUMBER]`

---

# 5. Assumption Status

Possible states are:

| Status | Meaning |
|---|---|
| OPEN | Assumption currently active |
| UNDER_REVIEW | Evidence is being evaluated |
| VALIDATED | Supporting evidence or testing confirms its use |
| REFINED | Replaced by a better-supported value/model |
| REJECTED | Assumption found unsuitable |
| CLOSED | Issue resolved and no longer an active assumption |

---

# 6. Assumption Record Structure

Each important assumption should eventually record:

```text
ID
Domain
Statement
Classification
Reason
Current Value / Model
Units
Range
Source
Evidence Level
Uncertainty
Affected Modules
Affected Requirements
Validation Method
Owner
Status
Date Introduced
Date Reviewed
Replacement / Resolution
Notes
```

Not every field is mandatory for every assumption.

---

# 7. Core Scientific Assumptions

## BQRC-ASM-CORE-001 — Progressive Fidelity

**Statement:**  
The initial BQRC simulator will use progressively increasing model fidelity rather than attempting full flight-level fidelity in the first implementation.

**Classification:** ASSUMPTION / DEVELOPMENT STRATEGY  
**Reason:** Full flight-quality models, measured hardware characteristics and BAS environmental information are not available during initial software development.  
**Affected Areas:** Entire platform  
**Status:** OPEN

---

## BQRC-ASM-CORE-002 — Simulation Before Hardware

**Statement:**  
Software interfaces, data contracts, algorithms and digital models will be developed before complete physical BQRC hardware becomes available.

**Classification:** DEVELOPMENT ASSUMPTION  
**Affected Areas:** Architecture, hardware abstraction, simulation  
**Status:** OPEN

---

## BQRC-ASM-CORE-003 — Model Replacement

**Statement:**  
Lower-fidelity models may be replaced by higher-fidelity models while maintaining stable external interfaces wherever practical.

**Classification:** ARCHITECTURAL ASSUMPTION  
**Status:** OPEN

---

# 8. BAS / Hosted Payload Unknowns

BQRC currently treats future BAS-specific engineering information conservatively.

## BQRC-UNK-BAS-001 — Exact Hosted Payload Interface

**Statement:**  
The final electrical, mechanical and data interface available to BQRC as a future BAS hosted payload is currently not baselined within this project.

**Classification:** UNKNOWN  
**Current Handling:** Generic hosted-payload interface abstraction  
**Resolution:** Replace with authoritative interface documentation when available.  
**Status:** OPEN

---

## BQRC-UNK-BAS-002 — Exact Magnetic Environment

**Statement:**  
The exact magnetic environment at the future BQRC installation location is unknown.

Potential contributors may include:

- station electrical equipment
- wiring
- power converters
- structural materials
- payload electronics
- current loops
- nearby experiments
- transient operations

**Classification:** UNKNOWN  
**Current Handling:** Parameterized local magnetic-disturbance models  
**Status:** OPEN

---

## BQRC-UNK-BAS-003 — Exact Microgravity Environment

**Statement:**  
The detailed residual acceleration, vibration and g-jitter environment at the future BQRC installation location is not currently known.

**Classification:** UNKNOWN  
**Current Handling:** Literature/data-supported scenario models where applicable  
**Status:** OPEN

---

## BQRC-UNK-BAS-004 — Exact Thermal Boundary Conditions

**Statement:**  
Final thermal boundary conditions for the future hosted payload are currently unknown.

**Classification:** UNKNOWN  
**Current Handling:** Configurable thermal scenarios  
**Status:** OPEN

---

## BQRC-UNK-BAS-005 — Exact Radiation Environment at Payload Location

**Statement:**  
The detailed radiation environment applicable to the final BQRC location, shielding and mission configuration is not currently baselined.

**Classification:** UNKNOWN  
**Current Handling:** Appropriate orbital radiation models/datasets and configurable shielding assumptions  
**Status:** OPEN

---

## BQRC-UNK-BAS-006 — Telemetry and Downlink Allocation

**Statement:**  
Final telemetry bandwidth, storage allocation, communication protocol and downlink opportunities for BQRC are currently unknown.

**Classification:** UNKNOWN  
**Current Handling:** Configurable generic telemetry architecture  
**Status:** OPEN

---

# 9. Orbit Assumptions

## BQRC-ASM-ORB-001 — Progressive Orbit Model

**Statement:**  
Initial development may use manual positions or simplified orbital trajectories before implementation of a validated orbital propagator.

**Classification:** DEVELOPMENT ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-ORB-002 — Time-Dependent Environment

**Statement:**  
Environmental models dependent on spacecraft location shall use the simulation's current orbital/position state rather than a permanently fixed Earth location when orbital simulation is enabled.

**Classification:** MODEL ASSUMPTION  
**Status:** OPEN

---

# 10. Reference Frame Assumptions

## BQRC-ASM-FRM-001 — Explicit Frames

**Statement:**  
Position-, attitude- and direction-dependent quantities will be represented in explicitly identified reference frames.

**Classification:** ARCHITECTURAL ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-FRM-002 — Sensor Orientation

**Statement:**  
Each orientation-sensitive sensor may have an orientation different from the BQRC body frame.

**Classification:** PHYSICAL ASSUMPTION  
**Status:** OPEN

---

# 11. Geomagnetic Assumptions

## BQRC-ASM-MAG-001 — Reference Geomagnetic Model

**Statement:**  
A recognized geomagnetic field model will provide the initial Earth magnetic-field reference.

**Classification:** MODEL ASSUMPTION  
**Current Model:** TBD during research/model selection  
**Status:** OPEN

---

## BQRC-ASM-MAG-002 — Local Magnetic Contribution

**Statement:**  
The magnetic field observed by BQRC may differ from the global geomagnetic reference because of local station and payload magnetic sources.

Conceptually:

```text
B_total =
    B_earth
  + B_station
  + B_payload
  + B_electrical
  + B_transient
  + other modelled contributions
```

**Classification:** PHYSICAL MODEL ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-MAG-003 — Unknown Station Appliances

**Statement:**  
When exact magnetic emissions from station equipment are unavailable, configurable disturbance models may be used.

These values shall not be described as actual BAS measurements.

**Classification:** ENGINEERING ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-MAG-004 — Magnetic Superposition

**Statement:**  
Where the selected physical approximation permits, magnetic contributions may be combined using vector superposition.

**Classification:** MODEL ASSUMPTION  
**Validation:** Review validity for each implemented source model.  
**Status:** OPEN

---

## BQRC-ASM-MAG-005 — High-Rate Mapping

**Statement:**  
The software may internally update magnetic state at high rates when useful for simulation or navigation research.

A microsecond computational update shall not automatically be interpreted as a physically independent magnetic measurement every microsecond.

**Classification:** SCIENTIFIC INTERPRETATION ASSUMPTION  
**Status:** OPEN

---

# 12. Microgravity Assumptions

## BQRC-ASM-MGR-001 — Microgravity Is Not Zero Gravity

**Statement:**  
The microgravity simulator shall not assume that acceleration is identically zero.

**Classification:** PHYSICAL MODEL PRINCIPLE  
**Status:** OPEN

---

## BQRC-ASM-MGR-002 — Disturbance Components

**Statement:**  
Residual acceleration may contain multiple components such as:

```text
quasi-static residual acceleration
+
g-jitter
+
structural vibration
+
equipment disturbance
+
transient events
```

where supporting models or datasets are available.

**Classification:** MODEL ASSUMPTION  
**Status:** OPEN

---

# 13. Thermal Assumptions

## BQRC-ASM-THM-001 — Thermal Coupling

**Statement:**  
Hardware power dissipation may affect component temperature, which may subsequently affect sensor measurements.

**Classification:** PHYSICAL MODEL ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-THM-002 — Initial Thermal Fidelity

**Statement:**  
The first thermal model may use simplified thermal dynamics before detailed thermal-network information becomes available.

**Classification:** DEVELOPMENT ASSUMPTION  
**Status:** OPEN

---

# 14. Radiation Assumptions

## BQRC-ASM-RAD-001 — Progressive Radiation Model

**Statement:**  
Initial radiation simulation may use environmental datasets or simplified models before detailed payload shielding and location information becomes available.

**Classification:** DEVELOPMENT ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-RAD-002 — Hardware Degradation

**Statement:**  
Radiation-induced component degradation shall only be simulated when supported by an applicable model, dataset or explicitly documented engineering assumption.

**Classification:** SCIENTIFIC ASSUMPTION  
**Status:** OPEN

---

# 15. NV-Center Assumptions

## BQRC-ASM-NV-001 — NV Magnetometry as Initial Quantum Vertical Slice

**Statement:**  
NV-center ODMR magnetometry will be the first fully implemented BQRC quantum-sensing pipeline.

**Classification:** DEVELOPMENT DECISION  
**Status:** OPEN

---

## BQRC-ASM-NV-002 — Ensemble NV Architecture

**Statement:**  
The initial BQRC modelling direction assumes an ensemble NV-center diamond sensing architecture unless later research or hardware trade studies justify a different configuration.

**Classification:** CANDIDATE DESIGN ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-NV-003 — Green Optical Excitation

**Statement:**  
The initial architecture assumes optical excitation around the commonly used green NV excitation region, with the final laser wavelength and hardware configuration to be baselined through component research.

**Classification:** CANDIDATE DESIGN ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-NV-004 — ODMR Readout

**Statement:**  
ODMR fluorescence detection is the initial measurement approach for the BQRC NV magnetometry simulation and prototype architecture.

**Classification:** DESIGN ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-NV-005 — Temperature Influence

**Statement:**  
Temperature-dependent shifts relevant to NV resonance shall be included when supported by the selected NV model.

**Classification:** PHYSICAL MODEL ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-NV-006 — NV Gyroscope Maturity

**Statement:**  
The NV gyroscope is treated as a research/concept subsystem and shall not initially be modelled as mature flight-qualified technology.

**Classification:** MATURITY ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-NV-007 — NV Accelerometer Maturity

**Statement:**  
A future NV-based acceleration-sensing capability is treated as research/future expansion until a defensible physical architecture and evidence base are established.

**Classification:** MATURITY ASSUMPTION  
**Status:** OPEN

---

# 16. ODMR Assumptions

## BQRC-ASM-ODMR-001 — Classical Baseline

**Statement:**  
Classical ODMR resonance estimation shall be implemented before ML/DL-based ODMR estimation.

**Classification:** DEVELOPMENT DECISION  
**Status:** OPEN

---

## BQRC-ASM-ODMR-002 — Lineshape Model

**Statement:**  
The initial ODMR lineshape model shall be selected from scientifically supported models after literature review and validation.

**Classification:** TBD  
**Current Model:** TBD  
**Status:** OPEN

---

## BQRC-ASM-ODMR-003 — Noise

**Statement:**  
ODMR noise shall be introduced through physically meaningful stages of the sensing/acquisition chain wherever practical rather than adding arbitrary noise only to the final magnetic estimate.

**Classification:** MODEL ASSUMPTION  
**Status:** OPEN

---

# 17. Conventional IMU Assumptions

## BQRC-ASM-IMU-001 — Hardware-Specific Profiles

**Statement:**  
IMU behaviour shall eventually depend on selected manufacturer/model-specific characteristics rather than a permanently generic IMU.

**Classification:** DEVELOPMENT ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-IMU-002 — Error Composition

**Statement:**  
Applicable IMU errors may include:

```text
bias
white noise
random walk
scale-factor error
misalignment
cross-axis coupling
thermal effects
saturation
quantization
```

The exact set shall depend on available evidence for the selected hardware.

**Classification:** MODEL ASSUMPTION  
**Status:** OPEN

---

# 18. Hardware Selection Assumptions

## BQRC-ASM-HW-001 — No Final Hardware Selection Yet

**Statement:**  
Hardware appearing in early simulations or trade studies is considered candidate hardware unless explicitly marked as selected.

**Classification:** CANDIDATE  
**Status:** OPEN

---

## BQRC-ASM-HW-002 — Datasheet-Based Digital Twins

**Statement:**  
Before laboratory characterization is available, component models may use manufacturer datasheet values.

**Classification:** DEVELOPMENT ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-HW-003 — Datasheet Limitations

**Statement:**  
Datasheet values may not fully represent individual hardware behaviour under the future BQRC environment.

**Classification:** SCIENTIFIC LIMITATION  
**Status:** OPEN

---

## BQRC-ASM-HW-004 — Laboratory Replacement

**Statement:**  
Datasheet-based parameters shall progressively be replaced or refined using BQRC laboratory characterization when physical hardware becomes available.

**Classification:** DEVELOPMENT STRATEGY  
**Status:** OPEN

---

# 19. Electronics Assumptions

## BQRC-ASM-ELEC-001 — Progressive Electronics Fidelity

**Statement:**  
The initial electronics simulation may model major effects such as gain, noise, saturation and quantization before detailed circuit-level models are available.

**Classification:** DEVELOPMENT ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-ELEC-002 — Electrical Magnetic Interference

**Statement:**  
BQRC electrical systems may contribute to the local magnetic environment and shall be considered in magnetic-cleanliness studies.

**Classification:** PHYSICAL ASSUMPTION  
**Status:** OPEN

---

# 20. Dataset Assumptions

## BQRC-ASM-DATA-001 — Real Data First

**Statement:**  
Applicable measured datasets will be preferred over synthetic datasets when suitable data exist.

**Classification:** DATA STRATEGY  
**Status:** OPEN

---

## BQRC-ASM-DATA-002 — Synthetic Data Gap Filling

**Statement:**  
Synthetic datasets may be generated when suitable measured data are unavailable or insufficient.

**Classification:** DATA STRATEGY  
**Status:** OPEN

---

## BQRC-ASM-DATA-003 — Hybrid Data

**Statement:**  
Measured datasets may be augmented with scientifically justified simulated disturbances to expand coverage.

**Classification:** DATA STRATEGY  
**Status:** OPEN

---

## BQRC-ASM-DATA-004 — Extreme Conditions

**Statement:**  
Generated and hybrid datasets may include controlled conditions beyond nominal measured datasets for robustness research.

Potential categories include:

```text
BEST_CREDIBLE
NOMINAL
DEGRADED
WORST_CREDIBLE
EXTREME_RESEARCH_CASE
```

**Classification:** DATA STRATEGY  
**Status:** OPEN

---

## BQRC-ASM-DATA-005 — Synthetic Labelling

**Statement:**  
Synthetic and hybrid data shall remain explicitly identifiable.

**Classification:** SCIENTIFIC INTEGRITY PRINCIPLE  
**Status:** OPEN

---

# 21. Noise Assumptions

## BQRC-ASM-NOISE-001 — Evidence-Based Noise

**Statement:**  
Noise models shall be based on measurements, datasets, datasheets, literature or documented engineering assumptions.

**Classification:** SCIENTIFIC PRINCIPLE  
**Status:** OPEN

---

## BQRC-ASM-NOISE-002 — Multiple Noise Sources

**Statement:**  
Multiple noise sources may operate simultaneously where physically appropriate.

**Classification:** MODEL ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-NOISE-003 — Correlated Noise

**Statement:**  
Noise sources shall not automatically be assumed independent when physical evidence indicates correlation.

**Classification:** SCIENTIFIC ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-NOISE-004 — Worst Case

**Statement:**  
A worst-case simulation shall use physically defensible combinations rather than arbitrarily setting every parameter to an extreme simultaneously.

**Classification:** SCIENTIFIC INTEGRITY PRINCIPLE  
**Status:** OPEN

---

# 22. AI / ML Assumptions

## BQRC-ASM-ML-001 — ML Is Supporting Technology

**Statement:**  
AI/ML/DL is not assumed to replace the BQRC physical simulator.

**Classification:** ARCHITECTURAL DECISION  
**Status:** OPEN

---

## BQRC-ASM-ML-002 — Baseline Comparison

**Statement:**  
ML models will be compared against appropriate physics-based or classical algorithm baselines.

**Classification:** RESEARCH STRATEGY  
**Status:** OPEN

---

## BQRC-ASM-ML-003 — Initial ML Applications

**Statement:**  
Initial ML investigation may focus on:

- anomaly detection
- fault/event classification
- ODMR estimation
- sensor-health analysis

before advanced navigation ML.

**Classification:** DEVELOPMENT STRATEGY  
**Status:** OPEN

---

# 23. Navigation Assumptions

## BQRC-ASM-NAV-001 — Magnetic Field Is Not Unique Position

**Statement:**  
A magnetic-field measurement alone shall not be assumed to uniquely determine spacecraft or astronaut position.

**Classification:** SCIENTIFIC PRINCIPLE  
**Status:** OPEN

---

## BQRC-ASM-NAV-002 — Multi-Sensor Navigation

**Statement:**  
Future navigation research may combine magnetic information with inertial and other available measurements.

**Classification:** RESEARCH ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-NAV-003 — Future Application

**Statement:**  
Astronaut navigation is treated as a future application/research pathway rather than an initial demonstrated BQRC capability.

**Classification:** MATURITY ASSUMPTION  
**Status:** OPEN

---

# 24. Manual Override Assumptions

## BQRC-ASM-UI-001 — Manual Experimentation

**Statement:**  
Users may override selected model parameters for controlled experiments.

**Classification:** FUNCTIONAL ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-UI-002 — Override Traceability

**Statement:**  
Manual overrides shall be recorded and distinguishable from default model values.

**Classification:** ARCHITECTURAL PRINCIPLE  
**Status:** OPEN

---

## BQRC-ASM-UI-003 — Out-of-Range Inputs

**Statement:**  
Users may be permitted to explore values outside validated model ranges for research purposes only when the interface clearly warns that the model is extrapolating or outside its validated domain.

**Classification:** RESEARCH INTERFACE ASSUMPTION  
**Status:** OPEN

---

# 25. Simulation Fidelity Assumptions

## BQRC-ASM-SIM-001 — Engineering Realism

**Statement:**  
The goal of BQRC simulation is engineering realism based on available evidence, not artificial numerical perfection.

**Classification:** PROJECT PRINCIPLE  
**Status:** OPEN

---

## BQRC-ASM-SIM-002 — Model Imperfection

**Statement:**  
Simulation models are approximations and may contain uncertainty.

**Classification:** SCIENTIFIC PRINCIPLE  
**Status:** OPEN

---

## BQRC-ASM-SIM-003 — Increasing Fidelity

**Statement:**  
Simulation fidelity shall improve as better datasets, research, hardware characterization and mission information become available.

**Classification:** DEVELOPMENT STRATEGY  
**Status:** OPEN

---

# 26. Application Assumptions

## BQRC-ASM-APP-001 — Application Uses Pipeline Data

**Statement:**  
BQRC applications will consume actual outputs from the simulation/measurement pipeline.

**Classification:** ARCHITECTURAL PRINCIPLE  
**Status:** OPEN

---

## BQRC-ASM-APP-002 — Demonstration vs Validation

**Statement:**  
A functioning application visualization demonstrates software behaviour but does not by itself validate the underlying physical model.

**Classification:** SCIENTIFIC PRINCIPLE  
**Status:** OPEN

---

# 27. Hardware-in-the-Loop Assumptions

## BQRC-ASM-HIL-001 — Common Interfaces

**Statement:**  
Simulation, dataset replay and physical hardware will use compatible interfaces wherever practical.

**Classification:** ARCHITECTURAL ASSUMPTION  
**Status:** OPEN

---

## BQRC-ASM-HIL-002 — Progressive Replacement

**Statement:**  
Simulated drivers will progressively be replaceable with physical hardware drivers.

**Classification:** DEVELOPMENT STRATEGY  
**Status:** OPEN

---

# 28. Uncertainty Assumptions

## BQRC-ASM-UNC-001 — Uncertainty Is Required

**Statement:**  
Important scientific outputs should not be treated as perfectly known values.

**Classification:** SCIENTIFIC PRINCIPLE  
**Status:** OPEN

---

## BQRC-ASM-UNC-002 — Progressive Uncertainty Models

**Statement:**  
Initial uncertainty estimates may be simplified and later replaced by experimentally validated uncertainty models.

**Classification:** DEVELOPMENT ASSUMPTION  
**Status:** OPEN

---

# 29. Model Maturity Assumptions

The following maturity structure is initially adopted:

```text
CONCEPTUAL
↓
LITERATURE_BASED
↓
DATASHEET_BASED
↓
LAB_CALIBRATED
↓
HARDWARE_VALIDATED
↓
FLIGHT_CALIBRATED
```

This structure may be refined later if the project adopts a formal model credibility or TRL framework.

---

# 30. Parameter Provenance Assumptions

Initial source categories are:

```text
PEER_REVIEWED
AGENCY_STANDARD
MANUFACTURER
PUBLIC_DATASET
BQRC_MEASURED
DERIVED
ENGINEERING_ASSUMPTION
```

Additional categories may be introduced when required.

---

# 31. Assumption Review Trigger

An assumption shall be reviewed when:

- new research is found
- a better dataset becomes available
- candidate hardware is selected
- a datasheet becomes available
- laboratory hardware is tested
- a model fails validation
- authoritative mission information becomes available
- BAS interface information becomes available
- simulation results show unexpected behaviour
- a requirement changes
- a design review identifies insufficient evidence

---

# 32. Assumption Replacement Process

The preferred lifecycle is:

```text
UNKNOWN
   ↓
ASSUMPTION
   ↓
RESEARCH
   ↓
SOURCE / MODEL
   ↓
LAB MEASUREMENT
   ↓
VALIDATION
   ↓
REFINED ENGINEERING VALUE
```

Not every parameter will necessarily pass through every stage.

---

# 33. Assumption-to-Code Traceability

Important assumptions should eventually be traceable to their implementation.

Example:

```text
BQRC-ASM-MAG-003
        ↓
Local Magnetic Disturbance Model
        ↓
simulation/environment/magnetic/
        ↓
Configuration Parameter
        ↓
Experiment
        ↓
Result
```

This prevents assumptions from becoming hidden inside source code.

---

# 34. Assumption-to-Requirement Traceability

Important assumptions shall be associated with relevant requirements where practical.

Example:

```text
BQRC-UNK-BAS-002
Exact BAS magnetic environment unknown
        ↓
BQRC-MAG-004
Local magnetic disturbance support
        ↓
BQRC-MAG-013
Unknown station sources must not be presented as known
```

---

# 35. Open Research Questions

The register shall also track questions requiring investigation.

Initial questions include:

### RQ-001

Which geomagnetic reference model and implementation are most appropriate for the initial BQRC simulator?

### RQ-002

Which orbital propagation method is appropriate for V1 and later high-fidelity simulation?

### RQ-003

Which ensemble NV diamond parameters are supported by the strongest experimental evidence?

### RQ-004

Which ODMR lineshape model is appropriate for the first simulator?

### RQ-005

Which noise sources dominate the proposed NV optical readout chain?

### RQ-006

Which commercial accelerometer and gyroscope models are realistic candidates for BQRC?

### RQ-007

Which laser architecture is most suitable for the laboratory prototype?

### RQ-008

Which APD/photodetector is suitable for the expected fluorescence range?

### RQ-009

What microwave source, amplifier and antenna architecture is appropriate?

### RQ-010

Which ADC characteristics are required by the proposed acquisition chain?

### RQ-011

What public microgravity/g-jitter datasets are available and applicable?

### RQ-012

What orbital radiation datasets/models are appropriate?

### RQ-013

What thermal datasets or models are appropriate for initial simulation?

### RQ-014

Which publicly available NV ODMR datasets can be used for model validation?

### RQ-015

Which real IMU datasets can be used to validate simulated noise and drift?

### RQ-016

Which magnetic datasets can be used to validate the geomagnetic and mapping pipeline?

### RQ-017

How should local spacecraft/station magnetic contamination be represented before measured BAS data exist?

### RQ-018

What simulation update rates are scientifically meaningful for each subsystem?

### RQ-019

What sampling rates are realistic for each candidate hardware component?

### RQ-020

Which uncertainty models should be implemented first?

---

# 36. Initial Unknowns Summary

| Area | Current State | Planned Resolution |
|---|---|---|
| BAS hosted interface | UNKNOWN | Authoritative interface information |
| BAS local magnetic environment | UNKNOWN | Parameterized model → future measurements |
| BAS local microgravity spectrum | UNKNOWN | Literature/data → future measurements |
| Final NV diamond | TBD | Research + hardware trade study |
| Final laser | TBD | Hardware trade study |
| Final microwave chain | TBD | Hardware trade study |
| Final detector/APD | TBD | Hardware trade study |
| Final ADC | TBD | Electronics design |
| Final IMU | TBD | Hardware trade study |
| Final temperature sensor | TBD | Hardware trade study |
| Final dosimeter | TBD | Hardware trade study |
| Final OBC | TBD | System design |
| Final power budget | TBD | Component selection |
| Final data budget | TBD | Sampling + telemetry design |
| ODMR lineshape model | TBD | Literature review + validation |
| Detailed noise model | TBD | Research + datasheets + datasets |
| Detailed thermal model | TBD | Architecture + evidence |
| Radiation model | TBD | Model/dataset selection |
| Navigation algorithm | FUTURE | After sensor models mature |
| NV gyro implementation | RESEARCH | Literature + prototype study |
| NV acceleration sensing | FUTURE RESEARCH | Evidence review |

---

# 37. Evidence Gap Register

As research progresses, evidence gaps should be recorded using:

| Gap ID | Topic | Missing Evidence | Importance | Search Needed | Status |
|---|---|---|---|---|---|
| EG-001 | Geomagnetic model | V1 model selection and validation source | Critical | Yes | OPEN |
| EG-002 | NV parameters | Experimentally supported ensemble parameters | Critical | Yes | OPEN |
| EG-003 | ODMR noise | Applicable detector/electronics noise values | Critical | Yes | OPEN |
| EG-004 | IMU | Candidate hardware datasets/specifications | High | Yes | OPEN |
| EG-005 | Microgravity | Applicable orbital disturbance dataset | High | Yes | OPEN |
| EG-006 | Thermal | Appropriate initial thermal model | High | Yes | OPEN |
| EG-007 | Radiation | Appropriate orbital model/dataset | High | Yes | OPEN |
| EG-008 | Local magnetic effects | Station/payload disturbance model | High | Yes | OPEN |

This table shall expand during the research phase.

---

# 38. Rule for Numerical Values

No numerical value shall be introduced into an important BQRC model merely because it appears reasonable.

Important values should follow:

```text
VALUE
  ↓
UNIT
  ↓
SOURCE
  ↓
OPERATING CONDITIONS
  ↓
UNCERTAINTY / TOLERANCE
  ↓
VALIDITY RANGE
  ↓
MODEL USING VALUE
```

If this information cannot yet be established, the value shall be identified as provisional, estimated or assumed.

---

# 39. Rule for Generated Data

Generated data shall have a documented generation chain.

Example:

```text
Research Equation
      ↓
Parameter Sources
      ↓
Physical Model
      ↓
Noise Model
      ↓
Environmental Model
      ↓
Generation Script
      ↓
Random Seed
      ↓
Synthetic Dataset
      ↓
Validation
```

This is particularly important because BQRC intends to generate realistic datasets when measured datasets are unavailable or incomplete.

---

# 40. Rule for Extreme Scenarios

Extreme simulations shall distinguish:

```text
WORST_CREDIBLE
```

from:

```text
EXTREME_RESEARCH_CASE
```

A worst-credible case should remain physically defensible.

An extreme research case may intentionally exceed expected operating conditions to investigate algorithm robustness.

The two shall not be presented as equivalent.

---

# 41. Rule for Future Hardware

When physical hardware is introduced, the corresponding assumption should progress from:

```text
ASSUMED / DATASHEET
        ↓
BENCH MEASURED
        ↓
CALIBRATED
        ↓
VALIDATED
```

The digital twin shall then be updated using measured characteristics.

---

# 42. Rule for Future BAS Information

When authoritative BAS information becomes available:

1. identify affected assumptions
2. preserve the previous assumption history
3. introduce the authoritative source
4. update relevant models
5. rerun affected verification tests
6. evaluate impact on existing experiments
7. update requirements where necessary

Historical results shall remain traceable to the assumptions under which they were generated.

---

# 43. Final Assumption Principle

BQRC shall never hide uncertainty simply to make the simulator appear more complete.

The project shall prefer:

```text
"UNKNOWN"
```

over an invented fact.

It shall prefer:

```text
"ASSUMED — based on X"
```

over an unsupported number.

It shall prefer:

```text
"MODELLED — validated against Y"
```

over calling a simulation a measurement.

And it shall prefer:

```text
"MEASURED — under these conditions"
```

when physical evidence becomes available.

The long-term objective is to progressively transform:

```text
UNKNOWN
↓
ASSUMED
↓
MODELLED
↓
SOURCED
↓
MEASURED
↓
VALIDATED
```

while preserving complete scientific and engineering traceability throughout the BQRC Digital Engineering Platform.