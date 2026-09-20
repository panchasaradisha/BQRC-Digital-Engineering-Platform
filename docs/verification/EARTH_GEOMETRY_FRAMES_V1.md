# BQRC Earth Geometry & Reference Frames V1 — Verification Record

**Project:** BQRC Digital Engineering Platform  
**Subsystem:** Space Environment / Reference Frames  
**Model:** Earth Geometry & Reference Frames V1  
**Verification Status:** Initial Numerical Verification Passed  
**Model Maturity:** V1 — Engineering Simulation Model  
**Parent Baseline:** `PROJECT_BASELINE.md`

---

# 1. Purpose

This document records the initial implementation, assumptions, verification results, limitations, and maturity of the BQRC Earth Geometry & Reference Frames V1 model.

The purpose of this model is to connect the orbital dynamics layer of the BQRC Digital Engineering Platform with Earth-relative environmental models.

The implemented processing chain is:

```text
Orbital State
      ↓
ECI Position
      ↓
Earth Rotation Model
      ↓
ECEF Position
      ↓
WGS-84 Earth Geometry
      ↓
Geodetic Position
      ↓
Latitude / Longitude / Altitude
```

This layer provides the Earth-relative spacecraft location required by future BQRC models including:

- geomagnetic environment modelling,
- radiation environment modelling,
- thermal and environmental studies,
- ground-track visualization,
- navigation research,
- sensor simulation,
- mission analysis.

The V1 implementation is an engineering simulation model and is not intended to represent a flight-qualified high-precision astrodynamics reference-frame implementation.

---

# 2. Coordinate Systems

## 2.1 Earth-Centered Inertial — ECI

The BQRC orbital propagator represents spacecraft position and velocity using an Earth-centered inertial frame.

The origin is located at Earth's center.

The V1 orbital dynamics model propagates the spacecraft state relative to inertially oriented axes.

The implementation identifies these vectors explicitly using:

```text
ReferenceFrame.ECI
```

This prevents Earth-fixed and inertial vectors from being silently mixed.

---

## 2.2 Earth-Centered Earth-Fixed — ECEF

ECEF is an Earth-centered coordinate system whose axes rotate with Earth.

The implementation identifies Earth-fixed vectors using:

```text
ReferenceFrame.ECEF
```

ECEF coordinates provide the intermediate representation required for converting the spacecraft position into Earth-relative geodetic coordinates.

---

# 3. Earth Geometry Model

BQRC Earth Geometry V1 uses the WGS-84 reference ellipsoid.

The implemented constants are:

| Parameter | Symbol | Implemented Value |
|---|---:|---:|
| Semi-major axis | a | 6,378,137.0 m |
| Inverse flattening | 1/f | 298.257223563 |
| Flattening | f | Derived from inverse flattening |
| Semi-minor axis | b | Derived |
| First eccentricity squared | e² | Derived |

The flattening is calculated using:

\[
f=\frac{1}{298.257223563}
\]

The semi-minor axis is calculated using:

\[
b=a(1-f)
\]

The first eccentricity squared is calculated using:

\[
e^2=f(2-f)
\]

The authoritative source and version for these constants must be recorded in the BQRC evidence registry before the model is promoted beyond initial V1 maturity.

---

# 4. Earth Rotation Model

The V1 Earth rotation implementation uses Earth Rotation Angle (ERA).

The implemented relationship is:

\[
\theta =
2\pi
\left[
0.7790572732640
+
1.00273781191135448
(JD_{UT1}-2451545.0)
\right]
\]

with the number of turns reduced to one revolution.

The resulting angle is normalized to:

\[
0 \leq \theta < 2\pi
\]

Earth Rotation Angle provides the rotation required by the V1 model to transform a vector from the BQRC inertial representation into the rotating Earth-fixed representation.

---

# 5. Time Approximation

Precise Earth Rotation Angle calculations require UT1.

The current BQRC V1 implementation uses the approximation:

```text
UT1 ≈ UTC
```

Therefore the current processing chain is:

```text
Timezone-Aware UTC datetime
        ↓
Julian Date
        ↓
UT1 ≈ UTC approximation
        ↓
Earth Rotation Angle
```

This approximation is explicitly recorded and must not be interpreted as a high-precision Earth-orientation implementation.

A future higher-maturity model may incorporate:

- DUT1,
- IERS Earth Orientation Parameters,
- polar motion,
- higher-precision time-scale handling,
- reference-frame transformations compliant with an explicitly selected standard.

