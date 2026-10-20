
"""Poisson Fisher information for NV-axis field-magnitude estimation.

The model assumes independent photon counts, a known noise-free
reference photon count, fixed ODMR contrast and linewidth, and
known zero-field splitting.

Results describe local theoretical estimation limits, not
empirical confidence intervals or sensitivity per sqrt(Hz).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf, isfinite, sqrt

from bqrc.sensors.nv.resonance import (
    ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T,
    NANOTESLA_PER_TESLA,
    ZERO_FIELD_SPLITTING_MHZ,
)


@dataclass(frozen=True, slots=True)
class NVFieldUncertainty:
    """Local theoretical uncertainty for unsigned NV-axis field."""

    fisher_information_per_nt_squared: float
    crlb_std_nt: float
    identifiable_locally: bool


def analyze_nv_field_uncertainty(
    frequencies_mhz: tuple[float, ...],
    projected_field_magnitude_nt: float,
    reference_photon_count: float,
    contrast: float = 0.1,
    linewidth_mhz: float = 1.0,
    zero_field_splitting_mhz: float = ZERO_FIELD_SPLITTING_MHZ,
) -> NVFieldUncertainty:
    """Calculate the Poisson CRLB for a fixed-parameter ODMR model."""

    if not frequencies_mhz:
        raise ValueError("frequencies_mhz must not be empty")

    if not all(isfinite(value) for value in frequencies_mhz):
        raise ValueError("frequency samples must be finite")

    if (
        not isfinite(projected_field_magnitude_nt)
        or projected_field_magnitude_nt < 0.0
    ):
        raise ValueError(
            "projected_field_magnitude_nt must be finite and nonnegative"
        )

    if (
        not isfinite(reference_photon_count)
        or reference_photon_count <= 0.0
    ):
        raise ValueError(
            "reference_photon_count must be finite and positive"
        )

    if not isfinite(contrast) or not 0.0 <= contrast <= 0.5:
        raise ValueError("contrast must be finite and within [0, 0.5]")

    if not isfinite(linewidth_mhz) or linewidth_mhz <= 0.0:
        raise ValueError("linewidth_mhz must be finite and positive")

    if (
        not isfinite(zero_field_splitting_mhz)
        or zero_field_splitting_mhz <= 0.0
    ):
        raise ValueError(
            "zero_field_splitting_mhz must be finite and positive"
        )

    gamma_mhz_per_nt = (
        ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T
        / NANOTESLA_PER_TESLA
    )

    splitting_mhz = gamma_mhz_per_nt * projected_field_magnitude_nt

    if not isfinite(splitting_mhz):
        raise ValueError("field produces nonfinite resonance splitting")

    lower_mhz = zero_field_splitting_mhz - splitting_mhz
    upper_mhz = zero_field_splitting_mhz + splitting_mhz

    half_width = linewidth_mhz / 2.0

    fisher_information = 0.0

    for frequency_mhz in frequencies_mhz:
        lower_offset = (frequency_mhz - lower_mhz) / half_width
        upper_offset = (frequency_mhz - upper_mhz) / half_width

        lower_lorentzian = 1.0 / (1.0 + lower_offset**2)
        upper_lorentzian = 1.0 / (1.0 + upper_offset**2)

        fluorescence = (
            1.0 - contrast * (lower_lorentzian + upper_lorentzian)
        )

        # dL/d(center) = 2*x / (half_width * (1+x**2)**2)
        lower_center_derivative = (
            2.0 * lower_offset
            / (half_width * (1.0 + lower_offset**2) ** 2)
        )
        upper_center_derivative = (
            2.0 * upper_offset
            / (half_width * (1.0 + upper_offset**2) ** 2)
        )

        fluorescence_derivative = (
            contrast
            * gamma_mhz_per_nt
            * (lower_center_derivative - upper_center_derivative)
        )

        if fluorescence <= 0.0:
            if fluorescence < 0.0:
                raise ValueError("model fluorescence became negative")

            if fluorescence_derivative != 0.0:
                raise ValueError(
                    "zero expected fluorescence with nonzero derivative"
                )

            continue

        fisher_information += (
            reference_photon_count
            * fluorescence_derivative**2
            / fluorescence
        )

    if fisher_information <= 0.0:
        return NVFieldUncertainty(
            fisher_information_per_nt_squared=0.0,
            crlb_std_nt=inf,
            identifiable_locally=False,
        )

    return NVFieldUncertainty(
        fisher_information_per_nt_squared=fisher_information,
        crlb_std_nt=1.0 / sqrt(fisher_information),
        identifiable_locally=True,
    )
