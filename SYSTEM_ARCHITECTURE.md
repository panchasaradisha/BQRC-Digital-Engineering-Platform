# BQRC Digital Engineering Platform

## System Architecture Specification

**Project:** BQRC-01 — Bharatiya Quantum Research Cube  
**Document:** System Architecture Specification  
**Status:** Initial Locked Architecture  
**Parent Baseline:** `PROJECT_BASELINE.md`  
**Architecture Objective:** Simulation → Dataset Replay → Laboratory Hardware → Hardware-in-the-Loop → Future Payload Hardware

---

# 1. Purpose

This document defines the software and digital-engineering architecture of the **BQRC Digital Engineering Platform**.

The architecture is designed so that BQRC can evolve from:

**Simulation → Dataset Replay → Laboratory Hardware → Engineering Model → Hardware-in-the-Loop → Future Payload Hardware**

without requiring the complete software system to be redesigned.

The central architectural principle is:

> Physics, sensors, hardware, algorithms, mission software, data analysis, applications and user interfaces must remain modular and communicate through clearly defined interfaces.

The web application is therefore not the scientific system itself. It is the interface through which users interact with the underlying BQRC digital-engineering system.

---

# 2. Top-Level Architecture

The BQRC Digital Engineering Platform is divided into the following major layers:

```text
┌───────────────────────────────────────────────────────────────┐
│                    USER / WEB INTERFACE                       │
│ Dashboard • Labs • Mission • Analysis • Knowledge • Design   │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                     BACKEND / API LAYER                       │
│ Requests • Validation • Sessions • Experiments • Data Access │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                  SIMULATION ORCHESTRATOR                      │
│ Scenario • Scheduler • Master Clock • Module Coordination    │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                  DIGITAL ENGINEERING CORE                     │
│ Time • Units • Frames • Config • Provenance • Uncertainty    │
└──────────────────────────────┬────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
     ENVIRONMENT           HARDWARE              TRUTH
       MODELS             DIGITAL TWIN           MODELS
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                       SENSOR LAYER                            │
│ NV • IMU • Temperature • Radiation • Future Sensors          │
└──────────────────────────────┬────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                 ELECTRONICS / ACQUISITION                     │
│ AFE • APD • ADC • Quantization • Timing • Electronics Noise  │
└──────────────────────────────┬────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                 ALGORITHMS / ESTIMATION                       │
│ ODMR • Calibration • Filtering • Fusion • Diagnostics        │
└──────────────────────────────┬────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────┐
│              MISSION SOFTWARE / TELEMETRY                     │
│ Modes • Commands • Health • Faults • Packets • Storage       │
└──────────────────────────────┬────────────────────────────────┘
                               ▼
┌───────────────────────────────────────────────────────────────┐
│              ANALYSIS / ML / APPLICATIONS                     │
│ Science • Verification • Trade Studies • Navigation Research │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                 DATA / EVIDENCE / KNOWLEDGE                   │
│ Datasets • Sources • Papers • Models • Experiments • Results │
└───────────────────────────────────────────────────────────────┘
```

---

# 3. Fundamental Runtime Pipeline

A normal BQRC simulated measurement shall follow:

```text
Simulation Clock
      ↓
Scenario Configuration
      ↓
Physical Truth
      ↓
Space Environment
      ↓
Reference-Frame Transformation
      ↓
Physical Sensor Model
      ↓
Hardware / Electronics Model
      ↓
Raw Measurement
      ↓
Signal Processing
      ↓
Calibration
      ↓
Estimated Measurement
      ↓
Uncertainty + Quality
      ↓
Sensor Fusion
      ↓
Mission Software
      ↓
Telemetry
      ↓
Scientific Analysis
      ↓
AI / ML Analysis where applicable
      ↓
Applications
      ↓
Verification
      ↓
Experiment Storage
```

The estimation algorithm shall **not receive hidden simulation ground truth directly**.

Ground truth exists for engineering validation, simulator verification and performance assessment.

---

# 4. Repository-to-Architecture Mapping

The repository shall progressively map to the architecture as follows:

```text
BQRC-Digital-Engineering-Platform/
│
├── frontend/
│   └── Web application and visualization
│
├── backend/
│   └── API, experiment management and application services
│
├── simulation/
│   └── Physics and simulation engines
│
├── algorithms/
│   └── Signal processing, calibration, fusion and estimation
│
├── hardware/
│   └── Hardware profiles, abstraction interfaces and future drivers
│
├── datasets/
│   └── Public, generated, hybrid and laboratory datasets
│
├── configs/
│   └── Mission, hardware, environment and scenario configurations
│
├── knowledge/
│   └── Structured scientific knowledge and evidence metadata
│
├── tests/
│   └── Unit, integration, regression and scientific golden tests
│
├── notebooks/
│   └── Research exploration and model-validation notebooks
│
├── scripts/
│   └── Dataset preparation, generation and engineering utilities
│
└── docs/
    └── Engineering, research and user documentation
```

---

# 5. Digital Engineering Core

The Digital Engineering Core provides common services required by nearly every BQRC module.

It shall progressively contain:

