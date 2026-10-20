
"""Quantitative performance metrics for photon-noisy ODMR spectra.

All fluorescence values are normalized and dimensionless.

The theoretical uncertainty assumes independent Poisson photon
counts and a fixed, noise-free reference photon count.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log10, sqrt

from bqrc.algorithms.odmr.shot_noise import NoisyODMRSpectrum
from bqrc.algorithms.odmr.spectrum import ODMRSpectrum


@dataclass(frozen=True, slots=True)
class ODMRNoiseMetrics:
    """Statistical comparison of ideal and measured ODMR fluorescence."""

    rmse: float
    theoretical_uncertainty: tuple[float, ...]
    theoretical_rms_noise: float
    theoretical_snr: float
    theoretical_snr_db: float


def analyze_odmr_noise(
    ideal: ODMRSpectrum,
    measured: NoisyODMRSpectrum,
) -> ODMRNoiseMetrics:
    """Analyze photon shot-noise performance on matching frequency grids.

    SNR is the ideal RMS fluorescence divided by theoretical RMS
    photon shot noise. It is not ODMR contrast SNR or magnetic
    field sensitivity.

    A zero-noise, zero-signal case has undefined SNR and is rejected.
    """

    if not ideal.frequencies_mhz:
        raise ValueError("ODMR spectra must not be empty")

    if ideal.frequencies_mhz != measured.frequencies_mhz:
        raise ValueError("ideal and measured frequency grids must match")

    sample_count = len(ideal.frequencies_mhz)

    if (
        len(ideal.fluorescence) != sample_count
        or len(measured.fluorescence) != sample_count
        or len(measured.photon_counts) != sample_count
    ):
        raise ValueError("ODMR spectrum arrays must have matching lengths")

    if not all(isfinite(value) for value in ideal.frequencies_mhz):
        raise ValueError("frequency samples must be finite")

    if not all(
        isfinite(value) and 0.0 <= value <= 1.0
        for value in ideal.fluorescence
    ):
        raise ValueError(
            "ideal fluorescence must be finite and within [0, 1]"
        )

    if not all(
        isfinite(value) and value >= 0.0
        for value in measured.fluorescence
    ):
        raise ValueError(
            "measured fluorescence must be finite and nonnegative"
        )

    reference_count = measured.reference_photon_count

    if not isfinite(reference_count) or reference_count <= 0.0:
        raise ValueError(
            "reference photon count must be finite and positive"
        )

    if not all(
        isinstance(count, int)
        and not isinstance(count, bool)
        and count >= 0
        for count in measured.photon_counts
    ):
        raise ValueError(
            "photon counts must be nonnegative integers"
        )

    for count, fluorescence in zip(
        measured.photon_counts,
        measured.fluorescence,
        strict=True,
    ):
        normalized_count = count / reference_count

        if (
            not isfinite(normalized_count)
            or abs(fluorescence - normalized_count) > 1e-12
        ):
            raise ValueError(
                "measured fluorescence must match normalized photon counts"
            )

    squared_errors = [
        (measured_value - ideal_value) ** 2
        for ideal_value, measured_value in zip(
            ideal.fluorescence,
            measured.fluorescence,
            strict=True,
        )
    ]

    rmse = sqrt(
        sum(squared_errors) / sample_count
    )

    theoretical_uncertainty = tuple(
        sqrt(value / reference_count)
        for value in ideal.fluorescence
    )

    mean_noise_power = (
        sum(
            uncertainty**2
            for uncertainty in theoretical_uncertainty
        )
        / sample_count
    )

    theoretical_rms_noise = sqrt(mean_noise_power)

    mean_signal_power = (
        sum(value**2 for value in ideal.fluorescence)
        / sample_count
    )

    if theoretical_rms_noise == 0.0:
        raise ValueError(
            "theoretical SNR is undefined for zero fluorescence"
        )

    theoretical_snr = sqrt(
        mean_signal_power / mean_noise_power
    )

    theoretical_snr_db = 20.0 * log10(theoretical_snr)

    return ODMRNoiseMetrics(
        rmse=rmse,
        theoretical_uncertainty=theoretical_uncertainty,
        theoretical_rms_noise=theoretical_rms_noise,
        theoretical_snr=theoretical_snr,
        theoretical_snr_db=theoretical_snr_db,
    )
