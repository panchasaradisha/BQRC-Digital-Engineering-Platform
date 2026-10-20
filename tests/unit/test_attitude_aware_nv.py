
"""Tests for attitude-aware NV magnetometer simulation."""

from math import sqrt
from typing import cast

import pytest

from bqrc.environment.simulator import SpaceEnvironmentState
from bqrc.frames.attitude import Quaternion
from bqrc.sensors.nv.environment_adapter import (
    simulate_attitude_aware_nv_response,
    simulate_nv_environment_response,
)


class MockMagneticField:
    """Minimal NED magnetic-field representation."""

    north_nt = 30_000.0
    east_nt = 10_000.0
    down_nt = 40_000.0


class MockEnvironment:
    """Minimal environment for adapter testing."""

    magnetic_field = MockMagneticField()


def make_environment() -> SpaceEnvironmentState:
    """Return a controlled magnetic environment."""
    return cast(SpaceEnvironmentState, MockEnvironment())


def test_identity_attitude_matches_existing_adapter() -> None:
    environment = make_environment()
    frequencies = (2868.0, 2870.0, 2872.0)
    axis = (1.0, 0.0, 0.0)

    actual = simulate_attitude_aware_nv_response(
        environment=environment,
        nv_axis_body=axis,
        attitude_body_to_ned=Quaternion(1.0, 0.0, 0.0, 0.0),
        frequencies_mhz=frequencies,
    )

    expected = simulate_nv_environment_response(
        environment=environment,
        nv_axis_ned=axis,
        frequencies_mhz=frequencies,
    )

    assert actual.resonance == expected.resonance
    assert actual.spectrum == expected.spectrum


def test_ninety_degree_rotation_changes_projection() -> None:
    environment = make_environment()
    half_sqrt = sqrt(0.5)

    response = simulate_attitude_aware_nv_response(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=Quaternion(
            half_sqrt, 0.0, 0.0, half_sqrt
        ),
        frequencies_mhz=(2868.0, 2870.0, 2872.0),
    )

    # Body X rotates into local East (+NED Y).
    assert response.resonance.projected_field_nt == pytest.approx(
        10_000.0, abs=1e-8
    )


def test_inverse_rotation_changes_projection_sign() -> None:
    environment = make_environment()
    half_sqrt = sqrt(0.5)

    response = simulate_attitude_aware_nv_response(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=Quaternion(
            half_sqrt, 0.0, 0.0, -half_sqrt
        ),
        frequencies_mhz=(2868.0, 2870.0, 2872.0),
    )

    # Body X rotates into local West (-NED Y).
    assert response.resonance.projected_field_nt == pytest.approx(
        -10_000.0, abs=1e-8
    )


def test_attitude_changes_resonance_splitting() -> None:
    environment = make_environment()
    half_sqrt = sqrt(0.5)
    frequencies = (2868.0, 2870.0, 2872.0)

    identity = simulate_attitude_aware_nv_response(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=Quaternion(1.0, 0.0, 0.0, 0.0),
        frequencies_mhz=frequencies,
    )

    rotated = simulate_attitude_aware_nv_response(
        environment=environment,
        nv_axis_body=(1.0, 0.0, 0.0),
        attitude_body_to_ned=Quaternion(
            half_sqrt, 0.0, 0.0, half_sqrt
        ),
        frequencies_mhz=frequencies,
    )

    identity_splitting = (
        identity.resonance.upper_mhz - identity.resonance.lower_mhz
    )
    rotated_splitting = (
        rotated.resonance.upper_mhz - rotated.resonance.lower_mhz
    )

    assert identity_splitting > rotated_splitting
    assert identity.spectrum != rotated.spectrum
