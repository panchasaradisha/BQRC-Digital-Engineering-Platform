
"""Tests for ideal and photon-noisy NV measurements."""

from math import cos, pi, sin
from types import SimpleNamespace
from typing import Any, cast

import pytest

from bqrc.environment.simulator import SpaceEnvironmentState
from bqrc.frames.attitude import Quaternion
from bqrc.sensors.nv.environment_adapter import (
    simulate_attitude_aware_nv_measurement,
    simulate_nv_environment_response,
    simulate_nv_measurement,
)


def make_environment() -> SpaceEnvironmentState:
    """Create a controlled magnetic environment in NED coordinates."""
    magnetic_field = SimpleNamespace(
        north_nt=30_000.0,
        east_nt=20_000.0,
        down_nt=40_000.0,
    )
    return cast(
        SpaceEnvironmentState,
        cast(Any, SimpleNamespace(magnetic_field=magnetic_field)),
    )


FREQUENCIES = (2867.0, 2868.0, 2869.0, 2870.0, 2871.0, 2872.0, 2873.0)


def test_measurement_preserves_ideal_response() -> None:
    environment = make_environment()

    result = simulate_nv_measurement(
        environment=environment,
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES,
        reference_photon_count=10_000.0,
        seed=42,
    )

    expected = simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES,
    )

    assert result.ideal == expected


def test_measurement_is_reproducible() -> None:
    kwargs = dict(
        environment=make_environment(),
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES,
        reference_photon_count=10_000.0,
        seed=2026,
    )

    first = simulate_nv_measurement(**kwargs)
    second = simulate_nv_measurement(**kwargs)

    assert first == second


def test_measurement_preserves_frequency_grid() -> None:
    result = simulate_nv_measurement(
        environment=make_environment(),
        nv_axis_ned=(0.0, 1.0, 0.0),
        frequencies_mhz=FREQUENCIES,
        reference_photon_count=1_000.0,
        seed=7,
    )

    assert result.ideal.spectrum.frequencies_mhz == FREQUENCIES
    assert result.measured.frequencies_mhz == FREQUENCIES
    assert len(result.measured.photon_counts) == len(FREQUENCIES)


def test_measured_fluorescence_matches_counts() -> None:
    reference_count = 10_000.0

    result = simulate_nv_measurement(
        environment=make_environment(),
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES,
        reference_photon_count=reference_count,
        seed=99,
    )

    assert result.measured.fluorescence == pytest.approx(
        tuple(
            count / reference_count
            for count in result.measured.photon_counts
        )
    )


def test_identity_attitude_matches_ned_measurement() -> None:
    environment = make_environment()
    identity = Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)

    attitude_result = simulate_attitude_aware_nv_measurement(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=identity,
        frequencies_mhz=FREQUENCIES,
        reference_photon_count=10_000.0,
        seed=42,
    )

    ned_result = simulate_nv_measurement(
        environment=environment,
        nv_axis_ned=(1.0, 0.0, 0.0),
        frequencies_mhz=FREQUENCIES,
        reference_photon_count=10_000.0,
        seed=42,
    )

    assert attitude_result == ned_result


def test_attitude_rotation_changes_projected_field() -> None:
    environment = make_environment()

    identity = Quaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    rotation = Quaternion(
        w=cos(pi / 4.0),
        x=0.0,
        y=0.0,
        z=sin(pi / 4.0),
    )

    north_result = simulate_attitude_aware_nv_measurement(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=identity,
        frequencies_mhz=FREQUENCIES,
        reference_photon_count=10_000.0,
        seed=42,
    )

    east_result = simulate_attitude_aware_nv_measurement(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=rotation,
        frequencies_mhz=FREQUENCIES,
        reference_photon_count=10_000.0,
        seed=42,
    )

    assert north_result.ideal.resonance.projected_field_nt == pytest.approx(
        30_000.0
    )
    assert east_result.ideal.resonance.projected_field_nt == pytest.approx(
        20_000.0
    )
    assert north_result.ideal.resonance != east_result.ideal.resonance


def test_invalid_reference_count_propagates_error() -> None:
    with pytest.raises(ValueError, match="reference_photon_count"):
        simulate_nv_measurement(
            environment=make_environment(),
            nv_axis_ned=(1.0, 0.0, 0.0),
            frequencies_mhz=FREQUENCIES,
            reference_photon_count=0.0,
        )

