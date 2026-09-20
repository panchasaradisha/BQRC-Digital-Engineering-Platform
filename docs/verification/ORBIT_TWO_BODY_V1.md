# BQRC Two-Body Orbit Model V1 — Verification Record

**Project:** BQRC Digital Engineering Platform  
**Model:** Two-Body Earth Orbit + RK4 Propagation  
**Verification Status:** Initial Numerical Verification Passed  
**Model Maturity:** V1 — Idealized Physics Model  
**Purpose:** Scientific and software verification of the initial BQRC orbital environment implementation

---

# 1. Model Purpose

The BQRC Two-Body Orbit Model V1 provides the initial orbital-motion capability for the BQRC Digital Engineering Platform.

The model propagates a spacecraft state consisting of:

- position,
- velocity,
- timestamp,
- reference frame,

under idealized Earth point-mass gravity.

The implementation is intended to provide:

- an initial scientifically testable orbital environment,
- a foundation for Earth-relative environment modelling,
- position and velocity input for future geomagnetic models,
- reference data for sensor and navigation simulations,
- a baseline against which higher-fidelity orbit models can later be compared.

This model is not intended to represent operational or flight-qualified BAS orbit prediction.

---

# 2. Governing Physics

The V1 gravitational acceleration model is:

\[
\mathbf{a}
=
-\frac{\mu}{|\mathbf{r}|^3}\mathbf{r}
\]

where:

- \(\mathbf{r}\) is the Earth-centered spacecraft position vector,
- \(|\mathbf{r}|\) is geocentric distance,
- \(\mu\) is Earth's gravitational parameter,
- \(\mathbf{a}\) is gravitational acceleration.

The implemented Earth gravitational parameter is:

\[
\mu = 3.986004418 \times 10^{14}\;m^3/s^2
\]

The authoritative reference for this constant must be recorded in the BQRC evidence system before the model is promoted beyond initial V1 maturity.

---

# 3. Numerical Integration

The orbital equations are propagated using a classical fourth-order Runge-Kutta integrator (RK4).

The propagated differential equations are:

\[
\frac{d\mathbf{r}}{dt}=\mathbf{v}
\]

and

\[
\frac{d\mathbf{v}}{dt}
=
-\frac{\mu}{|\mathbf{r}|^3}\mathbf{r}
\]

The V1 propagator currently requires:

- ECI reference frame,
- position in metres,
- velocity in metres per second,
- positive propagation timestep.

---

# 4. Verification Scenario

An ideal circular two-body orbit was used.

Initial orbital radius:

\[
r = 6,771,000\;m
\]

Circular velocity was calculated from:

\[
v_c = \sqrt{\frac{\mu}{r}}
\]

Theoretical orbital period was calculated using:

\[
T =
2\pi
\sqrt{\frac{r^3}{\mu}}
\]

Result:

- Theoretical period: **5544.855096 s**
- Theoretical period: **92.414252 min**
- Initial circular speed: **7672.598648 m/s**

These values define a numerical verification scenario and must not be interpreted as a confirmed BAS operational orbit.

---

# 5. One-Orbit Verification — 10 Second RK4 Step

Integration timestep:

**10 s**

Results after one theoretical orbital period:

| Metric | Result |
|---|---:|
| Initial radius | 6,771,000.000000 m |
| Final radius | 6,770,999.999779 m |
| Position closure error | 0.017119604 m |
| Velocity closure error | 0.000019387696 m/s |
| Maximum radius error | 0.003599961 m |
| Specific energy error | -9.588152170181e-04 J/kg |

The position closure error corresponds to approximately:

**1.71 cm after one ideal theoretical orbit.**

The maximum radial deviation was approximately:

**3.60 mm.**

---

# 6. Timestep Trade Study

The same theoretical orbit was propagated using several RK4 integration timesteps.