```text
simulation/core/
│
├── clock/
├── scheduler/
├── units/
├── configuration/
├── random/
├── provenance/
├── quality/
├── uncertainty/
└── common_types/
```

Responsibilities include:

- master simulation clock
- multi-rate scheduling
- standardized physical units
- deterministic random-number generation
- configuration loading
- parameter provenance
- model maturity
- measurement quality states
- uncertainty representation
- common data structures

The scientific modules should use these common services instead of implementing incompatible versions independently.

---

# 6. Master Simulation Clock

All simulated subsystems shall operate relative to a common simulation time.

The clock shall eventually support:

- start
- pause
- resume
- stop
- step
- real-time execution
- accelerated execution
- deterministic replay

Different systems may operate at different frequencies.

For example:

```text
Orbit propagation        → relatively slow update
Geomagnetic model        → relatively slow update
Thermal model            → relatively slow update
Radiation model          → environment-dependent update
IMU                      → high-rate update
Gyroscope                → high-rate update
ODMR acquisition         → measurement-cycle dependent
Telemetry                → packet-rate dependent
Web visualization        → display-rate dependent
```

A multi-rate scheduler shall coordinate these systems without requiring every model to execute at the same frequency.

---

# 7. Physical Truth Layer

The simulator shall maintain a hidden physical truth state.

Examples include:

```text
position_true
velocity_true
attitude_true
magnetic_field_true
acceleration_true
angular_rate_true
temperature_true
radiation_true
```

Truth represents the physical state being simulated.

Sensor algorithms shall not directly consume truth values.

Instead:

```text
TRUTH
  ↓
ENVIRONMENT
  ↓
SENSOR PHYSICS
  ↓
ELECTRONICS
  ↓
MEASUREMENT
```

Truth may be used later by verification tools to calculate estimation error.

---

# 8. Orbit and Position Architecture

The orbital engine shall progressively provide:

- simulation time
- spacecraft/station position
- velocity
- latitude
- longitude
- altitude
- orbital state

Development may progress through increasing levels of fidelity.

Initial development may use:

- fixed position
- manually entered position
- predefined trajectories

Later versions may support:

- orbital elements
- TLE input
- SGP4 propagation
- more advanced orbital modelling where required

The orbital model used for an experiment shall always be recorded.

---

# 9. Reference-Frame Architecture

BQRC shall explicitly represent coordinate frames.

Potential frames include:

```text
Inertial Frame
Earth-Fixed Frame
Local Orbital Frame
BAS / Station Frame
BQRC Body Frame
Sensor Frame
```

Frame transformations are essential because a sensor measures quantities relative to its own orientation.

For example:

```text
Earth Magnetic Field
        ↓
Earth / Orbital Frame
        ↓
Station Orientation
        ↓
BQRC Orientation
        ↓
Sensor Orientation
        ↓
Bx, By, Bz measured by sensor
```

Changing spacecraft orientation must not incorrectly appear as a physical magnetic anomaly.

Attitude representation should use numerically robust methods such as quaternions where appropriate.

---

# 10. Space-Environment Architecture

The environment system shall progressively represent the physical conditions affecting BQRC.

Suggested structure:

```text
simulation/environment/
│
├── magnetic/
├── microgravity/
├── vibration/
├── thermal/
├── radiation/
├── emi/
└── timing/
```

---

## 10.1 Magnetic Environment

The magnetic environment may include:

```text
Earth Magnetic Field
+
Orbital / Position Dependence
+
Station Magnetic Environment
+
BQRC Self-Generated Magnetic Field
+
Electrical Equipment
+
Current-Carrying Conductors
+
Power Electronics
+
Microwave Electronics
+
Magnetic Materials
+
Transient Disturbances
```

Exact BAS magnetic-environment values shall not be invented when unavailable.

Unknown effects shall instead be represented through:

- documented assumptions
- parameter ranges
- literature-supported models
- configurable scenarios
- future measured values

---

## 10.2 Microgravity Environment

The microgravity model may include:

- residual acceleration
- g-jitter
- structural vibration
- equipment operation
- transient disturbances
- crew-related disturbances where scientifically justified
- maneuver-related acceleration where applicable

The purpose is to simulate the environment that a real accelerometer would experience rather than simply setting acceleration to zero.

---

## 10.3 Thermal Environment

The thermal model may include:

- component heat generation
- laser heating
- microwave electronics heating
- processor heating
- conduction
- radiative heat transfer
- environmental temperature changes
- thermal gradients
- temperature-dependent sensor behaviour

---

## 10.4 Radiation Environment

The radiation model may progressively include:

- background orbital radiation
- radiation-rate variations
- transient events
- single-event effects
- accumulated degradation where scientifically supported

---

## 10.5 EMI and Electrical Environment

Possible contributions include:

- DC/DC converter switching
- power-supply ripple
- digital electronics
- microwave electronics
- current loops
- grounding effects
- nearby electrical equipment

These effects are particularly important for sensitive magnetic measurements.

---

## 10.6 Timing Environment

The timing model may include:

- clock drift
- jitter
- timestamp uncertainty
- synchronization errors
- dropped samples
- communication latency

---

