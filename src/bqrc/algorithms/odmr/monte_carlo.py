
"""Monte Carlo validation of NV-axis magnetic-field estimation.

Repeatedly simulate independent Poisson photon measurements,
estimate unsigned NV-axis magnetic-field magnitude, and compare
empirical estimation error with the theoretical Poisson CRLB.

The least-squares estimator is not assumed to attain the CRLB.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import numpy as np

from bqrc.algorithms.odmr.field_estimator import (
    estimate_nv_field_from_odmr,
)
from bqrc.algorithms.odmr.field_uncertainty import (
    analyze_nv_field_uncertainty,
)
from bqrc.algorithms.odmr.shot_noise import (
    simulate_photon_shot_noise,
)
from bqrc.algorithms.odmr.spectrum import simulate_odmr_spectrum
from bqrc.sensors.nv.resonance import (
    ZERO_FIELD_SPLITTING_MHZ,
    calculate_nv_resonance,
)


@dataclass(frozen=True, slots=True)
class NVMonteCarloResult:
    """Empirical field-estimation statistics and theoretical CRLB."""

    true_field_magnitude_nt: float
    estimated_fields_nt: tuple[float, ...]
    trial_count: int
    bias_nt: float
    empirical_std_nt: float
    rmse_nt: float
    theoretical_crlb_nt: float
    std_to_crlb_ratio: float
    all_fits_successful: bool


def run_nv_field_monte_carlo(
    frequencies_mhz: tuple[float, ...],
    true_field_magnitude_nt: float,
    reference_photon_count: float,
    trial_count: int = 20,
    seed: int = 42,
    contrast: float = 0.1,
    linewidth_mhz: float = 1.0,
    zero_field_splitting_mhz: float = ZERO_FIELD_SPLITTING_MHZ,
) -> NVMonteCarloResult:
    """Run reproducible Monte Carlo ODMR field-estimation trials.

    Assumes the magnetic field is aligned with the NV axis.
    The returned standard deviation uses the sample convention
    (ddof=1), while RMSE is relative to the known true field.

    The reference photon count applies independently at each
    frequency sample and in each simulated trial.
    """

    if (
        not isfinite(true_field_magnitude_nt)
        or true_field_magnitude_nt < 0.0
    ):
        raise ValueError(
            "true_field_magnitude_nt must be finite and nonnegative"
        )

    if not isinstance(trial_count, int) or isinstance(trial_count, bool):
        raise ValueError("trial_count must be an integer")

    if trial_count < 2:
        raise ValueError("at least two trials are required")

    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")

    if seed < 0:
        raise ValueError("seed must be nonnegative")

    # Validates the photon budget, contrast, linewidth and grid.
    uncertainty = analyze_nv_field_uncertainty(
        frequencies_mhz=frequencies_mhz,
        projected_field_magnitude_nt=true_field_magnitude_nt,
        reference_photon_count=reference_photon_count,
        contrast=contrast,
        linewidth_mhz=linewidth_mhz,
        zero_field_splitting_mhz=zero_field_splitting_mhz,
    )

    if contrast <= 0.0:
        raise ValueError("contrast must be positive for field fitting")

    if not (
        min(frequencies_mhz)
        < zero_field_splitting_mhz
        < max(frequencies_mhz)
    ):
        raise ValueError(
            "frequency grid must span the zero-field splitting"
        )

    if len(frequencies_mhz) < 5:
        raise ValueError("at least five frequency samples are required")

    resonance = calculate_nv_resonance(
        magnetic_field_nt=(true_field_magnitude_nt, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
        zero_field_splitting_mhz=zero_field_splitting_mhz,
    )

    ideal_spectrum = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=frequencies_mhz,
        contrast=contrast,
        linewidth_mhz=linewidth_mhz,
    )

    # A dedicated generator produces independent, reproducible
    # integer seeds for the photon-noise simulations.
    rng = np.random.default_rng(seed)

    estimated_fields: list[float] = []
    all_fits_successful = True

    for _ in range(trial_count):
        trial_seed = int(
            rng.integers(0, np.iinfo(np.int64).max)
        )

        measured = simulate_photon_shot_noise(
            spectrum=ideal_spectrum,
            reference_photon_count=reference_photon_count,
            seed=trial_seed,
        )

        estimate = estimate_nv_field_from_odmr(
            measured=measured,
            contrast=contrast,
            linewidth_mhz=linewidth_mhz,
            zero_field_splitting_mhz=zero_field_splitting_mhz,
        )

        if not estimate.fit_success:
            all_fits_successful = False

        estimated_fields.append(
            estimate.projected_field_magnitude_nt
        )

    estimates = np.asarray(estimated_fields, dtype=float)

    if not np.all(np.isfinite(estimates)):
        raise RuntimeError(
            "Monte Carlo field estimates must all be finite"
        )

    errors = estimates - true_field_magnitude_nt

    bias_nt = float(np.mean(errors))
    empirical_std_nt = float(np.std(estimates, ddof=1))
    rmse_nt = float(np.sqrt(np.mean(errors**2)))

    theoretical_crlb_nt = uncertainty.crlb_std_nt

    if theoretical_crlb_nt == float("inf"):
        std_to_crlb_ratio = float("nan")
    else:
        std_to_crlb_ratio = (
            empirical_std_nt / theoretical_crlb_nt
        )

    return NVMonteCarloResult(
        true_field_magnitude_nt=true_field_magnitude_nt,
        estimated_fields_nt=tuple(estimated_fields),
        trial_count=trial_count,
        bias_nt=bias_nt,
        empirical_std_nt=empirical_std_nt,
        rmse_nt=rmse_nt,
        theoretical_crlb_nt=theoretical_crlb_nt,
        std_to_crlb_ratio=std_to_crlb_ratio,
        all_fits_successful=all_fits_successful,
    )