---

# 6. Julian Date Conversion

Python timezone-aware timestamps are converted to Julian Date using the Unix epoch relationship.

The Unix epoch:

```text
1970-01-01 00:00:00 UTC
```

corresponds to:

\[
JD=2440587.5
\]

The J2000 reference Julian Date used by the Earth Rotation Angle relationship is:

\[
JD_{J2000}=2451545.0
\]

The implementation rejects naive timestamps to prevent ambiguous time interpretation.

Verification includes:

- Unix epoch Julian Date,
- J2000 Julian Date,
- timezone-awareness enforcement,
- normalized Earth Rotation Angle.

---

# 7. ECI → ECEF Transformation

The V1 transformation rotates the ECI vector around the Earth Z-axis using Earth Rotation Angle.

The transformation is:

\[
\begin{bmatrix}
x_{ECEF}\\
y_{ECEF}\\
z_{ECEF}
\end{bmatrix}
=
\begin{bmatrix}
\cos\theta & \sin\theta & 0\\
-\sin\theta & \cos\theta & 0\\
0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
x_{ECI}\\
y_{ECI}\\
z_{ECI}
\end{bmatrix}
\]

The transformation preserves:

- vector magnitude,
- physical units,
- Z-axis component for the V1 Z-axis rotation.

The resulting vector is explicitly marked as:

```text
ReferenceFrame.ECEF
```

The transformation rejects input vectors not identified as ECI.

This explicit frame checking is important because a numerically valid vector can still be physically incorrect if interpreted in the wrong coordinate frame.

---

# 8. Geodetic Coordinates

The Earth-fixed Cartesian position is converted to:

```text
Latitude
Longitude
Altitude
```

using the WGS-84 reference ellipsoid.

The BQRC representation is:

```text
GeodeticPosition
```

containing:

```text
latitude_deg
longitude_deg
altitude_m
```

Latitude is constrained to:

\[
-90^\circ \leq \phi \leq 90^\circ
\]

Longitude is constrained to:

\[
-180^\circ \leq \lambda \leq 180^\circ
\]

Altitude is expressed in metres relative to the WGS-84 reference ellipsoid.

---

# 9. Geodetic → ECEF Transformation

For geodetic latitude \(\phi\), longitude \(\lambda\), and altitude \(h\), the prime vertical radius of curvature is:

\[
N(\phi)=
\frac{a}
{\sqrt{1-e^2\sin^2\phi}}
\]

ECEF coordinates are then calculated as:

\[
x=(N+h)\cos\phi\cos\lambda
\]

\[
y=(N+h)\cos\phi\sin\lambda
\]

\[
z=
[N(1-e^2)+h]\sin\phi
\]

This transformation is non-iterative because geodetic latitude is already known.

The resulting Cartesian vector is expressed in:

```text
metres
```

and explicitly identified as:

```text
ReferenceFrame.ECEF
```

---

# 10. ECEF → Geodetic Transformation

The reverse conversion requires determining geodetic latitude from Cartesian coordinates.

Because the Earth model is ellipsoidal rather than spherical, the conversion is solved iteratively.

The V1 implementation follows the general process:

```text
ECEF X/Y/Z
    ↓
Horizontal Distance
    ↓
Initial Latitude Estimate
    ↓
Prime Vertical Radius
    ↓
Altitude Estimate
    ↓
Updated Latitude
    ↓
Convergence Test
    ↓
Latitude / Longitude / Altitude
```

The default angular convergence tolerance is:

```text
1 × 10^-12 rad
```

and the default maximum number of iterations is:

```text
20
```

The conversion raises an error if convergence is not achieved.

The exact Earth-center position:

```text
x = 0
y = 0
z = 0
```

is rejected because geodetic coordinates are undefined at Earth's center.

The polar-axis case is handled separately because the horizontal distance approaches zero.

---

# 11. Coordinate Round-Trip Verification

Round-trip verification was performed using:

```text
Known Geodetic Position
        ↓
Geodetic → ECEF
        ↓
ECEF Cartesian Position
        ↓
ECEF → Geodetic
        ↓
Recovered Position
```

Tests include:

- equatorial surface positions,
- polar surface positions,
- non-zero longitude,
- representative mid-latitude positions,
- representative orbital altitude.

A representative orbital-altitude scientific regression case uses:

```text
Latitude  = 37.25 deg
Longitude = -122.10 deg
Altitude  = 400,000 m
```