# 11. Hardware Digital Twin Architecture

The `hardware/` package shall progressively contain:

```text
hardware/
│
├── interfaces/
│
├── profiles/
│   ├── nv/
│   ├── laser/
│   ├── microwave/
│   ├── detector/
│   ├── optical/
│   ├── adc/
│   ├── imu/
│   ├── temperature/
│   ├── radiation/
│   ├── obc/
│   ├── storage/
│   └── power/
│
├── drivers/
│
└── custom/
```

A **hardware profile** describes a component.

A **hardware driver** communicates with an actual physical component.

These concepts shall remain separate.

---

# 12. Hardware Profile Structure

A hardware profile may contain:

```text
component_id
manufacturer
model
category
operating_range
sample_rate
bandwidth
dynamic_range
resolution
noise
bias
drift
scale_factor
nonlinearity
cross_axis_coupling
thermal_coefficients
radiation_information
power
mass
dimensions
interface
datasheet_source
measurement_source
model_maturity
calibration_information
```

Not every property applies to every component.

Only scientifically meaningful properties shall be used.

---

# 13. Hardware Abstraction Contract

Simulation and real hardware should share common interfaces wherever practical.

Conceptually:

```text
SensorInterface
│
├── initialize()
├── configure()
├── sample()
├── calibrate()
├── health()
└── shutdown()
```

Possible implementations include:

```text
SimulatedIMU
DatasetReplayIMU
RealIMU

SimulatedNVSensor
DatasetReplayNVSensor
RealNVSensor
```

Downstream algorithms should consume a standardized measurement interface rather than depending directly on a particular hardware implementation.

This is one of the most important architectural requirements for future hardware integration.

---

# 14. Measurement Data Contract

BQRC measurements shall progressively follow a standardized structure.

Conceptually:

```text
Measurement
├── timestamp
├── sensor_id
├── quantity
├── value
├── unit
├── uncertainty
├── quality
├── data_origin
├── reference_frame
├── model_version
├── configuration_id
└── provenance
```

Possible `data_origin` values may include:

```text
SIMULATED
MEASURED_PUBLIC
MEASURED_BQRC
DATASET_REPLAY
HYBRID
```

The same general contract should support simulated, replayed and physical measurements.

---

# 15. Data Processing Levels

The platform shall preserve distinct processing stages.

```text
L0 — TRUTH
L1 — RAW
L2 — CONDITIONED
L3 — CALIBRATED
L4 — ESTIMATED
L5 — FUSED
L6 — APPLICATION PRODUCT
```

Examples:

### L0 — Truth

Hidden physical simulation state.

### L1 — Raw

Direct simulated or physical acquisition.

### L2 — Conditioned

Basic signal conditioning.

### L3 — Calibrated

Bias, scale and calibration corrections applied.

### L4 — Estimated

Physical quantity estimated by an algorithm.

### L5 — Fused

Multiple measurements combined.

### L6 — Application Product

Engineering or scientific result derived for a specific application.

Earlier processing levels shall not be silently overwritten.

---

# 16. Configuration Architecture

The `configs/` area shall progressively contain:

```text
configs/
├── mission/
├── hardware/
├── environment/
├── scenarios/
├── algorithms/
└── defaults/
```

Configuration shall remain external to scientific code wherever practical.

This allows the same scientific model to run using different:

- hardware
- noise conditions
- environmental conditions
- mission states
- algorithms
- faults
- user settings

without rewriting the model itself.

---

# 17. Manual Parameter and Override Architecture

Important configurable parameters may originate from:

```text
MODEL
DATASET
MANUAL
HARDWARE
```

User controls may support:

```text
OVERRIDE
OFFSET
SCALE
LOCK
```

Example:

```text
Temperature Source = MODEL
Model Value = 28.2 °C

User selects:
Source = MANUAL
Override = 40 °C
```

The changed value must propagate through the actual dependency chain.

For example:

```text
Temperature Override
        ↓
NV Zero-Field Splitting
        ↓
ODMR Resonance
        ↓
Raw Spectrum
        ↓
Estimated Magnetic Field
```

The UI must not merely change a displayed number.

The platform should warn when a manually selected value lies outside the validated range of a model.

---

# 18. Dataset Architecture

The `datasets/` directory shall progressively contain:

```text
datasets/
├── public/
├── generated/
├── hybrid/
├── lab/
├── hardware/
├── schemas/
└── metadata/
```

Definitions:

### `public/`

Real externally sourced datasets.

### `generated/`

Physics-generated synthetic datasets.

### `hybrid/`

Measured datasets combined with simulated effects or augmentation.

### `lab/`

Future BQRC laboratory measurements.

### `hardware/`

Hardware characterization datasets.

### `schemas/`

Dataset structure definitions.

### `metadata/`

Provenance and dataset documentation.

Large datasets should not automatically be stored directly in Git.

Scripts required to reproduce generated datasets shall be retained wherever practical.

---

# 19. Dataset Priority and Flow

The preferred hierarchy is:

```text
REAL MEASURED DATA
        ↓
REAL + SCIENTIFICALLY JUSTIFIED AUGMENTATION
        ↓
PHYSICS-GENERATED SYNTHETIC DATA
        ↓
ENGINEERING-ASSUMPTION DATA
```

