
"""Integration tests for NV photon measurement performance analysis."""

from math import sqrt
from types import SimpleNamespace
from typing import cast

import pytest

from bqrc.environment.simulator import SpaceEnvironmentState
from bqrc.frames.attitude import Quaternion
from bqrc.simulation.nv_performance import (
    simulate_attitude_aware_nv_performance,
    simulate_nv_measurement,
    simulate_nv_performance,
)

FREQUENCIES_MHZ = (
    2860.0,
    2865.0,
    2868.0,
    2870.0,
    2872.0,
    2875.0,
    2880.0,
)



def make_environment() -> SpaceEnvironmentState:
    """Create a controlled magnetic environment for NV tests."""
    return cast(
        SpaceEnvironmentState,
        SimpleNamespace(
            magnetic_field=SimpleNamespace(
                north_nt=30_000.0,
                east_nt=20_000.0,
                down_nt=40_000.0,
            )
        ),
    )



def test_performance_preserves_original_measurement() -> None:
    environment = make_environment()

    performance = simulate_nv_performance(
        environment=environment,
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES_MHZ,
        reference_photon_count=10_000.0,
        seed=42,
    )

    measurement = simulate_nv_measurement(
        environment=environment,
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES_MHZ,
        reference_photon_count=10_000.0,
        seed=42,
    )

    assert performance.measurement == measurement


def test_performance_metrics_match_measurement() -> None:
    performance = simulate_nv_performance(
        environment=make_environment(),
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES_MHZ,
        reference_photon_count=10_000.0,
        seed=42,
    )

    ideal = performance.measurement.ideal.spectrum.fluorescence
    measured = performance.measurement.measured.fluorescence

    expected_rmse = sqrt(
        sum(
            (measured_value - ideal_value) ** 2
            for ideal_value, measured_value in zip(
                ideal, measured, strict=True
            )
        )
        / len(ideal)
    )

    assert performance.metrics.rmse == pytest.approx(expected_rmse)


def test_performance_uncertainty_matches_poisson_model() -> None:
    performance = simulate_nv_performance(
        environment=make_environment(),
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES_MHZ,
        reference_photon_count=10_000.0,
        seed=42,
    )

    ideal = performance.measurement.ideal.spectrum.fluorescence

    expected = tuple(
        sqrt(value / 10_000.0) for value in ideal
    )

    assert performance.metrics.theoretical_uncertainty == pytest.approx(
        expected
    )


def test_higher_photon_budget_improves_snr() -> None:
    arguments = dict(
        environment=make_environment(),
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES_MHZ,
        seed=42,
    )

    low = simulate_nv_performance(
        **arguments,
        reference_photon_count=100.0,
    )
    high = simulate_nv_performance(
        **arguments,
        reference_photon_count=10_000.0,
    )

    assert high.metrics.theoretical_snr == pytest.approx(
        low.metrics.theoretical_snr * 10.0
    )


def test_attitude_identity_matches_ned_performance() -> None:
    environment = make_environment()

    ned = simulate_nv_performance(
        environment=environment,
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES_MHZ,
        reference_photon_count=10_000.0,
        seed=42,
    )

    body = simulate_attitude_aware_nv_performance(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=Quaternion(
            w=1.0, x=0.0, y=0.0, z=0.0
        ),
        frequencies_mhz=FREQUENCIES_MHZ,
        reference_photon_count=10_000.0,
        seed=42,
    )

    assert body == ned


def test_attitude_rotation_changes_resonance() -> None:
    environment = make_environment()

    identity = simulate_attitude_aware_nv_performance(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=Quaternion(
            w=1.0, x=0.0, y=0.0, z=0.0
        ),
        frequencies_mhz=FREQUENCIES_MHZ,
        reference_photon_count=10_000.0,
        seed=42,
    )

    rotated = simulate_attitude_aware_nv_performance(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=Quaternion(
            w=sqrt(0.5),
            x=0.0,
            y=0.0,
            z=sqrt(0.5),
        ),
        frequencies_mhz=FREQUENCIES_MHZ,
        reference_photon_count=10_000.0,
        seed=42,
    )

    assert (
        identity.measurement.ideal.resonance
        != rotated.measurement.ideal.resonance
    )


def test_performance_is_reproducible_with_seed() -> None:
    arguments = dict(
        environment=make_environment(),
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES_MHZ,
        reference_photon_count=10_000.0,
        seed=123,
    )

    first = simulate_nv_performance(**arguments)
    second = simulate_nv_performance(**arguments)

    assert first == second


@pytest.mark.parametrize(
    "reference_count",
    [0.0, -1.0, float("nan"), float("inf")],
)
def test_invalid_photon_budget_rejected(
    reference_count: float,
) -> None:
    with pytest.raises(ValueError):
        simulate_nv_performance(
            environment=make_environment(),
            nv_axis_ned=(1.0, 0.0, 0.0),
            frequencies_mhz=FREQUENCIES_MHZ,
            reference_photon_count=reference_count,
            seed=42,
        )
