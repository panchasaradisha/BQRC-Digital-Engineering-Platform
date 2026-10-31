
"""Simplified Lorentzian ODMR fluorescence spectrum model.

Frequency inputs are in MHz.
Output fluorescence is normalized and dimensionless.

The model uses two resonance frequencies from the
first-order NV-center resonance model.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from bqrc.sensors.nv.resonance import NVResonance


@dataclass(frozen=True)
class ODMRSpectrum:
    """Frequency samples and normalized fluorescence values."""

    frequencies_mhz: tuple[float, ...]
    fluorescence: tuple[float, ...]


def lorentzian(
    frequency_mhz: float,
    center_mhz: float,
    linewidth_mhz: float,
) -> float:
    """Evaluate a unit-height Lorentzian with FWHM linewidth."""

    if not all(
        isfinite(value)
        for value in (frequency_mhz, center_mhz, linewidth_mhz)
    ):
        raise ValueError("Lorentzian parameters must be finite")

    if linewidth_mhz <= 0.0:
        raise ValueError("linewidth_mhz must be positive")

    half_width = linewidth_mhz / 2.0
    normalized_offset = (frequency_mhz - center_mhz) / half_width

    return 1.0 / (1.0 + normalized_offset**2)


def simulate_odmr_spectrum(
    resonance: NVResonance,
    frequencies_mhz: tuple[float, ...],
    contrast: float = 0.1,
    linewidth_mhz: float = 1.0,
) -> ODMRSpectrum:
    """Simulate two Lorentzian dips in normalized fluorescence."""

    if not 0.0 <= contrast <= 0.5 or not isfinite(contrast):
        raise ValueError("contrast must be finite and between 0 and 0.5")

    if not isfinite(linewidth_mhz) or linewidth_mhz <= 0.0:
        raise ValueError("linewidth_mhz must be finite and positive")

    if not all(
        isfinite(value)
        for value in (
            resonance.lower_mhz,
            resonance.upper_mhz,
        )
    ):
        raise ValueError("resonance frequencies must be finite")

    if not frequencies_mhz:
        raise ValueError("frequencies_mhz must not be empty")

    if not all(isfinite(value) for value in frequencies_mhz):
        raise ValueError("frequency samples must be finite")

    fluorescence_values: list[float] = []

    for frequency in frequencies_mhz:
        lower_dip = lorentzian(
            frequency_mhz=frequency,
            center_mhz=resonance.lower_mhz,
            linewidth_mhz=linewidth_mhz,
        )

        upper_dip = lorentzian(
            frequency_mhz=frequency,
            center_mhz=resonance.upper_mhz,
            linewidth_mhz=linewidth_mhz,
        )

        fluorescence = 1.0 - contrast * (lower_dip + upper_dip)

        fluorescence_values.append(fluorescence)

    return ODMRSpectrum(
        frequencies_mhz=frequencies_mhz,
        fluorescence=tuple(fluorescence_values),
    )