Synthetic data shall not replace suitable real data unnecessarily.

Synthetic data is appropriate when:

- suitable real data cannot be found
- real data is insufficient
- required operating ranges are absent
- extreme scenarios are needed
- controlled faults are required
- Monte Carlo analysis requires additional coverage

Generated data shall never be represented as measured flight or laboratory data.

---

# 20. Dataset Provenance

Every important dataset should have metadata describing:

```text
dataset_id
name
version
origin
source
license
variables
units
sampling_rate
preprocessing
generation_method
equations
parameter_ranges
noise_models
assumptions
random_seed
simulator_version
model_versions
validation_status
```

Dataset provenance shall remain accessible to users and researchers.

---

# 21. Noise Architecture

Noise shall not simply be implemented as arbitrary random values.

Noise models should originate from:

- measured datasets
- hardware characterization
- manufacturer datasheets
- peer-reviewed research
- physical models
- validated engineering assumptions

Potential scenarios include:

```text
IDEAL
BEST_CREDIBLE
NOMINAL
DEGRADED
WORST_CREDIBLE
EXTREME_RESEARCH_CASE
```

The simulator shall support combinations of noise sources where scientifically meaningful.

Noise sources may be correlated.

---

# 22. NV Quantum-Sensing Architecture

The main NV magnetometry simulation chain shall progressively represent:

```text
Magnetic Truth
      +
Temperature
      +
NV Orientation
      ↓
NV Energy-Level Model
      ↓
Resonance Frequencies
      ↓
Microwave Excitation
      ↓
ODMR Interaction
      ↓
Fluorescence Response
      ↓
Optical Filtering
      ↓
Photodetection
      ↓
Analog Front End
      ↓
ADC
      ↓
Raw ODMR Spectrum
```

The algorithm then receives the raw/conditioned spectrum.

---

# 23. ODMR Processing Architecture

The processing pipeline may include:

```text
Raw ODMR Spectrum
        ↓
Validation
        ↓
Baseline Correction
        ↓
Normalization
        ↓
Dip / Resonance Detection
        ↓
Lineshape Fitting
        ↓
Resonance Frequency Estimation
        ↓
Temperature Compensation
        ↓
Magnetic Field Estimation
        ↓
Uncertainty
        ↓
Quality Flag
```

Possible fitting approaches shall be scientifically justified.

Classical fitting will serve as the initial baseline before ML-based approaches are investigated.

---

# 24. Conventional IMU Architecture

The inertial simulation chain shall progressively represent:

```text
True Acceleration / Angular Rate
        ↓
Sensor Dynamics
        ↓
Bias
        ↓
Bias Instability
        ↓
White Noise
        ↓
Random Walk
        ↓
Scale-Factor Error
        ↓
Cross-Axis Coupling
        ↓
Misalignment
        ↓
Thermal Drift
        ↓
Vibration Response
        ↓
Saturation
        ↓
Quantization
        ↓
Raw IMU Measurement
```

Processing may then include:

```text
Raw IMU
↓
Calibration
↓
Filtering
↓
Bias Compensation
↓
Orientation / State Estimation
```

---

# 25. Electronics and Acquisition Architecture

Sensors shall not directly output unrealistically clean engineering values.

The acquisition chain may include:

```text
Physical Sensor Response
        ↓
Analog Front End
        ↓
Gain / Filtering
        ↓
Electronic Noise
        ↓
Detector Response
        ↓
Saturation
        ↓
ADC
        ↓
Quantization
        ↓
Timestamping
        ↓
Digital Sample
```

This is especially important for the NV optical detection chain.

---

# 26. Calibration Architecture

Calibration shall be treated as a defined engineering process.

Potential calibration information includes:

```text
calibration_id
sensor_id
timestamp
method
coefficients
temperature
valid_range
source
uncertainty
version
```

The generic flow is:

```text
RAW
↓
Offset Correction
↓
Scale Correction
↓
Temperature Compensation
↓
Axis / Alignment Correction
↓
Calibrated Measurement
↓
Uncertainty
```

---

# 27. Quality Architecture

Important measurements and derived products may carry quality flags.

Suggested states include:

```text
GOOD
DEGRADED
SUSPECT
INVALID
SATURATED
MISSING
EXTRAPOLATED
```

Downstream applications shall be able to respond appropriately to measurement quality.

---

# 28. Uncertainty Architecture

The platform shall progressively support uncertainty at multiple levels.

Potential sources include:

- sensor measurement uncertainty
- calibration uncertainty
- model uncertainty
- environmental uncertainty
- hardware parameter uncertainty
- fitting uncertainty
- propagated uncertainty

An engineering result should ideally communicate:

```text
VALUE
+
UNCERTAINTY
+
QUALITY
+
MODEL MATURITY
```

---

# 29. Model Maturity Architecture

Scientific models and hardware profiles shall carry maturity information.

Suggested levels:

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

The platform must not represent a literature-based simulation as flight-validated performance.

---

# 30. Parameter Provenance Architecture

