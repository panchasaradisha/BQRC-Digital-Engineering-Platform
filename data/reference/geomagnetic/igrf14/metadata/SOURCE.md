# IGRF-14 Coefficient Dataset Metadata

## Dataset Identity

Model Family: International Geomagnetic Reference Field
Model Generation: IGRF-14
Dataset Type: Spherical-harmonic Gauss coefficients
Original Filename: igrf14coeffs.txt
BQRC Status: Authoritative Raw Reference Dataset

## Source

Maintaining Organization: International Association of Geomagnetism and Aeronomy (IAGA)
Distribution Source: NOAA National Centers for Environmental Information (NCEI)

Source URL:
https://www.ngdc.noaa.gov/IAGA/vmod/coeffs/igrf14coeffs.txt

IGRF Information Page:
https://www.ncei.noaa.gov/products/international-geomagnetic-reference-field

Retrieved UTC:
2026-09-20T13:38:05Z

## Integrity

Hash Algorithm: SHA-256
SHA-256:
8f8d88403028fc4ee92c4f38d97b46e0a87e2cfc496045b43c9e26c1d6b0903c

File Size Bytes:
42411

## Scientific Characteristics

Main-Field Maximum Degree: 13
Predictive Secular-Variation Maximum Degree: 8
Latest Main-Field Epoch: 2025.0
Predictive Secular-Variation Interval: 2025.0-2030.0

Main-Field Coefficient Unit:
nanotesla (nT)

Secular-Variation Coefficient Unit:
nanotesla per year (nT/year)

Coefficient Normalization:
Schmidt semi-normalized

Magnetic Reference Radius:
6371.2 km

## BQRC Data Handling Policy

The file stored under:

data/reference/geomagnetic/igrf14/raw/

is treated as immutable authoritative source data.

BQRC software must not modify this raw file.

Any transformation, extraction, normalization, conversion, or derived dataset must be written to:

data/reference/geomagnetic/igrf14/processed/

Processing software must preserve provenance linking the derived data back to this raw dataset and checksum.

## Model Validity Policy

IGRF-14 provides the current model generation through 2030.0 using the predictive secular-variation model.

BQRC must not silently extrapolate the predictive model beyond its supported interval.

Simulations outside the supported interval require either:

1. an authoritative model covering the requested epoch, or
2. an explicitly labelled research extrapolation mode.

## Intended BQRC Use

This dataset will provide coefficients for the BQRC Geomagnetic Environment V1 model.

The resulting magnetic field represents the Earth main-field reference component.

It must remain separate from:

- spacecraft-generated magnetic fields,
- BAS local magnetic interference,
- electrical-system interference,
- crustal anomalies not represented by the selected model,
- ionospheric and magnetospheric disturbances,
- space-weather disturbances,
- NV sensor noise,
- optical-system noise,
- microwave-system errors,
- electronics and ADC errors.

## Traceability

Authoritative Dataset
        ↓
SHA-256 Integrity Record
        ↓
BQRC Coefficient Parser
        ↓
IGRF Mathematical Model
        ↓
Reference Magnetic Field
        ↓
Verification Against Independent Reference Outputs
        ↓
Scientific Regression Tests
        ↓
NV Magnetometer Truth Input
