
"""Scientific tests for NV magnetic-field Fisher information."""

from __future__ import annotations

from math import inf, isclose, isfinite, sqrt

import numpy as np
import pytest

from bqrc.algorithms.odmr.field_uncertainty import (
    analyze_nv_field_uncertainty,
)
from bqrc.sensors.nv.resonance import (
    ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T,
    NANOTESLA_PER_TESLA,
    ZERO_FIELD_SPLITTING_MHZ,
)


@pytest.fixture
def frequency_grid() -> tuple[float, ...]:
    """Frequency grid resolving both ODMR dips."""
    return tuple(np.linspace(2865.0, 2875.0, 401))


def test_positive_information_and_finite_crlb(
    frequency_grid: tuple[float, ...],
) -> None:
    result = analyze_nv_field_uncertainty(
        frequencies_mhz=frequency_grid,
        projected_field_magnitude_nt=50_000.0,
        reference_photon_count=1_000_000.0,
    )

    assert result.identifiable_locally
    assert result.fisher_information_per_nt_squared > 0.0
    assert isfinite(result.crlb_std_nt)
    assert result.crlb_std_nt > 0.0


def test_zero_field_has_no_first_order_information(
    frequency_grid: tuple[float, ...],
) -> None:
    result = analyze_nv_field_uncertainty(
        frequencies_mhz=frequency_grid,
        projected_field_magnitude_nt=0.0,
        reference_photon_count=1_000_000.0,
    )

    assert not result.identifiable_locally
    assert result.fisher_information_per_nt_squared == 0.0
    assert result.crlb_std_nt == inf


def test_zero_contrast_has_no_information(
    frequency_grid: tuple[float, ...],
) -> None:
    result = analyze_nv_field_uncertainty(
        frequencies_mhz=frequency_grid,
        projected_field_magnitude_nt=50_000.0,
        reference_photon_count=1_000_000.0,
        contrast=0.0,
    )

    assert not result.identifiable_locally
    assert result.crlb_std_nt == inf


def test_photon_count_scaling(
    frequency_grid: tuple[float, ...],
) -> None:
    low = analyze_nv_field_uncertainty(
        frequencies_mhz=frequency_grid,
        projected_field_magnitude_nt=50_000.0,
        reference_photon_count=100.0,
    )
    high = analyze_nv_field_uncertainty(
        frequencies_mhz=frequency_grid,
        projected_field_magnitude_nt=50_000.0,
        reference_photon_count=10_000.0,
    )

    assert isclose(
        high.fisher_information_per_nt_squared
        / low.fisher_information_per_nt_squared,
        100.0,
        rel_tol=1e-10,
    )
    assert isclose(
        low.crlb_std_nt / high.crlb_std_nt,
        10.0,
        rel_tol=1e-10,
    )


def test_crlb_matches_inverse_fisher_information(
    frequency_grid: tuple[float, ...],
) -> None:
    result = analyze_nv_field_uncertainty(
        frequencies_mhz=frequency_grid,
        projected_field_magnitude_nt=50_000.0,
        reference_photon_count=1_000_000.0,
    )

    assert isclose(
        result.crlb_std_nt,
        1.0 / sqrt(result.fisher_information_per_nt_squared),
        rel_tol=1e-12,
    )


def test_information_matches_finite_difference(
    frequency_grid: tuple[float, ...],
) -> None:
    """Compare analytical derivative against numerical differentiation."""

    field_nt = 50_000.0
    reference_count = 1_000_000.0
    contrast = 0.1
    linewidth_mhz = 1.0
    delta_nt = 1.0

    gamma = (
        ELECTRON_GYROMAGNETIC_RATIO_MHZ_PER_T
        / NANOTESLA_PER_TESLA
    )

    frequencies = np.asarray(frequency_grid)

    def model(field: float) -> np.ndarray:
        shift = gamma * field
        half_width = linewidth_mhz / 2.0

        lower = ZERO_FIELD_SPLITTING_MHZ - shift
        upper = ZERO_FIELD_SPLITTING_MHZ + shift

        lower_dip = 1.0 / (
            1.0 + ((frequencies - lower) / half_width) ** 2
        )
        upper_dip = 1.0 / (
            1.0 + ((frequencies - upper) / half_width) ** 2
        )

        return 1.0 - contrast * (lower_dip + upper_dip)

    fluorescence = model(field_nt)

    numerical_derivative = (
        model(field_nt + delta_nt) - model(field_nt - delta_nt)
    ) / (2.0 * delta_nt)

    numerical_information = float(
        reference_count
        * np.sum(numerical_derivative**2 / fluorescence)
    )

    analytical = analyze_nv_field_uncertainty(
        frequencies_mhz=frequency_grid,
        projected_field_magnitude_nt=field_nt,
        reference_photon_count=reference_count,
    )

    assert isclose(
        analytical.fisher_information_per_nt_squared,
        numerical_information,
        rel_tol=1e-6,
    )


@pytest.mark.parametrize(
    "field_nt",
    [-1.0, float("nan"), float("inf")],
)
def test_invalid_field(field_nt: float) -> None:
    with pytest.raises(ValueError):
        analyze_nv_field_uncertainty(
            frequencies_mhz=(2869.0, 2870.0, 2871.0),
            projected_field_magnitude_nt=field_nt,
            reference_photon_count=1_000.0,
        )


@pytest.mark.parametrize(
    "photon_count",
    [0.0, -1.0, float("nan"), float("inf")],
)
def test_invalid_photon_count(photon_count: float) -> None:
    with pytest.raises(ValueError):
        analyze_nv_field_uncertainty(
            frequencies_mhz=(2869.0, 2870.0, 2871.0),
            projected_field_magnitude_nt=50_000.0,
            reference_photon_count=photon_count,
        )


@pytest.mark.parametrize(
    "contrast",
    [-0.1, 0.6, float("nan"), float("inf")],
)
def test_invalid_contrast(contrast: float) -> None:
    with pytest.raises(ValueError):
        analyze_nv_field_uncertainty(
            frequencies_mhz=(2869.0, 2870.0, 2871.0),
            projected_field_magnitude_nt=50_000.0,
            reference_photon_count=1_000.0,
            contrast=contrast,
        )


@pytest.mark.parametrize(
    "linewidth",
    [0.0, -1.0, float("nan"), float("inf")],
)
def test_invalid_linewidth(linewidth: float) -> None:
    with pytest.raises(ValueError):
        analyze_nv_field_uncertainty(
            frequencies_mhz=(2869.0, 2870.0, 2871.0),
            projected_field_magnitude_nt=50_000.0,
            reference_photon_count=1_000.0,
            linewidth_mhz=linewidth,
        )


def test_empty_frequency_grid() -> None:
    with pytest.raises(ValueError):
        analyze_nv_field_uncertainty(
            frequencies_mhz=(),
            projected_field_magnitude_nt=50_000.0,
            reference_photon_count=1_000.0,
        )


def test_nonfinite_frequency_grid() -> None:
    with pytest.raises(ValueError):
        analyze_nv_field_uncertainty(
            frequencies_mhz=(2869.0, float("nan"), 2871.0),
            projected_field_magnitude_nt=50_000.0,
            reference_photon_count=1_000.0,
        )