Important parameters shall record their origin.

Suggested source categories:

```text
PEER_REVIEWED
AGENCY_STANDARD
MANUFACTURER
PUBLIC_DATASET
BQRC_MEASURED
DERIVED
ENGINEERING_ASSUMPTION
```

A user should eventually be able to inspect a parameter and determine:

- its value
- its units
- where it came from
- which source supports it
- which model uses it
- whether it has been overridden
- its uncertainty
- its maturity

---

# 31. Mission Software Architecture

The mission-software emulator shall progressively represent payload operational behaviour.

Potential states include:

```text
BOOT
↓
SELF_TEST
↓
INITIALIZATION
↓
CALIBRATION
↓
STANDBY
↓
SCIENCE
↓
DOWNLINK
```

Fault routes may include:

```text
FAULT
↓
SAFE
↓
RECOVERY
```

Mission state shall affect actual subsystem behaviour.

For example:

```text
STANDBY
Laser = OFF
Microwave Sweep = OFF

SCIENCE
Laser = ON
Microwave Sweep = ACTIVE
APD Acquisition = ACTIVE
```

Mission state must therefore affect the simulation rather than only the frontend display.

---

# 32. Command Architecture

Commands shall eventually follow:

```text
User / Ground
      ↓
Command Request
      ↓
Validation
      ↓
Mission Software
      ↓
Hardware Abstraction Layer
      ↓
Simulated or Real Subsystem
      ↓
Response
```

Examples may include:

```text
START_ODMR_SWEEP
STOP_ODMR_SWEEP
SET_SAMPLE_RATE
RUN_CALIBRATION
ENTER_SAFE_MODE
RESET_SUBSYSTEM
```

Commands shall be validated before execution.

---

# 33. Telemetry Architecture

Conceptual data flow:

```text
Sensors
↓
OBC / Processing
↓
Telemetry Packet
↓
Onboard Storage
↓
Hosted Payload Interface
↓
BAS
↓
Downlink
↓
Ground Decoder
↓
Scientific Database
↓
Analysis
```

Simulation may include:

- packet creation
- timestamps
- CRC
- packet loss
- corruption
- latency
- missing packets
- storage limits
- downlink constraints

Exact future BAS interfaces shall be incorporated only when authoritative interface information becomes available.

---

# 34. Fault Injection Architecture

The simulator shall support controlled faults.

Potential faults include:

```text
Laser Power Degradation
Laser Failure
Microwave Frequency Drift
Microwave Instability
APD Saturation
Detector Degradation
Accelerometer Bias
Gyroscope Bias
Sensor Dropout
Thermal Excursion
Magnetic Contamination
Vibration Event
Radiation Event
Clock Desynchronization
Packet Corruption
Storage Failure
OBC Reset
```

Faults should enter the correct physical or software layer.

They should not simply modify the final displayed output.

---

# 35. Algorithm Architecture

The `algorithms/` package shall progressively contain:

```text
algorithms/
├── odmr/
├── calibration/
├── filtering/
├── sensor_fusion/
├── navigation/
├── diagnostics/
└── ml/
```

Physics simulation and estimation algorithms shall remain separate.

This allows the same algorithm to be evaluated using:

- simulated data
- public measured datasets
- laboratory data
- future BQRC hardware data

---

# 36. Sensor-Fusion Architecture

Classical sensor fusion shall be implemented before advanced ML alternatives.

Potential methods include:

- complementary filtering
- Kalman filtering
- Extended Kalman filtering
- covariance-aware fusion
- residual monitoring
- outlier rejection
- statistical gating

The fusion engine shall use measurement uncertainty and quality information wherever possible.

---

# 37. AI / ML / DL Architecture

AI, machine learning and deep learning are supporting research modules.

They shall not replace physical modelling without justification.

The preferred sequence is:

```text
Physics / Real Measurement
        ↓
Dataset
        ↓
Classical Baseline
        ↓
Feature Engineering
        ↓
ML / DL Model
        ↓
Validation
        ↓
Comparison
```

Initial BQRC ML research candidates include:

### Telemetry Fault Classification

Possible classes:

```text
NORMAL
THERMAL_DRIFT
MAGNETIC_SPIKE
LASER_FLUCTUATION
MICROWAVE_INSTABILITY
APD_SATURATION
GYRO_BIAS
ACCEL_VIBRATION
RADIATION_EVENT
DATA_DROPOUT
```

### Anomaly Detection

Potential methods include:

- Isolation Forest
- One-Class SVM
- Autoencoder where justified

### ODMR ML Research

Compare:

```text
Noisy ODMR
    ↓
Classical Lineshape Fit

versus

Noisy ODMR
    ↓
ML / DL Model
```

Outputs may include resonance-frequency estimation and magnetic-field estimation.

### Future Research

Possible future ML applications include:

- learned bias correction
- sensor-health estimation
- surrogate simulation
- magnetic-map matching
- advanced navigation
- predictive degradation

These shall only be added when suitable validated data and baselines exist.

---

# 38. Backend Architecture

The backend shall eventually provide services for:

