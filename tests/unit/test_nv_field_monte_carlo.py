
"""Tests for Monte Carlo NV magnetic-field estimation."""

from __future__ import annotations

from math import isclose, isfinite, isnan, sqrt
from statistics import mean, stdev

import numpy as np
import pytest

from bqrc.algorithms.odmr.monte_carlo import (
    run_nv_field_monte_carlo,
)


@pytest.fixture(scope="module")
def frequency_grid() -> tuple[float, ...]:
    """Resolve both ODMR resonances around 2870 MHz."""
    return tuple(np.linspace(2867.0, 2873.0, 61))


def test_reproducible_monte_carlo(
    frequency_grid: tuple[float, ...],
) -> None:
    kwargs = dict(
        frequencies_mhz=frequency_grid,
        true_field_magnitude_nt=50_000.0,
        reference_photon_count=100_000.0,
        trial_count=3,
        seed=123,
    )

    first = run_nv_field_monte_carlo(**kwargs)
    second = run_nv_field_monte_carlo(**kwargs)

    assert first == second
    assert first.trial_count == 3
    assert len(first.estimated_fields_nt) == 3


def test_empirical_statistics_are_consistent(
    frequency_grid: tuple[float, ...],
) -> None:
    result = run_nv_field_monte_carlo(
        frequencies_mhz=frequency_grid,
        true_field_magnitude_nt=50_000.0,
        reference_photon_count=100_000.0,
        trial_count=4,
        seed=321,
    )

    estimates = result.estimated_fields_nt
    errors = [value - result.true_field_magnitude_nt for value in estimates]

    expected_bias = mean(errors)
    expected_std = stdev(estimates)
    expected_rmse = sqrt(mean(error**2 for error in errors))

    assert isclose(result.bias_nt, expected_bias, rel_tol=1e-10, abs_tol=1e-8)
    assert isclose(
        result.empirical_std_nt,
        expected_std,
        rel_tol=1e-10,
        abs_tol=1e-8,
    )
    assert isclose(result.rmse_nt, expected_rmse, rel_tol=1e-10, abs_tol=1e-8)


def test_finite_uncertainty_for_nonzero_field(
    frequency_grid: tuple[float, ...],
) -> None:
    result = run_nv_field_monte_carlo(
        frequencies_mhz=frequency_grid,
        true_field_magnitude_nt=50_000.0,
        reference_photon_count=100_000.0,
        trial_count=3,
        seed=17,
    )

    assert isfinite(result.theoretical_crlb_nt)
    assert result.theoretical_crlb_nt > 0.0
    assert isfinite(result.std_to_crlb_ratio)
    assert result.std_to_crlb_ratio >= 0.0
    assert all(isfinite(value) for value in result.estimated_fields_nt)


def test_zero_field_crlb_is_infinite(
    frequency_grid: tuple[float, ...],
) -> None:
    result = run_nv_field_monte_carlo(
        frequencies_mhz=frequency_grid,
        true_field_magnitude_nt=0.0,
        reference_photon_count=100_000.0,
        trial_count=2,
        seed=55,
    )

    assert result.theoretical_crlb_nt == float("inf")
    assert isnan(result.std_to_crlb_ratio)


def test_theoretical_crlb_improves_with_photons(
    frequency_grid: tuple[float, ...],
) -> None:
    low = run_nv_field_monte_carlo(
        frequencies_mhz=frequency_grid,
        true_field_magnitude_nt=50_000.0,
        reference_photon_count=10_000.0,
        trial_count=2,
        seed=7,
    )
    high = run_nv_field_monte_carlo(
        frequencies_mhz=frequency_grid,
        true_field_magnitude_nt=50_000.0,
        reference_photon_count=1_000_000.0,
        trial_count=2,
        seed=7,
    )

    assert isclose(
        low.theoretical_crlb_nt / high.theoretical_crlb_nt,
        10.0,
        rel_tol=1e-10,
    )


@pytest.mark.parametrize("trial_count", [0, 1, -1, 2.5, True])
def test_invalid_trial_count(
    frequency_grid: tuple[float, ...],
    trial_count: int,
) -> None:
    with pytest.raises(ValueError):
        run_nv_field_monte_carlo(
            frequencies_mhz=frequency_grid,
            true_field_magnitude_nt=50_000.0,
            reference_photon_count=100_000.0,
            trial_count=trial_count,
        )


@pytest.mark.parametrize("seed", [-1, 1.5, True])
def test_invalid_seed(
    frequency_grid: tuple[float, ...],
    seed: int,
) -> None:
    with pytest.raises(ValueError):
        run_nv_field_monte_carlo(
            frequencies_mhz=frequency_grid,
            true_field_magnitude_nt=50_000.0,
            reference_photon_count=100_000.0,
            trial_count=2,
            seed=seed,
        )


@pytest.mark.parametrize("field_nt", [-1.0, float("nan"), float("inf")])
def test_invalid_true_field(
    frequency_grid: tuple[float, ...],
    field_nt: float,
) -> None:
    with pytest.raises(ValueError):
        run_nv_field_monte_carlo(
            frequencies_mhz=frequency_grid,
            true_field_magnitude_nt=field_nt,
            reference_photon_count=100_000.0,
            trial_count=2,
        )


def test_rejects_zero_contrast(
    frequency_grid: tuple[float, ...],
) -> None:
    with pytest.raises(ValueError, match="contrast"):
        run_nv_field_monte_carlo(
            frequencies_mhz=frequency_grid,
            true_field_magnitude_nt=50_000.0,
            reference_photon_count=100_000.0,
            trial_count=2,
            contrast=0.0,
        )


def test_rejects_insufficient_frequency_samples() -> None:
    with pytest.raises(ValueError, match="five"):
        run_nv_field_monte_carlo(
            frequencies_mhz=(2869.0, 2870.0, 2871.0),
            true_field_magnitude_nt=50_000.0,
            reference_photon_count=100_000.0,
            trial_count=2,
        )


def test_rejects_grid_not_spanning_center() -> None:
    with pytest.raises(ValueError, match="span"):
        run_nv_field_monte_carlo(
            frequencies_mhz=(2871.0, 2871.5, 2872.0, 2872.5, 2873.0),
            true_field_magnitude_nt=50_000.0,
            reference_photon_count=100_000.0,
            trial_count=2,
        )
