# IGRF-14 External Reference Validation — V1

## 1. Purpose

Document an independent numerical comparison between the BQRC IGRF-14 magnetic-field implementation and the NOAA Geomagnetic Field Calculator.

## 2. Reference Configuration

| Parameter | Value |
|---|---|
| Reference provider | NOAA / NCEI Geomagnetic Field Calculator |
| Calculator model displayed | IGRF2025 |
| BQRC model | IGRF-14 |
| Date | 2025-01-01 |
| Decimal epoch | 2025.0 |
| Geodetic latitude | 0.0° |
| Longitude | 0.0° |
| Elevation | 0.0 km GPS |
| Magnetic component frame | Geodetic North-East-Down |
| Magnetic-field units | Nanotesla |

## 3. Numerical Comparison

| Quantity | BQRC | NOAA displayed | Absolute difference |
|---|---:|---:|---:|
| North X (nT) | 27456.621763 | 27456.6 | 0.021763 |
| East Y (nT) | -1926.548583 | -1926.5 | 0.048583 |
| Down Z (nT) | -15997.352904 | -15997.4 | 0.047096 |
| Horizontal H (nT) | 27524.128834 | 27524.1 | 0.028834 |
| Total F (nT) | 31835.404317 | 31835.4 | 0.004317 |
| Declination D (degrees) | -4.013694 | -4.0137 | 0.000006 |
| Inclination I (degrees) | -30.165667 | -30.1657 | 0.000033 |

## 4. Acceptance Criteria

For this displayed-precision comparison:

- Magnetic-field component differences must not exceed 0.05 nT.
- Angular differences must not exceed 0.00005 degrees.

These thresholds correspond to half of the final displayed decimal increment in the NOAA results. They are comparison thresholds for rounded output, not independently established scientific error tolerances.

## 5. Result

**PASS — Greenwich reference case.**

All seven compared quantities satisfy the displayed-precision acceptance criteria.

## 6. Limitations

1. NOAA's displayed values are rounded.
2. This comparison covers one location and one epoch.
3. It does not establish global, orbital-altitude, or multi-epoch accuracy.
4. Additional independent reference cases are required.
5. The NOAA calculator labels its selected model IGRF2025; the BQRC implementation uses IGRF-14 coefficients.

## 7. Evidence

Reference: NOAA / NCEI Geomagnetic Field Calculator.

https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml

The comparison was performed using the calculator's displayed results for 2025-01-01, 0° N, 0° E, and 0 km GPS elevation.

## 8. Next Verification Stage

Extend independent validation to multiple latitudes, longitudes, altitudes, and predictive epochs before treating the IGRF-14 implementation as fully scientifically validated.