- simulation execution
- simulation control
- scenario management
- configuration management
- parameter overrides
- hardware-profile access
- dataset access
- experiment management
- analysis requests
- requirement verification
- knowledge/evidence access
- future physical hardware communication

The frontend shall not contain core scientific physics.

---

# 39. Frontend Architecture

The web application shall progressively expose engineering workspaces such as:

```text
Mission Dashboard
Simulation Control
Payload Explorer
ODMR Lab
IMU Lab
Environment Lab
Hardware Library
Hardware Trade Study
Dataset Explorer
Analysis Lab
Fault Injection
Verification
Applications
Knowledge Base
Formula Library
Source Library
User Guide
```

Not all workspaces are required for the first version.

The interface shall expose real model outputs rather than decorative values.

---

# 40. Visualization Architecture

Visualizations may include:

- orbital position
- Earth representation
- BQRC payload model
- sensor locations
- vector fields
- magnetic-field vectors
- attitude
- time-series plots
- ODMR spectra
- FFT / PSD plots
- residual plots
- uncertainty bands
- thermal maps
- sensor health
- telemetry status
- mission state
- fault indicators

Animations shall represent actual simulation state whenever possible.

They should not imply greater physical fidelity than the underlying model provides.

---

# 41. Knowledge and Evidence Architecture

The knowledge layer shall connect scientific implementation to evidence.

Potential relationships include:

```text
Parameter → Source
Formula → Paper
Hardware Value → Datasheet
Dataset → Repository / Publication
Model → Equation + Assumptions
Requirement → Verification Test
Result → Configuration + Dataset + Model Version
```

The web application should eventually make these relationships navigable.

---

# 42. Formula Library Architecture

Important formulas shall be documented with:

```text
formula_id
name
equation
variables
units
physical_meaning
assumptions
valid_range
source
implementation_location
related_models
related_applications
```

The formula library shall serve both educational and engineering purposes.

---

# 43. Experiment Architecture

Each important simulation or hardware experiment shall eventually have an experiment manifest.

Conceptually:

```text
Experiment
├── experiment_id
├── timestamp
├── objective
├── scenario
├── configuration
├── hardware_profiles
├── model_versions
├── dataset_versions
├── algorithm_versions
├── parameter_overrides
├── random_seed
├── assumptions
├── results
├── notes
└── verification_status
```

This allows experiments to be reproduced.

---

# 44. Verification Architecture

Requirements shall connect to evidence through:

```text
REQUIREMENT
↓
TEST
↓
CONFIGURATION
↓
EXECUTION
↓
METRIC
↓
THRESHOLD
↓
RESULT
↓
PASS / MARGINAL / FAIL / NOT TESTED
↓
EVIDENCE
```

Simulation results alone shall not be described as physical hardware qualification.

---

# 45. Golden Scientific Test Cases

Known reference cases shall be maintained.

Potential examples include:

```text
Ideal ODMR Spectrum
Known Magnetic Field
Known Temperature Shift
Known Sensor Bias
Known Coordinate Rotation
Zero-Noise Case
Deterministic Noise Case
Calibration Recovery Case
Known Fault Case
```

These tests help detect scientific regressions when code changes.

---

# 46. Monte Carlo Architecture

The simulator shall support repeatable Monte Carlo experiments.

Conceptually:

```text
Parameter Distributions
        ↓
Random Seed
        ↓
Run 1
Run 2
Run 3
...
Run N
        ↓
Statistical Analysis
```

Parameters may include:

- sensor noise
- bias
- hardware tolerance
- temperature
- vibration
- magnetic contamination
- component variability
- environmental conditions

Monte Carlo results may support robustness and uncertainty studies.

---

# 47. Hardware Trade-Study Architecture

Candidate hardware shall be tested under comparable scenarios.

Example:

```text
Same Mission Scenario
      │
      ├── IMU A
      ├── IMU B
      └── IMU C
```

Each hardware profile may affect:

```text
Measurement Performance
Power
Thermal Behaviour
Data Rate
Noise
Mass
Integration
Application Performance
```

The platform shall expose the underlying criteria and evidence used in comparisons.

---

# 48. Power Architecture

The platform shall progressively model:

- subsystem power
- mission-mode power
- peak power
- average power
- power availability
- power-related heat generation

For example:

```text
STANDBY
↓
Low-power configuration

SCIENCE
↓
Laser + Microwave + Detector + Processing active
```

Power changes should influence the thermal model where appropriate.

---

# 49. Thermal Coupling Architecture

The thermal system shall eventually support interactions such as:

```text
Electrical Power
      ↓
Component Heat
      ↓
Thermal Network
      ↓
Component Temperature
      ↓
Sensor Drift / NV Shift
      ↓
Measurement Error
```

This allows environmental effects to propagate realistically through the system.

---

# 50. Magnetic Cleanliness Architecture

Because magnetometry is central to BQRC, the platform shall progressively support magnetic contamination studies.

Potential sources include:

```text
Power Converters
Wiring
Current Loops
Microwave Electronics
Processors
Motors / Actuators if applicable
Magnetic Materials
Nearby Station Equipment
```

Future capabilities may include:

