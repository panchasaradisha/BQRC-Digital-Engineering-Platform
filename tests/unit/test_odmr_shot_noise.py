
"""Unit tests for ODMR photon shot-noise simulation."""

from math import isfinite

import numpy as np
import pytest

from bqrc.algorithms.odmr.shot_noise import simulate_photon_shot_noise
from bqrc.algorithms.odmr.spectrum import ODMRSpectrum


def make_spectrum(
    fluorescence: tuple[float, ...] = (1.0, 0.9, 0.8),
) -> ODMRSpectrum:
    """Create a controlled ideal ODMR spectrum."""
    frequencies = tuple(
        2869.0 + index for index in range(len(fluorescence))
    )
    return ODMRSpectrum(
        frequencies_mhz=frequencies,
        fluorescence=fluorescence,
    )


def test_seed_produces_reproducible_measurements() -> None:
    spectrum = make_spectrum()

    first = simulate_photon_shot_noise(
        spectrum, reference_photon_count=10_000.0, seed=42
    )
    second = simulate_photon_shot_noise(
        spectrum, reference_photon_count=10_000.0, seed=42
    )

    assert first == second


def test_photon_counts_are_nonnegative_integers() -> None:
    result = simulate_photon_shot_noise(
        make_spectrum(), reference_photon_count=1_000.0, seed=7
    )

    assert all(
        isinstance(count, int) and count >= 0
        for count in result.photon_counts
    )


def test_normalized_fluorescence_matches_photon_counts() -> None:
    reference_count = 10_000.0
    result = simulate_photon_shot_noise(
        make_spectrum(), reference_photon_count=reference_count, seed=123
    )

    assert result.fluorescence == pytest.approx(
        tuple(count / reference_count for count in result.photon_counts)
    )
    assert result.frequencies_mhz == (2869.0, 2870.0, 2871.0)


def test_zero_fluorescence_produces_zero_photons() -> None:
    result = simulate_photon_shot_noise(
        make_spectrum((0.0, 0.0, 0.0)),
        reference_photon_count=10_000.0,
        seed=42,
    )

    assert result.photon_counts == (0, 0, 0)
    assert result.fluorescence == (0.0, 0.0, 0.0)


def test_poisson_mean_and_variance() -> None:
    """Large sample should approximately follow Poisson statistics."""
    sample_count = 20_000
    expected_count = 100.0

    spectrum = make_spectrum((1.0,) * sample_count)
    result = simulate_photon_shot_noise(
        spectrum,
        reference_photon_count=expected_count,
        seed=2026,
    )

    counts = np.asarray(result.photon_counts, dtype=np.float64)

    assert float(np.mean(counts)) == pytest.approx(
        expected_count, rel=0.03
    )
    assert float(np.var(counts)) == pytest.approx(
        expected_count, rel=0.08
    )


def test_higher_photon_count_reduces_relative_noise() -> None:
    """Relative shot noise scales approximately as 1/sqrt(N)."""
    sample_count = 20_000
    spectrum = make_spectrum((1.0,) * sample_count)

    low = simulate_photon_shot_noise(
        spectrum, reference_photon_count=100.0, seed=11
    )
    high = simulate_photon_shot_noise(
        spectrum, reference_photon_count=10_000.0, seed=11
    )

    low_std = float(np.std(low.fluorescence))
    high_std = float(np.std(high.fluorescence))

    assert high_std < low_std
    assert high_std / low_std == pytest.approx(0.1, rel=0.15)


@pytest.mark.parametrize(
    "reference_count",
    [0.0, -1.0, float("nan"), float("inf")],
)
def test_invalid_reference_photon_count_rejected(
    reference_count: float,
) -> None:
    with pytest.raises(ValueError, match="reference_photon_count"):
        simulate_photon_shot_noise(
            make_spectrum(), reference_photon_count=reference_count
        )


@pytest.mark.parametrize(
    "fluorescence",
    [
        (-0.1,),
        (1.1,),
        (float("nan"),),
        (float("inf"),),
    ],
)
def test_invalid_fluorescence_rejected(
    fluorescence: tuple[float, ...],
) -> None:
    with pytest.raises(ValueError, match="ideal fluorescence"):
        simulate_photon_shot_noise(
            make_spectrum(fluorescence),
            reference_photon_count=1_000.0,
        )


def test_mismatched_spectrum_lengths_rejected() -> None:
    spectrum = ODMRSpectrum(
        frequencies_mhz=(2869.0, 2870.0),
        fluorescence=(0.9,),
    )

    with pytest.raises(ValueError, match="equal lengths"):
        simulate_photon_shot_noise(spectrum, 1_000.0)


def test_empty_spectrum_rejected() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        simulate_photon_shot_noise(make_spectrum(()), 1_000.0)


def test_nonfinite_frequency_rejected() -> None:
    spectrum = ODMRSpectrum(
        frequencies_mhz=(float("nan"),),
        fluorescence=(0.9,),
    )

    with pytest.raises(ValueError, match="frequency samples"):
        simulate_photon_shot_noise(spectrum, 1_000.0)


def test_noisy_fluorescence_is_finite_and_nonnegative() -> None:
    result = simulate_photon_shot_noise(
        make_spectrum(),
        reference_photon_count=10_000.0,
        seed=99,
    )

    assert all(
        isfinite(value) and value >= 0.0
        for value in result.fluorescence
    )
