
"""Scientific validation tests for ODMR magnetic-field estimation."""

from __future__ import annotations

from math import isclose

import numpy as np
import pytest

from bqrc.algorithms.odmr.field_estimator import (
    estimate_nv_field_from_odmr,
)
from bqrc.algorithms.odmr.shot_noise import (
    NoisyODMRSpectrum,
    simulate_photon_shot_noise,
)
from bqrc.algorithms.odmr.spectrum import simulate_odmr_spectrum
from bqrc.sensors.nv.resonance import calculate_nv_resonance


def make_measurement(
    field_nt: float,
    photon_count: float = 1_000_000.0,
    seed: int = 42,
) -> NoisyODMRSpectrum:
    """Generate a shot-noise-limited ODMR measurement."""

    resonance = calculate_nv_resonance(
        magnetic_field_nt=(field_nt, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )

    frequencies = tuple(np.linspace(2865.0, 2875.0, 401))

    ideal = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=frequencies,
        contrast=0.1,
        linewidth_mhz=1.0,
    )

    return simulate_photon_shot_noise(
        spectrum=ideal,
        reference_photon_count=photon_count,
        seed=seed,
    )


def test_noiseless_recovery() -> None:
    """Fit an exact synthetic spectrum with no photon noise."""

    field_nt = 50_000.0

    resonance = calculate_nv_resonance(
        magnetic_field_nt=(field_nt, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )

    frequencies = tuple(np.linspace(2865.0, 2875.0, 401))

    ideal = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=frequencies,
        contrast=0.1,
        linewidth_mhz=1.0,
    )

    measurement = NoisyODMRSpectrum(
        frequencies_mhz=ideal.frequencies_mhz,
        photon_counts=tuple(0 for _ in frequencies),
        fluorescence=ideal.fluorescence,
        reference_photon_count=1.0,
    )

    estimate = estimate_nv_field_from_odmr(measurement)

    assert estimate.fit_success
    assert isclose(
        estimate.projected_field_magnitude_nt,
        field_nt,
        rel_tol=1e-4,
    )
    assert estimate.residual_rmse < 1e-6


def test_noisy_field_recovery() -> None:
    """Recover a known field from reproducible photon shot noise."""

    field_nt = 50_000.0
    measurement = make_measurement(field_nt)

    estimate = estimate_nv_field_from_odmr(measurement)

    assert estimate.fit_success
    assert abs(
        estimate.projected_field_magnitude_nt - field_nt
    ) < 3_000.0
    assert estimate.residual_rmse > 0.0


def test_negative_field_has_same_estimated_magnitude() -> None:
    """The symmetric ODMR model cannot recover projection sign."""

    positive = estimate_nv_field_from_odmr(
        make_measurement(50_000.0, seed=123)
    )
    negative = estimate_nv_field_from_odmr(
        make_measurement(-50_000.0, seed=123)
    )

    assert positive.fit_success
    assert negative.fit_success

    assert isclose(
        positive.projected_field_magnitude_nt,
        negative.projected_field_magnitude_nt,
        rel_tol=1e-8,
    )


@pytest.mark.parametrize(
    "field_nt",
    [10_000.0, 30_000.0, 50_000.0, 80_000.0],
)
def test_multiple_field_magnitudes(field_nt: float) -> None:
    """Recover different field magnitudes under high photon counts."""

    estimate = estimate_nv_field_from_odmr(
        make_measurement(
            field_nt,
            photon_count=10_000_000.0,
            seed=7,
        )
    )

    assert estimate.fit_success
    assert abs(
        estimate.projected_field_magnitude_nt - field_nt
    ) < 2_000.0


@pytest.mark.parametrize(
    "contrast, linewidth",
    [
        (0.0, 1.0),
        (-0.1, 1.0),
        (0.6, 1.0),
        (0.1, 0.0),
        (0.1, -1.0),
    ],
)
def test_invalid_model_parameters(
    contrast: float,
    linewidth: float,
) -> None:
    """Reject nonphysical model parameters."""

    measurement = make_measurement(50_000.0)

    with pytest.raises(ValueError):
        estimate_nv_field_from_odmr(
            measurement,
            contrast=contrast,
            linewidth_mhz=linewidth,
        )


def test_insufficient_frequency_samples() -> None:
    """Reject spectra with fewer than five frequency samples."""

    measurement = NoisyODMRSpectrum(
        frequencies_mhz=(2869.0, 2870.0, 2871.0),
        photon_counts=(1, 1, 1),
        fluorescence=(1.0, 1.0, 1.0),
        reference_photon_count=1.0,
    )

    with pytest.raises(ValueError, match="five"):
        estimate_nv_field_from_odmr(measurement)


def test_frequency_grid_must_span_center() -> None:
    """Reject grids that do not span the zero-field splitting."""

    measurement = NoisyODMRSpectrum(
        frequencies_mhz=(2871.0, 2872.0, 2873.0, 2874.0, 2875.0),
        photon_counts=(1, 1, 1, 1, 1),
        fluorescence=(1.0, 1.0, 1.0, 1.0, 1.0),
        reference_photon_count=1.0,
    )

    with pytest.raises(ValueError, match="span"):
        estimate_nv_field_from_odmr(measurement)