- component source modelling
- distance dependence
- orientation dependence
- placement studies
- magnetic-cleanliness trade studies

---

# 51. Data Budget Architecture

The platform shall estimate:

```text
Generated Data
↓
Processed Data
↓
Stored Data
↓
Compressed Data
↓
Downlinked Data
```

Data rate should depend on:

- sampling frequency
- number of channels
- data type
- mission mode
- compression
- experiment duration

---

# 52. Application Architecture

Applications shall consume outputs from the actual BQRC processing pipeline.

Initial applications may include:

- quantum magnetic-field measurement
- magnetic-field mapping
- residual microgravity characterization
- thermal characterization
- radiation characterization
- quantum-versus-classical sensor comparison
- environmental correlation
- disturbance detection
- long-duration stability
- payload health monitoring

Future research applications may include:

- magnetic-aided navigation
- quantum inertial sensing
- astronaut-assist navigation
- situational awareness
- standalone quantum payload concepts

---

# 53. Magnetic-Mapping Architecture

The magnetic-mapping chain may follow:

```text
Simulation Time
      ↓
Orbital Position
      ↓
Geomagnetic Reference Model
      ↓
Local Magnetic Environment
      ↓
NV Sensor Measurement
      ↓
Calibration
      ↓
Reference-Frame Transformation
      ↓
Estimated Magnetic Vector
      ↓
Map / Database
```

The platform may display:

```text
Reference Field
True Simulated Field
Raw Sensor Measurement
Corrected Estimate
Residual Error
Uncertainty
```

High-rate internal updates may be supported where computationally meaningful.

A high display/update frequency shall not be interpreted as equivalent to new independent physical information at the same frequency.

---

# 54. Microgravity Application Architecture

The microgravity analysis chain may follow:

```text
True Residual Acceleration
        ↓
Microgravity Disturbances
        ↓
Vibration
        ↓
Accelerometer Model
        ↓
Raw Acceleration
        ↓
Calibration
        ↓
Filtering
        ↓
Time / Frequency Analysis
        ↓
Microgravity Characterization
```

Potential analysis may include:

- time series
- RMS acceleration
- PSD
- FFT
- event detection
- disturbance correlation

---

# 55. Quantum-versus-Classical Comparison

Where appropriate, sensors should observe the same underlying physical state.

Conceptually:

```text
                  ┌──→ Quantum Sensor → Estimate
PHYSICAL TRUTH ───┤
                  └──→ Classical Sensor → Estimate
```

Comparison may include:

- RMSE
- bias
- drift
- stability
- SNR
- uncertainty
- bandwidth
- sensitivity to environment

This architecture supports meaningful comparison because both sensor paths share a common truth environment.

---

# 56. Future Navigation Architecture

Future navigation research may investigate:

```text
Accelerometer
      +
Gyroscope
      +
Magnetic Reference
      +
Other Available Measurements
      ↓
State Estimator
      ↓
Position
Velocity
Orientation
```

Potential displays may compare:

```text
True Trajectory
Pure Inertial Estimate
Corrected Estimate
```

Magnetic measurements shall not be assumed to uniquely determine position.

Ambiguity, local contamination and insufficient information shall be represented where applicable.

---

# 57. Analysis Architecture

The analysis platform may progressively support:

- time-series analysis
- residuals
- RMSE
- MAE where useful
- bias
- drift
- SNR
- FFT
- PSD
- Allan deviation
- correlation
- covariance
- uncertainty
- confidence
- sensor comparison
- calibration performance
- long-duration stability

Analysis methods shall document assumptions and units.

---

# 58. Explain-This-Event Architecture

A future diagnostic system may combine:

- telemetry
- residuals
- mission state
- environmental channels
- hardware status
- rules
- statistical models
- ML models where justified

Conceptually:

```text
Detected Anomaly
      ↓
Collect Related Channels
      ↓
Check Rules / Residuals / Models
      ↓
Generate Candidate Causes
      ↓
Rank Supporting Evidence
      ↓
Display Explanation
```

The system should distinguish correlation from proven causation.

---

# 59. Knowledge and User-Guide Architecture

The platform shall contain documentation at multiple levels.

### Level 1 — Understand

Simple explanations for new users.

### Level 2 — Engineering

Implementation details, equations, data flow and hardware behaviour.

### Level 3 — Research

Research papers, assumptions, uncertainty, model validity and advanced analysis.

The guide should explain:

- what BQRC is
- why the mission exists
- how the payload works
- how quantum sensing works
- how conventional sensors work
- how the simulator works
- how datasets are selected
- how hardware is represented
- how to run experiments
- how to interpret results
- how to use each major web-app feature

---

# 60. Model-to-Hardware Transition

The architecture shall support the progression:

```text
SIMULATED SENSOR
        ↓
DATASET REPLAY
        ↓
LAB SENSOR
        ↓
ENGINEERING MODEL
        ↓
HARDWARE-IN-THE-LOOP
        ↓
FUTURE FLIGHT HARDWARE
```

Software above the hardware abstraction layer should require minimal changes during this transition.

---

# 61. Digital-Twin Calibration Loop

When physical hardware becomes available:

