
"""Unit tests for quantitative ODMR photon shot-noise metrics."""

from math import log10, sqrt

import pytest

from bqrc.algorithms.odmr.noise_metrics import analyze_odmr_noise
from bqrc.algorithms.odmr.shot_noise import (
    NoisyODMRSpectrum,
    simulate_photon_shot_noise,
)
from bqrc.algorithms.odmr.spectrum import ODMRSpectrum


def make_ideal(
    fluorescence: tuple[float, ...] = (1.0, 0.8, 0.6),
) -> ODMRSpectrum:
    """Build a controlled ideal ODMR spectrum."""
    return ODMRSpectrum(
        frequencies_mhz=tuple(
            2869.0 + index for index in range(len(fluorescence))
        ),
        fluorescence=fluorescence,
    )


def make_measured(
    fluorescence: tuple[float, ...] = (1.0, 0.9, 0.5),
    reference_count: float = 100.0,
) -> NoisyODMRSpectrum:
    """Build a photon-count-consistent measured spectrum."""
    return NoisyODMRSpectrum(
        frequencies_mhz=(2869.0, 2870.0, 2871.0),
        photon_counts=tuple(
            round(value * reference_count)
            for value in fluorescence
        ),
        fluorescence=fluorescence,
        reference_photon_count=reference_count,
    )


def test_rmse_matches_known_result() -> None:
    metrics = analyze_odmr_noise(
        make_ideal(),
        make_measured(),
    )

    expected_rmse = sqrt((0.0**2 + 0.1**2 + (-0.1) ** 2) / 3)

    assert metrics.rmse == pytest.approx(expected_rmse)


def test_theoretical_uncertainty_matches_poisson_formula() -> None:
    metrics = analyze_odmr_noise(
        make_ideal(),
        make_measured(),
    )

    assert metrics.theoretical_uncertainty == pytest.approx(
        (sqrt(1.0 / 100), sqrt(0.8 / 100), sqrt(0.6 / 100))
    )


def test_theoretical_rms_noise_matches_formula() -> None:
    metrics = analyze_odmr_noise(
        make_ideal(),
        make_measured(),
    )

    expected = sqrt((1.0 + 0.8 + 0.6) / (3 * 100))

    assert metrics.theoretical_rms_noise == pytest.approx(expected)


def test_theoretical_snr_matches_formula() -> None:
    metrics = analyze_odmr_noise(
        make_ideal(),
        make_measured(),
    )

    expected_signal_power = (1.0**2 + 0.8**2 + 0.6**2) / 3
    expected_noise_power = (1.0 + 0.8 + 0.6) / (3 * 100)

    assert metrics.theoretical_snr == pytest.approx(
        sqrt(expected_signal_power / expected_noise_power)
    )


def test_snr_db_matches_amplitude_conversion() -> None:
    metrics = analyze_odmr_noise(
        make_ideal(),
        make_measured(),
    )

    assert metrics.theoretical_snr_db == pytest.approx(
        20.0 * log10(metrics.theoretical_snr)
    )


def test_zero_error_produces_zero_rmse() -> None:
    metrics = analyze_odmr_noise(
        make_ideal(),
        make_measured((1.0, 0.8, 0.6)),
    )

    assert metrics.rmse == pytest.approx(0.0)


def test_higher_photon_budget_improves_theoretical_snr() -> None:
    ideal = make_ideal()

    low = analyze_odmr_noise(
        ideal,
        make_measured(reference_count=100.0),
    )

    high = analyze_odmr_noise(
        ideal,
        make_measured(
            fluorescence=(1.0, 0.9, 0.5),
            reference_count=10_000.0,
        ),
    )

    assert high.theoretical_snr == pytest.approx(
        10.0 * low.theoretical_snr
    )
    assert high.theoretical_rms_noise == pytest.approx(
        low.theoretical_rms_noise / 10.0
    )


def test_simulated_shot_noise_integrates_with_metrics() -> None:
    ideal = make_ideal()

    measured = simulate_photon_shot_noise(
        spectrum=ideal,
        reference_photon_count=10_000.0,
        seed=42,
    )

    metrics = analyze_odmr_noise(ideal, measured)

    assert metrics.rmse >= 0.0
    assert metrics.theoretical_rms_noise > 0.0
    assert metrics.theoretical_snr > 0.0


def test_mismatched_frequency_grids_rejected() -> None:
    measured = make_measured()

    mismatched = NoisyODMRSpectrum(
        frequencies_mhz=(2800.0, 2801.0, 2802.0),
        photon_counts=measured.photon_counts,
        fluorescence=measured.fluorescence,
        reference_photon_count=measured.reference_photon_count,
    )

    with pytest.raises(ValueError, match="frequency grids"):
        analyze_odmr_noise(make_ideal(), mismatched)


def test_empty_spectra_rejected() -> None:
    ideal = make_ideal(())
    measured = NoisyODMRSpectrum(
        frequencies_mhz=(),
        photon_counts=(),
        fluorescence=(),
        reference_photon_count=100.0,
    )

    with pytest.raises(ValueError, match="must not be empty"):
        analyze_odmr_noise(ideal, measured)


@pytest.mark.parametrize(
    "reference_count",
    [0.0, -1.0, float("nan"), float("inf")],
)
def test_invalid_reference_count_rejected(
    reference_count: float,
) -> None:
    """Reject invalid reference photon counts."""
    measured = NoisyODMRSpectrum(
        frequencies_mhz=(2869.0, 2870.0, 2871.0),
        photon_counts=(100, 90, 50),
        fluorescence=(1.0, 0.9, 0.5),
        reference_photon_count=reference_count,
    )

    with pytest.raises(ValueError, match="reference photon count"):
        analyze_odmr_noise(make_ideal(), measured)


@pytest.mark.parametrize(
    "fluorescence",
    [
        (-0.1, 0.8, 0.6),
        (1.1, 0.8, 0.6),
        (float("nan"), 0.8, 0.6),
    ],
)
def test_invalid_ideal_fluorescence_rejected(
    fluorescence: tuple[float, ...],
) -> None:
    with pytest.raises(ValueError, match="ideal fluorescence"):
        analyze_odmr_noise(
            make_ideal(fluorescence),
            make_measured(),
        )


def test_inconsistent_photon_counts_rejected() -> None:
    measured = NoisyODMRSpectrum(
        frequencies_mhz=(2869.0, 2870.0, 2871.0),
        photon_counts=(100, 80, 60),
        fluorescence=(1.0, 0.9, 0.6),
        reference_photon_count=100.0,
    )

    with pytest.raises(ValueError, match="normalized photon counts"):
        analyze_odmr_noise(make_ideal(), measured)


def test_zero_fluorescence_snr_is_undefined() -> None:
    ideal = make_ideal((0.0, 0.0, 0.0))
    measured = make_measured((0.0, 0.0, 0.0))

    with pytest.raises(ValueError, match="undefined"):
        analyze_odmr_noise(ideal, measured)