Scientific regression protection requires representative coordinate recovery to remain within tight numerical tolerances.

This verifies internal numerical consistency of the implemented forward and reverse transformations.

It does not by itself establish absolute accuracy against an external authoritative geodetic software implementation.

---

# 12. Equatorial Orbit Ground-Track Experiment

An ideal circular zero-inclination orbit was propagated using the BQRC Two-Body Orbit V1 model.

Scenario:

```text
Geocentric orbital radius = 6,771,000 m
Inclination               = 0 deg
RK4 timestep              = 10 s
Displayed interval        = 300 s
```

The theoretical orbital period was:

```text
5544.855 s
```

or approximately:

```text
92.414 min
```

The experiment connected:

```text
OrbitalState
      ↓
RK4 Propagation
      ↓
ECI Position
      ↓
Earth Rotation Angle
      ↓
ECEF Position
      ↓
WGS-84 Conversion
      ↓
Latitude / Longitude / Altitude
```

Observed behavior:

- latitude remained approximately 0°,
- longitude changed continuously with Earth-relative spacecraft motion,
- longitude wrapped correctly across ±180°,
- geodetic altitude remained approximately 392.863 km.

The equatorial altitude follows from:

\[
6,771,000
-
6,378,137
=
392,863\;m
\]

or:

\[
392.863\;km
\]

This behavior is consistent with the defined ideal equatorial circular-orbit scenario.

---

# 13. Inclined Orbit Ground-Track Experiment

A second experiment used an ideal circular orbit with:

```text
Inclination = 51.6 deg
```

The inclination value is an engineering verification scenario and is not a statement of the operational BAS orbit.

The initial velocity direction was modified using:

\[
v_y=v\cos i
\]

and:

\[
v_z=v\sin i
\]

while maintaining the original circular velocity magnitude.

Because:

\[
\cos^2 i+\sin^2 i=1
\]

the total velocity magnitude remains equal to the circular orbital velocity.

The experiment therefore changes the orbital plane orientation without intentionally changing the circular-orbit energy.

Observed behavior included:

- increasing northern latitude,
- return toward the equator,
- southern latitude traversal,
- longitude evolution,
- ±180° longitude wrapping,
- changing geodetic altitude.

The continuously sampled geodetic latitude extrema were approximately:

```text
Maximum latitude = +51.775323 deg
Minimum latitude = -51.775901 deg
```

The extrema were approximately symmetric.

---

# 14. Geodetic Latitude vs Orbital Inclination

The orbital inclination used in the verification experiment was:

```text
51.6 deg
```

while the maximum WGS-84 geodetic latitude was approximately:

```text
51.775 deg
```

These quantities are not identical.

Orbital inclination describes the orientation of the orbital plane relative to the equatorial reference plane.

Geodetic latitude is defined relative to the normal of the WGS-84 reference ellipsoid.

Therefore:

```text
Orbital inclination
        ≠
Maximum geodetic latitude
```

in the strict geometric sense.

The difference must not automatically be interpreted as orbital propagation error.

---

# 15. Altitude Variation in the Inclined Circular Orbit

The two-body inclined orbit maintains approximately constant geocentric radius.

However, WGS-84 represents Earth as an oblate ellipsoid.

Therefore:

```text
Constant geocentric radius
```

does not imply:

```text
Constant geodetic altitude
```

at all latitudes.

The experiment showed approximately:

```text
Near equatorial region:
~392.9 km

Near higher latitude:
~406 km
```

This variation is consistent with measuring altitude relative to an oblate reference ellipsoid.

This is an important distinction for future BQRC environmental modelling.

---

# 16. Longitude Wrapping

Longitude is represented in the normalized range:

\[
-180^\circ \leq \lambda \leq 180^\circ
\]

Therefore a sequence such as:

```text
+170 deg
   ↓
+180 deg
   ↓
-180 deg
   ↓
-170 deg
```

represents continuous geographic motion across the longitude boundary.

This coordinate wrapping must not be interpreted as a discontinuity in spacecraft motion.

Future visualization and data-analysis modules must account for this behavior when plotting ground tracks.

For example, a direct plotting algorithm that connects +179° to -179° without wrap handling could incorrectly draw a line across the entire map.

---

# 17. Multi-Rate Experiment Behavior

The ground-track experiments separate:

```text
Propagation timestep
```

from:

```text
Displayed output interval
```

