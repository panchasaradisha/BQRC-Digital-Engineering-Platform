# BQRC Geomagnetic Model Selection & Evidence Baseline

**Project:** BQRC Digital Engineering Platform  
**Subsystem:** Space Environment Simulator  
**Domain:** Geomagnetic Environment  
**Status:** Initial Model Selection  
**Primary Model:** IGRF-14  
**Model Role:** Reference Earth Main Magnetic Field  
**Parent Baseline:** `PROJECT_BASELINE.md`

---

# 1. Purpose

This document defines the initial scientific model selection, evidence basis, scope, assumptions, validity constraints, and planned implementation strategy for the BQRC geomagnetic environment.

The geomagnetic environment model will provide the reference Earth magnetic field used by later BQRC modules including:

- NV-center magnetometer simulation,
- magnetic-field sensing studies,
- sensor-fusion research,
- astronaut navigation research,
- spacecraft magnetic-environment studies,
- calibration experiments,
- synthetic dataset generation,
- environmental analysis.

The geomagnetic model must remain separate from sensor errors and local spacecraft magnetic interference.

The intended architecture is:

```text
Orbital State
      ↓
Earth Geometry & Reference Frames
      ↓
Latitude / Longitude / Altitude
      +
Time
      ↓
IGRF-14
      ↓
Reference Earth Main Magnetic Field
      ↓
Local / Spacecraft Magnetic Disturbances
      ↓
Sensor Truth Field
      ↓
NV Magnetometer Digital Twin
      ↓
Optical + Microwave + Electronics Models
      ↓
ODMR Measurement
      ↓
Estimated Magnetic Field
```

---

# 2. Selected Primary Model

The selected primary geomagnetic reference model for the initial BQRC implementation is:

```text
International Geomagnetic Reference Field
14th Generation
IGRF-14
```

IGRF is maintained by the International Association of Geomagnetism and Aeronomy.

IGRF provides a mathematical representation of Earth's large-scale main magnetic field.

BQRC will use IGRF-14 as the initial scientific reference-field model.

---

# 3. Why IGRF-14 Was Selected

BQRC requires a model suitable for scientific modelling of Earth's main magnetic field rather than only a navigation-heading correction model.

IGRF-14 was selected because it provides:

- an internationally maintained geomagnetic reference model,
- spherical-harmonic representation of Earth's main field,
- published Gauss coefficients,
- secular-variation information,
- global coverage,
- support for scientific geomagnetic studies,
- authoritative reference implementations and calculators,
- traceable model generations.

This makes it appropriate for the BQRC scientific environment layer.

---

# 4. IGRF-14 Model Generation

The 14th generation of the International Geomagnetic Reference Field was adopted in November 2024.

The generation includes:

```text
DGRF-2020
IGRF-2025
SV-2025-2030
```

The 2025 main-field model represents Earth's main magnetic field at epoch:

```text
2025.0
```

A predictive secular-variation model describes expected linear field evolution over:

```text
2025.0 → 2030.0
```

---

# 5. Spherical-Harmonic Resolution

For the recent IGRF models, the main magnetic field is represented using spherical harmonics through degree and order:

```text
n = 13
```

The predictive secular-variation model for 2025–2030 extends through degree and order:

```text
n = 8
```

The BQRC implementation must preserve these model limits.

Coefficients outside the authoritative model definition must not be invented.

---

# 6. Model Validity

The current IGRF-14 generation supports the field model through:

```text
2030.0
```

using the predictive secular-variation model.

Therefore BQRC must distinguish between:

```text
SUPPORTED MODEL DATE
```

and:

```text
OUT-OF-RANGE SIMULATION DATE
```

The software must not silently extrapolate beyond the supported interval.

---

# 7. Important BQRC Date Constraint

Earlier BQRC orbital experiments used the engineering scenario date:

```text
2032-07-18
```

This date is outside the predictive interval of IGRF-14.

Therefore the initial geomagnetic implementation must NOT silently use IGRF-14 for the 2032 scenario.

Initial geomagnetic verification experiments will instead use dates inside the supported model interval.

Future BQRC/BAS-era scenarios must use one of the following:

1. a newer authoritative IGRF generation available for the mission epoch,
2. another validated model appropriate for that epoch,
3. or an explicitly labelled extrapolation mode used only for research and sensitivity studies.

Any extrapolation must be recorded in provenance and must never be represented as authoritative model output.

---

# 8. Mathematical Model

IGRF represents Earth's magnetic scalar potential using a spherical-harmonic expansion.

Conceptually:

```text
Gauss Coefficients
      +
Position
      +
Time
      ↓
Spherical-Harmonic Evaluation
      ↓
Magnetic Potential
      ↓
Spatial Derivatives
      ↓
Magnetic Field Components
```

