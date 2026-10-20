# BQRC IGRF-14 Coefficient Dataset Provenance

## Dataset Identity

Dataset: IGRF-14 spherical-harmonic coefficients

Model: International Geomagnetic Reference Field, 14th Generation

Maintaining Organization: International Association of Geomagnetism and Aeronomy (IAGA)

## Source

Official NOAA-hosted IGRF coefficient file:

https://www.ngdc.noaa.gov/IAGA/vmod/coeffs/igrf14coeffs.txt

Local Dataset:

data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt

## Dataset Integrity

File Size: 42411 bytes

SHA-256:

8F8D88403028FC4EE92C4F38D97B46E0A87E2CFC496045B43C9E26C1D6B0903C

This checksum was calculated from the locally downloaded file.

Independent checksum verification against an authoritative published digest remains pending.

## Coefficient Conventions

Coefficient normalization:

Schmidt semi-normalized spherical harmonics.

Main-field coefficient units:

nanotesla (nT).

Secular variation coefficient units:

nanotesla per year (nT/year).

Maximum main-field spherical-harmonic degree:

13.

Predictive secular variation degree:

8.

## Initial BQRC Simulation Interval

Initial verification interval:

2025.0 through 2030.0.

Initial test date:

2027-07-18.

Dates outside the supported predictive interval require explicit model-validity handling.

## Scientific Verification Status

Completed:

- Official NOAA-hosted file downloaded.
- Dataset structure inspected.
- Local file size recorded.
- Local SHA-256 fingerprint recorded.
- Model generation identified.
- Coefficient normalization identified.

Pending:

- Independent coefficient integrity comparison.
- Coefficient parser implementation.
- Epoch interpolation.
- Secular variation calculation.
- Spherical-harmonic magnetic-field evaluation.
- Coordinate transformation verification.
- Comparison against authoritative reference outputs.

## Scientific Integrity Rule

The coefficient dataset must remain unchanged.

No coefficient may be fabricated or silently modified.

The BQRC geomagnetic model must preserve source provenance, physical units, model epoch, and reference-frame conventions.

## Dataset Consolidation Verification

The existing canonical dataset and the newly downloaded
NOAA-hosted IGRF-14 coefficient file were compared using SHA-256.

Both files produced the same checksum:

8F8D88403028FC4EE92C4F38D97B46E0A87E2CFC496045B43C9E26C1D6B0903C

The existing dataset was retained at:

data/reference/geomagnetic/igrf14/raw/igrf14coeffs.txt

The redundant top-level copy was removed.

The existing IGRF implementation passed 26 selected unit,
scientific-reference, and orbit-integration tests.