```text
Digital Model
      ↓
Prediction

Physical Hardware
      ↓
Measurement
```

The two are compared.

Then:

```text
Prediction
      ↓
Residual
      ↓
Model Parameter Update
      ↓
Validation
      ↓
Improved Digital Twin
```

The long-term cycle is:

```text
SIMULATE
↓
MEASURE
↓
COMPARE
↓
CALIBRATE
↓
VALIDATE
↓
IMPROVE
↓
SIMULATE AGAIN
```

---

# 62. Reproducibility Architecture

Given the same:

- software version
- model versions
- configuration
- dataset
- hardware profile
- random seed
- initial conditions

a deterministic BQRC simulation should reproduce the same result within defined numerical tolerances.

Important experiments shall preserve this information.

---

# 63. Scientific Traceability

Important engineering results should eventually be traceable backward.

Example:

```text
Application Result
      ↓
Fused Estimate
      ↓
Calibrated Measurement
      ↓
Raw Measurement
      ↓
Sensor Model
      ↓
Hardware Profile
      ↓
Environmental Model
      ↓
Physical Truth
      ↓
Parameters
      ↓
Research Papers / Datasheets / Datasets
```

This chain is a core requirement of the BQRC platform.

---

# 64. V1 Scientific Vertical Slice

The first working version shall prioritize **one complete, scientifically traceable pipeline** rather than many incomplete modules.

The first vertical slice shall be:

```text
Master Simulation Clock
        ↓
Manual / Orbital Position
        ↓
Geomagnetic Reference
        ↓
Magnetic Truth
        ↓
Reference-Frame Transformation
        ↓
Local Magnetic Disturbance
        ↓
NV Physics
        ↓
ODMR Spectrum Generation
        ↓
Photodetection
        ↓
Electronics / Noise
        ↓
Raw ODMR Spectrum
        ↓
Classical ODMR Processing
        ↓
Resonance Estimate
        ↓
Magnetic-Field Estimate
        ↓
Truth Comparison
        ↓
Uncertainty / Quality
        ↓
Web Visualization
```

A basic conventional IMU channel shall be developed alongside this pipeline.

This establishes the architecture needed for later modules.

---

# 65. V1 Web Application

The first web application does not need every final BQRC feature.

V1 should demonstrate:

- simulation start/stop
- simulation time
- scenario selection
- important manual parameters
- magnetic truth
- raw ODMR spectrum
- estimated magnetic field
- estimation error
- sensor status
- basic IMU data
- source/model information
- experiment export

The interface should display outputs from the actual simulation engine.

---

# 66. V1 Data Flow

The first implementation shall approximately follow:

```text
Configuration
      ↓
Python Simulation Core
      ↓
Magnetic Environment
      ↓
NV Sensor Model
      ↓
ODMR Generator
      ↓
ODMR Estimator
      ↓
Measurement Object
      ↓
Backend API
      ↓
Frontend
      ↓
Plots / Controls / Status
```

Later modules shall extend this architecture rather than replace it.

---

# 67. Testing Architecture

Testing shall progressively include:

```text
tests/
├── unit/
├── integration/
├── regression/
├── scientific/
└── hardware/
```

### Unit Tests

Test individual functions.

### Integration Tests

Test module interaction.

### Regression Tests

Ensure previously working behaviour remains stable.

### Scientific Tests

Compare models against known equations, published values or reference datasets.

### Hardware Tests

Added when physical hardware becomes available.

---

# 68. Architectural Dependency Rule

Dependencies should generally flow downward through the architecture.

For example:

```text
Frontend
↓
Backend
↓
Application Services
↓
Simulation / Algorithms
↓
Core Models
```

Core scientific modules shall not depend on frontend code.

Physics models shall not require web-interface components.

Hardware drivers shall not contain visualization logic.

Algorithms should not secretly depend on hidden truth.

This separation is mandatory for maintainability and future hardware integration.

---

# 69. Architecture Evolution Rule

The architecture is intentionally modular.

Future capabilities should normally be introduced as:

- new models
- new datasets
- new hardware profiles
- new drivers
- new algorithms
- new applications
- new analysis modules
- new backend services
- new frontend components

rather than redesigning the entire system.

Fundamental architectural changes require deliberate review and documentation.

---

# 70. Final Architecture Principle

The complete BQRC Digital Engineering Platform shall preserve the relationship:

```text
SCIENTIFIC EVIDENCE
        ↓
PHYSICAL MODEL
        ↓
DIGITAL TWIN
        ↓
SIMULATION / REAL HARDWARE
        ↓
MEASUREMENT
        ↓
ALGORITHM
        ↓
ENGINEERING RESULT
        ↓
VERIFICATION
        ↓
APPLICATION
```

BQRC is therefore **not only a simulator**, **not only a website**, and **not only an AI/ML project**.

It is a complete digital-engineering environment through which the BQRC mission can progressively be:

**UNDERSTOOD → DESIGNED → SIMULATED → TESTED → VERIFIED → BUILT → INTEGRATED → OPERATED → ANALYZED → IMPROVED**

while maintaining scientific traceability from research evidence and physical models to datasets, algorithms, hardware and final applications.