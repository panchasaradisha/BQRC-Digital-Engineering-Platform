# BQRC Geomagnetic Environment V1 — Model Selection & Evidence Baseline

**Project:** BQRC Digital Engineering Platform  
**Subsystem:** Space Environment / Geomagnetic Field  
**Milestone:** Step 55  
**Status:** Model selection completed; implementation pending  
**Primary Model:** IGRF-14  
**Secondary Model:** WMM2025

---

## 1. Purpose

The BQRC geomagnetic environment provides an Earth magnetic-field reference for the digital engineering and NV-center quantum magnetometer simulation.

The required processing chain is:

```text
Orbital Propagator
       ↓
ECI Position
       ↓
Earth Rotation
       ↓
ECEF Position
       ↓
WGS-84 Geodetic Location
       +
Simulation Time
       ↓
IGRF-14 Magnetic Field
       ↓
Magnetic Field Vector
       ↓
Reference Frame Transformation
       ↓
NV Magnetometer Digital Twin
       ↓
Simulated Sensor Measurement
```

## 2. Model Selection

The primary reference-field model is **International Geomagnetic Reference Field, 14th Generation (IGRF-14)**.

IGRF-14 is maintained by the International Association of Geomagnetism and Aeronomy (IAGA).

Its 2025–2030 interval uses predictive secular variation.

The secondary comparison model is **World Magnetic Model 2025 (WMM2025)**, developed by NOAA/NCEI and the British Geological Survey for applications including navigation and attitude referencing.

The secondary model is intended for comparisons, not as an independent measurement of the true geomagnetic field.

## 3. Scientific Sources

### Primary

IAGA — International Geomagnetic Reference Field:

https://www.iaga-aiga.org/igrf/

IGRF-14 scientific paper:

https://doi.org/10.1186/s40623-025-02360-0

### Secondary

NOAA — World Magnetic Model:

https://www.ncei.noaa.gov/products/world-magnetic-model

WMM2025 Technical Report:

https://doi.org/10.25923/prbc-s316

## 4. Coefficient Integrity

Official model coefficients must be obtained from authoritative distribution sources.

BQRC must record:

- Model name and generation
- Coefficient source URL
- Download date
- Dataset file version
- SHA-256 checksum
- Applicable epoch and validity interval
- Normalization convention
- Reference radius
- Units
- License and attribution
- Verification dataset provenance

Coefficients must not be invented or manually approximated.

## 5. Initial Verification Scenario

The initial verification scenario will use:

- Simulation date: 2027-07-18
- Earth model: WGS-84
- Geocentric orbital radius: 6,771,000 m
- Orbital inclination: 51.6 degrees
- Propagation timestep: 10 seconds
- Geodetic altitude: computed from the orbital position

The scenario is an engineering verification case and is not a claim about operational BAS orbital parameters.

## 6. Magnetic Field Units

The model implementation will use magnetic field values with explicit units.

Expected scientific-model input/output units include:

```text
nanotesla (nT)
```

SI conversions must use:

```text
1 nT = 1e-9 T
```

The NV magnetometer subsystem will consume field vectors with explicit unit conversions.

## 7. Coordinate Conventions

The initial interface must distinguish:

```text
Geodetic latitude / longitude / height
Local North-East-Down magnetic components
ECEF magnetic vectors
ECI magnetic vectors
Sensor-body magnetic vectors
```

Reference-frame transformations must be explicit.

The geomagnetic model should not return an unlabelled three-component vector.

Local North-East-Down conventions and transformations into ECEF must be verified independently.

## 8. Model Boundary

IGRF-14 represents Earth's large-scale main magnetic field.

It does not independently account for all instantaneous field variations and local disturbances.

Future separate models may include:

- External magnetospheric fields
- Ionospheric contributions
- Magnetic storms and space weather
- Spacecraft-generated magnetic interference
- Electronic magnetic noise
- Sensor mounting and orientation errors
- Sensor bias and calibration effects

## 9. Model Validity

The 2025–2030 predictive interval must be respected for the initial implementation.

The software must validate simulation dates against the supported model interval.

A simulation outside the interval must not silently claim scientifically supported output.

A future scenario in 2032 requires a model with an appropriate validity period or a clearly identified extrapolation experiment.

## 10. Verification Requirements

Before declaring Geomagnetic Environment V1 verified, BQRC must demonstrate:

1. Official coefficient loading.
2. Coefficient file checksum recording.
3. Correct epoch handling.
4. Correct secular variation handling.
5. Correct spherical-harmonic evaluation.
6. Correct field units.
7. Explicit vector frame labels.
8. Comparison against official reference calculations.
9. Multiple geographic verification cases.
10. Verification at representative orbital altitudes.
11. Appropriate handling of validity boundaries.
12. Scientific regression tests.
13. Complete source and assumption traceability.

## 11. Planned Implementation Architecture

```text
src/bqrc/environment/geomagnetic/
    __init__.py
    model.py
    coefficients.py
    igrf.py
    transforms.py
```

The implementation should connect to the existing Earth geometry and orbital simulation layers.

It must preserve modular separation between:

- Reference magnetic-field physics
- Spacecraft magnetic disturbances
- Sensor physics
- Electronics noise
- Estimation algorithms

## 12. Acceptance Status

**Current state:** Scientific model selected and evidence requirements defined.

**Not yet completed:**

- Official coefficients integrated
- IGRF-14 implementation
- Official benchmark comparisons
- Orbital geomagnetic-field experiment
- Scientific regression verification

Geomagnetic Environment V1 must not be considered verified until those activities are completed.

---

**Step 55 outcome:** IGRF-14 selected as the primary BQRC geomagnetic reference-field model, with WMM2025 identified as a secondary comparison model. Implementation remains pending scientific verification.   