
"""Estimate NV-axis magnetic-field magnitude from ODMR fluorescence.

The estimator fits a symmetric two-Lorentzian model with fixed
zero-field splitting, contrast, and linewidth.

Because the resonance pair is unordered, the sign of the
projected magnetic field cannot be recovered from this model.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Protocol

import numpy as np
from scipy.optimize import least_squares

from bqrc.core.constants import (
    ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T,
    NANOTESLA_PER_TESLA,
    ZERO_FIELD_SPLITTING_MHZ,
)


class MeasuredODMR(Protocol):
    """Anything exposing a measured ODMR spectrum.

    Satisfied by ``NoisyODMRSpectrum`` and by ``ODMRAcquisition``. The
    estimator deliberately sees only frequencies and normalized
    fluorescence, never the ideal spectrum or any truth value.
    """

    @property
    def frequencies_mhz(self) -> tuple[float, ...]: ...

    @property
    def fluorescence(self) -> tuple[float, ...]: ...


@dataclass(frozen=True, slots=True)
class NVFieldEstimate:
    """Fitted ODMR resonances and unsigned NV-axis field projection."""

    lower_mhz: float
    upper_mhz: float
    projected_field_magnitude_nt: float
    residual_rmse: float
    fit_success: bool


def estimate_nv_field_from_odmr(
    measured: MeasuredODMR,
    contrast: float = 0.1,
    linewidth_mhz: float = 1.0,
    zero_field_splitting_mhz: float = ZERO_FIELD_SPLITTING_MHZ,
) -> NVFieldEstimate:
    """Fit the ODMR splitting and infer NV-axis field magnitude.

    Assumes known contrast, linewidth, and zero-field splitting.
    Requires frequency samples on both sides of the splitting center.
    """

    frequencies = np.asarray(measured.frequencies_mhz, dtype=float)
    fluorescence = np.asarray(measured.fluorescence, dtype=float)

    if frequencies.ndim != 1 or len(frequencies) < 5:
        raise ValueError("at least five frequency samples are required")

    if fluorescence.shape != frequencies.shape:
        raise ValueError("frequency and fluorescence arrays must match")

    if not np.all(np.isfinite(frequencies)):
        raise ValueError("frequencies must be finite")

    if not np.all(np.isfinite(fluorescence)):
        raise ValueError("fluorescence must be finite")

    if np.any(fluorescence < 0.0):
        raise ValueError("fluorescence must be nonnegative")

    if not isfinite(contrast) or not 0.0 < contrast <= 0.5:
        raise ValueError("contrast must be finite and within (0, 0.5]")

    if not isfinite(linewidth_mhz) or linewidth_mhz <= 0.0:
        raise ValueError("linewidth_mhz must be finite and positive")

    if (
        not isfinite(zero_field_splitting_mhz)
        or zero_field_splitting_mhz <= 0.0
    ):
        raise ValueError(
            "zero_field_splitting_mhz must be finite and positive"
        )

    if not (
        np.min(frequencies) < zero_field_splitting_mhz
        < np.max(frequencies)
    ):
        raise ValueError(
            "frequency grid must span the zero-field splitting"
        )

    half_width = linewidth_mhz / 2.0

    def model(splitting_mhz: float) -> np.ndarray:
        lower = zero_field_splitting_mhz - splitting_mhz
        upper = zero_field_splitting_mhz + splitting_mhz

        lower_dip = 1.0 / (
            1.0 + ((frequencies - lower) / half_width) ** 2
        )
        upper_dip = 1.0 / (
            1.0 + ((frequencies - upper) / half_width) ** 2
        )

        return 1.0 - contrast * (lower_dip + upper_dip)

    max_splitting = float(
        max(
            zero_field_splitting_mhz - np.min(frequencies),
            np.max(frequencies) - zero_field_splitting_mhz,
        )
    )

    if max_splitting <= 0.0:
        raise ValueError("frequency grid has insufficient span")

    def residual(parameters: np.ndarray) -> np.ndarray:
        return model(float(parameters[0])) - fluorescence

    # Multi-start fitting reduces sensitivity to local minima.
    initial_guesses = np.linspace(
        0.0,
        max_splitting,
        num=15,
    )

    best_result = None
    best_cost = float("inf")

    for initial in initial_guesses:
        result = least_squares(
            residual,
            x0=np.array([float(initial)]),
            bounds=(0.0, max_splitting),
            max_nfev=2000,
        )

        if result.cost < best_cost:
            best_cost = float(result.cost)
            best_result = result

    if best_result is None:
        raise RuntimeError("ODMR fitting failed")

    splitting = float(best_result.x[0])

    lower_mhz = zero_field_splitting_mhz - splitting
    upper_mhz = zero_field_splitting_mhz + splitting

    field_magnitude_nt = (
        splitting
        * NANOTESLA_PER_TESLA
        / ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T
    )

    fitted = model(splitting)
    residual_rmse = float(
        np.sqrt(np.mean((fitted - fluorescence) ** 2))
    )

    return NVFieldEstimate(
        lower_mhz=lower_mhz,
        upper_mhz=upper_mhz,
        projected_field_magnitude_nt=field_magnitude_nt,
        residual_rmse=residual_rmse,
        fit_success=bool(best_result.success),
    )
