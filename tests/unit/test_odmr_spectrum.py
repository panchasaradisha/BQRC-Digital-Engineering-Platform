
"""Unit tests for the simplified Lorentzian ODMR spectrum."""

from __future__ import annotations

from math import inf, nan

import pytest

from bqrc.algorithms.odmr.spectrum import (
    lorentzian,
    simulate_odmr_spectrum,
)
from bqrc.sensors.nv.resonance import (
    NVResonance,
    calculate_nv_resonance,
)


def test_lorentzian_peak() -> None:
    """A Lorentzian has unit height at its center."""

    assert lorentzian(2870.0, 2870.0, 1.0) == pytest.approx(
        1.0
    )


def test_lorentzian_half_maximum() -> None:
    """At half the FWHM offset, the response equals 0.5."""

    assert lorentzian(2870.5, 2870.0, 1.0) == pytest.approx(
        0.5
    )
    assert lorentzian(2869.5, 2870.0, 1.0) == pytest.approx(
        0.5
    )


def test_zero_contrast_produces_flat_spectrum() -> None:
    """Zero contrast gives unit normalized fluorescence."""

    resonance = NVResonance(
        lower_mhz=2869.0,
        upper_mhz=2871.0,
        projected_field_nt=0.0,
    )

    spectrum = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=(2868.0, 2870.0, 2872.0),
        contrast=0.0,
    )

    assert spectrum.fluorescence == (1.0, 1.0, 1.0)


def test_resonance_dips_are_symmetric() -> None:
    """Symmetric resonances produce symmetric fluorescence."""

    resonance = calculate_nv_resonance(
        magnetic_field_nt=(30_000.0, 0.0, 0.0),
        nv_axis=(1.0, 0.0, 0.0),
    )

    spectrum = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=(
            resonance.lower_mhz,
            resonance.upper_mhz,
        ),
    )

    assert spectrum.fluorescence[0] == pytest.approx(
        spectrum.fluorescence[1]
    )


def test_overlapping_resonances() -> None:
    """At zero splitting, both Lorentzians overlap."""

    resonance = calculate_nv_resonance(
        magnetic_field_nt=(0.0, 0.0, 0.0),
        nv_axis=(0.0, 0.0, 1.0),
    )

    spectrum = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=(2870.0,),
        contrast=0.1,
    )

    assert spectrum.fluorescence[0] == pytest.approx(0.8)


def test_maximum_contrast_stays_nonnegative() -> None:
    """The allowed contrast bound prevents negative fluorescence."""

    resonance = NVResonance(
        lower_mhz=2870.0,
        upper_mhz=2870.0,
        projected_field_nt=0.0,
    )

    spectrum = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=(2870.0,),
        contrast=0.5,
    )

    assert spectrum.fluorescence[0] == pytest.approx(0.0)


def test_frequency_order_is_preserved() -> None:
    """The simulator preserves the supplied frequency sample order."""

    resonance = NVResonance(
        lower_mhz=2869.0,
        upper_mhz=2871.0,
        projected_field_nt=0.0,
    )

    frequencies = (2872.0, 2868.0, 2870.0)

    spectrum = simulate_odmr_spectrum(
        resonance=resonance,
        frequencies_mhz=frequencies,
    )

    assert spectrum.frequencies_mhz == frequencies
    assert len(spectrum.fluorescence) == len(frequencies)


@pytest.mark.parametrize(
    ("contrast", "linewidth_mhz"),
    [
        (-0.1, 1.0),
        (0.6, 1.0),
        (nan, 1.0),
        (0.1, 0.0),
        (0.1, -1.0),
        (0.1, inf),
    ],
)
def test_invalid_spectrum_parameters(
    contrast: float,
    linewidth_mhz: float,
) -> None:
    """Invalid contrast or linewidth values must be rejected."""

    resonance = NVResonance(
        lower_mhz=2869.0,
        upper_mhz=2871.0,
        projected_field_nt=0.0,
    )

    with pytest.raises(ValueError):
        simulate_odmr_spectrum(
            resonance=resonance,
            frequencies_mhz=(2870.0,),
            contrast=contrast,
            linewidth_mhz=linewidth_mhz,
        )


def test_empty_frequency_samples_rejected() -> None:
    """An ODMR spectrum must contain at least one sample."""

    resonance = NVResonance(
        lower_mhz=2869.0,
        upper_mhz=2871.0,
        projected_field_nt=0.0,
    )

    with pytest.raises(ValueError):
        simulate_odmr_spectrum(
            resonance=resonance,
            frequencies_mhz=(),
        )


def test_nonfinite_frequency_rejected() -> None:
    """Nonfinite microwave frequency samples must be rejected."""

    resonance = NVResonance(
        lower_mhz=2869.0,
        upper_mhz=2871.0,
        projected_field_nt=0.0,
    )

    with pytest.raises(ValueError):
        simulate_odmr_spectrum(
            resonance=resonance,
            frequencies_mhz=(nan,),
        )


def test_nonfinite_resonance_rejected() -> None:
    """Invalid resonance frequencies must be rejected."""

    resonance = NVResonance(
        lower_mhz=nan,
        upper_mhz=2871.0,
        projected_field_nt=0.0,
    )

    with pytest.raises(ValueError):
        simulate_odmr_spectrum(
            resonance=resonance,
            frequencies_mhz=(2870.0,),
        )
