
"""Photon shot-noise simulation for ODMR fluorescence measurements.

Photon counts follow Poisson statistics.

The model assumes independent photon-count measurements at each
frequency sample, a fixed reference photon count, and ideal
photon detection apart from shot noise.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

import numpy as np

from bqrc.algorithms.odmr.spectrum import ODMRSpectrum


@dataclass(frozen=True, slots=True)
class NoisyODMRSpectrum:
    """Photon-count measurements and normalized noisy fluorescence."""

    frequencies_mhz: tuple[float, ...]
    photon_counts: tuple[int, ...]
    fluorescence: tuple[float, ...]
    reference_photon_count: float


def simulate_photon_shot_noise(
    spectrum: ODMRSpectrum,
    reference_photon_count: float,
    seed: int | None = None,
) -> NoisyODMRSpectrum:
    """Sample Poisson photon counts from an ideal ODMR spectrum.

    The reference photon count is the expected number of detected
    photons for normalized fluorescence equal to one.

    A seed provides reproducible simulated measurements.
    """

    if (
        not isfinite(reference_photon_count)
        or reference_photon_count <= 0.0
    ):
        raise ValueError(
            "reference_photon_count must be finite and positive"
        )

    if len(spectrum.frequencies_mhz) != len(spectrum.fluorescence):
        raise ValueError(
            "frequency and fluorescence arrays must have equal lengths"
        )

    if not spectrum.frequencies_mhz:
        raise ValueError("spectrum must not be empty")

    if not all(isfinite(value) for value in spectrum.frequencies_mhz):
        raise ValueError("frequency samples must be finite")

    if not all(
        isfinite(value) and 0.0 <= value <= 1.0
        for value in spectrum.fluorescence
    ):
        raise ValueError(
            "ideal fluorescence must be finite and between 0 and 1"
        )

    expected_counts = np.asarray(
        spectrum.fluorescence,
        dtype=np.float64,
    ) * reference_photon_count

    if not np.all(np.isfinite(expected_counts)):
        raise ValueError("expected photon counts must be finite")

    # NumPy's Poisson generator has an upper limit on lambda.
    if np.any(expected_counts > 1e15):
        raise ValueError(
            "expected photon counts exceed supported simulation range"
        )

    rng = np.random.default_rng(seed)
    counts = rng.poisson(expected_counts)

    photon_counts = tuple(int(count) for count in counts)
    measured_fluorescence = tuple(
        count / reference_photon_count
        for count in photon_counts
    )

    return NoisyODMRSpectrum(
        frequencies_mhz=spectrum.frequencies_mhz,
        photon_counts=photon_counts,
        fluorescence=measured_fluorescence,
        reference_photon_count=reference_photon_count,
    )