The implementation will use the official IGRF equations and coefficient conventions.

The BQRC implementation must not derive or invent replacement coefficients.

---

# 9. Gauss Coefficients

The IGRF model is parameterized using Gauss coefficients conventionally represented as:

```text
g_n^m
h_n^m
```

where:

```text
n = spherical-harmonic degree
m = spherical-harmonic order
```

The coefficients encode the spatial structure of Earth's main magnetic field.

For time-dependent prediction, secular-variation coefficients describe the expected rate of coefficient change.

BQRC will store authoritative coefficients separately from model algorithms.

The intended architecture is:

```text
Model Algorithm
      +
Coefficient Dataset
      ↓
Geomagnetic Evaluation
```

This allows future IGRF generations to replace coefficient datasets without redesigning the entire geomagnetic subsystem.

---

# 10. Coefficient Provenance

Every coefficient dataset introduced into BQRC must record:

```text
Model family
Model generation
Epoch
Validity interval
Maximum degree/order
Source organization
Source document or dataset
Retrieval date
File checksum
Original filename
Processing history
```

Modified coefficient files must never overwrite the original authoritative source file.

The intended data structure is conceptually:

```text
data/
└── reference/
    └── geomagnetic/
        └── igrf14/
            ├── raw/
            ├── processed/
            └── metadata/
```

The raw source should remain immutable.

---

# 11. Coordinate Inputs

The geomagnetic model requires location and time.

BQRC Earth Geometry & Reference Frames V1 already provides:

```text
Geodetic latitude
Geodetic longitude
Ellipsoidal altitude
Timestamp
```

The geomagnetic implementation must explicitly convert these inputs into the coordinate quantities required by the selected IGRF equations.

Geodetic and geocentric latitude must not be treated as interchangeable.

---

# 12. Magnetic Field Outputs

The geomagnetic model should ultimately provide magnetic-field components including a local vector representation.

A useful local convention is:

```text
X = North component
Y = East component
Z = Vertical component
```

Derived quantities may include:

```text
H = horizontal intensity
F = total intensity
D = declination
I = inclination
```

The precise sign conventions and coordinate definitions must be documented before implementation.

---

# 13. Units

The geomagnetic layer must use explicit units.

Typical IGRF magnetic-field outputs are expressed in:

```text
nanotesla
nT
```

The BQRC internal interface must explicitly record units rather than relying on implicit numerical conventions.

Future sensor modules may additionally require:

```text
tesla
T
```

with:

```text
1 nT = 1 × 10^-9 T
```

Unit conversion must occur explicitly at subsystem boundaries.

---

# 14. Relationship to NV Magnetometry

The IGRF output is NOT the final simulated NV measurement.

The correct conceptual chain is:

```text
IGRF Main Field
      ↓
Reference Environmental Field
      +
Local Magnetic Disturbances
      +
Spacecraft / BAS Interference
      +
Sensor Orientation
      ↓
Magnetic Field at Diamond
      ↓
NV Hamiltonian / ODMR Model
      ↓
Optical Excitation
      ↓
Microwave Excitation
      ↓
Fluorescence Response
      ↓
Photodetection
      ↓
Electronics / ADC
      ↓
ODMR Spectrum
      ↓
Field Estimation Algorithm
```

This separation prevents environmental truth from being mixed with sensor behavior.

---

# 15. What IGRF Does Not Represent

IGRF must not be treated as a complete description of the magnetic field experienced by the BQRC sensor.

The BQRC magnetic environment may eventually include:

```text
Earth main field
+
crustal magnetic field
+
magnetospheric contributions
+
ionospheric contributions
+
space-weather disturbances
+
spacecraft-generated magnetic field
+
electrical-system interference
+
local magnetic materials
+
payload electronics
+
sensor noise
```

IGRF primarily provides the large-scale Earth main-field reference.

Additional effects must be implemented as separate models with their own evidence and maturity records.

---

# 16. Spacecraft / BAS Magnetic Interference

A hosted payload may experience magnetic interference from nearby systems.

Potential contributors include:

- power electronics,
- electrical currents,
- motors,
- switching converters,
- cables,
- magnetic materials,
- payload electronics,
- nearby experiments,
- onboard appliances,
- structural magnetic contamination.

These effects must not be inserted into the IGRF model.

Instead:

```text
IGRF Reference Field
        +
Local Interference Model
        ↓
Field at Sensor Location
```

This preserves scientific traceability.

---

# 17. World Magnetic Model

The World Magnetic Model is another authoritative geomagnetic model.

The current generation is:

```text
WMM2025
```

WMM2025 is designed particularly for navigation, attitude, and heading applications.

It is valid for the 2025–2029 model period.

WMM2025 uses a spherical-harmonic main-field representation through degree and order 12.