For the current experiment:

```text
Propagation timestep = 10 s
Displayed interval   = 300 s
```

This demonstrates an early form of the BQRC multi-rate simulation concept.

The numerical orbit can be updated more frequently than the displayed or stored output.

Future BQRC architecture may independently schedule:

```text
Orbit model
Magnetic environment
Thermal environment
Radiation environment
IMU sampling
NV acquisition
Telemetry
Data storage
User-interface visualization
```

at different rates coordinated by the simulation orchestrator.

---

# 18. Scientific Regression Protection

Scientific regression tests currently protect the following properties:

- geodetic/ECEF round-trip numerical consistency,
- equatorial altitude consistency,
- expected inclined-orbit geodetic latitude range,
- approximate north/south latitude symmetry.

The inclined-orbit latitude regression range currently requires approximately:

```text
Maximum latitude:
51.7 deg < latitude < 51.9 deg

Minimum latitude:
-51.9 deg < latitude < -51.7 deg
```

The north/south extrema must also remain approximately symmetric.

These bounds are engineering verification thresholds.

They are not mission requirements, navigation accuracy specifications, or flight-qualification limits.

---

# 19. Verified Capabilities

Earth Geometry & Reference Frames V1 currently demonstrates:

- WGS-84 ellipsoid constants,
- derived ellipsoid parameters,
- timezone-aware Julian Date conversion,
- Earth Rotation Angle calculation,
- ECI → ECEF vector transformation,
- reference-frame validation,
- physical-unit preservation,
- ECEF → geodetic conversion,
- geodetic → ECEF conversion,
- coordinate round-trip consistency,
- equatorial orbit Earth-location conversion,
- inclined orbit Earth-location conversion,
- longitude normalization,
- geodetic altitude behavior over an oblate Earth,
- end-to-end orbit-to-Earth-location processing,
- scientific regression protection.

---

# 20. Current Software Verification Status

At the completion of Earth Geometry & Reference Frames V1, the BQRC test suite contains:

```text
89 passing tests
```

The project quality gates also pass:

```text
pytest       → PASS
ruff         → PASS
mypy         → PASS
```

The test suite includes:

```text
Unit tests
    +
Scientific regression tests
```

The passing software tests demonstrate consistency with the implemented model definitions.

They do not constitute independent external scientific validation or flight qualification.

---

# 21. Current Limitations

The V1 model does not currently include:

- measured DUT1,
- IERS Earth Orientation Parameters,
- polar motion,
- full precession and nutation modelling,
- high-precision celestial/intermediate reference-frame chains,
- relativistic reference-frame corrections,
- operational BAS ephemeris,
- uncertainty in Earth-orientation parameters,
- covariance propagation through coordinate transformations,
- external-library cross-validation,
- authoritative geodetic benchmark dataset validation.

The current ECI label represents the BQRC V1 inertial-frame abstraction and must not automatically be interpreted as a fully realized ICRF, GCRF, TEME, or another high-precision astronomical reference frame.

This distinction must remain explicit as the platform evolves.

---

# 22. Model Maturity

Current maturity:

```text
Earth Geometry & Reference Frames V1
```

Status:

```text
Initial engineering implementation
        +
Unit verification
        +
Special-case verification
        +
Round-trip numerical verification
        +
End-to-end orbit experiments
        +
Scientific regression protection
```

This model is suitable as the initial Earth-location backbone of the BQRC Digital Engineering Platform.

It is not flight qualification evidence.

It is also not intended to replace a validated high-precision astrodynamics library for operational mission navigation.

---

# 23. Scientific Traceability Status

The V1 implementation currently contains scientifically meaningful constants and relationships including:

```text
WGS-84 semi-major axis
WGS-84 inverse flattening
Derived flattening
Derived semi-minor axis
Derived eccentricity
Julian Date conversion
Earth Rotation Angle relationship
Geodetic conversion equations
```

These quantities must ultimately be linked to authoritative references in the BQRC Knowledge, Documentation & Evidence layer.

The intended traceability chain is:

```text
Scientific Quantity
        ↓
Authoritative Source
        ↓
Document / Publication / Standard
        ↓
Version
        ↓
Value / Equation
        ↓
Software Implementation
        ↓
Tests
        ↓
Verification Experiment
        ↓
Generated Result
```

This evidence chain will allow future users to determine why a model exists, where its constants came from, which implementation uses them, and how the implementation was verified.

---

# 24. Planned Evolution

