"""L4 field measurement product from a raw ODMR acquisition.

Wraps the classical estimator and the Poisson CRLB into the universal
``Measurement`` contract, with processing level, provenance, uncertainty
and quality flags.

Current honest limitations, reflected in the output:

* No calibration stage exists, so every product carries ``UNCALIBRATED``.
* The estimator assumes contrast, linewidth and zero-field splitting
  (passed explicitly). The reported CRLB assumes the same values are
  exactly known, so it is a lower bound that is optimistic when they
  are not.
"""

from __future__ import annotations

from math import isfinite

from bqrc.algorithms.odmr.field_estimator import estimate_nv_field_from_odmr
from bqrc.algorithms.odmr.field_uncertainty import analyze_nv_field_uncertainty
from bqrc.core.levels import ProcessingLevel
from bqrc.core.measurement import Measurement
from bqrc.core.quality import QualityFlag
from bqrc.core.uncertainty import Uncertainty, UncertaintyType
from bqrc.sensors.nv.acquisition import ODMRAcquisition

FIELD_QUANTITY = "nv_axis_field_magnitude"
ESTIMATOR_VERSION = "odmr-lorentzian-fixed-shape-0.1"


def estimate_field_measurement(
    acquisition: ODMRAcquisition,
    *,
    assumed_contrast: float,
    assumed_linewidth_mhz: float,
    assumed_zero_field_splitting_mhz: float,
) -> Measurement:
    """Estimate the unsigned NV-axis field magnitude as a ``Measurement``."""

    estimate = estimate_nv_field_from_odmr(
        measured=acquisition,
        contrast=assumed_contrast,
        linewidth_mhz=assumed_linewidth_mhz,
        zero_field_splitting_mhz=assumed_zero_field_splitting_mhz,
    )

    crlb = analyze_nv_field_uncertainty(
        frequencies_mhz=acquisition.frequencies_mhz,
        projected_field_magnitude_nt=estimate.projected_field_magnitude_nt,
        reference_photon_count=acquisition.reference_photon_count,
        contrast=assumed_contrast,
        linewidth_mhz=assumed_linewidth_mhz,
        zero_field_splitting_mhz=assumed_zero_field_splitting_mhz,
    )

    quality = QualityFlag.UNCALIBRATED

    if not estimate.fit_success or not crlb.identifiable_locally:
        quality |= QualityFlag.DEGRADED

    uncertainty = None

    if isfinite(crlb.crlb_std_nt):
        uncertainty = Uncertainty(
            value=crlb.crlb_std_nt,
            uncertainty_type=UncertaintyType.MODEL_ESTIMATE,
            method="Poisson CRLB, contrast/linewidth/D assumed exact",
        )

    return Measurement(
        quantity=FIELD_QUANTITY,
        value=estimate.projected_field_magnitude_nt,
        unit="nT",
        timestamp=acquisition.timestamp,
        source=acquisition.data_source,
        quality=quality,
        uncertainty=uncertainty,
        sensor_id=acquisition.sensor_id,
        level=ProcessingLevel.L4_ESTIMATED,
        configuration_id=acquisition.configuration_id,
        model_version=f"{acquisition.model_version}+{ESTIMATOR_VERSION}",
        metadata={
            "lower_mhz": estimate.lower_mhz,
            "upper_mhz": estimate.upper_mhz,
            "residual_rmse": estimate.residual_rmse,
            "fit_success": estimate.fit_success,
            "assumed_contrast": assumed_contrast,
            "assumed_linewidth_mhz": assumed_linewidth_mhz,
            "assumed_zero_field_splitting_mhz": assumed_zero_field_splitting_mhz,
        },
    )