---

# 18. Role of WMM in BQRC

WMM2025 will not initially replace IGRF-14 as the primary BQRC scientific reference model.

Instead, it may later be used for:

```text
Independent comparison
Navigation-oriented experiments
Cross-model verification
Sensitivity studies
```

This gives BQRC the future architecture:

```text
Geomagnetic Model Interface
        │
        ├── IGRF-14
        │      Primary scientific reference
        │
        └── WMM2025
               Future comparison /
               navigation model
```

The model interface should therefore eventually avoid hard-coding the entire platform directly to one geomagnetic model.

---

# 19. Model Versioning

The software must explicitly identify the geomagnetic model generation.

For example:

```text
IGRF-14
```

must never be represented merely as:

```text
IGRF
```

in scientific provenance.

This ensures that future updates such as a later IGRF generation can coexist with older experiment records.

A historical experiment must remain reproducible using the model version that originally generated it.

---

# 20. Verification Strategy

The BQRC IGRF implementation will be verified in stages.

## Stage 1 — Coefficient Integrity

Verify:

```text
Coefficient count
Degree/order structure
Epoch
Secular-variation structure
Metadata
Checksum
```

## Stage 2 — Mathematical Unit Tests

Verify:

```text
Associated Legendre functions
Coefficient time adjustment
Coordinate conversion
Field-component equations
Derived magnetic quantities
```

## Stage 3 — Authoritative Reference Points

Evaluate selected locations and dates and compare BQRC results against authoritative IGRF calculator/reference outputs.

## Stage 4 — Orbital Evaluation

Run:

```text
Orbit
 ↓
ECI
 ↓
ECEF
 ↓
Geodetic
 ↓
IGRF
 ↓
Magnetic Field Along Orbit
```

## Stage 5 — Scientific Regression

Freeze representative verified outputs within justified tolerances.

---

# 21. No Self-Referential Verification

BQRC must not validate its IGRF implementation only by comparing it against another calculation produced by the same BQRC implementation.

Verification should include independent authoritative outputs.

The intended relationship is:

```text
BQRC Implementation
        ↘
         Compare
        ↗
Authoritative Reference Output
```

This reduces the risk of reproducing the same implementation error in both expected and calculated values.

---

# 22. Model Maturity

Initial maturity:

```text
Geomagnetic Environment
Model Selection Stage
```

Current status:

```text
Authoritative model family selected
        ↓
Model generation selected
        ↓
Validity constraints identified
        ↓
Evidence architecture defined
        ↓
Implementation not yet accepted
```

No BQRC IGRF implementation should be labelled verified until the authoritative coefficient dataset and independent reference-output comparisons have been completed.

---

# 23. Scientific Traceability Chain

The required traceability chain is:

```text
IAGA / Authoritative Source
        ↓
IGRF-14 Definition
        ↓
Official Coefficient Dataset
        ↓
BQRC Evidence Metadata
        ↓
BQRC Coefficient Loader
        ↓
BQRC IGRF Algorithm
        ↓
Unit Tests
        ↓
Authoritative Reference Comparison
        ↓
Orbital Experiment
        ↓
Scientific Regression Tests
        ↓
Verification Record
        ↓
NV Magnetometer Truth Input
```

Every stage must remain inspectable.

---

# 24. Implementation Principle

BQRC will separate:

```text
DATA
```

from:

```text
ALGORITHM
```

and from:

```text
SENSOR MODEL
```

Therefore:

```text
Official IGRF coefficients
        ↓
Geomagnetic algorithm
        ↓
Reference field
        ↓
Environmental disturbances
        ↓
Sensor truth field
        ↓
NV sensor model
```

will remain separate software responsibilities.

---

# 25. Initial Implementation Roadmap

The initial Geomagnetic Environment V1 development sequence is:

```text
Model selection
        ↓
Evidence baseline
        ↓
Acquire official coefficients
        ↓
Record provenance + checksum
        ↓
Coefficient parser
        ↓
Coefficient integrity tests
        ↓
Coordinate preparation
        ↓
IGRF spherical-harmonic core
        ↓
Magnetic vector output model
        ↓
Authoritative reference comparison
        ↓
Orbit magnetic-field experiment
        ↓
Scientific regression tests
        ↓
Verification document
```

---

# 26. Current Decision

The BQRC Digital Engineering Platform adopts:

```text
IGRF-14
```

as the primary initial reference model for Earth's main magnetic field.

WMM2025 is retained as a future navigation-oriented comparison and cross-verification model.

IGRF-14 outputs will not be silently extrapolated beyond the supported model period.

The model will remain separate from local magnetic disturbances and NV sensor behaviour.

This decision establishes the scientific baseline for development of:

```text
BQRC Geomagnetic Environment V1
```