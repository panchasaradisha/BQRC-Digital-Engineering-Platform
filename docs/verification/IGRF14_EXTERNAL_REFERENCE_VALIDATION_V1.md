
# IGRF-14 External Reference Validation - V1

## 1. Purpose

Document independent numerical comparisons between the BQRC IGRF-14 magnetic-field implementation and the NOAA/NCEI Geomagnetic Field Calculator.

The verification covers five geographic and altitude configurations, including a predictive epoch and an orbital-altitude case.

## 2. Reference Configuration

| Parameter | Value |
|---|---|
| Reference provider | NOAA / NCEI |
| Reference calculator | Geomagnetic Field Calculator |
| Calculator model displayed | IGRF2025 |
| BQRC model | IGRF-14 |
| Coefficient dataset | igrf14coeffs.txt |
| Coordinate system | WGS-84 geodetic |
| Magnetic component frame | North-East-Down (NED) |
| Magnetic-field units | Nanotesla (nT) |
| Angular units | Degrees |
| Surface reference date | 2025-01-01 |
| Orbital-altitude NOAA date | 2027-07-02 |
| Orbital-altitude BQRC epoch | 2027.5 |

Reference calculator:

https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml

## 3. Reference Cases

| Case | Latitude (deg) | Longitude (deg) | GPS altitude (km) | BQRC epoch |
|---|---:|---:|---:|---:|
| A - Greenwich equator | 0.0 | 0.0 | 0 | 2025.0 |
| B - Northern midlatitude | 45.0 | 0.0 | 0 | 2025.0 |
| C - Western longitude | 20.0 | -75.0 | 0 | 2025.0 |
| D - Southern hemisphere | -35.0 | 140.0 | 0 | 2025.0 |
| E - Ahmedabad region, orbital altitude | 23.0 | 72.5 | 400 | 2027.5 |

All five reference configurations were manually compared with the NOAA calculator.

## 4. Numerical Comparisons

### Case A - Greenwich Equator

Date: 2025-01-01

| Quantity | BQRC | NOAA | Absolute difference |
|---|---:|---:|---:|
| North X (nT) | 27456.621763 | 27456.6 | 0.021763 |
| East Y (nT) | -1926.548583 | -1926.5 | 0.048583 |
| Down Z (nT) | -15997.352904 | -15997.4 | 0.047096 |
| Horizontal H (nT) | 27524.128834 | 27524.1 | 0.028834 |
| Total F (nT) | 31835.404317 | 31835.4 | 0.004317 |
| Declination D (deg) | -4.013694 | -4.0137 | 0.000006 |
| Inclination I (deg) | -30.165667 | -30.1657 | 0.000033 |

Result: PASS.

### Case B - Northern Midlatitude

Date: 2025-01-01

| Quantity | BQRC | NOAA | Absolute difference |
|---|---:|---:|---:|
| North X (nT) | 23117.824186 | 23117.8 | 0.024186 |
| East Y (nT) | 513.486977 | 513.5 | 0.013023 |
| Down Z (nT) | 40936.121381 | 40936.1 | 0.021381 |
| Horizontal H (nT) | 23123.526201 | 23123.5 | 0.026201 |
| Total F (nT) | 47015.566547 | 47015.6 | 0.033453 |
| Declination D (deg) | 1.272429 | 1.2724 | 0.000029 |
| Inclination I (deg) | 60.539263 | 60.5393 | 0.000037 |

Result: PASS.

### Case C - Western Longitude

Date: 2025-01-01

| Quantity | BQRC | NOAA | Absolute difference |
|---|---:|---:|---:|
| North X (nT) | 26093.192448 | 26093.2 | 0.007552 |
| East Y (nT) | -4383.594618 | -4383.6 | 0.005382 |
| Down Z (nT) | 28242.331549 | 28242.3 | 0.031549 |
| Horizontal H (nT) | 26458.847177 | 26458.8 | 0.047177 |
| Total F (nT) | 38700.127716 | 38700.1 | 0.027716 |
| Declination D (deg) | -9.536504 | -9.5365 | 0.000004 |
| Inclination I (deg) | 46.867418 | 46.8674 | 0.000018 |

Result: PASS.

### Case D - Southern Hemisphere

Date: 2025-01-01

| Quantity | BQRC | NOAA | Absolute difference |
|---|---:|---:|---:|
| North X (nT) | 23018.888572 | 23018.9 | 0.011428 |
| East Y (nT) | 3540.403448 | 3540.4 | 0.003448 |
| Down Z (nT) | -54359.225813 | -54359.2 | 0.025813 |
| Horizontal H (nT) | 23289.561775 | 23289.6 | 0.038225 |
| Total F (nT) | 59138.220456 | 59138.2 | 0.020456 |
| Declination D (deg) | 8.743818 | 8.7438 | 0.000018 |
| Inclination I (deg) | -66.807865 | -66.8079 | 0.000035 |