| Step | Propagation Steps | Position Closure Error | Velocity Closure Error | Maximum Radius Error | Specific Energy Error |
|---:|---:|---:|---:|---:|---:|
| 1 s | 5545 | 1.815811817e-06 m | 2.082690793e-09 m/s | 3.539025784e-07 m | -1.899898052e-07 J/kg |
| 5 s | 1109 | 1.037256791e-03 m | 1.175264411e-06 m/s | 2.215048298e-04 m | -2.998486161e-05 J/kg |
| 10 s | 555 | 1.711960413e-02 m | 1.938769577e-05 m/s | 3.599961288e-03 m | -9.588152170e-04 J/kg |
| 30 s | 185 | 1.555812232e+00 m | 1.759809344e-03 m/s | 3.100652909e-01 m | -2.326486148e-01 J/kg |
| 60 s | 93 | 2.893984309e+01 m | 3.268023014e-02 m/s | 5.422846973e+00 m | -7.437359087e+00 J/kg |

---

# 7. Runtime Observations

Runtime was measured using Python `perf_counter`.

Observed execution times varied slightly between repeated runs because runtime depends on:

- operating-system scheduling,
- processor load,
- background applications,
- Python execution conditions,
- development environment activity.

The orbital numerical outputs remained deterministic between repeated runs.

Therefore runtime measurements are treated as approximate engineering-performance indicators rather than physical verification quantities.

---

# 8. Interpretation

The experiment demonstrates that RK4 timestep strongly affects accumulated numerical error.

For this specific ideal circular two-body scenario:

- 1 s produced extremely small numerical error,
- 5 s produced approximately millimetre-scale closure error,
- 10 s produced approximately centimetre-scale closure error,
- 30 s produced metre-scale closure error,
- 60 s produced tens-of-metres closure error.

Smaller timesteps require more propagation calculations but substantially reduce numerical integration error.

No single timestep is declared universally optimal for BQRC.

Timestep selection must depend on:

- required simulation accuracy,
- experiment purpose,
- computational resources,
- coupling to other environment models,
- sensor update rates,
- application requirements.

---

# 9. Verified Properties

The V1 verification currently demonstrates:

- gravitational acceleration points toward Earth,
- gravitational acceleration magnitude follows the two-body equation,
- orbital position and velocity propagate through RK4,
- circular-orbit radius is approximately conserved,
- specific orbital energy is approximately conserved,
- the propagated state approximately closes after one theoretical orbit,
- decreasing timestep substantially reduces numerical integration error.

---

# 10. Current Model Limitations

The following effects are not included in Two-Body Orbit Model V1:

- Earth oblateness and J2 perturbation,
- higher-order geopotential terms,
- atmospheric drag,
- solar radiation pressure,
- Sun gravitational perturbation,
- Moon gravitational perturbation,
- spacecraft maneuvers,
- attitude-orbit coupling,
- real BAS ephemeris,
- operational orbit determination,
- Earth-orientation-parameter corrections,
- high-precision time-system transformations.

Therefore numerical integration accuracy must not be interpreted as real-orbit prediction accuracy.

---

# 11. Planned Evolution

Future orbital-model development may include:

1. ECI/ECEF transformations.
2. Earth rotation modelling.
3. Geodetic latitude, longitude and altitude.
4. Orbital/local reference frames.
5. Higher-fidelity perturbation models.
6. TLE/SGP4 support where scientifically appropriate.
7. Recorded orbit dataset replay.
8. BAS-compatible orbit/environment scenarios when validated data become available.
9. Comparison between multiple propagator fidelities.
10. Uncertainty and covariance propagation.

---

# 12. BQRC Engineering Principle Demonstrated

This verification establishes the BQRC workflow:

Physics definition  
→ software implementation  
→ unit testing  
→ scientific verification  
→ numerical trade study  
→ documented evidence  
→ model maturity tracking  
→ later higher-fidelity replacement

This workflow should be repeated for other major BQRC scientific models.