"""NV measurement performance analysis on top of the NV sensor models.

These helpers combine sensor forward models (``bqrc.sensors.nv``) with
estimation-side analysis (``bqrc.algorithms.odmr``). They live in the
simulation layer, which may depend on both, so that ``sensors`` never
imports ``algorithms``.
"""

from __future__ import annotations

from dataclasses import dataclass

from bqrc.algorithms.odmr.noise_metrics import (
    ODMRNoiseMetrics,
    analyze_odmr_noise,
)
from bqrc.environment.simulator import SpaceEnvironmentState
from bqrc.frames.attitude import Quaternion
from bqrc.sensors.nv.environment_adapter import (
    NVMeasurementResponse,
    simulate_attitude_aware_nv_measurement,
    simulate_nv_measurement,
)


@dataclass(frozen=True, slots=True)
class NVPerformanceResponse:
    """NV photon measurement with quantitative noise performance."""

    measurement: NVMeasurementResponse
    metrics: ODMRNoiseMetrics


def simulate_nv_performance(
    environment: SpaceEnvironmentState,
    nv_axis_ned: tuple[float, float, float],
    frequencies_mhz: tuple[float, ...],
    reference_photon_count: float,
    contrast: float = 0.1,
    linewidth_mhz: float = 1.0,
    seed: int | None = None,
) -> NVPerformanceResponse:
    """Simulate NV measurement and analyze its photon shot noise.

    Metrics describe normalized ODMR fluorescence performance,
    not magnetic-field sensitivity.
    """

    measurement = simulate_nv_measurement(
        environment=environment,
        nv_axis_ned=nv_axis_ned,
        frequencies_mhz=frequencies_mhz,
        reference_photon_count=reference_photon_count,
        contrast=contrast,
        linewidth_mhz=linewidth_mhz,
        seed=seed,
    )

    metrics = analyze_odmr_noise(
        ideal=measurement.ideal.spectrum,
        measured=measurement.measured,
    )

    return NVPerformanceResponse(
        measurement=measurement,
        metrics=metrics,
    )


def simulate_attitude_aware_nv_performance(
    environment: SpaceEnvironmentState,
    nv_axis_body: tuple[float, float, float],
    attitude_body_to_ned: Quaternion,
    frequencies_mhz: tuple[float, ...],
    reference_photon_count: float,
    contrast: float = 0.1,
    linewidth_mhz: float = 1.0,
    seed: int | None = None,
) -> NVPerformanceResponse:
    """Analyze attitude-aware NV measurement performance."""

    measurement = simulate_attitude_aware_nv_measurement(
        environment=environment,
        nv_axis_body=nv_axis_body,
        attitude_body_to_ned=attitude_body_to_ned,
        frequencies_mhz=frequencies_mhz,
        reference_photon_count=reference_photon_count,
        contrast=contrast,
        linewidth_mhz=linewidth_mhz,
        seed=seed,
    )

    metrics = analyze_odmr_noise(
        ideal=measurement.ideal.spectrum,
        measured=measurement.measured,
    )

    return NVPerformanceResponse(
        measurement=measurement,
        metrics=metrics,
    )