Result: PASS.

### Case E - Ahmedabad Region, Orbital Altitude

NOAA reference date: 2027-07-02

BQRC decimal epoch: 2027.5

Altitude: 400 km GPS

| Quantity | BQRC | NOAA | Absolute difference |
|---|---:|---:|---:|
| North X (nT) | 30050.410850 | 30050.4 | 0.010850 |
| East Y (nT) | 225.183799 | 225.2 | 0.016201 |
| Down Z (nT) | 21375.608643 | 21375.6 | 0.008643 |
| Horizontal H (nT) | 30051.254549 | 30051.2 | 0.054549 |
| Total F (nT) | 36878.103867 | 36878.1 | 0.003867 |
| Declination D (deg) | 0.429340 | 0.4293 | 0.000040 |
| Inclination I (deg) | 35.424434 | 35.4244 | 0.000034 |

Result: PASS under the epoch-mismatch comparison tolerances.

Important: NOAA's reference date is not exactly equivalent to decimal epoch 2027.5. This case is an approximate-epoch comparison, not an exact-epoch displayed-rounding validation.

## 5. Acceptance Criteria

### 5.1 Exact-Epoch Surface Comparisons

Cases A through D:

- Magnetic-field absolute difference: at most 0.05 nT.
- Angular absolute difference: at most 0.00005 degrees.

These values represent half of NOAA's final displayed decimal increment.

They are comparison thresholds for rounded output, not independently established scientific error tolerances.

### 5.2 Approximate-Epoch Orbital Comparison

Case E:

- Magnetic-field absolute difference: at most 0.2 nT.
- Angular absolute difference: at most 0.0002 degrees.

These wider thresholds accommodate the small difference between the NOAA reference date and the BQRC decimal epoch.

The thresholds are comparison criteria for this reference case, not a global IGRF-14 accuracy guarantee.

## 6. Automated Regression Tests

The repository contains two relevant scientific test modules:

1. `tests/scientific/test_igrf14_reference.py`
   - Five reference configurations.
   - North, East, and Down components.
   - Horizontal and total magnetic intensity.

2. `tests/scientific/test_igrf14_noaa_angles.py`
   - Five NOAA angular reference configurations.
   - Declination and inclination.
   - Separate tolerance for the orbital-altitude case.

Verification checkpoint:

- Full pytest suite: 202 passed.
- Ruff: all checks passed.
- mypy: no issues in 61 source files.

Note: The pre-existing magnetic-field reference tests use their own stored values and tolerances. They should not be interpreted as enforcing every acceptance criterion in this document.

## 7. Scientific Result

All five manually evaluated NOAA reference cases agree with the BQRC IGRF-14 implementation within their specified comparison thresholds.

The comparisons cover:

- Equatorial and midlatitude locations.
- Northern and Southern Hemispheres.
- Eastern and Western longitudes.
- Sea-level and orbital-altitude conditions.
- Base and predictive model epochs.

This provides independent numerical evidence supporting the implemented IGRF-14 field evaluation and temporal prediction for the selected cases.

## 8. Limitations

1. NOAA calculator values were transcribed from displayed results and are rounded.
2. Five selected cases do not establish global numerical accuracy.
3. The orbital-altitude case has a small reference epoch mismatch.
4. The comparisons do not validate spacecraft magnetic disturbances or sensor response.
5. External reference screenshots are not automatically reproduced by the test suite.
6. Further validation may be needed near geomagnetic poles, at additional altitudes, and across the complete model validity interval.
7. The NOAA calculator displays the model name IGRF2025, while BQRC uses the IGRF-14 coefficient dataset.

## 9. Evidence and Reproducibility

Reference provider:

NOAA / NCEI Geomagnetic Field Calculator

https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml

BQRC coefficient provenance:

`docs/verification/IGRF14_DATASET_PROVENANCE.md`

Automated regression tests:

`tests/scientific/test_igrf14_reference.py`

`tests/scientific/test_igrf14_noaa_angles.py`

The recorded values and configurations allow future comparisons against the same external calculator.

## 10. Next Verification Stage

Proceed to integration of the validated magnetic-field environment with the NV-center quantum magnetometer digital twin.

Integration testing must separately verify magnetic-field frame conventions, units, time handling, sensor orientation, and the distinction between the environmental field and measured sensor response.