Future development may include:

1. Authoritative-source evidence records for WGS-84 constants.
2. Authoritative-source evidence records for the ERA formulation.
3. Explicit UTC and UT1 handling.
4. DUT1 ingestion.
5. IERS Earth Orientation Parameter support.
6. Polar-motion modelling.
7. Explicit high-fidelity reference-frame definitions.
8. External geodetic implementation comparison.
9. External astrodynamics implementation comparison.
10. Ground-track visualization.
11. Uncertainty propagation.
12. Coordinate-transformation covariance propagation.
13. Dataset replay using recorded orbital data.
14. BAS-specific scenario support when validated information becomes available.
15. Configurable reference-frame fidelity.
16. Model-maturity selection for engineering versus higher-fidelity simulations.

---

# 25. BQRC Engineering Workflow Demonstrated

This milestone extends the BQRC engineering workflow:

```text
Physical / Geometric Definition
        ↓
Constants and Assumptions
        ↓
Software Implementation
        ↓
Unit Tests
        ↓
Special-Case Verification
        ↓
Round-Trip Verification
        ↓
End-to-End Orbit Experiment
        ↓
Inclined-Orbit Experiment
        ↓
Scientific Regression Tests
        ↓
Verification Documentation
        ↓
Model Maturity Tracking
```

The same evidence-driven workflow should be applied to future BQRC environment, sensor, hardware, algorithm, and mission-software models.

---

# 26. Relationship to Future Geomagnetic Modelling

Earth Geometry & Reference Frames V1 establishes the location input required by the future BQRC geomagnetic environment.

The intended processing chain is:

```text
Orbital State
      ↓
ECI Position
      ↓
Earth Rotation
      ↓
ECEF Position
      ↓
WGS-84
      ↓
Geodetic Position
      │
      ├── Latitude
      ├── Longitude
      └── Altitude
      │
      + Time
      ↓
Geomagnetic Environment Model
      ↓
Reference Magnetic Field
      ↓
Sensor Truth Input
      ↓
NV Magnetometer Digital Twin
      ↓
Electronics / Acquisition
      ↓
ODMR Processing
      ↓
Estimated Magnetic Field
```

The geomagnetic model must use:

- an explicitly selected scientific model,
- an explicitly recorded model version,
- authoritative coefficient data,
- defined validity dates,
- documented coordinate conventions,
- documented units,
- source provenance,
- verification against authoritative reference outputs.

No geomagnetic field values should be invented or treated as authoritative without that evidence chain.

---

# 27. Relationship to the BQRC Digital Engineering Architecture

This milestone currently occupies the following part of the BQRC architecture:

```text
SPACE ENVIRONMENT SIMULATOR
│
├── Orbit Dynamics
│   └── Two-Body Orbit V1
│
├── Earth Geometry
│   └── WGS-84 V1
│
├── Earth Rotation
│   └── ERA V1
│
├── Reference Frames
│   └── ECI → ECEF V1
│
└── Geodetic Location
    ├── ECEF → Geodetic
    └── Geodetic → ECEF
```

Future environment modules will consume the outputs of this layer rather than independently recreating spacecraft location calculations.

This maintains the BQRC architectural principle:

> Physics, sensors, hardware, algorithms, mission software, data analysis, and user interfaces remain modular and communicate through clearly defined interfaces.

---

# 28. Verification Conclusion

Earth Geometry & Reference Frames V1 has successfully established the first complete Earth-relative location pipeline for the BQRC Digital Engineering Platform.

The verified processing chain is:

```text
Time
  +
Orbital State
      ↓
Two-Body Propagation
      ↓
ECI Position
      ↓
Earth Rotation Angle
      ↓
ECEF Position
      ↓
WGS-84 Geometry
      ↓
Latitude / Longitude / Altitude
```

The implementation has demonstrated:

- stable software behavior,
- explicit coordinate-frame handling,
- Earth rotation,
- ellipsoidal Earth geometry,
- forward and reverse geodetic conversion,
- round-trip numerical consistency,
- equatorial ground-track behavior,
- inclined ground-track behavior,
- scientific regression protection.

The current model remains intentionally modular so that higher-fidelity Earth-orientation and reference-frame implementations can replace V1 components without redesigning the complete BQRC Digital Engineering Platform.

**Earth Geometry & Reference Frames V1 is therefore accepted as the initial verified Earth-location backbone for continued BQRC digital-engineering development.**